"""
房屋租赁管理系统 - 初始化示例数据
添加100条房屋和100条租客数据（含登录账号）
"""

from app import app, db, House, Tenant, User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import random


def generate_house_data():
    """生成房屋数据"""
    districts = ['朝阳区', '海淀区', '丰台区', '东城区', '西城区', '昌平区', '通州区', '大兴区']
    streets = ['建国路', '长安街', '中关村大街', '西直门外大街', '东三环', '北四环', '南二环', '西五环']
    house_types = ['小区', '公寓', '别墅', '四合院', '写字楼']
    orientations = ['南', '北', '东', '西', '南北通透', '东南', '西南']
    decorations = ['精装', '简装', '毛坯', '豪华装修']
    
    houses = []
    for i in range(1, 101):
        district = random.choice(districts)
        street = random.choice(streets)
        house_num = random.randint(1, 200)
        room_num = random.randint(101, 2500)
        
        title = f"{random.choice(decorations)}{random.randint(1, 4)}室{random.choice(['近地铁', '采光好', '拎包入住', '交通便利', '环境优美'])}"
        address = f"{district}{street}{house_num}号{random.choice(house_types)}{room_num}室"
        
        area = random.uniform(30, 150)
        price = int(area * random.uniform(60, 120))
        room_count = random.randint(1, 4)
        hall_count = random.randint(1, 2)
        toilet_count = random.randint(1, 2)
        floor = f"{random.randint(1, 30)}/{random.randint(10, 33)}"
        orientation = random.choice(orientations)
        
        descriptions = [
            "交通便利，近地铁站，周边配套设施完善",
            "采光充足，南北通透，视野开阔",
            "精装修，家具家电齐全，拎包入住",
            "小区环境优美，绿化率高，安静舒适",
            "周边有大型商场、超市、医院，生活便利",
            "学区房，附近有优质学校",
            "高层视野好，可俯瞰城市美景",
            "户型方正，空间利用率高"
        ]
        description = random.choice(descriptions)
        
        owner_names = ['张先生', '李女士', '王先生', '刘女士', '陈先生', '赵女士', '周先生', '吴女士']
        owner_name = random.choice(owner_names)
        owner_phone = f"138{random.randint(10000000, 99999999)}"
        
        status = random.choice(['available', 'available', 'available', 'rented', 'unavailable'])
        
        house = House(
            title=title,
            address=address,
            area=round(area, 2),
            price=price,
            room_count=room_count,
            hall_count=hall_count,
            toilet_count=toilet_count,
            floor=floor,
            orientation=orientation,
            description=description,
            status=status,
            owner_name=owner_name,
            owner_phone=owner_phone
        )
        houses.append(house)
    
    return houses


def generate_tenant_data(house_ids):
    """生成租客数据（包含登录账号）"""
    first_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']
    last_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞']
    
    tenants = []
    tenant_accounts = []  # 记录账号密码
    
    for i in range(1, 101):
        name = random.choice(first_names) + random.choice(last_names)
        phone = f"1{random.choice(['3', '5', '7', '8', '9'])}{random.randint(100000000, 999999999)}"
        
        # 生成身份证号
        id_card = f"{random.randint(110000, 500000)}{random.randint(19900101, 20051231)}{random.randint(1000, 9999)}"
        
        house_id = random.choice(house_ids)
        
        # 生成租期
        start_date = date.today() - timedelta(days=random.randint(0, 365))
        end_date = start_date + timedelta(days=random.randint(180, 730))

        rent_amount = random.randint(3000, 15000)
        
        # 生成用户名和密码
        username = f"tenant{i:03d}"  # tenant001, tenant002, ...
        password = f"pwd{i:04d}"     # pwd0001, pwd0002, ...
        
        tenant = Tenant(
            name=name,
            phone=phone,
            id_card=id_card,
            username=username,
            password=generate_password_hash(password),
            house_id=house_id,
            rent_start=start_date,
            rent_end=end_date,
            rent_amount=rent_amount
        )
        tenants.append(tenant)
        tenant_accounts.append({
            'id': i,
            'name': name,
            'username': username,
            'password': password
        })
    
    return tenants, tenant_accounts


def init_database():
    """初始化数据库并添加示例数据"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        print("=" * 60)
        print("房屋租赁管理系统 - 数据初始化")
        print("=" * 60)
        
        # 检查是否已有数据
        existing_houses = House.query.count()
        existing_tenants = Tenant.query.count()
        
        if existing_houses > 0 or existing_tenants > 0:
            print(f"\n数据库中已有 {existing_houses} 条房屋数据，{existing_tenants} 条租客数据")
            response = input("是否清空现有数据并重新生成？(y/n): ")
            if response.lower() == 'y':
                # 清空现有数据
                Tenant.query.delete()
                House.query.delete()
                db.session.commit()
                print("已清空现有数据")
            else:
                print("保持现有数据，退出")
                return
        
        # 确保管理员存在
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("[OK] 管理员账号已创建: admin / admin123")
        
        # 添加房屋数据
        print("\n正在生成 100 条房屋数据...")
        houses = generate_house_data()
        for house in houses:
            db.session.add(house)
        db.session.commit()
        print(f"[OK] 成功添加 {len(houses)} 条房屋数据")
        
        # 获取房屋ID列表
        house_ids = [h.id for h in House.query.all()]
        
        # 添加租客数据
        print("\n正在生成 100 条租客数据...")
        tenants, tenant_accounts = generate_tenant_data(house_ids)
        for tenant in tenants:
            db.session.add(tenant)
        db.session.commit()
        print(f"[OK] 成功添加 {len(tenants)} 条租客数据")
        
        # 保存租客账号信息到文件
        print("\n正在保存租客账号信息...")
        with open('tenant_accounts.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("租客账号信息 - 请妥善保管\n")
            f.write("=" * 60 + "\n\n")
            f.write("格式: 序号 | 姓名 | 用户名 | 密码\n")
            f.write("-" * 60 + "\n")
            for acc in tenant_accounts:
                f.write(f"{acc['id']:3d} | {acc['name']:4s} | {acc['username']:10s} | {acc['password']}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("示例登录:\n")
            f.write(f"  用户名: {tenant_accounts[0]['username']}\n")
            f.write(f"  密码: {tenant_accounts[0]['password']}\n")
            f.write("=" * 60 + "\n")
        print("[OK] 租客账号信息已保存到 tenant_accounts.txt")
        
        # 显示部分账号
        print("\n" + "=" * 60)
        print("部分租客账号示例（前10个）:")
        print("=" * 60)
        print(f"{'序号':6s}{'姓名':8s}{'用户名':12s}{'密码':10s}")
        print("-" * 60)
        for acc in tenant_accounts[:10]:
            print(f"{acc['id']:6d}  {acc['name']:8s}  {acc['username']:12s}  {acc['password']:10s}")
        print("=" * 60)
        print(f"\n全部 {len(tenant_accounts)} 个账号已保存到 tenant_accounts.txt")
        
        print("\n" + "=" * 60)
        print("数据初始化完成！")
        print("=" * 60)
        print(f"房屋总数: {House.query.count()}")
        print(f"租客总数: {Tenant.query.count()}")
        print(f"可租房屋: {House.query.filter_by(status='available').count()}")
        print(f"已租房屋: {House.query.filter_by(status='rented').count()}")
        print("\n登录方式:")
        print("  1. 管理员: admin / admin123")
        print("  2. 租客: tenant001 / pwd0001 (示例)")
        print("=" * 60)


if __name__ == '__main__':
    init_database()
