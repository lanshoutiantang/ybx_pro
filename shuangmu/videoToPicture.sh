#!/bin/bash

directory="../videoOut" # 指定要遍历的目录路径
dirOut="../videoOutPicture" #创建路径
echo "$dirOut"
if [ ! -d "$dirOut" ]; then
    mkdir "$dirOut"
else
    rm -rf "$dirOut"
fi

for file in $directory/*; do   # 通过*获取该目录下所有文件或子目录
    if [ -f "$file" ]; then     # 判断当前元素是否为文件（非目录）
        echo "这是一个文件：$file"
        # 其他操作...
    elif [ -d "$file" ]; then   # 判断当前元素是否为目录
        echo "这是一个目录：$file"
        # 进入子目录并再次调用此脚本
    wbwenjianming1=$(echo $file | cut -d "/" -f 3) #
    echo "$wbwenjianming1"
    directory2=""$dirOut"/"$wbwenjianming1""
    echo "$directory2"
    if [ ! -d "$directory2" ]; then
        mkdir "$directory2"
    fi
	for filezi in $file/*; do   # 通过*获取该目录下所有文件或子目录
	    if [ -f "$filezi" ]; then     # 判断当前元素是否为文件（非目录）
		echo "这是一个文件：$filezi"
	    elif [ -d "$filezi" ]; then   # 判断当前元素是否为目录
		echo "这是一个目录：$filezi"
		# 取字段名
		file_path="$filezi"
		wenjianming=$(echo $file_path | cut -d "/" -f 4) #
        echo "$wenjianming"
		directory1=""$dirOut"/"$wbwenjianming1"/"$wenjianming""
		echo "$directory1"
        if [ ! -d "$directory1" ]; then
            mkdir "$directory1"
		fi
		# # 进入子目录并再次调用此脚本
        # ./trt_infer $filezi $directory1
	    fi
	done
    fi
done