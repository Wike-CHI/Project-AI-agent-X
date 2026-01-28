#!/bin/bash
#===============================================================================
# Qwen 2.5 3B 性能测试脚本
# 用法: bash qwen_performance_test.sh [测试类型]
#
# 测试类型:
#   all     - 运行所有测试 (默认)
#   memory  - 仅内存测试
#   speed   - 仅速度测试
#   concurrent - 仅并发测试
#===============================================================================

set -e

# 配置
MODEL_NAME="qwen2.5:3b-instruct-q4_0"
OLLAMA_HOST="http://localhost:11434"
TEST_OUTPUT_DIR="./test_results"
DURATION_SECONDS=60

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 创建输出目录
mkdir -p "$TEST_OUTPUT_DIR"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

#-------------------------------------------------------------------------------
# 测试 1: 内存占用测试
#-------------------------------------------------------------------------------
test_memory() {
    log_info "开始内存占用测试..."

    local output_file="$TEST_OUTPUT_DIR/memory_test_$(date +%Y%m%d_%H%M%S).txt"
    local pid_file="$TEST_OUTPUT_DIR/ollama_pid.txt"

    # 检查ollama是否运行
    if curl -s "$OLLAMA_HOST/api/version" > /dev/null 2>&1; then
        log_info "Ollama 已在运行，停止它进行冷启动测试..."
        pkill -f "ollama serve" || true
        sleep 2
    fi

    # 启动ollama
    log_info "启动 Ollama..."
    OLLAMA_HOST=$OLLAMA_HOST nohup ollama serve > "$TEST_OUTPUT_DIR/ollama.log" 2>&1 &
    OLLAMA_PID=$!
    echo $OLLAMA_PID > "$pid_file"

    # 等待ollama启动
    for i in {1..30}; do
        if curl -s "$OLLAMA_HOST/api/version" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    if ! curl -s "$OLLAMA_HOST/api/version" > /dev/null 2>&1; then
        log_error "Ollama 启动失败"
        cat "$TEST_OUTPUT_DIR/ollama.log"
        return 1
    fi

    log_info "Ollama 启动成功，PID: $OLLAMA_PID"

    # 加载模型
    log_info "加载模型 $MODEL_NAME..."
    load_start=$(date +%s)
    curl -s "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$MODEL_NAME\"}" > /dev/null
    load_end=$(date +%s)
    load_time=$((load_end - load_start))
    log_info "模型加载时间: ${load_time}秒"

    # 运行模型（生成测试响应）
    log_info "运行模型并监控内存..."
    test_prompt="你好，请简单介绍一下你自己，保持简短，50字以内。"

    # 启动测试请求
    curl -s "$OLLAMA_HOST/api/generate" \
        -d "{\"model\": \"$MODEL_NAME\", \"prompt\": \"$test_prompt\", \"stream\": false}" &
    TEST_PID=$!

    # 等待模型开始处理
    sleep 3

    # 收集内存数据
    {
        echo "timestamp,memory_mb,cpu_percent"
        for i in {1..30}; do
            if ps -p $TEST_PID > /dev/null 2>&1; then
                timestamp=$(date +%s)
                # 获取Ollama相关进程的内存
                memory=$(ps -p $OLLAMA_PID -o rss= 2>/dev/null || echo "0")
                memory_kb=${memory:-0}
                memory_mb=$((memory_kb / 1024))
                cpu=$(ps -p $OLLAMA_PID -o %cpu= 2>/dev/null || echo "0")
                echo "$timestamp,$memory_mb,$cpu"
            fi
            sleep 1
        done
    } > "$output_file"

    # 等待测试完成
    wait $TEST_PID 2>/dev/null || true

    # 分析结果
    log_info "分析内存测试结果..."

    local max_memory=$(awk -F',' 'NR>1 {print $2}' "$output_file" | sort -n | tail -1)
    local avg_memory=$(awk -F',' 'NR>1 {sum+=$2; count++} END {print int(sum/count)}' "$output_file")

    echo ""
    echo "========================================"
    echo "         内存测试结果"
    echo "========================================"
    echo "最大内存占用: ${max_memory} MB"
    echo "平均内存占用: ${avg_memory} MB"
    echo "目标: < 4GB (含系统)"
    echo ""

    if [ "${max_memory}" -lt 4096 ]; then
        log_success "内存测试通过！"
        return 0
    else
        log_warn "内存占用较高，可能需要优化"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# 测试 2: 推理速度测试
#-------------------------------------------------------------------------------
test_speed() {
    log_info "开始推理速度测试..."

    local output_file="$TEST_OUTPUT_DIR/speed_test_$(date +%Y%m%d_%H%M%S).txt"

    # 测试用例
    declare -a TEST_CASES=(
        "你好，请简单介绍一下你自己，保持简短。"
        "解释一下什么是人工智能，用简单的语言。"
        "帮我写一个简短的待办事项列表。"
        "今天天气不错，说说你对未来的想法。"
        "什么是机器学习？请用通俗的话解释。"
    )

    {
        echo "test_case,prompt_length,response_tokens,first_token_ms,total_ms,tok_per_sec"
        for test_case in "${TEST_CASES[@]}"; do
            prompt_len=${#test_case}

            # 测量首次token时间和总时间
            start_time=$(date +%s%N)

            response=$(curl -s "$OLLAMA_HOST/api/generate" \
                -d "{\"model\": \"$MODEL_NAME\", \"prompt\": \"$test_case\", \"stream\": false}")

            end_time=$(date +%s%N)
            total_ms=$(( (end_time - start_time) / 1000000 ))

            # 解析响应
            response_tokens=$(echo "$response" | grep -o '"response":"[^"]*"' | wc -c)
            response_tokens=$((response_tokens / 10))

            # 计算token/s
            if [ $total_ms -gt 0 ]; then
                tok_per_sec=$(echo "scale=2; $response_tokens / ($total_ms / 1000)" | bc)
            else
                tok_per_sec="N/A"
            fi

            echo "\"$test_case\",$prompt_len,$response_tokens,N/A,$total_ms,$tok_per_sec"

            log_info "测试完成: ${total_ms}ms, ${tok_per_sec} tok/s"
        done
    } > "$output_file"

    # 计算平均速度
    avg_speed=$(awk -F',' 'NR>1 {sum+=$6; count++} END {print sum/count}' "$output_file" 2>/dev/null || echo "0")

    echo ""
    echo "========================================"
    echo "         推理速度测试结果"
    echo "========================================"
    echo "平均生成速度: ${avg_speed} token/s"
    echo "目标: > 15 token/s"
    echo ""

    if (( $(echo "$avg_speed > 15" | bc -l) )); then
        log_success "速度测试通过！"
        return 0
    else
        log_warn "速度低于目标，可能影响用户体验"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# 测试 3: 并发测试
#-------------------------------------------------------------------------------
test_concurrent() {
    log_info "开始并发测试..."

    local output_file="$TEST_OUTPUT_DIR/concurrent_test_$(date +%Y%m%d_%H%M%S).txt"
    local num_requests=5
    local timeout_seconds=120

    log_info "发送 $num_requests 个并发请求..."

    # 启动并发请求
    start_time=$(date +%s)

    # 创建命名管道用于收集结果
    rm -f /tmp/concurrent_result_*
    for i in $(seq 1 $num_requests); do
        mkfifo /tmp/concurrent_result_$i
    done

    # 并发发送请求
    for i in $(seq 1 $num_requests); do
        (
            req_start=$(date +%s%N)
            response=$(curl -s -m $timeout_seconds "$OLLAMA_HOST/api/generate" \
                -d "{\"model\": \"$MODEL_NAME\", \"prompt\": \"简单回复：测试$i\", \"stream\": false}" 2>&1)
            req_end=$(date +%s%N)
            req_ms=$(( (req_end - req_start) / 1000000 ))

            if echo "$response" | grep -q '"response"'; then
                echo "$req_ms" > /tmp/concurrent_result_$i
            else
                echo "FAILED" > /tmp/concurrent_result_$i
            fi
        ) &
    done

    # 等待所有请求完成
    wait

    # 收集结果
    success_count=0
    fail_count=0
    total_time=0
    times=()

    for i in $(seq 1 $num_requests); do
        result=$(cat /tmp/concurrent_result_$i 2>/dev/null || echo "FAILED")
        if [ "$result" = "FAILED" ]; then
            ((fail_count++))
            log_error "请求 $i 失败"
        else
            ((success_count++))
            times+=($result)
            total_time=$((total_time + result))
        fi
        rm -f /tmp/concurrent_result_$i
    done

    end_time=$(date +%s)
    total_duration=$((end_time - start_time))

    # 计算统计
    if [ ${#times[@]} -gt 0 ]; then
        avg_time=$((total_time / success_count))
        max_time=$(printf '%s\n' "${times[@]}" | sort -n | tail -1)
        min_time=$(printf '%s\n' "${times[@]}" | sort -n | head -1)
    else
        avg_time=0
        max_time=0
        min_time=0
    fi

    {
        echo "concurrent_requests,success_count,fail_count,avg_response_ms,min_response_ms,max_response_ms,total_duration_sec"
        echo "$num_requests,$success_count,$fail_count,$avg_time,$min_time,$max_time,$total_duration"
    } > "$output_file"

    echo ""
    echo "========================================"
    echo "         并发测试结果"
    echo "========================================"
    echo "并发请求数: $num_requests"
    echo "成功: $success_count"
    echo "失败: $fail_count"
    echo "平均响应时间: ${avg_time}ms"
    echo "最快: ${min_time}ms"
    echo "最慢: ${max_time}ms"
    echo "总耗时: ${total_duration}秒"
    echo ""

    if [ $fail_count -eq 0 ]; then
        log_success "并发测试通过！"
        return 0
    else
        log_warn "部分请求失败，需要检查系统负载能力"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# 测试 4: 长时间稳定性测试
#-------------------------------------------------------------------------------
test_stability() {
    log_info "开始长时间稳定性测试 (${DURATION_SECONDS}秒)..."

    local output_file="$TEST_OUTPUT_DIR/stability_test_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "timestamp,request_num,success,response_time_ms,error"
        request_num=0
        start_time=$(date +%s)

        while [ $(( $(date +%s) - start_time )) -lt $DURATION_SECONDS ]; do
            ((request_num++))
            req_start=$(date +%s%N)

            response=$(curl -s -m 30 "$OLLAMA_HOST/api/generate" \
                -d "{\"model\": \"$MODEL_NAME\", \"prompt\": \"快速回复\", \"stream\": false}" 2>&1)

            if echo "$response" | grep -q '"response"'; then
                req_end=$(date +%s%N)
                req_ms=$(( (req_end - req_start) / 1000000 ))
                echo "$(date +%s),$request_num,1,$req_ms,N/A"
            else
                echo "$(date +%s),$request_num,0,0,Timeout or Error"
            fi

            sleep 1
        done
    } > "$output_file"

    # 分析结果
    total_requests=$(awk -F',' 'NR>1 {print $3}' "$output_file" | wc -l)
    successful_requests=$(awk -F',' 'NR>1 && $3==1 {print}' "$output_file" | wc -l)
    failed_requests=$((total_requests - successful_requests))

    success_rate=$(echo "scale=2; $successful_requests * 100 / $total_requests" | bc)

    echo ""
    echo "========================================"
    echo "       长时间稳定性测试结果"
    echo "========================================"
    echo "测试时长: ${DURATION_SECONDS}秒"
    echo "总请求数: $total_requests"
    echo "成功: $successful_requests"
    echo "失败: $failed_requests"
    echo "成功率: ${success_rate}%"
    echo "目标成功率: > 95%"
    echo ""

    if (( $(echo "$success_rate > 95" | bc -l) )); then
        log_success "稳定性测试通过！"
        return 0
    else
        log_warn "稳定性需要改进"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# 生成汇总报告
#-------------------------------------------------------------------------------
generate_report() {
    log_info "生成测试汇总报告..."

    local report_file="$TEST_OUTPUT_DIR/test_report_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# Qwen 2.5 3B 性能测试报告

生成时间: $(date)

## 测试环境
- 模型: $MODEL_NAME
- Ollama Host: $OLLAMA_HOST
- 测试日期: $(date +%Y-%m-%d)

## 测试结果汇总

| 测试项 | 结果 | 详情 |
|-------|------|------|
| 内存占用 | 待分析 | 查看 memory_test 文件 |
| 推理速度 | 待分析 | 查看 speed_test 文件 |
| 并发能力 | 待分析 | 查看 concurrent_test 文件 |
| 稳定性 | 待分析 | 查看 stability_test 文件 |

## 结论

待完成所有测试后填写...

## 建议

待分析后填写...
EOF

    log_success "报告已生成: $report_file"
}

#-------------------------------------------------------------------------------
# 主程序
#-------------------------------------------------------------------------------
main() {
    echo "========================================"
    echo "  Qwen 2.5 3B 性能测试套件"
    echo "========================================"
    echo ""

    # 检查ollama是否可用
    if ! curl -s "$OLLAMA_HOST/api/version" > /dev/null 2>&1; then
        log_warn "Ollama 未运行或无法连接"
        log_info "请确保 Ollama 已启动: ollama serve"
        exit 1
    fi

    local test_type=${1:-all}

    case $test_type in
        memory)
            test_memory
            ;;
        speed)
            test_speed
            ;;
        concurrent)
            test_concurrent
            ;;
        stability)
            test_stability
            ;;
        all)
            log_info "运行所有测试..."
            echo ""

            test_memory
            echo ""
            test_speed
            echo ""
            test_concurrent
            echo ""
            test_stability

            generate_report
            ;;
        help|--help|-h)
            echo "用法: $0 [测试类型]"
            echo ""
            echo "测试类型:"
            echo "  all        - 运行所有测试 (默认)"
            echo "  memory     - 仅内存测试"
            echo "  speed      - 仅速度测试"
            echo "  concurrent - 仅并发测试"
            echo "  stability  - 仅稳定性测试"
            ;;
        *)
            log_error "未知测试类型: $test_type"
            echo "使用 help 查看用法"
            exit 1
            ;;
    esac
}

main "$@"
