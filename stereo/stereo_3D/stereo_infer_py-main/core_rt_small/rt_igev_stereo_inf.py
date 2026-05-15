import torch
import torch.nn as nn
import torch.nn.functional as F
from core_rt_small.update import BasicUpdateBlock
from core_rt_small.extractor import Feature
from core_rt_small.geometry import Geo_Encoding_Volume
from core_rt_small.submodule import *


try:
    autocast = torch.cuda.amp.autocast
except:
    class autocast:
        def __init__(self, enabled):
            pass
        def __enter__(self):
            pass
        def __exit__(self, *args):
            pass

class hourglass(nn.Module):
    def __init__(self, in_channels):
        super(hourglass, self).__init__()

        self.conv1 = nn.Sequential(BasicConv(in_channels, in_channels*2, is_3d=True, bn=True, relu=True, kernel_size=3,
                                             padding=1, stride=2, dilation=1),
                                   BasicConv(in_channels*2, in_channels*2, is_3d=True, bn=True, relu=True, kernel_size=3,
                                             padding=1, stride=1, dilation=1))
                                    
        self.conv2 = nn.Sequential(BasicConv(in_channels*2, in_channels*4, is_3d=True, bn=True, relu=True, kernel_size=3,
                                             padding=1, stride=2, dilation=1),
                                   BasicConv(in_channels*4, in_channels*4, is_3d=True, bn=True, relu=True, kernel_size=3,
                                             padding=1, stride=1, dilation=1))                             


        self.conv2_up = BasicConv(in_channels*4, in_channels*2, deconv=True, is_3d=True, bn=True,
                                  relu=True, kernel_size=(4, 4, 4), padding=(1, 1, 1), stride=(2, 2, 2))

        self.conv1_up = BasicConv(in_channels*2, 8, deconv=True, is_3d=True, bn=False,
                                  relu=False, kernel_size=(4, 4, 4), padding=(1, 1, 1), stride=(2, 2, 2))

        self.agg_0 = nn.Sequential(BasicConv(in_channels*4, in_channels*2, is_3d=True, kernel_size=1, padding=0, stride=1),
                                   BasicConv(in_channels*2, in_channels*2, is_3d=True, kernel_size=3, padding=1, stride=1),
                                   BasicConv(in_channels*2, in_channels*2, is_3d=True, kernel_size=3, padding=1, stride=1),)

        self.feature_att_16 = FeatureAtt(in_channels*2, 192)
        self.feature_att_32 = FeatureAtt(in_channels*4, 160)
        self.feature_att_up_16 = FeatureAtt(in_channels*2, 192)

    def forward(self, x, features):
        # print("aggregate")
        conv1 = self.conv1(x)
        conv1 = self.feature_att_16(conv1, features[1]) #16

        conv2 = self.conv2(conv1)
        conv2 = self.feature_att_32(conv2, features[2]) # 32

        # print(conv2.shape)
        
        conv2_up = self.conv2_up(conv2)
        conv1 = torch.cat((conv2_up, conv1), dim=1)
        conv1 = self.agg_0(conv1)
        conv1 = self.feature_att_up_16(conv1, features[1]) # 16

        conv = self.conv1_up(conv1) # 8

        return conv

class IGEVStereo(nn.Module):
    def __init__(self, args):
        super().__init__()
        self.args = args       
        context_dim = args.hidden_dim
        self.update_block = BasicUpdateBlock(self.args, hidden_dim=args.hidden_dim)
        self.hnet = nn.Sequential(BasicConv(128, args.hidden_dim, kernel_size=3, stride=1, padding=1),
                                     nn.Conv2d(args.hidden_dim, args.hidden_dim, 3, 1, 1, bias=False))

        self.cnet = BasicConv(128, context_dim, kernel_size=3, stride=1, padding=1)
        self.context_zqr_conv = nn.Conv2d(context_dim, context_dim*3, 3, padding=3//2)
        self.feature = Feature()

        self.stem_2 = nn.Sequential(
            BasicConv_IN(3, 32, kernel_size=3, stride=2, padding=1),
            nn.Conv2d(32, 32, 3, 1, 1, bias=False),
            nn.InstanceNorm2d(32), nn.ReLU()
            )
        self.stem_4 = nn.Sequential(
            BasicConv_IN(32, 48, kernel_size=3, stride=2, padding=1),
            nn.Conv2d(48, 48, 3, 1, 1, bias=False),
            nn.InstanceNorm2d(48), nn.ReLU()
            )
        
        self.stem_8 = nn.Sequential(
            BasicConv_IN(48, 64, kernel_size=3, stride=2, padding=1),
            nn.Conv2d(64, 64, 3, 1, 1, bias=False),
            nn.InstanceNorm2d(64), nn.ReLU()
            )

        self.spx_4_gru = Conv2x(32, 48, True)  # 1/8 → 1/4
        self.spx_2_gru = Conv2x(96, 32, True)  # 1/4 → 1/2
        self.spx_gru = nn.Sequential(nn.ConvTranspose2d(2*32, 9, kernel_size=4, stride=2, padding=1),)  # 1/2 → 1/1

        self.conv = BasicConv_IN(128, 96, kernel_size=3, padding=1, stride=1)
        self.desc = nn.Conv2d(96, 96, kernel_size=1, padding=0, stride=1)

        self.cost_agg = hourglass(8)
        self.classifier = nn.Conv3d(8, 1, 3, 1, 1, bias=False)

    def freeze_bn(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()

    def upsample_disp(self, disp, mask_feat_8, stem_2x, stem_4x):

        with autocast(enabled=self.args.mixed_precision, dtype=getattr(torch, self.args.precision_dtype, torch.float16)):
            # print(mask_feat_8.shape)
            # print(stem_4x.shape)
            xspx = self.spx_4_gru(mask_feat_8, stem_4x)
            xspx = self.spx_2_gru(xspx, stem_2x)
            spx_pred = self.spx_gru(xspx)
            spx_pred = F.softmax(spx_pred, 1)
            
            up_disp = context_upsample(disp*8., spx_pred)
        return up_disp


    def forward(self, image1, image2, iters=4, flow_init=None, test_mode=True):
        """ Estimate disparity between pair of frames """
        # print(iters)
        image1 = (2 * (image1 / 255.0) - 1.0).contiguous()
        image2 = (2 * (image2 / 255.0) - 1.0).contiguous()
        with autocast(enabled=self.args.mixed_precision, dtype=getattr(torch, self.args.precision_dtype, torch.float16)):
            features_left = self.feature(image1)
            features_right = self.feature(image2)
            
            stem_2x = self.stem_2(image1)
            stem_4x = self.stem_4(stem_2x)
            stem_8x = self.stem_8(stem_4x)
            
            stem_2y = self.stem_2(image2)
            stem_4y = self.stem_4(stem_2y)
            stem_8y = self.stem_8(stem_4y)
            
            features_left[0] = torch.cat((features_left[0], stem_8x), 1)
            features_right[0] = torch.cat((features_right[0], stem_8y), 1)

            match_left = self.desc(self.conv(features_left[0]))
            match_right = self.desc(self.conv(features_right[0]))
            gwc_volume = build_gwc_volume(match_left, match_right, self.args.max_disp//8, 8)
            
            # print(gwc_volume.shape)
            
            geo_encoding_volume = self.cost_agg(gwc_volume, features_left)

            # Init disp from geometry encoding volume
            prob = F.softmax(self.classifier(geo_encoding_volume).squeeze(1), dim=1)
            init_disp = disparity_regression(prob, self.args.max_disp//8, 1)
            
            del prob, gwc_volume

            hidden = self.hnet(features_left[0])
            net = torch.tanh(hidden)
            context = self.cnet(features_left[0])
            context = list(self.context_zqr_conv(context).split(split_size=self.args.hidden_dim, dim=1))


        geo_block = Geo_Encoding_Volume
        geo_fn = geo_block(geo_encoding_volume.float(), radius=self.args.corr_radius, num_levels=self.args.corr_levels)
        b, c, h, w = match_left.shape
        disp = init_disp
        disp_preds = []

        # GRUs iterations to update disparity
        for itr in range(iters):
            disp = disp.detach()
            geo_feat = geo_fn(disp)
            with autocast(enabled=self.args.mixed_precision, dtype=getattr(torch, self.args.precision_dtype, torch.float16)):
                net, mask_feat_8, delta_disp = self.update_block(net, context, geo_feat, disp)
            disp = disp + delta_disp
            if test_mode and itr < iters-1:
                continue

            # upsample predictions
            disp_up = self.upsample_disp(disp, mask_feat_8, stem_2x, stem_4x)
            disp_preds.append(disp_up)

        if test_mode:
            return disp_up

        init_disp = context_upsample(init_disp*8., spx_pred.float())
        return init_disp, disp_preds
