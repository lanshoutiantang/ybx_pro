# app.py - 五大行高股息监控后端（增强版）
# 功能：实时股价 + 真实股息率计算 + 历史趋势 + 排名对比

from flask import Flask, jsonify
from flask_cors import CORS
import akshare as ak
import pandas as pd
import time
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import re
import json

app = Flask(__name__)
CORS(app)

# 配置 requests 重试策略
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
session.mount('http://', adapter)
session.mount('https://', adapter)

BANK_STOCKS = {
    "工商银行": "601398",
    "建设银行": "601939",
    "农业银行": "601288",
    "中国银行": "601988",
    "交通银行": "601328"
}

# 备用数据（当网络不通时使用）
FALLBACK_DATA = {
    "工商银行": {"price": 5.12, "dividend": 6.2, "dps": 0.32, "change": 0.5},
    "建设银行": {"price": 6.38, "dividend": 5.8, "dps": 0.37, "change": 0.3},
    "农业银行": {"price": 4.25, "dividend": 6.5, "dps": 0.28, "change": 0.8},
    "中国银行": {"price": 4.58, "dividend": 5.9, "dps": 0.27, "change": 0.2},
    "交通银行": {"price": 6.02, "dividend": 5.3, "dps": 0.32, "change": -0.1}
}

# 缓存
CACHE = {
    "data": None,
    "history": None,
    "timestamp": 0,
    "history_timestamp": 0,
    "ttl": 60,          # 实时数据缓存60秒
    "history_ttl": 300  # 历史数据缓存5分钟
}

# ==================== 实时股价获取 ====================

def fetch_realtime_price_sina(stock_code):
    """使用新浪接口获取实时股价"""
    try:
        url = f"https://hq.sinajs.cn/list=sh{stock_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn'
        }
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            if '=' in content:
                data_str = content.split('"')[1] if '"' in content else content.split('=')[1].strip()
                parts = data_str.split(',')
                if len(parts) >= 4:
                    price = float(parts[3])
                    yesterday = float(parts[2]) if len(parts) > 2 and parts[2] else price
                    change = round((price - yesterday) / yesterday * 100, 2) if yesterday != 0 else 0
                    return price, change
        return None, None
    except Exception as e:
        print(f"新浪接口获取 {stock_code} 失败: {e}")
        return None, None

def fetch_realtime_price_tencent(stock_code):
    """使用腾讯接口获取实时股价（备用）"""
    try:
        url = f"https://qt.gtimg.cn/q=sh{stock_code}"
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.qq.com'}
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.text
            if '~' in content:
                parts = content.split('~')
                if len(parts) >= 5:
                    price = float(parts[3]) if parts[3] else None
                    change = float(parts[32]) if len(parts) > 32 and parts[32] else 0
                    return price, change
        return None, None
    except Exception as e:
        print(f"腾讯接口获取 {stock_code} 失败: {e}")
        return None, None

# ==================== 股息率真实计算 ====================

def get_dividend_data_from_akshare(stock_code):
    """
    从 akshare 获取真实分红数据
    返回: 每股分红(DPS) 或 None
    """
    try:
        df = ak.stock_fhps_detail_em(symbol=stock_code)
        if df is not None and not df.empty:
            latest = df.iloc[0]
            dps = None
            for col in ['每股分红', '每股股利', '分红', '股利']:
                if col in latest and latest[col]:
                    val = str(latest[col]).strip()
                    try:
                        dps = float(val)
                        if dps > 0:
                            break
                    except:
                        continue
            return dps
        return None
    except Exception as e:
        print(f"akshare获取分红数据 {stock_code} 失败: {e}")
        return None

def get_dps(stock_code, name):
    """
    获取每股分红（DPS），多数据源轮询
    股息率 = DPS / 当前股价 × 100%
    """
    # 1. 尝试 akshare
    dps = get_dividend_data_from_akshare(stock_code)
    if dps and dps > 0:
        print(f"✅ akshare获取 {name} DPS: {dps}")
        return dps

    # 2. 使用备用数据
    fallback_dps = FALLBACK_DATA.get(name, {}).get('dps', 0.30)
    print(f"⚠️ 使用备用DPS数据 {name}: {fallback_dps}")
    return fallback_dps

# ==================== 核心数据获取 ====================

def get_bank_data_internal():
    """获取五大行数据（内部调用，无缓存）"""
    result = []

    for name, code in BANK_STOCKS.items():
        try:
            # 获取实时股价（多数据源）
            price, change = None, None

            price, change = fetch_realtime_price_sina(code)
            if price is None:
                price, change = fetch_realtime_price_tencent(code)

            data_source = "实时"
            if price is None:
                fallback = FALLBACK_DATA.get(name, {})
                price = fallback.get('price', 5.0)
                change = fallback.get('change', 0)
                data_source = "备用"
                print(f"⚠️ 使用备用股价: {name}")

            # 获取每股分红（DPS）
            dps = get_dps(code, name)

            # 计算真实股息率 = DPS / 股价 × 100%
            if price and price > 0 and dps and dps > 0:
                dividend_yield = round((dps / price) * 100, 2)
            else:
                dividend_yield = FALLBACK_DATA.get(name, {}).get('dividend', 5.5)

            result.append({
                "name": name,
                "code": code,
                "price": round(price, 2) if price else 0,
                "dividend": round(dividend_yield, 2),
                "dps": round(dps, 4) if dps else 0,
                "change": round(change, 2) if change else 0,
                "data_source": data_source,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as e:
            print(f"处理 {name} 异常: {e}")
            fallback = FALLBACK_DATA.get(name, {})
            result.append({
                "name": name,
                "code": code,
                "price": fallback.get('price', 5.0),
                "dividend": fallback.get('dividend', 5.5),
                "dps": fallback.get('dps', 0.30),
                "change": fallback.get('change', 0),
                "data_source": "备用(异常)",
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    return result

def generate_history_data():
    """
    生成近30个交易日的模拟历史数据
    基于真实当前价格 + 真实分红数据进行模拟推算
    """
    history = []
    today = datetime.now()

    current_data = get_bank_data_internal()

    for bank in current_data:
        name = bank['name']
        current_price = bank['price']
        current_dividend = bank['dividend']
        current_dps = bank['dps']

        prices = []
        dividends = []
        dates = []
        volumes = []

        # 从30天前的价格开始模拟
        price = current_price * 0.92
        for i in range(30):
            date = (today - timedelta(days=30 - i)).strftime("%m-%d")
            change = random.uniform(-0.008, 0.008)
            price = price * (1 + change)
            if i == 29:
                price = current_price

            prices.append(round(price, 2))
            div = round((current_dps / price * 100), 2) if current_dps > 0 and price > 0 else current_dividend
            dividends.append(div)
            dates.append(date)
            volumes.append(random.randint(500000, 5000000))

        history.append({
            "name": name,
            "code": bank['code'],
            "dates": dates,
            "prices": prices,
            "dividends": dividends,
            "volumes": volumes
        })

    return history

# ==================== API 路由 ====================

@app.route('/api/dividend', methods=['GET'])
def get_dividend_data():
    """获取五大行实时数据（带缓存）"""
    current_time = time.time()
    if CACHE["data"] and (current_time - CACHE["timestamp"]) < CACHE["ttl"]:
        return jsonify({
            "status": "success",
            "data": CACHE["data"],
            "cached": True,
            "data_source": "缓存",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "股息率 = 每股分红(DPS) / 当前股价 × 100%"
        })

    try:
        data = get_bank_data_internal()
        CACHE["data"] = data
        CACHE["timestamp"] = current_time

        # 计算数据来源统计
        sources = {}
        for d in data:
            src = d.get('data_source', '未知')
            sources[src] = sources.get(src, 0) + 1

        return jsonify({
            "status": "success",
            "data": data,
            "cached": False,
            "data_source": "实时采集",
            "sources_summary": sources,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "note": "股息率 = 每股分红(DPS) / 当前股价 × 100%"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history_data():
    """获取近30日历史趋势数据（带缓存）"""
    current_time = time.time()
    if CACHE["history"] and (current_time - CACHE["history_timestamp"]) < CACHE["history_ttl"]:
        return jsonify({
            "status": "success",
            "data": CACHE["history"],
            "cached": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    try:
        data = generate_history_data()
        CACHE["history"] = data
        CACHE["history_timestamp"] = current_time
        return jsonify({
            "status": "success",
            "data": data,
            "cached": False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.route('/api/rank', methods=['GET'])
def get_rank_data():
    """获取五大行指标排名"""
    try:
        # 获取最新数据
        data = get_bank_data_internal()

        # 按股息率排名
        rank_dividend = sorted(data, key=lambda x: x.get('dividend', 0), reverse=True)
        # 按股价排名
        rank_price = sorted(data, key=lambda x: x.get('price', 0), reverse=True)
        # 按涨跌幅排名
        rank_change = sorted(data, key=lambda x: x.get('change', 0), reverse=True)

        ranks = []
        for item in data:
            name = item['name']
            ranks.append({
                "name": name,
                "dividend_rank": next(i + 1 for i, d in enumerate(rank_dividend) if d['name'] == name),
                "price_rank": next(i + 1 for i, d in enumerate(rank_price) if d['name'] == name),
                "change_rank": next(i + 1 for i, d in enumerate(rank_change) if d['name'] == name),
                "dividend_value": item['dividend'],
                "price_value": item['price'],
                "change_value": item['change']
            })

        return jsonify({
            "status": "success",
            "data": ranks,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "五大行高股息监控",
        "version": "2.0",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "endpoints": {
            "/api/dividend": "实时股息率数据",
            "/api/history": "近30日历史趋势",
            "/api/rank": "五大行指标排名",
            "/api/health": "健康检查"
        }
    })

if __name__ == '__main__':
    print("🚀 五大行高股息监控后端 v2.0 启动...")
    print("=" * 50)
    print("📍 接口地址:")
    print("   http://127.0.0.1:5001/api/dividend  - 实时数据")
    print("   http://127.0.0.1:5001/api/history   - 历史趋势")
    print("   http://127.0.0.1:5001/api/rank      - 排名对比")
    print("   http://127.0.0.1:5001/api/health    - 健康检查")
    print("=" * 50)
    print("💡 股息率 = 每股分红(DPS) / 当前股价 × 100%")
    print("⏱️  实时数据缓存60秒 | 历史数据缓存5分钟")
    app.run(debug=True, host='0.0.0.0', port=5001)