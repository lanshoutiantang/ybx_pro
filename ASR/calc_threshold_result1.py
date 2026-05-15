import os
import pandas as pd
import pdb

### infos格式['47', '47', 0.887249]，通过阈值去计算接受率，准确率，虚警率
def calc_threshold_acc(f1_infos, f2_infos, threshold):
	### 先用f1_infos统计接受率，准确率
	### log_show
	log_show_fl = True if threshold==0.75 else False
	total_num = len(f1_infos)
	accept_num = 0
	correct_num = 0
	for i in range(total_num):
		info = f1_infos[i]
		if info[2]>threshold:
			accept_num += 1
			if info[0] == info[1]:   #只有接受了才统计准确率
				correct_num +=1
			else:
				if log_show_fl:
				 print('line%d have error_rec!'%i)
		else:
			if log_show_fl:
				print('line%d fail to rec!'%i)
	accept_rate = float(accept_num)/float(total_num)
	accept_num = 0.000001 if accept_num==0 else accept_num
	correct_rate = float(correct_num)/float(accept_num) 	
	### 用f2_infos统计虚警率
	total_num2 = len(f2_infos)
	alarm_num = 0
	for i in range(total_num2):
		info = f2_infos[i]
		if info[2]>threshold:
			alarm_num += 1
	alarm_rate = float(alarm_num)/float(total_num2)
	return accept_rate, correct_rate, alarm_rate
	N = 1

### 输入文本,输出infos格式的list
def read_infos(filename):
	f1 = open(filename, 'r')
	f1_lines = f1.readlines()
	### f1_infos [rec_name,  regname,  score] like ['47', '47', 0.887249]
	f1_infos = []   
	for line in f1_lines:
		info = line.strip().split('\t')
		info[0] = info[0].split('/')[0]
		info[1] = info[1].split('/')[0]
		info[2] = float(info[2])
		f1_infos.append(info)  
	return f1_infos

if __name__ == '__main__':
	file1 = r'D:\桌面\UBT\2024\WalkerS_FaceRec\3_11chongxinyanzheng\dierci_lm\0_3_zhenglian\rec_info.txt'  ###库内阈值文件
	file2 = r'D:\桌面\UBT\2024\WalkerS_FaceRec\3_11chongxinyanzheng\dierci_lm\0_3_zhenglian\unreg_info.txt'  ###库外阈值文件
	file_out = r'D:\桌面\UBT\2024\WalkerS_FaceRec\3_11chongxinyanzheng\dierci_lm\0_3_zhenglian\threshold_result.xlsx'  ###输出结果文件
	f1_infos = read_infos(file1)
	f2_infos = read_infos(file2)
	
	#threshold =0.75
	res_combine = []
	for threshold in range(50,100):
		threshold = float(threshold)/100
		res = calc_threshold_acc(f1_infos, f2_infos, threshold)
		res = [threshold, res[0], res[1], res[2]]
		res_combine.append(res)

	out_res = pd.DataFrame(res_combine)
	
	out_res.to_excel(file_out)
	print('finish!')
	#pdb.set_trace()
	




