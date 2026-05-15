#!/bin/bash
# 实时进程CPU/内存监控脚本（TOP瞬时值+进程退出自动重启）
# 用法: ./monitor.sh <进程名或PID> （按Ctrl+C停止，完全保持原输入方式）

# 配置（可按需修改）
INTERVAL=1  # 采集间隔（1秒/次，实时性最优）
LOG_FILE="$(cd $(dirname "$0") && pwd)/process_monitor_$(date +%Y%m%d_%H%M%S).log"  # 日志带时间戳
MAX_RESTART=0  # 最大重启次数（避免无限重启，0表示无限制）
RESTART_INTERVAL=3  # 重启间隔（秒，防止频繁重启）

# 入参校验（完全保持原有格式，仅需1个参数）
[ $# -ne 1 ] && { echo "用法: $0 <进程名/PID>"; exit 1; }
TARGET=$1
PID=""
START_CMD=""  # 自动获取的进程启动命令
RESTART_COUNT=0  # 重启计数器

# 核心函数：获取PID + 对应的完整启动命令
get_pid_and_cmd() {
    # 情况1：输入的是PID
    if [[ $TARGET =~ ^[0-9]+$ ]]; then
        if ps -p $TARGET >/dev/null; then
            PID=$TARGET
            # 自动获取进程完整启动命令（排除ps自身进程，取原始命令）
            START_CMD=$(ps -p $PID -o cmd= | sed 's/^ *//; s/ *$//')
            [ -n "$START_CMD" ] && return 0
            echo "错误：无法获取PID $PID 的启动命令，无法自动重启" | tee -a "$LOG_FILE"
            exit 1
        else
            echo "错误：PID $TARGET 不存在" | tee -a "$LOG_FILE"
            exit 1
        fi
    # 情况2：输入的是进程名
    else
        PID=$(pgrep -x $TARGET | head -n1)
        if [ -n "$PID" ]; then
            # 自动获取进程完整启动命令
            START_CMD=$(ps -p $PID -o cmd= | sed 's/^ *//; s/ *$//')
            [ -n "$START_CMD" ] && return 0
            echo "错误：无法获取进程 $TARGET（PID:$PID）的启动命令，无法自动重启" | tee -a "$LOG_FILE"
            exit 1
        else
            echo "进程 $TARGET 未运行，尝试查找默认启动命令..." | tee -a "$LOG_FILE"
            # 尝试通过which查找可执行文件（仅适用于系统全局命令，如rosa）
            EXEC_PATH=$(which $TARGET 2>/dev/null)
            if [ -n "$EXEC_PATH" ]; then
                START_CMD=$EXEC_PATH  # 若为简单命令（无参数），直接用可执行路径启动
                echo "找到默认启动路径：$START_CMD（无额外参数，若需自定义参数请手动修改脚本）" | tee -a "$LOG_FILE"
                return 1  # 标记需要启动进程
            else
                echo "错误：未找到进程 $TARGET 的启动命令，无法启动" | tee -a "$LOG_FILE"
                exit 1
            fi
        fi
    fi
}

# 核心函数：启动进程并重新获取PID+命令
start_process() {
    # 检查最大重启次数
    if [ $MAX_RESTART -ne 0 ] && [ $RESTART_COUNT -ge $MAX_RESTART ]; then
        echo -e "\n❌ 已达到最大重启次数（$MAX_RESTART 次），停止尝试！" | tee -a "$LOG_FILE"
        exit 1
    fi

    # 执行启动命令（后台运行，不阻塞监控）
    echo -e "\n🚀 执行启动命令：$START_CMD" | tee -a "$LOG_FILE"
    eval $START_CMD &
    sleep 2  # 等待进程启动稳定

    # 重新获取PID和启动命令
    new_pid=$(pgrep -x $TARGET | head -n1)
    if [ -z "$new_pid" ]; then
        RESTART_COUNT=$((RESTART_COUNT + 1))
        echo "❌ 进程启动失败！$RESTART_COUNT 次重启尝试（间隔 $RESTART_INTERVAL 秒）" | tee -a "$LOG_FILE"
        sleep $RESTART_INTERVAL
        start_process  # 递归重试启动
    else
        PID=$new_pid
        # 重新获取启动命令（确保与新进程匹配）
        START_CMD=$(ps -p $PID -o cmd= | sed 's/^ *//; s/ *$//')
        RESTART_COUNT=$((RESTART_COUNT + 1))
        restart_info="✅ 进程启动成功！新PID: $PID | 累计重启次数: $RESTART_COUNT | 启动命令: $START_CMD"
        echo $restart_info | tee -a "$LOG_FILE"
        echo "-------------------------------"
    fi
}

# 初始化：获取初始PID和启动命令
get_pid_and_cmd
# 若进程未运行，启动进程
if [ -z "$PID" ]; then
    start_process
fi

# 初始化日志（新增重启记录字段）
echo "时间,瞬时%CPU,瞬时%MEM,重启次数,PID,启动命令" > "$LOG_FILE"

# 优雅退出（保留日志路径）
trap 'echo -e "\n🛑 监控停止！日志文件：$LOG_FILE"; exit 0' SIGINT SIGTERM

# 启动提示（保持原有风格，仅补充重启相关信息）
echo "=== 实时监控（进程退出自动重启）==="
echo "监控目标：$TARGET | 当前PID: $PID"
echo "启动命令：$START_CMD"
echo "采集间隔：${INTERVAL}秒 | 日志：$LOG_FILE"
echo "最大重启次数：${MAX_RESTART}次（0=无限制） | 重启间隔：${RESTART_INTERVAL}秒"
echo "按 Ctrl+C 停止监控"
echo "========================"
echo "时间                 瞬时%CPU  瞬时%MEM  重启次数  PID"
echo "---------------------------------------------------"

# 核心监控循环（保持原有采集逻辑，新增自动重启）
while true; do
    # 检查进程存活，退出则自动重启
    if ! ps -p $PID >/dev/null; then
        echo -e "\n⚠️  检测到进程 $PID 已退出！" | tee -a "$LOG_FILE"
        start_process  # 自动重启进程
    fi
    
    # 采集瞬时CPU/内存（保持原有逻辑，无延迟）
    read CPU MEM <<< $(top -bn1 -p $PID | awk -v p="$PID" '$1==p{print $9+0, $10+0; exit}')
    
    # 异常值兜底（避免脚本中断）
    CPU=${CPU:-0.0}
    MEM=${MEM:-0.0}
    
    # 格式化输出（保持原有对齐风格，新增重启次数和PID）
    CURRENT_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    printf "%-20s %6.1f %8.1f %8d %8d\n" "$CURRENT_TIME" "$CPU" "$MEM" "$RESTART_COUNT" "$PID"
    
    # 写入日志（记录关键信息，便于分析）
    echo "$CURRENT_TIME,$CPU,$MEM,$RESTART_COUNT,$PID,$START_CMD" >> "$LOG_FILE"
    
    # 按间隔采集（保持原有实时性）
    sleep $INTERVAL
done

