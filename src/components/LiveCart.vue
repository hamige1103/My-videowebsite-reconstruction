<template>
  <div class="live-cart">
    <!-- 购物车头部 -->
    <div class="cart-header">
      <h3>🛒 购物车</h3>
      <div class="cart-info">
        <span class="item-count">{{ totalItems }} 件商品</span>
        <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
      </div>
    </div>

    <!-- 购物车商品列表 -->
    <div class="cart-items" v-if="items.length > 0">
      <div 
        v-for="item in items" 
        :key="item.productId"
        class="cart-item">
        
        <div class="item-image">
          <img :src="item.image_url || '/placeholder-product.jpg'" :alt="item.name">
        </div>
        
        <div class="item-details">
          <h4 class="item-name">{{ item.name }}</h4>
          <div class="item-price">¥{{ item.price.toFixed(2) }}</div>
          
          <div class="quantity-controls">
            <button 
              @click="decreaseQuantity(item)"
              :disabled="item.quantity <= 1"
              class="quantity-btn">
              -
            </button>
            <span class="quantity">{{ item.quantity }}</span>
            <button 
              @click="increaseQuantity(item)"
              :disabled="item.quantity >= item.stock"
              class="quantity-btn">
              +
            </button>
          </div>
          
          <div class="item-subtotal">
            小计: ¥{{ (item.price * item.quantity).toFixed(2) }}
          </div>
        </div>
        
        <button @click="removeItem(item.productId)" class="remove-btn">
          ❌
        </button>
      </div>
    </div>

    <!-- 空购物车 -->
    <div v-else class="empty-cart">
      <div class="empty-icon">🛒</div>
      <p>购物车是空的</p>
      <p class="empty-hint">快去添加喜欢的商品吧！</p>
    </div>

    <!-- 购物车底部操作 -->
    <div v-if="items.length > 0" class="cart-footer">
      <div class="cart-summary">
        <div class="summary-row">
          <span>商品数量:</span>
          <span>{{ totalItems }} 件</span>
        </div>
        <div class="summary-row">
          <span>商品总价:</span>
          <span>¥{{ totalPrice.toFixed(2) }}</span>
        </div>
        <div class="summary-row total">
          <span>应付总额:</span>
          <span>¥{{ totalPrice.toFixed(2) }}</span>
        </div>
      </div>
      
      <div class="cart-actions">
        <button @click="clearCart" class="clear-btn">
          清空购物车
        </button>
        <button @click="createOrder" class="checkout-btn">
          立即下单
        </button>
      </div>
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
import { createLiveOrder } from '../apis/live.js'

export default {
  name: 'LiveCart',
  props: {
    liveId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      items: [],
      loading: false,
      error: null
    }
  },
  computed: {
    // 计算总商品数量
    totalItems() {
      return this.items.reduce((total, item) => total + item.quantity, 0)
    },
    
    // 计算总价格
    totalPrice() {
      return this.items.reduce((total, item) => total + (item.price * item.quantity), 0)
    }
  },
  methods: {
    // 添加商品到购物车
    addItem(product) {
      const existingItem = this.items.find(item => item.productId === product.id)
      
      if (existingItem) {
        // 如果商品已在购物车中，增加数量
        if (existingItem.quantity < product.stock) {
          existingItem.quantity += 1
        } else {
          this.$message.warning('库存不足，无法添加更多')
        }
      } else {
        // 添加新商品
        this.items.push({
          productId: product.id,
          name: product.name,
          price: product.price,
          image_url: product.image_url,
          stock: product.stock,
          quantity: 1
        })
      }
      
      this.saveCart()
      this.$message.success('已添加到购物车')
    },

    // 增加商品数量
    increaseQuantity(item) {
      if (item.quantity < item.stock) {
        item.quantity += 1
        this.saveCart()
      } else {
        this.$message.warning('库存不足')
      }
    },

    // 减少商品数量
    decreaseQuantity(item) {
      if (item.quantity > 1) {
        item.quantity -= 1
        this.saveCart()
      }
    },

    // 移除商品
    removeItem(productId) {
      this.items = this.items.filter(item => item.productId !== productId)
      this.saveCart()
      this.$message.info('已从购物车移除')
    },

    // 清空购物车
    clearCart() {
      this.items = []
      this.saveCart()
      this.$message.info('购物车已清空')
    },

    // 保存购物车到本地存储
    saveCart() {
      localStorage.setItem(`live_cart_${this.liveId}`, JSON.stringify(this.items))
      // 通知其他组件购物车已更新
      this.$root.$emit('cart-updated')
    },

    // 从本地存储加载购物车
    loadCart() {
      const savedCart = localStorage.getItem(`live_cart_${this.liveId}`)
      if (savedCart) {
        this.items = JSON.parse(savedCart)
      }
    },

    // 创建订单
    async createOrder() {
      if (this.items.length === 0) {
        this.$message.warning('购物车为空')
        return
      }

      this.loading = true
      this.error = null

      try {
        const orderData = {
          live_id: this.liveId,
          items: this.items.map(item => ({
            product_id: item.productId,
            quantity: item.quantity
          }))
        }

        const response = await createLiveOrder(orderData)
        
        // 订单创建成功
        this.$message.success('订单创建成功！')
        this.clearCart()
        
        // 触发订单创建成功事件
        this.$emit('order-created', response.data)
        
      } catch (error) {
        this.error = '创建订单失败：' + (error.response?.data?.detail || error.message)
        this.$message.error('创建订单失败')
      } finally {
        this.loading = false
      }
    }
  },
  
  mounted() {
    this.loadCart()
    
    // 监听添加商品事件
    this.$root.$on('add-to-cart', (product) => {
      this.addItem(product)
    })
  },
  
  // 清理事件监听
  beforeUnmount() {
    this.$root.$off('add-to-cart')
  }
}
</script>

<style scoped>
.live-cart {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 600px;
  overflow-y: auto;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.cart-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.item-count {
  font-size: 14px;
  color: #666;
}

.total-price {
  font-size: 18px;
  font-weight: bold;
  color: #ff4757;
}

.cart-items {
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 12px;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-name {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-price {
  font-size: 16px;
  font-weight: bold;
  color: #ff4757;
  margin-bottom: 8px;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.quantity-btn {
  width: 24px;
  height: 24px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
}

.quantity-btn:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #999;
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity {
  min-width: 30px;
  text-align: center;
  font-weight: bold;
}

.item-subtotal {
  font-size: 12px;
  color: #666;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.remove-btn:hover {
  background: #ffebee;
}

.empty-cart {
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

.cart-footer {
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.cart-summary {
  margin-bottom: 20px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.summary-row.total {
  font-size: 16px;
  font-weight: bold;
  color: #ff4757;
  border-top: 1px solid #e0e0e0;
  padding-top: 8px;
  margin-top: 8px;
}

.cart-actions {
  display: flex;
  gap: 12px;
}

.clear-btn {
  flex: 1;
  padding: 12px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: #e0e0e0;
}

.checkout-btn {
  flex: 2;
  padding: 12px;
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.checkout-btn:hover {
  transform: translateY(-1px);
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
  .live-cart {
    max-height: none;
  }
  
  .cart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .cart-info {
    align-items: flex-start;
  }
  
  .cart-item {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }
  
  .item-image {
    align-self: flex-start;
  }
  
  .cart-actions {
    flex-direction: column;
  }
}
</style>