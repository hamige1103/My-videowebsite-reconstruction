import { createStore } from 'vuex';
import { createPinia } from 'pinia';
import appStore from "./appStore"

// 创建Vuex store
export default createStore({
  modules: {
      appStore
  }
})

// 创建Pinia store
export const pinia = createPinia()