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
            // 尝试播放失败时，更新UI状态
            this.isPlaying = false;
            this.updatePlayButtonUI();
        });

        // 监听播放状态
        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayButtonUI();
        });

        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayButtonUI();
        });

        // 更新时间显示
        this.audio.addEventListener('timeupdate', () => {
            this.updateProgressUI();
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
                // 异步增加播放计数
                this.incrementPlayCount(song.id);
            }).catch(err => {
                console.error('播放失败:', err);
                alert('无法播放此歌曲，音频文件可能不存在或格式不支持');
            });
        }
    }

    // 通过歌曲ID播放（从服务器获取歌曲信息）
    playById(songId, songTitle, songArtist, songFilePath) {
        const song = {
            id: songId,
            title: songTitle,
            artist: songArtist,
            file_path: songFilePath
        };
        this.play(song);
    }

    // 异步增加播放计数
    incrementPlayCount(songId) {
        fetch(`/play/${songId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        }).catch(err => console.error('播放计数更新失败:', err));
    }

    togglePlay() {
        if (this.audio.paused) {
            if (this.audio.src) {
                this.audio.play();
            }
        } else {
            this.audio.pause();
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

        // 更新浮动播放器UI
        const playerBar = document.getElementById('music-player-bar');
        if (playerBar) {
            playerBar.style.display = 'flex';
            const titleEl = document.getElementById('player-song-title');
            const artistEl = document.getElementById('player-song-artist');
            if (titleEl) titleEl.textContent = song.title;
            if (artistEl) artistEl.textContent = song.artist;

            // 更新播放/暂停按钮图标
            const playBtn = document.getElementById('player-play-btn');
            if (playBtn) {
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }
        }
    }

    updatePlayButtonUI() {
        // 更新浮动播放器的播放/暂停按钮
        const playBtn = document.getElementById('player-play-btn');
        if (playBtn) {
            playBtn.innerHTML = this.isPlaying ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
        }

        // 更新所有页面上的播放按钮
        document.querySelectorAll('.play-btn').forEach(btn => {
            const songId = btn.dataset.songId;
            if (this.currentSong && songId && parseInt(songId) === this.currentSong.id) {
                btn.innerHTML = this.isPlaying ? '<i class="fas fa-pause"></i>' : '<i class="fas fa-play"></i>';
            }
        });
    }

    updateProgressUI() {
        const progressBar = document.getElementById('player-progress');
        const currentTimeEl = document.getElementById('player-current-time');
        const durationEl = document.getElementById('player-duration');
        if (progressBar && this.audio.duration) {
            const progress = (this.audio.currentTime / this.audio.duration) * 100;
            progressBar.style.width = progress + '%';
        }
        if (currentTimeEl) {
            currentTimeEl.textContent = this.formatTime(this.audio.currentTime);
        }
        if (durationEl && this.audio.duration) {
            durationEl.textContent = this.formatTime(this.audio.duration);
        }
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    seekTo(e) {
        const progressContainer = document.getElementById('player-progress-container');
        if (progressContainer && this.audio.duration) {
            const rect = progressContainer.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            this.audio.currentTime = pos * this.audio.duration;
        }
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

// 播放歌曲（使用JS播放器，不跳转页面）
function playSong(songId) {
    // 查找当前页面的歌曲数据
    const card = document.querySelector(`[data-song-id="${songId}"]`);
    if (card) {
        // 尝试从song-card中获取标题和歌手
        let titleEl = card.querySelector('.song-title');
        let artistEl = card.querySelector('.song-artist');
        let title = titleEl ? titleEl.textContent : '';
        let artist = artistEl ? artistEl.textContent : '';
        
        // 如果找不到（可能在详情页），从页面其他地方获取
        if (!title) {
            titleEl = document.querySelector('h4'); // 详情页的歌曲标题是h4
            if (titleEl && titleEl.textContent && !titleEl.querySelector('i')) {
                title = titleEl.textContent;
            }
        }
        if (!artist) {
            // 查找详情页中灰色文字的歌手名
            const detailPage = document.querySelector('.col-md-4 .card .card-body p');
            if (detailPage) {
                artist = detailPage.textContent;
            }
        }
        if (!title) title = '未知歌曲';
        if (!artist) artist = '未知艺术家';
        
        musicPlayer.playById(songId, title, artist, 'sample.mp3');
    } else {
        // 如果页面上没有找到卡片数据，跳转到详情页
        window.location.href = `/play/${songId}`;
    }
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

    // 播放按钮点击事件（使用JS播放器）
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const songId = this.dataset.songId;
            if (songId) {
                // 如果当前正在播放此歌曲，则切换播放/暂停
                if (musicPlayer.currentSong && parseInt(songId) === musicPlayer.currentSong.id) {
                    musicPlayer.togglePlay();
                } else {
                    playSong(songId);
                }
            }
        });
    });

    // 浮动播放器的进度条点击
    const progressContainer = document.getElementById('player-progress-container');
    if (progressContainer) {
        progressContainer.addEventListener('click', function(e) {
            musicPlayer.seekTo(e);
        });
    }

    // 浮动播放器的播放/暂停按钮
    const playerPlayBtn = document.getElementById('player-play-btn');
    if (playerPlayBtn) {
        playerPlayBtn.addEventListener('click', function() {
            musicPlayer.togglePlay();
        });
    }

    // 上一首/下一首
    const prevBtn = document.getElementById('player-prev-btn');
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            musicPlayer.prev();
        });
    }
    const nextBtn = document.getElementById('player-next-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            musicPlayer.next();
        });
    }
});