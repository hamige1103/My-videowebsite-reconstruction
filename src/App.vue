<template>
  <div class="common-layout">
    <el-container >
      <el-header style="width: 100%; position: sticky; border-bottom: 1px solid #dcdfe6; top: 0; left: 0; z-index:1000; padding: 0">
      <div class="sakura-header">
        <SakuraMenu/>
      </div>
      </el-header>
      <el-main style="overflow: hidden; top: 0; left: 0; padding: 0;">
        <div class="sakura-main">
          <router-view v-slot="{ Component }" :key="key">
          <keep-alive :exclude="['MovDetailPageVue', 'MovieKeywordPageVue', 'LoginVue']">
            <component :is="Component"/>
          </keep-alive>
          </router-view>
        </div>
        
      </el-main>
      <el-footer style="padding: 0">
        <FooterVue/>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import SakuraMenu from './components/SakuraMenu.vue'
import MovieCardList from './components/MovieCardList.vue'
import FooterVue from './components/Footer.vue'
import MovDetailPageVue from './views/MovDetailPage.vue'
import MovieKeywordPageVue from './views/MovieKeywordPage.vue'
import LoginVue from './views/Login.vue'
import { useStore } from 'vuex'

export default {
  name: 'App',
  components: {
    SakuraMenu,
    MovieCardList,
    FooterVue,
    MovDetailPageVue,
    MovieKeywordPageVue,
    LoginVue
  },

  setup() {
    const store = useStore()
    
    // 应用启动时初始化用户状态
    const initUserState = () => {
      const token = localStorage.getItem('token')
      const userInfoStr = localStorage.getItem('userInfo')
      
      if (token && userInfoStr) {
        try {
          const userInfo = JSON.parse(userInfoStr)
          store.commit('SET_USER_INFO', userInfo)
          store.commit('SET_LOGIN_STATUS', true)
        } catch (error) {
          console.error('解析用户信息失败:', error)
        }
      }
    }
    
    initUserState()
    
    return {
      store
    }
  },

  computed: {
    key() {
      // 只要保证 key 唯一性就可以了，保证不同页面的 key 不相同
      // console.log(this.$route.fullPath);
      return this.$route.fullPath
    }
  },
}
</script>
