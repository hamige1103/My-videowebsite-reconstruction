<template>  
  <div class="collect-card">
    <el-row style="margin: 15px 0 0 0">
        <span class="collect-card-type">我的收藏</span>
    </el-row>
    
   <el-row alignment="flex-start" 
            v-infinite-scroll="loadMore"
            :infinite-scroll-disabled="disabled"
            infinite-scroll-distance="30"
            :infinite-scroll-immediate="true"
            class="mov-card-row"
            v-show="contenshow">
      <el-col 
        v-for="o in movieList"
        :key="o.vod_id"
        :xs="8" :sm="4" :md="4" 
        style="padding: 9px;">   
        <router-link :to="'/movdetail/'+ o.vod_id" style="text-decoration: none;" target="_blank">
        <el-card
        class="box-card" 
        shadow="hover"
        :body-style="{ padding: '8px 5px' }">
        <div class="card-div">
          <img :src="o.vod_pic" class="card-image"/>
          <span class="card-remark">{{ o.vod_remarks }}</span>
        </div>
        <div style="padding: 0px;">
          
          <span style="line-height: 26px; font-size: 15px; color:#777; display: flex; margin-top: 4px; text-overflow: ellipsis; overflow: hidden; width: 80%; white-space: nowrap;">
            <el-tooltip class="box-item" effect="dark" :content="o.vod_name" placement="bottom-end" :show-after="1000">
            {{ o.vod_name }}
            </el-tooltip>
          </span>
          <!-- <div class="bottom">
            <p style="font-size:smaller; color:#777; margin: 4px 0">{{ o.vod_remarks }}</p>
          </div> -->
        </div>
      </el-card>
      </router-link>
      </el-col>
  </el-row>
  <el-backtop :right="50" :bottom="80" />
  <p v-show="infiniteMsgShow" class="tips" style="font-size:smaller; color:#777;">Loading...</p>
  <p v-show="!infiniteMsgShow" class="tips" style="font-size:smaller; color:#777;">到底啦</p>
  </div>
</template>

<script>
import { ref } from 'vue'
import { getCollectionListByPage } from '../apis/videoCollection'
import { useStore } from 'vuex'

export default {
  // 视频收藏组件
    name: "CollectVideos",
    props: {
        user_id: String
    },
    components: {
      
    },

    setup() {
      const store = useStore()  // 该方法用于返回store 实例
      return {
            store
        }
    },

    data() {
      return {
        disabled: false,
        page: 1,
        contenshow: true,
        infiniteMsgShow: true,
        movieList: [
            ],
      }
    },

    methods: {
        // 当属性滚动的时候  加载  滚动加载
        loadMore () {
          this.disabled = true // 将无限滚动给禁用
          setTimeout(
            () => {
              this.page++ // 增加页数
              this.getCollectMovList() // 请求数据
            }, 500)  // 间隔500毫秒后发送请求
           },

        getCollectMovList() {
          const param =  { 
              page: this.page
              }

          console.log('获取收藏列表参数:', param)
          getCollectionListByPage(param).then(
            (res) => { 
              console.log('收藏列表响应:', res)
              if (res && res.data && res.data.code == 200 && res.data.data) {
                this.contenshow = true
                if (res.data.data.length > 0) {
                  this.infiniteMsgShow = true
                  for (var i in res.data.data) {
                    // 适配后端数据结构
                    const video = res.data.data[i]
                    this.movieList.push({
                      vod_id: video.video_id || video.id,
                      vod_pic: video.video_pic || '',
                      vod_name: video.video_name || '',
                      vod_remarks: video.video_remarks || video.video_type || ''
                    })
                 }
                  this.disabled = false // 还有多余数据时 无限滚动打开
                } else {
                  // 数据为空时，显示"到底啦"提示，但不隐藏内容区域
                  this.infiniteMsgShow = false
                  this.disabled = true
                }
              } else {
                // API错误时，显示错误信息但不隐藏内容区域
                this.infiniteMsgShow = false
                this.disabled = true
                console.error('获取收藏列表失败:', res && res.data ? res.data.message : '未知错误')
              }
             }
          ).catch(
            (error) => {
                console.error('获取收藏列表错误:', error)
                this.infiniteMsgShow = false
                this.disabled = true
            }
          )
      }
   },

   created() {
    this.getCollectMovList()
   }
}
</script>


<style>
span.collect-card-type {
    float: left;
    margin: 10px;
    font-size: 20px; 
    font-weight: bold;
    line-height: 20px;
}
</style>
