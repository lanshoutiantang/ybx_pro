#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import numpy as np
import re


if __name__ == '__main__':
	outer_path = r'D:\桌面\UBT\2024\WalkerS_FaceRec\3_11chongxinyanzheng\newcamera_0311_hou'
	folderlist = os.listdir(outer_path)          #列举文件夹
	# print(folderlist)
	for folder in folderlist:
		print(folder)
		inner_path = os.path.join(outer_path, folder) #获取子文件夹路径
		print(inner_path)
		total_num_folder = len(folderlist)       #子文件夹的总数
		print(total_num_folder)
		filelist = os.listdir(inner_path)        #列举子文件夹图片

		# rules = re.compile(r'\d+_', re.S)
		for filename in filelist:
					print("旧的名字是:\t"+filename)
					print("开始截取！")
					# 将后四位删除
					newFilename = re.sub('.jpg', '', str(filename))
					# 将.变成p
					newFilename1 = re.sub('\.', 'p', newFilename)
					newFilename2 = str(newFilename1) + ".jpg"
					# 输出保留的内容
					print("新名字是:\t"+newFilename2)
					print("开始改名。。。")
					os.rename(os.path.join(inner_path, filename), os.path.join(inner_path, newFilename2))
					print("改名完毕！")





		# filelist_sort = list(np.zeros(len(filelist))) #获取列表1*n,n为当前文件夹图片数量
		# print('np.zeros(len(filelist)):',np.zeros(len(filelist)))
		# print('list(np.zeros(len(filelist))):',list(np.zeros(len(filelist))))
		# index_list = []
		# end_list = []
		# for item in filelist:
		# 	name, end = os.path.splitext(item)#将文件名和后缀分开
		# 	index_list.append(int(name)) #获取所有图片name列表，乱序
		# 	end_list.append(end)#获取所有图片后缀列表
		# max_index = max(index_list)
		# print('max_index:',max_index)
		# print('index_list:',index_list)
		# print('end_list:',end_list)
		# j = 0
		# for i in range(max_index+1):
		# 	if i in index_list:  #如果i在name列表中
		# 		filelist_sort[j] = str(i) + end_list[index_list.index(i)]
		# 		print('str(i):',str(i))
		# 		print('end_list[index_list.index(i):',end_list[index_list.index(i)]) #i对应后缀
		# 		print('filelist_sort[j]:',filelist_sort[j])#i+后缀，即name+后缀
		# 		j += 1
		# print('filelist_sort:',filelist_sort)#获取所有图片name+后缀列表，正序由小到大
		# assert len(filelist) == len(filelist_sort), 'Lengths are not same:{}, {}'.format(len(filelist), len(filelist_sort))#报警保证排序后和原列表一样长
		# print('(len(rotation_list)*len(distance_list):',(len(rotation_list)*len(distance_list)))
		# print('len(filelist)/(len(rotation_list)*len(distance_list):',len(filelist)/(len(rotation_list)*len(distance_list)))
		# for i in range(int(len(filelist)/(len(rotation_list)*len(distance_list)))+1):
		# 	for j, d in enumerate(distance_list):
		# 		for k, r in enumerate(rotation_list):
		# 			index = i*len(rotation_list)*len(distance_list) + j *len(rotation_list) + k
		# 			if index >= len(filelist_sort):
		# 				print("Reach the end of the list!")
		# 				break
		# 			item = filelist_sort[index]
		# 			print(item, j, d, k, r)#61.jpg 0 0.5 0 0 /62.jpg 0 0.5 1 0 /63.jpg 0 0.5 2 15/ 64.jpg 0 0.5 3 15 /65.jpg 0 0.5 4 30
		#
		# 			name, end = os.path.splitext(item)
		# 			name = name + "_" + str(d) + "_" + str(r)
		# 			dst = os.path.join(inner_path, name+end)
		# 			# print(name, end, dst)
		# 			os.rename(os.path.join(inner_path, item), dst)
