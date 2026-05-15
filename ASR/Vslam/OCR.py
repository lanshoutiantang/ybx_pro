import re

import openpyxl
import pandas as pd







def ocr_shuju(data,string):
    # 读取文件
    # # 标识文件
    # data = pd.read_csv(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/内容.csv", sep='\t', header=None,encoding="utf-8")
    print(data)
    # data = data.drop(0)
    # data["1"] = data[0].apply(lambda x: x.split(",")[0])
    # data["2"] = data[0].apply(lambda x: x.split(",")[1])
    # 去掉空格
    data["2"] = data["2"].apply(lambda x: str(x).replace(" ",""))
    # data2["2"] = data2["2"].apply(lambda x: "".join(list(filter(str.isalpha, x))))
    print(data["1"])
    print(data["2"])
    data["3"] = data["2"].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    data["4"] = data["2"].apply(lambda x: x.translate(x.maketrans("", "", "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")))
    print(data["3"])
    # data2["5"] = data2["2"].apply(lambda x: str(x).replace("[^a-z^A-Z]",""))
    data["5"] = data["2"].apply(lambda x: re.sub("[^a-z^A-Z]", "", str(x)))

    # # 预测文件
    # data1 = pd.read_csv(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/ocr_res.csv", sep='\t', header=None, encoding="utf-8")
    # print(data1)


    # 输出
    data.to_excel(str('D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/'+string+'_output4.xlsx'))

    return data

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # # 标识文件
    # data2 = pd.read_csv(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/内容.csv", sep='\t', header=None, encoding="utf-8")
    # data2 = data2.drop(0)
    #
    # data2.to_excel(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/data3_output4.xlsx")
    # data2["1"] = data2[0].apply(lambda x: x.split(",")[0])
    # data2["1"] = data2["1"].apply(lambda x: x.split(".")[0]+".jpg")
    # data2["2"] = data2[0].apply(lambda x: x.split(",")[1])
    # print(data2["2"])
    # da2 = ocr_shuju(data2, "data2")
    # # 预测文件
    # data1 = pd.read_csv(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/ocr_res.csv", sep='\t')
    # data1.iloc[0] = ['1.jpg    USTECHI保持工位环境卫生以下物品可酒精消毒']
    # data1 = data1.rename(columns={'1.jpg    USTECHI保持工位环境卫生以下物品可酒精消毒': '0'})
    # print(data1.columns)
    # data1["1"] = data1['0'].apply(lambda x: x.split("jpg")[0]+"jpg")
    # data1["2"] = data1['0'].apply(lambda x: x.split("jpg")[1])
    # da1 = ocr_shuju(data1, "data1")
    #
    #
    # print(da1)
    # print(da2)
    # # 合并数据
    # da3 = pd.merge(da1, da2,  left_on="1", right_on="1" )
    # print(da3.iloc[:, [0, 1]])
    # da3.to_excel(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/data3_output4.xlsx")
    # da4 = da3[["0", "2_x", "2_y"]]
    # da4["2_x"] = da4["2_x"].apply(lambda x: re.sub(r'[\s，。？?！“”‘’\[\]…：；:（）·()￥#／,+！！!&|【丨℃!」|'：“”、，；：/：；、，￥《》/、+—.．*~～＿－-]', '', x))
    # da4["2_y"] = da4["2_y"].apply(lambda x: re.sub(r'[\s，。？?！“”‘’\[\]…：；:（）·()￥#／,+！！!&|【丨℃!」|'：“”、，；：/：；、，￥《》/、+—.．*~～＿－-]', '', x))
    # print(da4)
    # da4.to_excel(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/da3_output4.xlsx")


    # 处理好的数据，再进行分割
    data6 = pd.read_excel(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/da3_output4 - 副本.xlsx")
    print(data6)
    data6 = data6.fillna('')
    data6["3_x"] = data6["2_x"].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    data6["4_x"] = data6["2_x"].apply(lambda x: x.translate(x.maketrans("", "", "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")))
    data6["5_x"] = data6["2_x"].apply(lambda x: re.sub("[^a-z^A-Z]", "", str(x)))
    data6["3_y"] = data6["2_y"].apply(lambda x: "".join(list(filter(str.isdigit, x))))
    data6["4_y"] = data6["2_y"].apply(lambda x: x.translate(x.maketrans("", "", "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")))
    data6["5_y"] = data6["2_y"].apply(lambda x: re.sub("[^a-z^A-Z]", "", str(x)))

    data6.to_excel(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/da7_output4.xlsx")
    # 加入后缀音频标识文本
    data6["tupian"] = data6["0"].apply(lambda x: x.split(" ")[0])
    print(data6["tupian"])
    data6["2_x"] = data6["2_x"] + "(" + data6["tupian"] + ")"
    data6["3_x"] = data6["3_x"] + "(" + data6["tupian"] + ")"
    data6["4_x"] = data6["4_x"] + "(" + data6["tupian"] + ")"
    data6["5_x"] = data6["5_x"] + "(" + data6["tupian"] + ")"
    data6["2_y"] = data6["2_y"] + "(" + data6["tupian"] + ")"
    data6["3_y"] = data6["3_y"] + "(" + data6["tupian"] + ")"
    data6["4_y"] = data6["4_y"] + "(" + data6["tupian"] + ")"
    data6["5_y"] = data6["5_y"] + "(" + data6["tupian"] + ")"
    data6.to_excel(r"D:/桌面/UBT/语义3期slam/Semantic_VSLAM_OCR/第三版/da8_output4.xlsx")