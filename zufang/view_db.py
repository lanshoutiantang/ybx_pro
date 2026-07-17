"""
数据库查看工具
"""

from app import app, db, House, Tenant, User


def view_stats():
    """查看统计信息"""
    with app.app_context():
        print("=" * 60)
        print("数据库统计信息")
        print("=" * 60)
        print(f"管理员数量: {User.query.count()}")
        print(f"房屋总数: {House.query.count()}")
        print(f"租客总数: {Tenant.query.count()}")
        print(f"  - 有账号的租客: {Tenant.query.filter(Tenant.username != None).count()}")
        print(f"  - 无账号的租客: {Tenant.query.filter(Tenant.username == None).count()}")
        print("=" * 60)


def view_houses(limit=10):
    """查看房屋数据"""
    with app.app_context():
        print("\n" + "=" * 60)
        print(f"房屋列表 (前{limit}条)")
        print("=" * 60)
        print(f"{'ID':5s} {'标题':20s} {'地址':25s} {'租金':10s} {'状态':8s}")
        print("-" * 60)
        for h in House.query.limit(limit).all():
            status = "可租" if h.status == "available" else "已租" if h.status == "rented" else "不可租"
            title = h.title[:18] + ".." if len(h.title) > 18 else h.title
            addr = h.address[:23] + ".." if len(h.address) > 23 else h.address
            print(f"{h.id:5d} {title:20s} {addr:25s} {h.price:10.0f} {status:8s}")
        print("=" * 60)


def view_tenants(limit=10):
    """查看租客数据"""
    with app.app_context():
        print("\n" + "=" * 60)
        print(f"租客列表 (前{limit}条)")
        print("=" * 60)
        print(f"{'ID':5s} {'姓名':8s} {'用户名':12s} {'手机号':15s} {'房屋ID':8s}")
        print("-" * 60)
        for t in Tenant.query.limit(limit).all():
            username = t.username if t.username else "未设置"
            house_id = str(t.house_id) if t.house_id else "-"
            print(f"{t.id:5d} {t.name:8s} {username:12s} {t.phone:15s} {house_id:8s}")
        print("=" * 60)


def view_tenant_accounts():
    """查看所有租客账号"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("租客账号列表 (用于登录)")
        print("=" * 60)
        print(f"{'序号':6s} {'姓名':8s} {'用户名':12s} {'密码':10s}")
        print("-" * 60)
        for t in Tenant.query.filter(Tenant.username != None).all():
            print(f"{t.id:6d} {t.name:8s} {t.username:12s} {'见文件':10s}")
        print("=" * 60)
        print("提示: 完整账号密码请查看 tenant_accounts.txt 文件")


def search_tenant(name=""):
    """搜索租客"""
    with app.app_context():
        print("\n" + "=" * 60)
        print(f"搜索租客: '{name}'")
        print("=" * 60)
        tenants = Tenant.query.filter(Tenant.name.contains(name)).all()
        if tenants:
            for t in tenants:
                print(f"ID: {t.id}")
                print(f"  姓名: {t.name}")
                print(f"  用户名: {t.username or '未设置'}")
                print(f"  电话: {t.phone}")
                print(f"  身份证号: {t.id_card}")
                if t.house:
                    print(f"  租住房屋: {t.house.title}")
                    print(f"  房屋地址: {t.house.address}")
                print("-" * 40)
        else:
            print("未找到匹配的租客")
        print("=" * 60)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 1:
        view_stats()
        view_houses(5)
        view_tenants(5)
    elif sys.argv[1] == 'stats':
        view_stats()
    elif sys.argv[1] == 'houses':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        view_houses(limit)
    elif sys.argv[1] == 'tenants':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        view_tenants(limit)
    elif sys.argv[1] == 'accounts':
        view_tenant_accounts()
    elif sys.argv[1] == 'search' and len(sys.argv) > 2:
        search_tenant(sys.argv[2])
    else:
        print("用法:")
        print("  python view_db.py           # 显示统计信息")
        print("  python view_db.py stats     # 查看统计")
        print("  python view_db.py houses    # 查看房屋列表")
        print("  python view_db.py tenants   # 查看租客列表")
        print("  python view_db.py accounts  # 查看租客账号")
        print("  python view_db.py search 张三 # 搜索租客")
