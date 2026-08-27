<template>
  <el-menu
    :default-active="activeIndex"
    background-color="white"
    text-color="black"
    active-text-color="#24b8f2"
    :router="true"
    class="el-menu-demo"
    mode="horizontal"
    :ellipsis="true"
    @select="handleSelect"
  >
    <el-menu-item index="/" style="font-size:larger; color:#409EFF; ">Avalon</el-menu-item>
    <el-menu-item index="/movtype/30">动漫</el-menu-item>
    <el-menu-item index="/movtype/22">电影</el-menu-item>
    <el-menu-item index="/movtype/13">电视剧</el-menu-item>
    <el-menu-item index="/movtype/26">综艺</el-menu-item>
    <el-menu-item index="/live">🎥 直播</el-menu-item>
    <!-- <el-menu-item index="/movtype/5">社区</el-menu-item> -->
    <div class="menu-input">
      <el-input
        v-model="input"
        placeholder="Search"
        style = "width: 65%; margin-left: 3%"
        @keyup.enter="searchChange"
        :suffix-icon="Search"
      />
      <el-button 
        type="primary" 
        @click="goToSmartSearch"
        style="margin-left: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none;"
      >
        🔍 智能搜索
      </el-button>
    </div>
    <div style="position: absolute; right: 0px;">
        <el-dropdown class="login-out" style="margin: 15px 11px" v-if="isLogining"  trigger="click">
          <span class="el-dropdown-link">
            {{ user.name }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>
                  <router-link :to="'/personSapce/'+ user.id" style="text-decoration: none; color: #606266">个人空间</router-link>
              </el-dropdown-item>
              
              <!-- 管理员入口 -->
              <el-dropdown-item v-if="user.role === 'admin'">
                  <router-link to="/admin" style="text-decoration: none; color: #606266">管理后台</router-link>
              </el-dropdown-item>
            
              <el-dropdown-item @click="loginOut">
                  登出
		          </el-dropdown-item>
              
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-button link type="primary" class="login" style="margin: 15px 11px; color: black" v-else @click="login">
            登录/注册
        </el-button>
    </div>
  </el-menu>
</template>

<script>
// 导航栏
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { localRemove } from '../utils'
import { getUserInfo } from '../apis/login'
import { ElMessage } from 'element-plus'


export default {
    name: "SakuraMenu",
    setup() {
        const store = useStore()
        const router = useRouter()
        // console.log(router.currentRoute.value)
        const activeIndex = ref('/')
        // console.log(activeIndex.value)
        // console.log(router.currentRoute.value)
        const input = ref('')
        const isLogining = ref(store.state.appStore.isLogining)
        
        const loginOut = function() {
          localRemove('token')
          window.location.reload()
        }

        const login = function() {
          router.push({ name: 'login' })
        }

        return {
            router,
            activeIndex,
            input,
            store,
            isLogining,
            loginOut,
            login,
            Search
            }
    },

    data() {
      return {
        user: {}
      }
    },

    methods: {
        handleSelect(key, keyPath)  {
            // console.log(key)
            this.activeIndex = key
            this.input = ''
          },
        
        // 输入框输入数据时 路由改变
        searchChange(value) {
          if(this.input) {
            this.activeIndex = '/'
            this.router.push({ name: 'search', query: { keyword: this.input }})
          }
        },

        // 跳转到智能搜索页面
        goToSmartSearch() {
          this.activeIndex = '/smart-search'
          this.router.push({ name: 'smart-search' })
        },

        getUserInfo() {
          if (this.isLogining) {
            // 已登录用户获取用户名
            getUserInfo().then(
              (res) => {
                console.log('用户信息响应:', res)
                if (res.data && res.data.code == 200 && res.data.data) {
                  // 使用mutation更新store
                  this.store.commit('SET_USER_INFO', res.data.data)
                  this.user = res.data.data
                  console.log('用户信息:', this.user)
                } else {
                  ElMessage({
                    message: res.data?.message || '获取用户信息失败',
                    type: 'warning',
                  })
                }
              }
            ).catch(error => {
              console.error('获取用户信息错误:', error)
              // 只在登录状态下显示错误信息
              if (this.isLogining) {
                ElMessage({
                  message: '获取用户信息失败，请检查网络连接',
                  type: 'error',
                })
              }
            })
          } 
        },

        ToUserCenter() {
          console.log("前往用户中心")
          this.router.push({name: 'personSapce'})
        }

    },


    mounted() {
      this.router.isReady().then(
        () => {
          var currentPath = this.$route.fullPath
          if (currentPath.indexOf('search?keyword=') > -1) {
            this.input = this.$route.query.keyword ? this.$route.query.keyword : ''
          } else if (currentPath.indexOf('/movtype/') > -1) {
            this.activeIndex = currentPath
          }
        }
        ).catch(
          () => {
            this.input = ''
            this.activeIndex = '/'
          }
        )
    },

    created() {
      this.getUserInfo()
    },

    watch: {
      moniterLogining() {
        return this.store.state.appStore.isLogining
      }
    },

    computed: {
      moniterLogining() {
        this.isLogining = this.store.state.appStore.isLogining
      }
    }
}


</script>

<style>
.flex-grow {
  flex-grow: 1;
}


/* 取消过渡效果 */
.el-menu-item {
  border-bottom: 0 !important;
}

.el-menu-item.is-active {
  background-color: white !important;
  border-bottom: 0 !important;
}

.el-menu-item:focus {
  background-color: white !important;
}

.el-menu-item:hover {
  background-color: white !important;
  color: #24b8f2 !important;
}

/* .el-button.login:hover {
  color: #24b8f2
}

p.login-out:hover {
  color: #24b8f2
} */

.el-menu {
  border: none !important;
  height: 100%;
  position: relative;
}

.el-input {
  margin: 10px 0px;
}

div.menu-input {
  position: absolute;
  right: 10%;
  width: 25%;
}
</style>
