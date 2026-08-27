<template>
    <div class="vod-detail" style="margin: 20px 0; width: 90%; overflow: hidden;">
        <el-row class="vod-detail">
            <el-col :xs="24" :sm="6" class="vod-detail">
                <div class="vod-detail">
                    <img :src="mov_detail.vod_pic" alt=""/>
                </div>
                
            </el-col>
            <el-col  :sm="18" style="padding: 0 10px">
                <el-row style="margin: 0 0 15px 0">
                    <p style="margin: 0; font-size: 18px;">{{ mov_detail.vod_name }}</p>
                </el-row>

                <el-row v-if="mov_detail.vod_sub">
                    <span class="des-name">
                        又名:&nbsp; &nbsp; 
                        <p class="des-content">{{ mov_detail.vod_sub }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">地区:&nbsp;&nbsp;</span>
                    <p class="des-content"> {{ mov_detail.vod_area }}</p>
                </el-row>

                <el-row>
                    <span class="des-name">
                        语言:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_lang }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        类型:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.type_name }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        上映:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_year }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        集数:&nbsp; &nbsp;
                        <p class="des-content">{{ mov_detail.vod_remark }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        导演:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_director }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        更新时间:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_time }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        收藏:&nbsp;&nbsp;
                        <p class="des-content"> 
                            <el-icon :size="26" style="vertical-align: middle;" v-if="!isCollect" color="#999" @click="addCollect"><StarFilled /></el-icon>
                            <el-icon :size="26" style="vertical-align: middle" v-else color="yellow" @click="removeCollect"><StarFilled /></el-icon>  
                        </p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        主演:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_actor }}</p>
                    </span>
                    
                </el-row>

                <el-row class="detail3">
                    <span class="des-name">
                        详情:&nbsp;&nbsp; 
                        <p class="des-content" style="font-size:15px" v-if="checkHtml(mov_detail.vod_content)" v-html="mov_detail.vod_content"/>
                        <p class="des-content" style="font-size:15px" v-else>{{ mov_detail.vod_content }}</p>
                    </span>  
                    
                </el-row>

            </el-col>  
        </el-row>

        <el-row class="vod-play-url">
            <el-col class="vod-play-url"
                v-for="(episode, index) in parsePlayUrls(mov_detail.vod_play_url)" 
                :key="index"
                :xs="8" :sm="3"
                style="margin: 5px 0;"
                >
                <el-button 
                class="vod-play-url" 
                style="float: left;" 
                @click="videoPlay($event, episode.url)" 
                :class="[{active: activeName == episode.url}]">{{ episode.name }}
                </el-button>
            </el-col>
        </el-row>
        
        <el-row class="video-play" v-if="video_play" style="margin: 40px 0; min-height: 450px; background: #000; border-radius: 8px; padding: 20px; border: 2px solid #ddd;">
            <VideoPlay 
                :src="video_play_url" 
                @playbackFailed="handlePlaybackFailed"
                @playbackEnded="handlePlaybackEnded"/>
        </el-row>
        

        
        <!-- 错误提示 -->
        <el-row v-if="showError" style="margin: 40px 0">
            <div class="error-message">
                <div class="error-content">
                    <h3>视频播放失败</h3>
                    <p>{{ errorMessage }}</p>
                    <el-button @click="closeError" class="error-close-btn">关闭</el-button>
                </div>
            </div>
        </el-row>
    </div>
</template>

<script>
// 视频详情
import apiGetMovDetail from '../apis/getMovDetail'
import { getVideoPlay } from '../apis/getVideoPlay'
import VideoPlay from './VideoPlay.vue'
import { ElMessage } from 'element-plus'
import { StarFilled } from '@element-plus/icons-vue'
import { ref } from 'vue'
import { useStore } from 'vuex'
import { checkCollection, addCollection, removeCollection } from '../apis/videoCollection'

export default {
  name: 'MovDetail',

  setup() {
    const store = useStore()
    return {
        store
    }
  },

  components: {
    VideoPlay
  },

  props: {
        vod_id: String
    },
  data() {
    return {
        mov_detail: {},
        video_play: false,
        video_play_url: '',  // 此时正在播放的 视频url
        activeName: '',
        isCollect: false,  // 此视频是否被收藏
        showError: false,
        errorMessage: ''
    }
  },

  methods: {
    getMovDetail() {
        var param = {
            vod_id: this.vod_id
        }
        console.log('MovDetail API请求参数:', param)
        apiGetMovDetail(param).then(
            (res) => {
                console.log('MovDetail API响应:', res)
                console.log('MovDetail API响应数据:', res.data)
                if (res.data && res.data.code === 200 && res.data.data) {
                    console.log('MovDetail 获取到数据:', res.data.data)
                    this.mov_detail = res.data.data
                    // 获取视频播放地址
                    this.getVideoPlayUrl()
                } else {
                    console.log('MovDetail 没有数据或API错误:', res.data)
                }
            }
        ).catch(
            (error) => {
                console.error('MovDetail API调用错误:', error)
            }
        )
    },
    
    async getVideoPlayUrl() {
        try {
            console.log('开始获取视频播放地址，视频ID:', this.vod_id)
            
            // 调用后端API获取视频播放地址
            const response = await getVideoPlay(this.vod_id)
            console.log('视频播放API响应:', response)
            
            if (response.data && response.data.code === 200 && response.data.data) {
                const playData = response.data.data
                console.log('获取到播放数据:', playData)
                
                // 检查是否有播放地址
                if (playData.play_urls && playData.play_urls.length > 0) {
                    // 使用第一个播放地址
                    const firstPlayUrl = playData.play_urls[0].url
                    console.log('使用播放地址:', firstPlayUrl)
                    this.video_play_url = firstPlayUrl
                } else {
                    // 如果没有播放地址，使用备用MP4源
                    console.log('没有找到播放地址，使用备用MP4源')
                    this.video_play_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
                }
            } else {
                // API调用失败，使用备用MP4源
                console.log('API调用失败，使用备用MP4源:', response.data ? response.data.message : '未知错误')
                this.video_play_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
            }
            
            console.log('最终播放地址:', this.video_play_url)
            // 显示播放器
            this.video_play = true
        } catch (error) {
            console.error('获取视频播放地址失败:', error)
            // 出错时使用备用MP4源
            this.video_play_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
            this.video_play = true
        }
    },

    async addCollect() {
        // 将此视频添加收藏
        console.log("add collect")
        if (this.store.state.appStore.isLogining) {
            try {
                var params = {
                    video_id: this.vod_id
                }
                const res = await addCollection(params)
                console.log('添加收藏响应:', res)
                if (res && res.data && res.data.code == 200) {
                    this.isCollect = true
                    ElMessage({
                        message: '收藏成功',
                        type: 'success',
                    })
                } else if (res && res.data && res.data.code == 400 && res.data.message === '已收藏该视频') {
                    // 如果已经收藏了，也设置收藏状态为true
                    this.isCollect = true
                    ElMessage({
                        message: '您已收藏该视频',
                        type: 'info',
                    })
                } else {
                    ElMessage({
                        message: res && res.data ? res.data.message : '收藏失败',
                        type: 'warning',
                    })
                }
            } catch (error) {
                console.error('添加收藏失败:', error)
                ElMessage({
                    message: '收藏失败，请重试',
                    type: 'error',
                })
            }
        } else {
            ElMessage({
                message: '请先登录',
                type: 'warning',
            })
        }
    },

    async removeCollect() {
        console.log("remove collect")
        if (this.store.state.appStore.isLogining) {
            try {
                var params = {
                    video_id: this.vod_id
                }
                const res = await removeCollection(params)
                console.log('取消收藏响应:', res)
                if (res && res.data && res.data.code == 200) {
                    this.isCollect = false
                    ElMessage({
                        message: '取消收藏成功',
                        type: 'success',
                    })
                } else {
                    ElMessage({
                        message: res && res.data ? res.data.message : '取消收藏失败',
                        type: 'warning',
                    })
                }
            } catch (error) {
                console.error('取消收藏失败:', error)
                ElMessage({
                    message: '取消收藏失败，请重试',
                    type: 'error',
                })
            }
        } else {
            ElMessage({
                message: '请先登录',
                type: 'warning',
            })
        }
    },

    async showIsCollect() {
        // 显示此视频是否被收藏
        if (this.store.state.appStore.isLogining) {
            try {
                var params = {
                    video_id: this.vod_id
                }
                const res = await checkCollection(params)
                console.log('检查收藏状态响应:', res)
                if (res && res.data && res.data.code == 200) {
                    this.isCollect = res.data.data
                    console.log("收藏状态:", this.isCollect)
                } else {
                    ElMessage({
                        message: res && res.data ? res.data.message : '检查收藏状态失败',
                        type: 'warning',
                    })
                }
            } catch (error) {
                console.error('检查收藏状态失败:', error)
                this.isCollect = false
            }
        } else {
            // 用户未登录时，设置默认值
            this.isCollect = false
        }
    },

    async videoPlay(event, url) {
        try {
            console.log('开始播放视频，视频ID:', this.vod_id, '点击的URL:', url)
            
            // 如果点击的URL是有效的，直接使用它
            if (url && url.startsWith('http')) {
                console.log('使用点击的播放地址:', url)
                this.video_play_url = url
            } else {
                // 否则调用后端API获取视频播放地址
                console.log('调用后端API获取播放地址')
                const response = await getVideoPlay(this.vod_id)
                console.log('视频播放API响应:', response)
                
                if (response.data && response.data.code === 200 && response.data.data) {
                    const playData = response.data.data
                    console.log('获取到播放数据:', playData)
                    
                    // 检查是否有播放地址
                    if (playData.play_urls && playData.play_urls.length > 0) {
                        // 使用第一个播放地址
                        const firstPlayUrl = playData.play_urls[0].url
                        console.log('使用播放地址:', firstPlayUrl)
                        this.video_play_url = firstPlayUrl
                    } else {
                        // 如果没有播放地址，使用备用MP4源
                        console.log('没有找到播放地址，使用备用MP4源')
                        this.video_play_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
                    }
                } else {
                    // API调用失败，使用备用MP4源
                    console.log('API调用失败，使用备用MP4源:', response.data ? response.data.message : '未知错误')
                    this.video_play_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
                }
            }
            
            this.video_play = true
            this.activeName = this.video_play_url
            this.showError = false
            this.errorMessage = ''
            
            console.log('开始播放视频:', this.video_play_url)
        } catch (error) {
            console.error('播放视频失败:', error)
            // 出错时使用备用MP4源
            this.video_play_url = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
            this.video_play = true
            this.activeName = this.video_play_url
        }
    },
    
    // 处理播放失败
    handlePlaybackFailed(error) {
        console.log('视频播放失败:', error)
        this.showError = true
        this.errorMessage = '视频播放失败，请重新播放'
        
        // 保持播放器可见，让用户看到错误信息
        this.video_play = true
    },
    
    // 处理播放结束
    handlePlaybackEnded() {
      console.log('视频播放结束')
      this.$message.success('视频播放完成')
    },

    closeError() {
        this.showError = false
        this.errorMessage = ''
    },

    checkHtml(s) {
        // 判断它是否是html
        if (typeof(s) == 'string') {
            if (s.indexOf('<p>')>-1) {
                return true
            } else if (s.indexOf('<span>')>-1) {
                return true
            } else {
                return false
            }
        } else {
            return false
        }
    },
    
    parsePlayUrls(playUrlString) {
        // 解析播放地址字符串格式：剧集名称$播放地址#剧集名称$播放地址
        if (!playUrlString || typeof playUrlString !== 'string') {
            return []
        }
        
        const episodes = []
        const episodeList = playUrlString.split('#')
        
        for (const episode of episodeList) {
            if (episode.includes('$')) {
                const [name, url] = episode.split('$', 2)
                if (name && url) {
                    episodes.push({
                        name: name.trim(),
                        url: url.trim()
                    })
                }
            }
        }
        
        return episodes
    }
  },

   watch: {
      // user出现变化后 请求数据 查看是视频是否被收藏
      'store.state.appStore.user.id': {
        handler(newVal, oldVal) {
          if (newVal !== oldVal) {
            this.showIsCollect()
          }
        },
        immediate: true
      }
    },

  created() {
    this.getMovDetail()
  }
}

</script>

<style>

div.vod-detail .el-row {
    margin: 0 0 10px;
}

span.des-name {
    line-height: 20px;
    margin: 0;
    color: #999;
    font-weight: 400;
    display: inline;
    text-align: left;
}

p.des-content {
    margin: 0;
    line-height: 20px;
    text-align: left;
    display: inline;
    color:black;
}


.el-col.vod-detail div.vod-detail {
    position: relative;
    width: 100%;
    height: auto;
    overflow: visible;
}

.el-col.vod-detail div img {
    width: 95%;
    max-width: 300px;
    height: auto;
    display: block;
    margin: 0 auto;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    object-fit: cover;
}

.el-button.vod-play-url.active {
  background-color: rgb(36, 184, 242);
  color: white;
  border-radius: 4px;
}
/* p {
    margin: 0;
    padding: 0;
} */
</style>