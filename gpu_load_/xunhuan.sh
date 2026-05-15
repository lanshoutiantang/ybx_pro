#!/bin/bash
##############################################################################
# 最终稳定版：无嵌套+Ctrl+C秒停+汇总日志保存+失败立即停止
# 核心优势：进程层级仅1层，无任何嵌套，停止无残留，无语法报错
##############################################################################

source setup.bash

# -------------------------- 可配置参数 --------------------------
RUN_CMD="rosa run stereo_depth_estimation imaging_from_local -- -c=/mnt/testdata/2026_project_data/stereo/shiyan_0916/stereo_params.json -l=/mnt/testdata/2026_project_data/stereo/shiyan_0916/left/big_bluebox_1_1743626872.475195160.png -r=/mnt/testdata/2026_project_data/stereo/shiyan_0916/right/big_bluebox_1_1743626872.475195160.png"  
LOG_DIR="./stereo_1h_logs"  # 每轮详细日志目录
# 汇总日志（带时间戳，避免覆盖）
SUMMARY_LOG="./stereo_1h_logs/test_summary_$(date +"%Y%m%d_%H%M%S").txt"
LOOP_INTERVAL=0             # 轮次间隔（秒）
TOTAL_TIME=180               # 总测试时间（秒）=30秒（注释和参数统一）
##############################################################################

# -------------------------- 关键：捕获Ctrl+C，秒停无残留 --------------------------
trap '
    echo -e "\n\n🛑 收到中断信号，正在停止测试..." | tee -a "$SUMMARY_LOG"
    exit 0
' SIGINT SIGQUIT  # 捕获Ctrl+C和Ctrl+\，强制终止

# 1. 路径检查（同时写入汇总日志）
LEFT_DIR="/mnt/testdata/2026_project_data/stereo/shiyan_0916/left/"
RIGHT_DIR="/mnt/testdata/2026_project_data/stereo/shiyan_0916/right/"
if [ ! -d "$LEFT_DIR" ] || [ ! -d "$RIGHT_DIR" ]; then
    echo "❌ 错误：左右图目录不存在！" | tee -a "$SUMMARY_LOG"
    exit 1
fi


# 2. 创建日志目录（确保汇总日志目录存在）
mkdir -p "$LOG_DIR" || {
    echo "❌ 日志目录创建失败！" | tee -a "$SUMMARY_LOG"
    exit 1
}

# 3. 初始化变量（记录测试启动时间）
start_time=$(date +%s)
run_count=0

# 4. 测试启动信息（屏幕+汇总日志同时输出）
{
echo "======================================================"
echo "  🔄 立体视觉串行循环测试（30秒+失败立即停止）"
echo "  核心逻辑：上一轮执行完才启动下一轮，Ctrl+C秒停"
echo "  原始指令：$RUN_CMD"
echo "  总时长：$TOTAL_TIME 秒（30秒）"
echo "  轮次间隔：$LOOP_INTERVAL 秒"
echo "  详细日志目录：$LOG_DIR"
echo "  汇总日志文件：$SUMMARY_LOG"
echo "  启动时间：$(date +"%Y-%m-%d %H:%M:%S")"
echo "  停止方式：Ctrl+C 手动停止 / 30秒到点自动停止 / 失败立即停止"
echo "======================================================"
echo ""
} | tee -a "$SUMMARY_LOG"

# -------------------------- 核心循环（无任何嵌套，简单直观） --------------------------
while true; do
    # 检查总时长，到点自动停止
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))
    if [ $elapsed_time -ge $TOTAL_TIME ]; then
        {
        echo -e "\n🎉 总时长已到（$elapsed_time 秒），测试正常结束！"
        echo "======================================================"
        } | tee -a "$SUMMARY_LOG"
        break
    fi

    # 执行一轮测试
    run_count=$((run_count + 1))
    timestamp=$(date +"%Y%m%d_%H%M%S_%N" | cut -c1-17)
    round_log="$LOG_DIR/round_${run_count}_${timestamp}.log"  # 每轮详细日志

    # 打印轮次信息（屏幕+汇总日志）
    {
    echo "------------------------------------------------------"
    echo "  🚀 第 $run_count 轮开始（已运行：$elapsed_time 秒）"
    echo "  📜 详细日志：$round_log"
    echo "------------------------------------------------------"
    } | tee -a "$SUMMARY_LOG"

    # 串行执行指令（详细日志写入文件，状态写入汇总日志）
    $RUN_CMD >> "$round_log" 2>&1
    exit_code=$?

    # 检查执行结果
    if [ $exit_code -eq 0 ]; then
        # 计算本轮耗时
        round_end=$(date +%s)
        round_duration=$((round_end - current_time))
        {
        echo "  ✅ 第 $run_count 轮执行成功！耗时：$round_duration 秒"
        } | tee -a "$SUMMARY_LOG"
    else
        {
        echo "  ❌ 第 $run_count 轮执行失败！"
        echo "  ❌ 详细错误日志：$round_log"
        echo "  ❌ 立即停止测试..."
        echo "======================================================"
        } | tee -a "$SUMMARY_LOG"
        exit 1  # 失败后退出，停止测试
    fi

    # 轮次间隔（可选）
    if [ $LOOP_INTERVAL -gt 0 ]; then
        {
        echo "  ⏳ 等待 $LOOP_INTERVAL 秒，准备下一轮..."
        } | tee -a "$SUMMARY_LOG"
        sleep $LOOP_INTERVAL
    fi

    echo "" | tee -a "$SUMMARY_LOG"
done

# -------------------------- 测试汇总 --------------------------
{
echo "  📊 测试汇总"
echo "  结束时间：$(date +"%Y-%m-%d %H:%M:%S")"
echo "  总执行轮次：$run_count"
echo "  汇总日志文件：$SUMMARY_LOG"
echo "  详细日志汇总：$LOG_DIR"
echo "======================================================"
} | tee -a "$SUMMARY_LOG"

