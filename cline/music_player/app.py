"""
在线音乐管理系统 - Flask后端应用
支持游客、用户、管理员三种角色，集成音乐歌单推荐
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime, date
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'music-player-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 文件上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
MUSIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'music')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'flac'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MUSIC_FOLDER'] = MUSIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大50MB

db = SQLAlchemy(app)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload_file(file, subfolder='uploads'):
    """保存上传的文件"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        if subfolder == 'music':
            filepath = os.path.join(app.config['MUSIC_FOLDER'], filename)
        else:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filename
    return None


def delete_file(filename, subfolder='uploads'):
    """删除文件"""
    if filename:
        if subfolder == 'music':
            filepath = os.path.join(app.config['MUSIC_FOLDER'], filename)
        else:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)


# ==================== 数据模型 ====================

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin
    avatar = db.Column(db.String(200), default='default_avatar.png')
    created_at = db.Column(db.DateTime, default=db.func.now())

    favorites = db.relationship('Favorite', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    playlists = db.relationship('Playlist', backref='creator', lazy=True)
    play_history = db.relationship('PlayHistory', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Song(db.Model):
    """歌曲表"""
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), default='未知艺术家')
    album = db.Column(db.String(100), default='未知专辑')
    genre = db.Column(db.String(50), default='流行')  # 流派：流行、摇滚、古典、电子、民谣、R&B、爵士、嘻哈
    duration = db.Column(db.Integer, default=0)  # 时长（秒）
    file_path = db.Column(db.String(200), nullable=False)  # 音乐文件路径
    cover_image = db.Column(db.String(200), default='default_cover.jpg')
    lyrics = db.Column(db.Text, default='')  # 歌词
    play_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    reviews = db.relationship('Review', backref='song', lazy=True)
    favorites = db.relationship('Favorite', backref='song', lazy=True)
    playlist_songs = db.relationship('PlaylistSong', backref='song', lazy=True)
    play_history = db.relationship('PlayHistory', backref='song', lazy=True)

    def __repr__(self):
        return f'<Song {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'genre': self.genre,
            'duration': self.duration,
            'file_path': self.file_path,
            'cover_image': self.cover_image,
            'play_count': self.play_count,
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }


class Playlist(db.Model):
    """歌单表"""
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    cover_image = db.Column(db.String(200), default='default_playlist.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 创建者，管理员可为null
    is_official = db.Column(db.Boolean, default=False)  # 官方推荐歌单
    play_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())

    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True)

    def __repr__(self):
        return f'<Playlist {self.name}>'


class PlaylistSong(db.Model):
    """歌单歌曲关联表"""
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    added_at = db.Column(db.DateTime, default=db.func.now())


class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    __table_args__ = (db.UniqueConstraint('user_id', 'song_id', name='unique_user_song'),)


class Review(db.Model):
    """评论表"""
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    rating = db.Column(db.Integer, default=5)  # 1-5 评分
    content = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=db.func.now())


class PlayHistory(db.Model):
    """播放记录表"""
    __tablename__ = 'play_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 游客可为null
    session_id = db.Column(db.String(50), nullable=True)  # 游客用session标识
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    played_at = db.Column(db.DateTime, default=db.func.now())


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


def get_recommended_playlists(limit=6):
    """获取推荐歌单（官方推荐+热门）"""
    official = Playlist.query.filter_by(is_official=True).order_by(Playlist.play_count.desc()).limit(limit).all()
    if len(official) < limit:
        user_playlists = Playlist.query.filter_by(is_official=False).order_by(Playlist.play_count.desc()).limit(limit - len(official)).all()
        official.extend(user_playlists)
    return official


def get_hot_songs(limit=10):
    """获取热门歌曲"""
    return Song.query.filter_by(is_active=True).order_by(Song.play_count.desc()).limit(limit).all()


def get_new_songs(limit=10):
    """获取最新歌曲"""
    return Song.query.filter_by(is_active=True).order_by(Song.created_at.desc()).limit(limit).all()


def get_recommended_by_genre(limit=5):
    """按流派推荐（随机取5个流派各取一首）"""
    genres = ['流行', '摇滚', '古典', '电子', '民谣', 'R&B', '爵士', '嘻哈']
    recommendations = []
    selected_genres = random.sample(genres, min(limit, len(genres)))
    for genre in selected_genres:
        song = Song.query.filter_by(genre=genre, is_active=True).order_by(Song.play_count.desc()).first()
        if song:
            recommendations.append(song)
    return recommendations


# ==================== 路由 - 首页与通用 ====================

@app.route('/')
def index():
    """首页"""
    recommended_playlists = get_recommended_playlists(4)
    hot_songs = get_hot_songs(8)
    new_songs = get_new_songs(8)
    genre_recommendations = get_recommended_by_genre(5)
    song_count = Song.query.filter_by(is_active=True).count()
    playlist_count = Playlist.query.count()
    user_count = User.query.count()
    return render_template('index.html',
                         recommended_playlists=recommended_playlists,
                         hot_songs=hot_songs,
                         new_songs=new_songs,
                         genre_recommendations=genre_recommendations,
                         song_count=song_count,
                         playlist_count=playlist_count,
                         user_count=user_count)


@app.route('/search')
def search():
    """搜索页面"""
    keyword = request.args.get('keyword', '')
    genre = request.args.get('genre', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Song.query.filter_by(is_active=True)

    if keyword:
        query = query.filter(
            (Song.title.contains(keyword)) |
            (Song.artist.contains(keyword)) |
            (Song.album.contains(keyword))
        )

    if genre:
        query = query.filter_by(genre=genre)

    songs = query.order_by(Song.play_count.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    genres = ['流行', '摇滚', '古典', '电子', '民谣', 'R&B', '爵士', '嘻哈']
    return render_template('search.html',
                         songs=songs,
                         keyword=keyword,
                         genre=genre,
                         genres=genres)


@app.route('/songs')
def songs():
    """歌曲列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    genre_filter = request.args.get('genre', '')
    sort = request.args.get('sort', 'new')  # new, hot

    query = Song.query.filter_by(is_active=True)

    if genre_filter:
        query = query.filter_by(genre=genre_filter)

    if sort == 'hot':
        query = query.order_by(Song.play_count.desc())
    else:
        query = query.order_by(Song.created_at.desc())

    songs = query.paginate(page=page, per_page=per_page, error_out=False)
    genres = ['全部', '流行', '摇滚', '古典', '电子', '民谣', 'R&B', '爵士', '嘻哈']

    return render_template('songs.html', songs=songs, genres=genres, genre_filter=genre_filter, sort=sort)


@app.route('/song/<int:song_id>')
def song_detail(song_id):
    """歌曲详情"""
    song = Song.query.get_or_404(song_id)
    reviews = Review.query.filter_by(song_id=song_id).order_by(Review.created_at.desc()).all()
    is_favorited = False
    user_rating = None

    if 'user_id' in session:
        fav = Favorite.query.filter_by(user_id=session['user_id'], song_id=song_id).first()
        is_favorited = fav is not None
        user_review = Review.query.filter_by(user_id=session['user_id'], song_id=song_id).first()
        if user_review:
            user_rating = user_review.rating

    # 用户歌单（用于添加到歌单下拉）
    user_playlists = []
    if 'user_id' in session:
        user_playlists = Playlist.query.filter_by(user_id=session['user_id']).all()

    # 相关推荐（同流派）
    related_songs = Song.query.filter(
        Song.genre == song.genre,
        Song.id != song_id,
        Song.is_active == True
    ).order_by(Song.play_count.desc()).limit(5).all()

    return render_template('song_detail.html',
                         song=song,
                         reviews=reviews,
                         is_favorited=is_favorited,
                         user_rating=user_rating,
                         user_playlists=user_playlists,
                         related_songs=related_songs)


@app.route('/playlists')
def playlists():
    """歌单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    filter_type = request.args.get('type', 'all')  # all, official, user

    query = Playlist.query

    if filter_type == 'official':
        query = query.filter_by(is_official=True)
    elif filter_type == 'user':
        query = query.filter_by(is_official=False)

    playlists = query.order_by(Playlist.play_count.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('playlists.html', playlists=playlists, filter_type=filter_type)


@app.route('/playlist/<int:playlist_id>')
def playlist_detail(playlist_id):
    """歌单详情"""
    playlist = Playlist.query.get_or_404(playlist_id)
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).order_by(PlaylistSong.sort_order).all()

    # 更新播放计数
    playlist.play_count += 1
    db.session.commit()

    return render_template('playlist_detail.html', playlist=playlist, playlist_songs=playlist_songs)


# ==================== 路由 - 播放与API ====================

@app.route('/play/<int:song_id>')
def play_song(song_id):
    """播放歌曲（增加播放计数）"""
    song = Song.query.get_or_404(song_id)
    song.play_count += 1
    db.session.commit()

    # 记录播放历史
    if 'user_id' in session:
        history = PlayHistory(user_id=session['user_id'], song_id=song_id)
    else:
        # 游客使用session_id
        if 'visitor_id' not in session:
            session['visitor_id'] = os.urandom(8).hex()
        history = PlayHistory(session_id=session['visitor_id'], song_id=song_id)

    db.session.add(history)
    db.session.commit()

    return redirect(url_for('song_detail', song_id=song_id))


@app.route('/api/music/<filename>')
def serve_music(filename):
    """提供音乐文件"""
    return send_from_directory(app.config['MUSIC_FOLDER'], filename)


@app.route('/api/uploads/<filename>')
def serve_upload(filename):
    """提供上传文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/playlist/<int:playlist_id>/songs')
def api_playlist_songs(playlist_id):
    """API: 获取歌单歌曲列表"""
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).order_by(PlaylistSong.sort_order).all()
    songs_data = [ps.song.to_dict() for ps in playlist_songs if ps.song.is_active]
    return jsonify(songs_data)


@app.route('/api/hot_songs')
def api_hot_songs():
    """API: 获取热门歌曲"""
    limit = request.args.get('limit', 10, type=int)
    songs = get_hot_songs(limit)
    return jsonify([s.to_dict() for s in songs])


# ==================== 路由 - 认证 ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'欢迎回来，{user.username}！', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('用户名和密码不能为空', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('两次密码输入不一致', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('密码长度不能少于6位', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('该用户名已被注册', 'danger')
            return render_template('register.html')

        user = User(
            username=username,
            password=generate_password_hash(password),
            role='user'
        )
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))


# ==================== 路由 - 用户中心 ====================

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """用户个人中心"""
    user = User.query.get(session['user_id'])
    favorites_count = Favorite.query.filter_by(user_id=user.id).count()
    playlists_count = Playlist.query.filter_by(user_id=user.id).count()
    reviews_count = Review.query.filter_by(user_id=user.id).count()
    recent_history = PlayHistory.query.filter_by(user_id=user.id).order_by(PlayHistory.played_at.desc()).limit(10).all()
    user_playlists = Playlist.query.filter_by(user_id=user.id).order_by(Playlist.created_at.desc()).all()
    user_favorites = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).limit(10).all()

    return render_template('user/dashboard.html',
                         user=user,
                         favorites_count=favorites_count,
                         playlists_count=playlists_count,
                         reviews_count=reviews_count,
                         recent_history=recent_history,
                         user_playlists=user_playlists,
                         user_favorites=user_favorites)


@app.route('/user/favorites')
@login_required
def user_favorites():
    """我的收藏"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    favorites = Favorite.query.filter_by(user_id=session['user_id']).order_by(
        Favorite.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('user/favorites.html', favorites=favorites)


@app.route('/favorite/add/<int:song_id>', methods=['POST'])
@login_required
def favorite_add(song_id):
    """收藏歌曲"""
    existing = Favorite.query.filter_by(user_id=session['user_id'], song_id=song_id).first()
    if existing:
        flash('该歌曲已在收藏列表中', 'info')
    else:
        fav = Favorite(user_id=session['user_id'], song_id=song_id)
        db.session.add(fav)
        db.session.commit()
        flash('收藏成功', 'success')
    return redirect(url_for('song_detail', song_id=song_id))


@app.route('/favorite/remove/<int:song_id>', methods=['POST'])
@login_required
def favorite_remove(song_id):
    """取消收藏"""
    fav = Favorite.query.filter_by(user_id=session['user_id'], song_id=song_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash('已取消收藏', 'info')
    return redirect(url_for('song_detail', song_id=song_id))


@app.route('/favorite/delete/<int:fav_id>', methods=['POST'])
@login_required
def favorite_delete(fav_id):
    """从收藏列表中删除"""
    fav = Favorite.query.get_or_404(fav_id)
    if fav.user_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('user_favorites'))
    db.session.delete(fav)
    db.session.commit()
    flash('已取消收藏', 'info')
    return redirect(url_for('user_favorites'))


@app.route('/user/playlists')
@login_required
def user_playlists():
    """我的歌单"""
    playlists = Playlist.query.filter_by(user_id=session['user_id']).order_by(Playlist.created_at.desc()).all()
    return render_template('user/playlists.html', playlists=playlists)


@app.route('/user/playlist/create', methods=['GET', 'POST'])
@login_required
def user_playlist_create():
    """创建歌单"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')

        if not name:
            flash('歌单名称不能为空', 'danger')
            return render_template('user/playlist_form.html', playlist=None)

        playlist = Playlist(
            name=name,
            description=description,
            user_id=session['user_id'],
            is_official=False
        )
        db.session.add(playlist)
        db.session.commit()
        flash('歌单创建成功', 'success')
        return redirect(url_for('user_playlists'))

    return render_template('user/playlist_form.html', playlist=None)


@app.route('/user/playlist/edit/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def user_playlist_edit(playlist_id):
    """编辑歌单"""
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('user_playlists'))

    if request.method == 'POST':
        playlist.name = request.form.get('name')
        playlist.description = request.form.get('description', '')
        db.session.commit()
        flash('歌单已更新', 'success')
        return redirect(url_for('user_playlists'))

    return render_template('user/playlist_form.html', playlist=playlist)


@app.route('/user/playlist/delete/<int:playlist_id>', methods=['POST'])
@login_required
def user_playlist_delete(playlist_id):
    """删除歌单"""
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('无权操作', 'danger')
        return redirect(url_for('user_playlists'))

    PlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
    db.session.delete(playlist)
    db.session.commit()
    flash('歌单已删除', 'success')
    return redirect(url_for('user_playlists'))


@app.route('/user/playlist/<int:playlist_id>/add-song/<int:song_id>', methods=['POST'])
@login_required
def user_playlist_add_song(playlist_id, song_id):
    """向歌单添加歌曲"""
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('song_detail', song_id=song_id))

    existing = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
    if existing:
        flash('该歌曲已在歌单中', 'info')
    else:
        max_order = db.session.query(db.func.max(PlaylistSong.sort_order)).filter_by(playlist_id=playlist_id).scalar()
        sort_order = (max_order or 0) + 1
        ps = PlaylistSong(playlist_id=playlist_id, song_id=song_id, sort_order=sort_order)
        db.session.add(ps)
        db.session.commit()
        flash('歌曲已添加到歌单', 'success')

    return redirect(url_for('song_detail', song_id=song_id))


@app.route('/user/playlist/<int:playlist_id>/remove-song/<int:ps_id>', methods=['POST'])
@login_required
def user_playlist_remove_song(playlist_id, ps_id):
    """从歌单移除歌曲"""
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != session['user_id']:
        flash('无权操作', 'danger')
        return redirect(url_for('user_playlists'))

    ps = PlaylistSong.query.get_or_404(ps_id)
    db.session.delete(ps)
    db.session.commit()
    flash('歌曲已从歌单移除', 'success')
    return redirect(url_for('user_playlist_detail', playlist_id=playlist_id))


@app.route('/user/playlist/view/<int:playlist_id>')
@login_required
def user_playlist_detail(playlist_id):
    """用户歌单详情"""
    playlist = Playlist.query.get_or_404(playlist_id)
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).order_by(PlaylistSong.sort_order).all()
    return render_template('user/playlist_detail.html', playlist=playlist, playlist_songs=playlist_songs)


# ==================== 路由 - 评论 ====================

@app.route('/review/add/<int:song_id>', methods=['POST'])
@login_required
def review_add(song_id):
    """添加评论"""
    rating = int(request.form.get('rating', 5))
    content = request.form.get('content', '')

    if rating < 1 or rating > 5:
        rating = 5

    # 检查是否已评论过
    existing = Review.query.filter_by(user_id=session['user_id'], song_id=song_id).first()
    if existing:
        existing.rating = rating
        existing.content = content
        flash('评论已更新', 'success')
    else:
        review = Review(
            user_id=session['user_id'],
            song_id=song_id,
            rating=rating,
            content=content
        )
        db.session.add(review)
        flash('评论发表成功', 'success')

    db.session.commit()
    return redirect(url_for('song_detail', song_id=song_id))


@app.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def review_delete(review_id):
    """删除评论"""
    review = Review.query.get_or_404(review_id)
    if review.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('无权操作', 'danger')
        return redirect(url_for('index'))

    song_id = review.song_id
    db.session.delete(review)
    db.session.commit()
    flash('评论已删除', 'info')
    return redirect(url_for('song_detail', song_id=song_id))


# ==================== 路由 - 管理员 ====================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """管理员控制台"""
    total_songs = Song.query.count()
    active_songs = Song.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_playlists = Playlist.query.count()
    total_play_count = db.session.query(db.func.sum(Song.play_count)).scalar() or 0
    total_reviews = Review.query.count()

    # 热门歌曲排行
    hot_songs = Song.query.order_by(Song.play_count.desc()).limit(10).all()

    # 各流派统计
    genres_data = db.session.query(
        Song.genre,
        db.func.count(Song.id).label('count')
    ).filter(Song.is_active == True).group_by(Song.genre).all()

    return render_template('admin/dashboard.html',
                         total_songs=total_songs,
                         active_songs=active_songs,
                         total_users=total_users,
                         total_playlists=total_playlists,
                         total_play_count=total_play_count,
                         total_reviews=total_reviews,
                         hot_songs=hot_songs,
                         genres_data=genres_data)


@app.route('/admin/songs')
@admin_required
def admin_songs():
    """歌曲管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    search = request.args.get('search', '')
    genre_filter = request.args.get('genre', '')

    query = Song.query

    if search:
        query = query.filter(
            (Song.title.contains(search)) |
            (Song.artist.contains(search))
        )

    if genre_filter:
        query = query.filter_by(genre=genre_filter)

    songs = query.order_by(Song.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    genres = ['流行', '摇滚', '古典', '电子', '民谣', 'R&B', '爵士', '嘻哈']
    return render_template('admin/songs.html', songs=songs, search=search, genre_filter=genre_filter, genres=genres)


@app.route('/admin/song/add', methods=['GET', 'POST'])
@admin_required
def admin_song_add():
    """添加歌曲"""
    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            flash('歌曲名称不能为空', 'danger')
            return render_template('admin/song_form.html', song=None)

        # 处理音乐文件上传
        music_file = request.files.get('music_file')
        file_path = ''
        if music_file and music_file.filename:
            filename = save_upload_file(music_file, 'music')
            if filename:
                file_path = filename
            else:
                flash('音乐文件格式不支持（支持 mp3/wav/flac）', 'danger')
                return render_template('admin/song_form.html', song=None)
        else:
            flash('请上传音乐文件', 'danger')
            return render_template('admin/song_form.html', song=None)

        # 处理封面图片
        cover_file = request.files.get('cover_image')
        cover_path = 'default_cover.jpg'
        if cover_file and cover_file.filename:
            filename = save_upload_file(cover_file)
            if filename:
                cover_path = filename

        song = Song(
            title=title,
            artist=request.form.get('artist', '未知艺术家'),
            album=request.form.get('album', '未知专辑'),
            genre=request.form.get('genre', '流行'),
            duration=int(request.form.get('duration', 0)),
            file_path=file_path,
            cover_image=cover_path,
            lyrics=request.form.get('lyrics', ''),
            is_active=True
        )
        db.session.add(song)
        db.session.commit()
        flash('歌曲添加成功', 'success')
        return redirect(url_for('admin_songs'))

    return render_template('admin/song_form.html', song=None)


@app.route('/admin/song/edit/<int:song_id>', methods=['GET', 'POST'])
@admin_required
def admin_song_edit(song_id):
    """编辑歌曲"""
    song = Song.query.get_or_404(song_id)

    if request.method == 'POST':
        song.title = request.form.get('title')
        song.artist = request.form.get('artist', '未知艺术家')
        song.album = request.form.get('album', '未知专辑')
        song.genre = request.form.get('genre', '流行')
        song.duration = int(request.form.get('duration', 0))
        song.lyrics = request.form.get('lyrics', '')

        # 处理音乐文件更新
        music_file = request.files.get('music_file')
        if music_file and music_file.filename:
            delete_file(song.file_path, 'music')
            filename = save_upload_file(music_file, 'music')
            if filename:
                song.file_path = filename

        # 处理封面更新
        cover_file = request.files.get('cover_image')
        if cover_file and cover_file.filename:
            if song.cover_image and song.cover_image != 'default_cover.jpg':
                delete_file(song.cover_image)
            filename = save_upload_file(cover_file)
            if filename:
                song.cover_image = filename

        db.session.commit()
        flash('歌曲信息已更新', 'success')
        return redirect(url_for('admin_songs'))

    return render_template('admin/song_form.html', song=song)


@app.route('/admin/song/toggle/<int:song_id>', methods=['POST'])
@admin_required
def admin_song_toggle(song_id):
    """切换歌曲状态（上架/下架）"""
    song = Song.query.get_or_404(song_id)
    song.is_active = not song.is_active
    db.session.commit()
    status = '上架' if song.is_active else '下架'
    flash(f'歌曲已{status}', 'success')
    return redirect(url_for('admin_songs'))


@app.route('/admin/song/delete/<int:song_id>', methods=['POST'])
@admin_required
def admin_song_delete(song_id):
    """删除歌曲"""
    song = Song.query.get_or_404(song_id)

    # 删除关联数据
    PlaylistSong.query.filter_by(song_id=song_id).delete()
    Favorite.query.filter_by(song_id=song_id).delete()
    Review.query.filter_by(song_id=song_id).delete()
    PlayHistory.query.filter_by(song_id=song_id).delete()

    # 删除文件
    delete_file(song.file_path, 'music')
    if song.cover_image and song.cover_image != 'default_cover.jpg':
        delete_file(song.cover_image)

    db.session.delete(song)
    db.session.commit()
    flash('歌曲已删除', 'success')
    return redirect(url_for('admin_songs'))


@app.route('/admin/users')
@admin_required
def admin_users():
    """用户管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(User.username.contains(search))

    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/users.html', users=users, search=search)


@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_user_delete(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('不能删除管理员账户', 'danger')
        return redirect(url_for('admin_users'))

    # 删除关联数据
    Favorite.query.filter_by(user_id=user_id).delete()
    Review.query.filter_by(user_id=user_id).delete()
    PlayHistory.query.filter_by(user_id=user_id).delete()
    PlaylistSong.query.filter(
        PlaylistSong.playlist_id.in_(
            db.session.query(Playlist.id).filter_by(user_id=user_id)
        )
    ).delete(synchronize_session=False)
    Playlist.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/playlists')
@admin_required
def admin_playlists():
    """歌单管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    filter_type = request.args.get('type', 'all')

    query = Playlist.query
    if filter_type == 'official':
        query = query.filter_by(is_official=True)
    elif filter_type == 'user':
        query = query.filter_by(is_official=False)

    playlists = query.order_by(Playlist.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/playlists.html', playlists=playlists, filter_type=filter_type)


@app.route('/admin/playlist/create', methods=['GET', 'POST'])
@admin_required
def admin_playlist_create():
    """创建推荐歌单"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        is_official = request.form.get('is_official') == 'on'

        if not name:
            flash('歌单名称不能为空', 'danger')
            return render_template('admin/playlist_form.html', playlist=None, songs=[])

        playlist = Playlist(
            name=name,
            description=description,
            user_id=session['user_id'],
            is_official=is_official
        )
        db.session.add(playlist)
        db.session.commit()

        # 添加歌曲到歌单
        song_ids = request.form.getlist('song_ids')
        for i, sid in enumerate(song_ids):
            ps = PlaylistSong(playlist_id=playlist.id, song_id=int(sid), sort_order=i)
            db.session.add(ps)

        db.session.commit()
        flash('歌单创建成功', 'success')
        return redirect(url_for('admin_playlists'))

    songs = Song.query.filter_by(is_active=True).order_by(Song.title).all()
    return render_template('admin/playlist_form.html', playlist=None, songs=songs)


@app.route('/admin/playlist/edit/<int:playlist_id>', methods=['GET', 'POST'])
@admin_required
def admin_playlist_edit(playlist_id):
    """编辑推荐歌单"""
    playlist = Playlist.query.get_or_404(playlist_id)

    if request.method == 'POST':
        playlist.name = request.form.get('name')
        playlist.description = request.form.get('description', '')
        playlist.is_official = request.form.get('is_official') == 'on'

        # 更新歌曲列表
        PlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
        song_ids = request.form.getlist('song_ids')
        for i, sid in enumerate(song_ids):
            ps = PlaylistSong(playlist_id=playlist.id, song_id=int(sid), sort_order=i)
            db.session.add(ps)

        db.session.commit()
        flash('歌单已更新', 'success')
        return redirect(url_for('admin_playlists'))

    songs = Song.query.filter_by(is_active=True).order_by(Song.title).all()
    playlist_song_ids = [ps.song_id for ps in PlaylistSong.query.filter_by(playlist_id=playlist_id).all()]
    return render_template('admin/playlist_form.html', playlist=playlist, songs=songs, playlist_song_ids=playlist_song_ids)


@app.route('/admin/playlist/delete/<int:playlist_id>', methods=['POST'])
@admin_required
def admin_playlist_delete(playlist_id):
    """删除推荐歌单"""
    PlaylistSong.query.filter_by(playlist_id=playlist_id).delete()
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    flash('歌单已删除', 'success')
    return redirect(url_for('admin_playlists'))


@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    """数据统计"""
    total_songs = Song.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_playlists = Playlist.query.count()
    total_play_count = db.session.query(db.func.sum(Song.play_count)).scalar() or 0
    total_reviews = Review.query.count()

    # 按流派统计
    genre_stats = db.session.query(
        Song.genre,
        db.func.count(Song.id).label('count'),
        db.func.sum(Song.play_count).label('total_plays')
    ).filter(Song.is_active == True).group_by(Song.genre).all()

    # 每月新增歌曲（最近6个月）
    monthly_songs = []
    from datetime import timedelta
    for i in range(5, -1, -1):
        month_start = datetime.now().replace(day=1) - timedelta(days=30 * i)
        if i < 5:
            month_end = datetime.now().replace(day=1) - timedelta(days=30 * (i - 1))
        else:
            month_end = datetime.now()
        count = Song.query.filter(Song.created_at >= month_start, Song.created_at < month_end).count()
        monthly_songs.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })

    return render_template('admin/statistics.html',
                         total_songs=total_songs,
                         total_users=total_users,
                         total_playlists=total_playlists,
                         total_play_count=total_play_count,
                         total_reviews=total_reviews,
                         genre_stats=genre_stats,
                         monthly_songs=monthly_songs)


# ==================== 初始化数据 ====================

def init_db():
    """初始化数据库和默认数据"""
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

    # 创建演示用户
    if not User.query.filter_by(username='demo').first():
        demo = User(
            username='demo',
            password=generate_password_hash('demo123'),
            role='user'
        )
        db.session.add(demo)
        db.session.commit()
        print('演示用户已创建: demo / demo123')

    # 初始化示例音乐数据（如果没有歌曲）
    if Song.query.count() == 0:
        print('初始化示例音乐数据...')
        init_sample_music()


def init_sample_music():
    """初始化示例音乐数据（内置推荐歌单）"""
    sample_songs = [
        # 流行
        {'title': '晴天', 'artist': '周杰伦', 'album': '叶惠美', 'genre': '流行', 'duration': 269, 'file_path': 'sample.mp3'},
        {'title': '起风了', 'artist': '买辣椒也用券', 'album': '起风了', 'genre': '流行', 'duration': 325, 'file_path': 'sample.mp3'},
        {'title': '平凡之路', 'artist': '朴树', 'album': '猎户星座', 'genre': '流行', 'duration': 301, 'file_path': 'sample.mp3'},
        {'title': '光年之外', 'artist': 'G.E.M.邓紫棋', 'album': '光年之外', 'genre': '流行', 'duration': 264, 'file_path': 'sample.mp3'},
        # 摇滚
        {'title': '海阔天空', 'artist': 'Beyond', 'album': '乐与怒', 'genre': '摇滚', 'duration': 315, 'file_path': 'sample.mp3'},
        {'title': '无地自容', 'artist': '黑豹乐队', 'album': '黑豹', 'genre': '摇滚', 'duration': 292, 'file_path': 'sample.mp3'},
        {'title': '梦回唐朝', 'artist': '唐朝乐队', 'album': '唐朝', 'genre': '摇滚', 'duration': 346, 'file_path': 'sample.mp3'},
        # 古典
        {'title': '月光奏鸣曲', 'artist': '贝多芬', 'album': '贝多芬钢琴奏鸣曲集', 'genre': '古典', 'duration': 455, 'file_path': 'sample.mp3'},
        {'title': '四季·春', 'artist': '维瓦尔第', 'album': '四季', 'genre': '古典', 'duration': 208, 'file_path': 'sample.mp3'},
        {'title': '卡农', 'artist': '帕赫贝尔', 'album': '巴洛克名曲集', 'genre': '古典', 'duration': 312, 'file_path': 'sample.mp3'},
        # 电子
        {'title': 'Faded', 'artist': 'Alan Walker', 'album': 'Faded', 'genre': '电子', 'duration': 212, 'file_path': 'sample.mp3'},
        {'title': 'Unity', 'artist': 'TheFatRat', 'album': 'Unity', 'genre': '电子', 'duration': 274, 'file_path': 'sample.mp3'},
        # 民谣
        {'title': '成都', 'artist': '赵雷', 'album': '无法长大', 'genre': '民谣', 'duration': 328, 'file_path': 'sample.mp3'},
        {'title': '南山南', 'artist': '马頔', 'album': '南山南', 'genre': '民谣', 'duration': 308, 'file_path': 'sample.mp3'},
        # R&B
        {'title': '爱很简单', 'artist': '陶喆', 'album': 'David Tao', 'genre': 'R&B', 'duration': 268, 'file_path': 'sample.mp3'},
        {'title': '将军令', 'artist': '王力宏', 'album': '心中的日月', 'genre': 'R&B', 'duration': 221, 'file_path': 'sample.mp3'},
        # 爵士
        {'title': 'Fly Me to the Moon', 'artist': 'Frank Sinatra', 'album': 'It Might as Well Be Swing', 'genre': '爵士', 'duration': 216, 'file_path': 'sample.mp3'},
        {'title': 'Take Five', 'artist': 'Dave Brubeck', 'album': 'Time Out', 'genre': '爵士', 'duration': 324, 'file_path': 'sample.mp3'},
        # 嘻哈
        {'title': '以父之名', 'artist': '周杰伦', 'album': '叶惠美', 'genre': '嘻哈', 'duration': 342, 'file_path': 'sample.mp3'},
        {'title': '中国话', 'artist': 'S.H.E', 'album': 'Play', 'genre': '嘻哈', 'duration': 194, 'file_path': 'sample.mp3'},
    ]

    song_objects = []
    for s in sample_songs:
        song = Song(**s, is_active=True, play_count=random.randint(100, 10000))
        db.session.add(song)
        song_objects.append(song)
    db.session.commit()

    # 创建官方推荐歌单
    official_playlists = [
        {'name': '热门金曲榜', 'description': '当前最受欢迎的热门歌曲，大家都在听！', 'genre': '流行'},
        {'name': '摇滚经典', 'description': '经典摇滚歌曲合集，感受摇滚的魅力', 'genre': '摇滚'},
        {'name': '古典音乐精选', 'description': '古典音乐大师代表作精选集', 'genre': '古典'},
        {'name': '电子音乐派对', 'description': '燃爆全场的电子音乐，一起嗨起来', 'genre': '电子'},
        {'name': '民谣故事', 'description': '每一首民谣都是一个故事', 'genre': '民谣'},
        {'name': '华语流行精选', 'description': '精选华语乐坛最动听的流行歌曲', 'genre': '流行'},
    ]

    for i, pl in enumerate(official_playlists):
        playlist = Playlist(
            name=pl['name'],
            description=pl['description'],
            is_official=True,
            user_id=1,
            play_count=random.randint(500, 5000)
        )
        db.session.add(playlist)
        db.session.flush()

        # 给歌单添加对应流派的歌曲
        genre_songs = [s for s in song_objects if s.genre == pl['genre']]
        for j, song in enumerate(genre_songs):
            ps = PlaylistSong(playlist_id=playlist.id, song_id=song.id, sort_order=j)
            db.session.add(ps)

    db.session.commit()
    print(f'已创建 {len(sample_songs)} 首示例歌曲和 {len(official_playlists)} 个推荐歌单')


# ==================== 主程序 ====================

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='127.0.0.1', port=5001)