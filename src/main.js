import { createApp } from 'vue'
import App from './App.vue'
import './index.css'
import router from './router/index.js'
import store, { pinia } from './store/index.js'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.use(store)
app.use(pinia)
app.mount('#app')
