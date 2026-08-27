<template>
  <div class="video-player-container">
    <!-- 视频播放区域 -->
    <div class="video-wrapper">
      <video
        ref="videoPlayer"
        class="video-element"
        :src="actualSrc || src"
        :type="videoType"
        :poster="poster"
        @ended="onEnd"
        @error="handleVideoError"
        @canplay="handleCanPlay"
        @waiting="handleWaiting"
        @loadeddata="handleLoadedData"
        @play="handlePlay"
        @pause="handlePause">
        您的浏览器不支持HTML5 video标签。
      </video>
      
      <!-- 自定义播放控制栏 -->
      <div class="custom-controls" v-if="!loading && !error">
        <div class="progress-bar" @click="handleProgressClick" @mousedown="startDrag" @touchstart="startDrag">
          <div class="progress" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="controls-bottom">
          <button class="control-btn" @click="togglePlay">
            <span v-if="!isPlaying">▶</span>
            <span v-else>⏸</span>
          </button>
          <div class="time-display">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </div>
          <button class="control-btn" @click="toggleMute">
            <span v-if="!isMuted">🔊</span>
            <span v-else>🔇</span>
          </button>
          <button class="control-btn" @click="toggleFullscreen">
            ⛶
          </button>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p class="loading-text">{{ loadingMessage }}</p>
      </div>
    </div>
    
    <!-- 错误状态 -->
    <div v-if="error" class="error-overlay">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3 class="error-title">视频播放失败</h3>
        <p class="error-message">{{ errorMessage }}</p>
        <div class="error-actions">
          <button @click="retryPlay" class="action-btn primary">
            重新播放
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Hls from 'hls.js'

export default {
  name: 'VideoPlay',
  props: {
    src: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'video/mp4'
    },
    poster: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      actualSrc: null,
      videoType: 'video/mp4',
      hls: null,
      loading: false,
      error: false,
      errorMessage: '',
      loadingMessage: '视频加载中...',
      retryCount: 0,
      isPlaying: false,
      isMuted: false,
      currentTime: 0,
      duration: 0,
      progress: 0
    }
  },
  mounted() {
    this.startPlayback()
    this.setupVideoListeners()
  },
  beforeUnmount() {
    this.cleanupVideoListeners()
    
    // 清理HLS实例
    if (this.hls) {
      this.hls.destroy()
      this.hls = null
    }
  },
  methods: {
    startPlayback() {
      this.loading = true
      this.error = false
      this.retryCount = 0
      this.loadingMessage = '视频加载中...'
      
      // 使用从父组件传递的视频源
      this.actualSrc = this.src
      
      // 检测视频类型
      this.detectVideoType(this.src)
      
      // 初始化播放器
      this.initPlayer()
    },
    
    detectVideoType(url) {
      if (!url) {
        this.videoType = 'video/mp4'
        return
      }
      
      // 检测HLS流
      if (url.includes('.m3u8')) {
        this.videoType = 'application/x-mpegURL'
      } 
      // 检测MP4
      else if (url.includes('.mp4')) {
        this.videoType = 'video/mp4'
      }
      // 检测WebM
      else if (url.includes('.webm')) {
        this.videoType = 'video/webm'
      }
      // 默认使用MP4
      else {
        this.videoType = 'video/mp4'
      }
      
      console.log('检测到视频类型:', this.videoType, 'URL:', url)
    },
    
    initPlayer() {
      const video = this.$refs.videoPlayer
      if (!video) {
        console.error('视频元素未找到')
        this.handlePlaybackError('视频元素未找到')
        return
      }
      
      // 如果是HLS流，使用HLS.js
      if (this.videoType === 'application/x-mpegURL') {
        this.initHlsPlayer(video)
      } else {
        // 普通视频格式
        this.initNativePlayer(video)
      }
    },
    
    initHlsPlayer(video) {
      console.log('初始化HLS播放器')
      
      // 清理之前的HLS实例
      if (this.hls) {
        this.hls.destroy()
        this.hls = null
      }
      
      // 检查浏览器是否支持HLS
      if (Hls.isSupported()) {
        console.log('浏览器支持HLS，使用HLS.js')
        this.hls = new Hls({
          enableWorker: false,
          lowLatencyMode: true,
          backBufferLength: 90
        })
        
        this.hls.loadSource(this.src)
        this.hls.attachMedia(video)
        
        this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
          console.log('HLS流解析完成，可以播放')
          this.loading = false
          this.error = false
        })
        
        this.hls.on(Hls.Events.ERROR, (event, data) => {
          console.error('HLS播放错误:', data)
          this.handlePlaybackError('HLS流播放失败')
        })
        
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari等原生支持HLS的浏览器
        console.log('浏览器原生支持HLS')
        video.src = this.src
        this.loading = false
        this.error = false
      } else {
        console.error('浏览器不支持HLS播放')
        this.handlePlaybackError('您的浏览器不支持HLS视频播放')
      }
    },
    
    initNativePlayer(video) {
      console.log('初始化原生播放器')
      video.src = this.src
      video.type = this.videoType
      
      // 监听视频事件
      video.addEventListener('canplay', () => {
        console.log('视频可以播放')
        this.loading = false
        this.error = false
      })
      
      video.addEventListener('error', (e) => {
        console.error('视频播放错误:', e)
        this.handlePlaybackError('视频播放失败')
      })
      
      // 设置超时检测
      setTimeout(() => {
        if (this.loading) {
          console.log('视频加载超时')
          this.handlePlaybackError('视频加载超时，请检查网络连接')
        }
      }, 10000)
    },
    
    handlePlaybackError(message) {
      console.error('播放错误:', message)
      this.loading = false
      this.error = true
      this.errorMessage = message
      
      // 尝试使用备用MP4源
      this.useFallbackSource()
    },
    
    useFallbackSource() {
      console.log('使用备用MP4源')
      const fallbackUrl = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
      
      // 清理HLS实例
      if (this.hls) {
        this.hls.destroy()
        this.hls = null
      }
      
      const video = this.$refs.videoPlayer
      if (video) {
        video.src = fallbackUrl
        video.type = 'video/mp4'
        this.actualSrc = fallbackUrl
        this.videoType = 'video/mp4'
        
        video.addEventListener('canplay', () => {
          console.log('备用视频可以播放')
          this.loading = false
          this.error = false
        })
      }
    },
    
    setupVideoListeners() {
      const video = this.$refs.videoPlayer
      if (video) {
        video.addEventListener('timeupdate', this.handleTimeUpdate)
        video.addEventListener('durationchange', this.handleDurationChange)
      }
    },
    
    cleanupVideoListeners() {
      const video = this.$refs.videoPlayer
      if (video) {
        video.removeEventListener('timeupdate', this.handleTimeUpdate)
        video.removeEventListener('durationchange', this.handleDurationChange)
      }
    },
    
    handleTimeUpdate() {
      const video = this.$refs.videoPlayer
      if (video) {
        this.currentTime = video.currentTime
        this.duration = video.duration || 0
        this.progress = video.duration ? (video.currentTime / video.duration) * 100 : 0
      }
    },
    
    handleDurationChange() {
      const video = this.$refs.videoPlayer
      if (video) {
        this.duration = video.duration || 0
      }
    },
    
    togglePlay() {
      const video = this.$refs.videoPlayer
      if (video) {
        if (video.paused) {
          video.play()
        } else {
          video.pause()
        }
      }
    },
    
    handlePlay() {
      this.isPlaying = true
    },
    
    handlePause() {
      this.isPlaying = false
    },
    
    toggleMute() {
      const video = this.$refs.videoPlayer
      if (video) {
        video.muted = !video.muted
        this.isMuted = video.muted
      }
    },
    
    toggleFullscreen() {
      const videoWrapper = this.$el.querySelector('.video-wrapper')
      if (videoWrapper) {
        if (!document.fullscreenElement) {
          if (videoWrapper.requestFullscreen) {
            videoWrapper.requestFullscreen()
          }
        } else {
          if (document.exitFullscreen) {
            document.exitFullscreen()
          }
        }
      }
    },
    
    formatTime(seconds) {
      if (!seconds || isNaN(seconds)) return '00:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    
    retryPlay() {
      this.startPlayback()
    },
    
    handleVideoError(event) {
      console.error('视频播放错误:', event)
      this.error = true
      this.loading = false
      this.errorMessage = '视频播放失败，请重新播放'
    },
    
    handleCanPlay() {
      this.loading = false
      this.error = false
    },
    
    handleWaiting() {
      this.loading = true
      this.loadingMessage = '视频缓冲中...'
    },
    
    handleLoadedData() {
      this.loading = false
    },
    
    onEnd() {
      console.log('视频播放结束')
      this.isPlaying = false
    },
    
    handleProgressClick(event) {
      const progressBar = event.currentTarget
      const rect = progressBar.getBoundingClientRect()
      const clickPosition = event.clientX - rect.left
      const progressBarWidth = rect.width
      const percentage = (clickPosition / progressBarWidth) * 100
      
      this.seekToPercentage(percentage)
    },
    
    startDrag(event) {
      event.preventDefault()
      
      const progressBar = event.currentTarget
      const rect = progressBar.getBoundingClientRect()
      const progressBarWidth = rect.width
      
      const handleMove = (moveEvent) => {
        const clientX = moveEvent.clientX || (moveEvent.touches && moveEvent.touches[0].clientX)
        if (!clientX) return
        
        const clickPosition = Math.max(0, Math.min(clientX - rect.left, progressBarWidth))
        const percentage = (clickPosition / progressBarWidth) * 100
        
        this.progress = percentage
      }
      
      const handleEnd = () => {
        document.removeEventListener('mousemove', handleMove)
        document.removeEventListener('mouseup', handleEnd)
        document.removeEventListener('touchmove', handleMove)
        document.removeEventListener('touchend', handleEnd)
        
        this.seekToPercentage(this.progress)
      }
      
      document.addEventListener('mousemove', handleMove)
      document.addEventListener('mouseup', handleEnd)
      document.addEventListener('touchmove', handleMove)
      document.addEventListener('touchend', handleEnd)
      
      // 立即更新一次位置
      handleMove(event)
    },
    
    seekToPercentage(percentage) {
      const video = this.$refs.videoPlayer
      if (video && video.duration) {
        const targetTime = (percentage / 100) * video.duration
        video.currentTime = targetTime
        this.currentTime = targetTime
        
        // 如果视频暂停，播放视频
        if (video.paused) {
          video.play()
        }
      }
    }
  }
}
</script>

<style scoped>
.video-player-container {
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.video-wrapper {
  position: relative;
  width: 100%;
  min-height: 400px;
  max-height: 600px;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: auto;
  max-height: 100%;
  object-fit: contain;
}

.custom-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
  padding: 25px 20px 20px;
  transition: all 0.3s ease;
  z-index: 20;
  backdrop-filter: blur(20px);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  margin-bottom: 20px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.progress-bar:hover {
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
}

.progress {
  height: 100%;
  background: linear-gradient(90deg, #ff6b6b, #ffa726, #ffd93d);
  border-radius: 3px;
  transition: width 0.2s ease;
  position: relative;
  box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
}

.controls-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}

.control-btn {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s ease;
  backdrop-filter: blur(15px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
}

.control-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.15));
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.time-display {
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  font-weight: 600;
  flex: 1;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.5px;
}

/* 加载状态样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
}

.loading-content {
  text-align: center;
  color: white;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #ff6b6b;
  border-right: 4px solid #ffa726;
  border-bottom: 4px solid #ffd93d;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin: 0 auto 20px;
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
}

.loading-text {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

/* 错误状态样式 */
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
}

.error-content {
  text-align: center;
  color: white;
  padding: 40px;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #ff6b6b;
  text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
}

.error-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 15px 0;
  color: #ff6b6b;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.error-message {
  font-size: 16px;
  margin: 0 0 25px 0;
  opacity: 0.9;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.error-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.action-btn.primary {
  background: linear-gradient(135deg, #ff6b6b, #ff5252);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn.primary:hover {
  background: linear-gradient(135deg, #ff5252, #ff1744);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
}

.action-btn.secondary {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn.secondary:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.15));
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
}

/* 备用源提示样式 */
.backup-notice {
  position: absolute;
  top: 20px;
  left: 20px;
  background: linear-gradient(135deg, #ffa726, #ff6b6b, #ff1744);
  color: white;
  padding: 10px 20px;
  border-radius: 25px;
  font-size: 13px;
  font-weight: 600;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: pulse 2s infinite;
}

.backup-icon {
  font-size: 14px;
}

/* 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { transform: scale(1); box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4); }
  50% { transform: scale(1.05); box-shadow: 0 12px 35px rgba(255, 107, 107, 0.6); }
  100% { transform: scale(1); box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-player-container {
    border-radius: 8px;
    margin: 0 10px;
  }
  
  .controls-bottom {
    gap: 10px;
  }
  
  .control-btn {
    padding: 6px 10px;
    font-size: 14px;
  }
  
  .time-display {
    font-size: 12px;
  }
  
  .error-content {
    padding: 20px;
  }
  
  .error-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style>