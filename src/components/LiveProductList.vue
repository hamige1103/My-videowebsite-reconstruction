<template>
  <div class="live-product-list">
    <!-- 商品列表头部 -->
    <div class="product-list-header">
      <h3>🛍️ 直播商品</h3>
      <div class="product-count">{{ products.length }} 件商品</div>
    </div>

    <!-- 商品列表 -->
    <div class="products-grid" v-if="products.length > 0">
      <div 
        v-for="product in products" 
        :key="product.id"
        class="product-card"
        :class="{ 'out-of-stock': product.stock <= 0 }">
        
        <div class="product-image">
          <img :src="product.image_url || '/placeholder-product.jpg'" :alt="product.name">
          <div v-if="product.stock <= 0" class="sold-out-badge">已售罄</div>
          <div v-else-if="product.sold_count > 0" class="hot-badge">热卖</div>
        </div>
        
        <div class="product-content">
          <h4 class="product-name">{{ product.name }}</h4>
          <p class="product-description">{{ product.description }}</p>
          
          <div class="product-price">
            <span class="current-price">¥{{ product.price.toFixed(2) }}</span>
            <span v-if="product.original_price && product.original_price > product.price" 
                  class="original-price">¥{{ product.original_price.toFixed(2) }}</span>
          </div>
          
          <div class="product-stats">
            <span class="stock">库存: {{ product.stock }}</span>
            <span class="sold">已售: {{ product.sold_count }}</span>
          </div>
          
          <div class="product-actions">
            <button 
              v-if="product.stock > 0"
              @click="addToCart(product)"
              class="add-to-cart-btn"
              :disabled="isInCart(product.id)">
              {{ isInCart(product.id) ? '✅ 已添加' : '🛒 加入购物车' }}
            </button>
            <button v-else class="sold-out-btn" disabled>已售罄</button>
            
            <a v-if="product.product_url" :href="product.product_url" target="_blank" class="product-link">
              查看详情
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">🛍️</div>
      <p>暂无商品</p>
      <p class="empty-hint">主播尚未添加商品</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { getLiveProducts } from '../apis/live.js'

export default {
  name: 'LiveProductList',
  props: {
    liveId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      products: [],
      loading: false,
      error: null,
      cartItems: []
    }
  },
  computed: {
    // 检查商品是否在购物车中
    isInCart() {
      return (productId) => {
        return this.cartItems.some(item => item.productId === productId)
      }
    }
  },
  methods: {
    // 加载商品列表
    async loadProducts() {
      this.loading = true
      this.error = null
      
      try {
        const response = await getLiveProducts(this.liveId)
        this.products = response.data.products || []
      } catch (error) {
        this.error = '加载商品失败：' + (error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },

    // 添加商品到购物车
    addToCart(product) {
      // 触发购物车组件的添加方法
      this.$emit('add-to-cart', product)
      
      // 更新本地状态
      const existingItem = this.cartItems.find(item => item.productId === product.id)
      if (!existingItem) {
        this.cartItems.push({
          productId: product.id,
          name: product.name,
          price: product.price,
          image_url: product.image_url,
          stock: product.stock,
          quantity: 1
        })
      }
      
      this.$message.success('已添加到购物车')
    },

    // 从本地存储加载购物车
    loadCart() {
      const savedCart = localStorage.getItem(`live_cart_${this.liveId}`)
      if (savedCart) {
        this.cartItems = JSON.parse(savedCart)
      }
    }
  },
  mounted() {
    this.loadProducts()
    this.loadCart()
    
    // 监听购物车变化
    this.$root.$on('cart-updated', () => {
      this.loadCart()
    })
  },
  
  // 清理事件监听
  beforeUnmount() {
    this.$root.$off('cart-updated')
  }
}
</script>

<style scoped>
.live-product-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.product-count {
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
  padding: 4px 12px;
  border-radius: 12px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.product-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: white;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.product-card.out-of-stock {
  opacity: 0.6;
}

.product-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sold-out-badge,
.hot-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.sold-out-badge {
  background: #666;
}

.hot-badge {
  background: #ff4757;
}

.product-content {
  padding: 16px;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: bold;
  color: #333;
  line-height: 1.4;
}

.product-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.current-price {
  font-size: 18px;
  font-weight: bold;
  color: #ff4757;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

.product-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 12px;
  color: #666;
}

.product-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.add-to-cart-btn {
  padding: 8px 12px;
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.add-to-cart-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.add-to-cart-btn:disabled {
  background: #28a745;
  cursor: default;
}

.sold-out-btn {
  padding: 8px 12px;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: not-allowed;
}

.product-link {
  padding: 8px 12px;
  background: #f8f9fa;
  color: #666;
  text-decoration: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  transition: all 0.2s ease;
}

.product-link:hover {
  background: #e9ecef;
  color: #333;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-hint {
  font-size: 12px;
  margin-top: 8px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff4757;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .product-list-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .product-actions {
    flex-direction: row;
  }
  
  .add-to-cart-btn,
  .sold-out-btn,
  .product-link {
    flex: 1;
  }
}
</style>