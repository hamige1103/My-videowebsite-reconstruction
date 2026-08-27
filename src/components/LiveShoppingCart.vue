<template>
  <div class="live-shopping-cart">
    <!-- 购物车头部 -->
    <div class="cart-header">
      <h3>🛒 购物车</h3>
      <div class="cart-stats">
        <span>{{ cartItems.length }} 件商品</span>
        <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
      </div>
    </div>

    <!-- 购物车商品列表 -->
    <div class="cart-items" v-if="cartItems.length > 0">
      <div 
        v-for="item in cartItems" 
        :key="item.productId"
        class="cart-item">
        
        <div class="item-image">
          <img :src="item.image_url || '/placeholder-product.jpg'" :alt="item.name">
        </div>
        
        <div class="item-info">
          <h4>{{ item.name }}</h4>
          <p class="item-price">¥{{ item.price.toFixed(2) }}</p>
        </div>
        
        <div class="quantity-controls">
          <button 
            @click="updateQuantity(item.productId, item.quantity - 1)"
            :disabled="item.quantity <= 1"
            class="quantity-btn">
            -
          </button>
          <span class="quantity">{{ item.quantity }}</span>
          <button 
            @click="updateQuantity(item.productId, item.quantity + 1)"
            :disabled="item.quantity >= item.stock"
            class="quantity-btn">
            +
          </button>
        </div>
        
        <div class="item-total">
          ¥{{ (item.price * item.quantity).toFixed(2) }}
        </div>
        
        <button @click="removeFromCart(item.productId)" class="remove-btn">
          🗑️
        </button>
      </div>
    </div>

    <!-- 空购物车 -->
    <div v-else class="empty-cart">
      <div class="empty-icon">🛒</div>
      <p>购物车是空的</p>
      <p class="empty-hint">点击商品下方的"加入购物车"按钮添加商品</p>
    </div>

    <!-- 结算区域 -->
    <div v-if="cartItems.length > 0" class="checkout-section">
      <div class="checkout-summary">
        <div class="summary-row">
          <span>商品总价：</span>
          <span>¥{{ totalPrice.toFixed(2) }}</span>
        </div>
        <div class="summary-row">
          <span>运费：</span>
          <span>¥0.00</span>
        </div>
        <div class="summary-row total">
          <span>应付总额：</span>
          <span>¥{{ totalPrice.toFixed(2) }}</span>
        </div>
      </div>
      
      <button @click="showCheckout = true" class="checkout-btn">
        💳 立即结算
      </button>
    </div>

    <!-- 结算弹窗 -->
    <div v-if="showCheckout" class="checkout-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>订单结算</h3>
          <button @click="closeCheckout" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="createOrder">
            <!-- 收货信息 -->
            <div class="form-section">
              <h4>收货信息</h4>
              <div class="form-group">
                <label>收货人姓名 *</label>
                <input v-model="orderForm.buyer_name" type="text" required>
              </div>
              <div class="form-group">
                <label>联系电话 *</label>
                <input v-model="orderForm.buyer_contact" type="tel" required>
              </div>
              <div class="form-group">
                <label>收货地址 *</label>
                <textarea v-model="orderForm.shipping_address" rows="3" required></textarea>
              </div>
            </div>
            
            <!-- 订单商品 -->
            <div class="form-section">
              <h4>订单商品</h4>
              <div class="order-items">
                <div 
                  v-for="item in cartItems" 
                  :key="item.productId"
                  class="order-item">
                  <span>{{ item.name }}</span>
                  <span>×{{ item.quantity }}</span>
                  <span>¥{{ (item.price * item.quantity).toFixed(2) }}</span>
                </div>
              </div>
              <div class="order-total">
                总计：¥{{ totalPrice.toFixed(2) }}
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeCheckout" class="btn btn-secondary">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? '创建中...' : '确认下单' }}
              </button>
            </div>
          </form>
        </div>
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
  name: 'LiveShoppingCart',
  props: {
    liveId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      cartItems: [],
      loading: false,
      error: null,
      showCheckout: false,
      orderForm: {
        buyer_name: '',
        buyer_contact: '',
        shipping_address: ''
      }
    }
  },
  computed: {
    totalPrice() {
      return this.cartItems.reduce((total, item) => {
        return total + (item.price * item.quantity)
      }, 0)
    }
  },
  methods: {
    // 添加商品到购物车
    addToCart(product) {
      const existingItem = this.cartItems.find(item => item.productId === product.id)
      
      if (existingItem) {
        if (existingItem.quantity < product.stock) {
          existingItem.quantity++
        } else {
          this.$message.warning('库存不足')
        }
      } else {
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
      this.saveCart()
    },

    // 更新商品数量
    updateQuantity(productId, newQuantity) {
      const item = this.cartItems.find(item => item.productId === productId)
      if (item) {
        if (newQuantity <= 0) {
          this.removeFromCart(productId)
        } else if (newQuantity <= item.stock) {
          item.quantity = newQuantity
          this.saveCart()
        } else {
          this.$message.warning('库存不足')
        }
      }
    },

    // 从购物车移除商品
    removeFromCart(productId) {
      this.cartItems = this.cartItems.filter(item => item.productId !== productId)
      this.saveCart()
      this.$message.info('已从购物车移除')
    },

    // 清空购物车
    clearCart() {
      this.cartItems = []
      this.saveCart()
    },

    // 保存购物车到本地存储
    saveCart() {
      localStorage.setItem(`live_cart_${this.liveId}`, JSON.stringify(this.cartItems))
    },

    // 从本地存储加载购物车
    loadCart() {
      const savedCart = localStorage.getItem(`live_cart_${this.liveId}`)
      if (savedCart) {
        this.cartItems = JSON.parse(savedCart)
      }
    },

    // 创建订单
    async createOrder() {
      this.loading = true
      this.error = null
      
      try {
        // 为每个商品创建订单
        for (const item of this.cartItems) {
          const orderData = {
            product_id: item.productId,
            quantity: item.quantity,
            total_price: item.price * item.quantity,
            buyer_name: this.orderForm.buyer_name,
            buyer_contact: this.orderForm.buyer_contact,
            shipping_address: this.orderForm.shipping_address
          }
          
          await createLiveOrder(this.liveId, orderData)
        }
        
        this.$message.success('订单创建成功！')
        this.clearCart()
        this.closeCheckout()
        
        // 通知父组件订单创建成功
        this.$emit('order-created')
        
      } catch (error) {
        this.error = '创建订单失败：' + (error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },

    // 关闭结算弹窗
    closeCheckout() {
      this.showCheckout = false
      this.orderForm = {
        buyer_name: '',
        buyer_contact: '',
        shipping_address: ''
      }
    }
  },
  mounted() {
    this.loadCart()
  }
}
</script>

<style scoped>
.live-shopping-cart {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 500px;
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

.cart-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: #666;
}

.total-price {
  font-size: 18px;
  font-weight: bold;
  color: #ff4757;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.item-image {
  width: 50px;
  height: 50px;
  margin-right: 12px;
  border-radius: 4px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
}

.item-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #333;
}

.item-price {
  margin: 0;
  font-size: 14px;
  color: #ff4757;
  font-weight: bold;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 16px;
}

.quantity-btn {
  width: 24px;
  height: 24px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
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

.item-total {
  font-weight: bold;
  color: #ff4757;
  margin: 0 16px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.6;
}

.remove-btn:hover {
  opacity: 1;
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

.checkout-section {
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.checkout-summary {
  margin-bottom: 16px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.summary-row.total {
  font-weight: bold;
  font-size: 16px;
  color: #ff4757;
  border-top: 1px solid #e0e0e0;
  padding-top: 8px;
}

.checkout-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.checkout-btn:hover {
  transform: translateY(-2px);
}

.checkout-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.order-items {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 12px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.order-item:last-child {
  border-bottom: none;
}

.order-total {
  text-align: right;
  font-weight: bold;
  font-size: 16px;
  color: #ff4757;
  margin-top: 12px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
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
</style>