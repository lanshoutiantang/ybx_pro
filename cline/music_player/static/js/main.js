// ==================== 在线音乐管理系统 - 前端交互 ====================

// 播放器功能
class MusicPlayer {
    constructor() {
        this.audio = new Audio();
        this.currentSong = null;
        this.isPlaying = false;
        this.playlist = [];
        this.currentIndex = 0;
        this.init();
    }

    init() {
        // 监听歌曲结束自动下一首
        this.audio.addEventListener('ended', () => this.next());

        // 监听播放错误
        this.audio.addEventListener('error', (e) => {
            console.error('播放错误:', e);
        });
    }

    play(song) {
        if (typeof song === 'object') {
            this.currentSong = song;
            const musicUrl = `/api/music/${song.file_path}`;
            this.audio.src = musicUrl;
            this.audio.play().then(() => {
                this.isPlaying = true;
                this.updatePlayerUI(song);
            }).catch(err => {
                console.error('播放失败:', err);
            });
        }
    }

    togglePlay() {
        if (this.audio.paused) {
            this.audio.play();
            this.isPlaying = true;
        } else {
            this.audio.pause();
            this.isPlaying = false;
        }
    }

    next() {
        if (this.playlist.length > 0) {
            this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
            this.play(this.playlist[this.currentIndex]);
        }
    }

    prev() {
        if (this.playlist.length > 0) {
            this.currentIndex = (this.currentIndex - 1 + this.playlist.length) % this.playlist.length;
            this.play(this.playlist[this.currentIndex]);
        }
    }

    setPlaylist(songs, startIndex = 0) {
        this.playlist = songs;
        this.currentIndex = startIndex;
    }

    updatePlayerUI(song) {
        // 更新页面标题
        document.title = `${song.title} - ${song.artist} - 在线音乐管理系统`;

        // 触发自定义事件
        const event = new CustomEvent('songChange', { detail: song });
        document.dispatchEvent(event);
    }
}

// 初始化全局播放器
const musicPlayer = new MusicPlayer();

// ==================== DOM 操作函数 ====================

function formatDuration(seconds) {
    if (!seconds || seconds === 0) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatPlayCount(count) {
    if (!count) return '0';
    if (count >= 10000) {
        return (count / 10000).toFixed(1) + '万';
    }
    return count.toString();
}

// 播放歌曲（通过play路由，增加播放计数）
function playSong(songId) {
    window.location.href = `/play/${songId}`;
}

// 添加到歌单
function addToPlaylist(playlistId, songId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/user/playlist/${playlistId}/add-song/${songId}`;
    form.style.display = 'none';
    document.body.appendChild(form);
    form.submit();
}

// 收藏/取消收藏切换
function toggleFavorite(songId, isFavorited) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = isFavorited ? `/favorite/remove/${songId}` : `/favorite/add/${songId}`;
    form.style.display = 'none';
    document.body.appendChild(form);
    form.submit();
}

// ==================== 页面加载完成后执行 ====================

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有 tooltip
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) {
        return new bootstrap.Tooltip(el);
    });

    // 为歌曲卡片添加点击事件
    document.querySelectorAll('.song-card').forEach(card => {
        card.addEventListener('click', function(e) {
            const songId = this.dataset.songId;
            if (songId && !e.target.closest('.play-btn') && !e.target.closest('button') && !e.target.closest('a')) {
                window.location.href = `/song/${songId}`;
            }
        });
    });

    // 为歌单卡片添加点击事件
    document.querySelectorAll('.playlist-card').forEach(card => {
        card.addEventListener('click', function(e) {
            const playlistId = this.dataset.playlistId;
            if (playlistId && !e.target.closest('a')) {
                window.location.href = `/playlist/${playlistId}`;
            }
        });
    });

    // 确认删除弹窗
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || '确定要执行此操作吗？')) {
                e.preventDefault();
            }
        });
    });
});