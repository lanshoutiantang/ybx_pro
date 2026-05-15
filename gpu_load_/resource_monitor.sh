#!/bin/bash

process_name="mcpl_tracking"
while true; do
    current_time=$(date "+%Y-%m-%d %H:%M:%S")
    echo "$current_time $(ps -C $process_name -o %cpu,%mem --no-headers)" >> resource_usage_${process_name}.log
    sleep 1
done