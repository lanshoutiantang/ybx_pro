"""
房屋租赁管理系统 - Flask后端应用
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zufang-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zufang.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==================== 数据模型 ====================

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<User {self.username}>'


class House(db.Model):
    """房屋表"""
    __tablename__ = 'houses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # 标题
    address = db.Column(db.String(200), nullable=False)  # 地址
    area = db.Column(db.Float)  # 面积（平方米）
    price = db.Column(db.Float, nullable=False)  # 月租价格
    room_count = db.Column(db.Integer)  # 房间数
    hall_count = db.Column(db.Integer)  # 客厅数
    toilet_count = db.Column(db.Integer)  # 卫生间数
    floor = db.Column(db.String(50))  # 楼层
    orientation = db.Column(db.String(20))  # 朝向
    description = db.Column(db.Text)  # 详细描述
    status = db.Column(db.String(20), default='available')  # available, rented, unavailable
    image = db.Column(db.String(200))  # 图片路径
    owner_name = db.Column(db.String(50))  # 房东姓名
    owner_phone = db.Column(db.String(20))  # 房东电话
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f'<House {self.title}>'


class Tenant(db.Model):
    """租客表"""
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    id_card = db.Column(db.String(20))  # 身份证
    username = db.Column(db.String(50), unique=True)  # 登录账号
    password = db.Column(db.String(200))  # 登录密码
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'))
    rent_start = db.Column(db.Date)  # 租期开始
    rent_end = db.Column(db.Date)  # 租期结束
    rent_amount = db.Column(db.Float)  # 已付租金
    created_at = db.Column(db.DateTime, default=db.func.now())

    house = db.relationship('House', backref=db.backref('tenants', lazy=True))

    def __repr__(self):
        return f'<Tenant {self.name}>'

    def set_password(self, password):
        """设置密码"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password, password)


class Contract(db.Model):
    """合同表"""
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'))
    contract_no = db.Column(db.String(50), unique=True)  # 合同编号
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    rent_price = db.Column(db.Float)  # 月租
    deposit = db.Column(db.Float)  # 押金
    payment_cycle = db.Column(db.Integer, default=1)  # 付款周期（月）
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled
    created_at = db.Column(db.DateTime, default=db.func.now())

    tenant = db.relationship('Tenant', backref=db.backref('contracts', lazy=True))
    house = db.relationship('House', backref=db.backref('contracts', lazy=True))

    def __repr__(self):
        return f'<Contract {self.contract_no}>'


# ==================== 辅助函数 ====================

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('需要管理员权限', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def tenant_required(f):
    """租客验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tenant_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('tenant_login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== 路由 - 认证 ====================

@app.route('/')
def index():
    """首页"""
    houses = House.query.filter_by(status='available').order_by(House.created_at.desc()).limit(6).all()
    total_houses = House.query.count()
    total_tenants = Tenant.query.count()
    return render_template('index.html',
                         houses=houses,
                         total_houses=total_houses,
                         total_tenants=total_tenants)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """管理员登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')


@app.route('/tenant/login', methods=['GET', 'POST'])
def tenant_login():
    """租客登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        tenant = Tenant.query.filter_by(username=username).first()

        if tenant and tenant.check_password(password):
            session['tenant_id'] = tenant.id
            session['tenant_name'] = tenant.name
            session['role'] = 'tenant'
            flash(f'欢迎回来，{tenant.name}！', 'success')
            return redirect(url_for('tenant_dashboard'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('tenant_login.html')


@app.route('/tenant/register', methods=['GET', 'POST'])
def tenant_register():
    """租客注册页面"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        id_card = request.form.get('id_card')
        username = request.form.get('username')
        password = request.form.get('password')

        # 检查用户名是否已存在
        if Tenant.query.filter_by(username=username).first():
            flash('该用户名已被注册', 'danger')
            return render_template('tenant_register.html')

        if User.query.filter_by(username=username).first():
            flash('该用户名已被注册', 'danger')
            return render_template('tenant_register.html')

        tenant = Tenant(
            name=name,
            phone=phone,
            id_card=id_card,
            username=username
        )
        tenant.set_password(password)

        db.session.add(tenant)
        db.session.commit()

        flash('注册成功，请登录', 'success')
        return redirect(url_for('tenant_login'))

    return render_template('tenant_register.html')


@app.route('/tenant/dashboard')
@tenant_required
def tenant_dashboard():
    """租客个人中心"""
    tenant = Tenant.query.get(session['tenant_id'])
    return render_template('tenant_dashboard.html', tenant=tenant)


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))


@app.route('/tenant/logout')
def tenant_logout():
    """租客退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('tenant_login'))


# ==================== 路由 - 房屋管理 ====================

@app.route('/houses')
def houses():
    """房屋列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    query = House.query

    if search:
        query = query.filter(
            (House.title.contains(search)) |
            (House.address.contains(search))
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    houses = query.order_by(House.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('houses.html', houses=houses, search=search, status_filter=status_filter)


@app.route('/house/<int:house_id>')
def house_detail(house_id):
    """房屋详情"""
    house = House.query.get_or_404(house_id)
    return render_template('house_detail.html', house=house)


@app.route('/house/add', methods=['GET', 'POST'])
@admin_required
def house_add():
    """添加房屋"""
    if request.method == 'POST':
        house = House(
            title=request.form.get('title'),
            address=request.form.get('address'),
            area=float(request.form.get('area', 0)),
            price=float(request.form.get('price', 0)),
            room_count=int(request.form.get('room_count', 0)),
            hall_count=int(request.form.get('hall_count', 0)),
            toilet_count=int(request.form.get('toilet_count', 0)),
            floor=request.form.get('floor'),
            orientation=request.form.get('orientation'),
            description=request.form.get('description'),
            owner_name=request.form.get('owner_name'),
            owner_phone=request.form.get('owner_phone'),
            status=request.form.get('status', 'available')
        )
        db.session.add(house)
        db.session.commit()
        flash('房屋添加成功', 'success')
        return redirect(url_for('houses'))

    return render_template('house_form.html', house=None, action='add')


@app.route('/house/edit/<int:house_id>', methods=['GET', 'POST'])
@admin_required
def house_edit(house_id):
    """编辑房屋"""
    house = House.query.get_or_404(house_id)

    if request.method == 'POST':
        house.title = request.form.get('title')
        house.address = request.form.get('address')
        house.area = float(request.form.get('area', 0))
        house.price = float(request.form.get('price', 0))
        house.room_count = int(request.form.get('room_count', 0))
        house.hall_count = int(request.form.get('hall_count', 0))
        house.toilet_count = int(request.form.get('toilet_count', 0))
        house.floor = request.form.get('floor')
        house.orientation = request.form.get('orientation')
        house.description = request.form.get('description')
        house.owner_name = request.form.get('owner_name')
        house.owner_phone = request.form.get('owner_phone')
        house.status = request.form.get('status', 'available')

        db.session.commit()
        flash('房屋信息已更新', 'success')
        return redirect(url_for('houses'))

    return render_template('house_form.html', house=house, action='edit')


@app.route('/house/delete/<int:house_id>', methods=['POST'])
@admin_required
def house_delete(house_id):
    """删除房屋"""
    house = House.query.get_or_404(house_id)
    db.session.delete(house)
    db.session.commit()
    flash('房屋已删除', 'success')
    return redirect(url_for('houses'))


# ==================== 路由 - 租客管理 ====================

@app.route('/tenants')
@login_required
def tenants():
    """租客列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    search = request.args.get('search', '')
    query = Tenant.query

    if search:
        query = query.filter(
            (Tenant.name.contains(search)) |
            (Tenant.phone.contains(search))
        )

    tenants = query.order_by(Tenant.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('tenants.html', tenants=tenants, search=search)


@app.route('/tenant/add', methods=['GET', 'POST'])
@login_required
def tenant_add():
    """添加租客"""
    houses = House.query.filter_by(status='available').all()

    if request.method == 'POST':
        tenant = Tenant(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            id_card=request.form.get('id_card'),
            house_id=request.form.get('house_id'),
            rent_start=request.form.get('rent_start'),
            rent_end=request.form.get('rent_end'),
            rent_amount=float(request.form.get('rent_amount', 0))
        )
        db.session.add(tenant)
        db.session.commit()
        flash('租客添加成功', 'success')
        return redirect(url_for('tenants'))

    return render_template('tenant_form.html', tenant=None, houses=houses, action='add')


@app.route('/tenant/edit/<int:tenant_id>', methods=['GET', 'POST'])
@login_required
def tenant_edit(tenant_id):
    """编辑租客"""
    tenant = Tenant.query.get_or_404(tenant_id)
    houses = House.query.all()

    if request.method == 'POST':
        tenant.name = request.form.get('name')
        tenant.phone = request.form.get('phone')
        tenant.id_card = request.form.get('id_card')
        tenant.house_id = request.form.get('house_id')
        tenant.rent_start = request.form.get('rent_start')
        tenant.rent_end = request.form.get('rent_end')
        tenant.rent_amount = float(request.form.get('rent_amount', 0))

        db.session.commit()
        flash('租客信息已更新', 'success')
        return redirect(url_for('tenants'))

    return render_template('tenant_form.html', tenant=tenant, houses=houses, action='edit')


@app.route('/tenant/delete/<int:tenant_id>', methods=['POST'])
@login_required
def tenant_delete(tenant_id):
    """删除租客"""
    tenant = Tenant.query.get_or_404(tenant_id)
    db.session.delete(tenant)
    db.session.commit()
    flash('租客已删除', 'success')
    return redirect(url_for('tenants'))


# ==================== 路由 - 统计报表 ====================

@app.route('/statistics')
@login_required
def statistics():
    """统计报表"""
    total_houses = House.query.count()
    available_houses = House.query.filter_by(status='available').count()
    rented_houses = House.query.filter_by(status='rented').count()

    total_tenants = Tenant.query.count()
    active_contracts = Contract.query.filter_by(status='active').count()

    # 收入统计（简化）
    total_rent = db.session.query(db.func.sum(Tenant.rent_amount)).scalar() or 0

    return render_template('statistics.html',
                         total_houses=total_houses,
                         available_houses=available_houses,
                         rented_houses=rented_houses,
                         total_tenants=total_tenants,
                         active_contracts=active_contracts,
                         total_rent=total_rent)


# ==================== 初始化数据 ====================

def init_db():
    """初始化数据库和默认管理员"""
    db.create_all()

    # 创建默认管理员
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('默认管理员已创建: admin / admin123')


# ==================== 主程序 ====================

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)