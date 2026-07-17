"""测试后端 API"""
import urllib.request
import json

def test_api(url, name):
    try:
        data = urllib.request.urlopen(url).read()
        result = json.loads(data)
        print(f"✅ {name}: {result['status']}")
        if 'data' in result:
            for d in result['data']:
                if isinstance(d, dict) and 'name' in d:
                    print(f"   {d['name']}: 股价={d.get('price')} 股息率={d.get('dividend')}% DPS={d.get('dps')} 涨跌={d.get('change')}% 数据源={d.get('data_source')}")
        return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

print("=" * 50)
print("五大行高股息监控 API 测试")
print("=" * 50)

test_api("http://127.0.0.1:5001/api/health", "健康检查")
test_api("http://127.0.0.1:5001/api/dividend", "实时股息率")
test_api("http://127.0.0.1:5001/api/history", "历史趋势")
test_api("http://127.0.0.1:5001/api/rank", "排名对比")

print()
print("=" * 50)
print("所有 API 测试完成！")
print("=" * 50)
