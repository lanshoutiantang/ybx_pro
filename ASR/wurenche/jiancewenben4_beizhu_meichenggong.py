#!/usr/bin/python
# -*- coding:utf-8 -*-
import ast
import os
import numpy as np
import re

import pandas as pd

if __name__ == '__main__':

    outer_path = r'D:\桌面\UBT\2024\bev\1.2.2xin\jieguo\map'
    filelist = os.listdir(outer_path)  # 列举文件
    print(filelist)
    total_num_file = len(filelist)  # label子文件的总数
    print(total_num_file)
    ddddd = pd.read_csv(r"D:\桌面\UBT\2024\bev\1.2.2xin\ssss________________________.csv")
    print(ddddd)
    #添加一行为0的元素
    new_row = pd.DataFrame({col: 0 for col in ddddd.columns}, index=ddddd.index)
    ddddd = pd.concat([ddddd, new_row], ignore_index=True)

    ddddd = ddddd.iloc[[8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]]
    print(ddddd)
    iiiii = 0
    for filename in filelist:
        # 将map_jieguo里面这个文件的内容也放到csv中，暂时先不搞了，手动输入吧
        file_path1 = os.path.join(outer_path, filename)
        with open(file_path1, "r") as f:
            read_data1 = f.read()
            print(read_data1)
            aa = read_data1.split('\n')
            dfaa = aa
            colaa = 2
            ii = 0
            print("sssssssssssssssssssssss", dfaa[len(dfaa) - 2])
            print(re.split(":", dfaa[1])[1])
            print(iiiii)
            ddddd.iloc[iiiii, 17] = re.split(":", dfaa[1])[1]
            # print(re.sub(r'[^0-9.]', "", re.split(",", dfaa[len(dfaa) - 2])[0]))
            while colaa < len(dfaa) - 2:
                print(re.split(" ", dfaa[colaa + 1])[1])
                # print(type(int(re.split(" ", dfaa[colaa+1])[1])))
                print(re.sub(r'[^0-9.]', "", re.split(",", dfaa[len(dfaa) - 2])[ii]))
                # print(type(float(re.sub(r'[^0-9.]', "", re.split(",", dfaa[len(dfaa) - 2])[ii]))))
                # ddddd.iloc[0][re.split(" ", dfaa[colaa+1])[1]] = re.sub(r'[^0-9.]', "", re.split(",", dfaa[len(dfaa) - 2])[ii])
                ddddd.iloc[iiiii, int(re.split(" ", dfaa[colaa + 1])[1])] = re.sub(r'[^0-9.]', "",
                                                                                   re.split(",", dfaa[len(dfaa) - 2])[
                                                                                       ii])
                # ddddd.iloc[0][int(re.split(" ", dfaa[colaa + 1])[1])] = float(
                #     re.sub(r'[^0-9.]', "", re.split(",", dfaa[len(dfaa) - 2])[ii]))
                colaa = colaa + 2
                ii = ii + 1
            print(ddddd)

        f.closed
        print(iiiii)
        iiiii = iiiii + 1
    # #----------------------------------------
    # # 只为了1.2.2版本和1.5.0版本作对比
    # # new:pedestrian	bicycle	motorcycle	tricycle	rider	car	truck	forklift	trailer	rack	shelves	traffic_cone	goods	traffic_light	other_vehicle	chitu	agv
    # # old:person	bicycle	car	bus	truck	forklift	trailer	rack	shelves	traffic_cone	cargo	traffic_light	other_vehicle	chitu	agv	tricycle
    # ddddd["motorcycle"] = 0
    # ddddd["rider"] = 0
    # oldlist = ["person","bicycle","motorcycle","tricycle","rider","car","truck","forklift","trailer","rack","shelves","traffic_cone","cargo",
    #            "traffic_light","other_vehicle","chitu","agv","bus","名称"]
    # ddddd = ddddd[oldlist]
    # #----------------------------------------
    ddddd.to_csv(r"D:\桌面\UBT\2024\bev\1.2.2xin\sssssssssssssssssssssssssssssssssssss.csv")
