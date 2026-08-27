<template>
  <div class="live-product-manager">
    <!-- 商品管理头部 -->
    <div class="product-manager-header">
      <h3>商品管理</h3>
      <button @click="showAddProduct = true" class="btn btn-primary">
        ➕ 添加商品
      </button>
    </div>

    <!-- 商品列表 -->
    <div class="product-list" v-if="products.length > 0">
      <div 
        v-for="product in products" 
        :key="product.id"
        class="product-item"
        :class="{ 'out-of-stock': product.stock <= 0 }">
        
        <div class="product-image">
          <img :src="product.image_url || '/placeholder-product.jpg'" :alt="product.name">
        </div>
        
        <div class="product-info">
          <h4>{{ product.name }}</h4>
          <p class="product-description">{{ product.description }}</p>
          <div class="product-price">
            <span class="current-price">¥{{ product.price }}</span>
            <span v-if="product.original_price" class="original-price">¥{{ product.original_price }}</span>
          </div>
          <div class="product-stats">
            <span>库存: {{ product.stock }}</span>
            <span>已售: {{ product.sold_count }}</span>
          </div>
        </div>
        
        <div class="product-actions">
          <button @click="editProduct(product)" class="btn btn-secondary btn-sm">
            编辑
          </button>
          <button @click="promoteProduct(product.id)" class="btn btn-primary btn-sm">
            推广
          </button>
          <button @click="removeProduct(product.id)" class="btn btn-danger btn-sm">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">🛒</div>
      <p>暂无商品，点击"添加商品"开始带货</p>
    </div>

    <!-- 添加/编辑商品弹窗 -->
    <div v-if="showAddProduct || editingProduct" class="product-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingProduct ? '编辑商品' : '添加商品' }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="saveProduct">
            <div class="form-group">
              <label>商品名称 *</label>
              <input v-model="productForm.name" type="text" required>
            </div>
            
            <div class="form-group">
              <label>商品描述</label>
              <textarea v-model="productForm.description" rows="3"></textarea>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>价格 (元) *</label>
                <input v-model="productForm.price" type="number" step="0.01" min="0" required>
              </div>
              
              <div class="form-group">
                <label>原价 (元)</label>
                <input v-model="productForm.original_price" type="number" step="0.01" min="0">
              </div>
            </div>
            
            <div class="form-group">
              <label>库存数量 *</label>
              <input v-model="productForm.stock" type="number" min="0" required>
            </div>
            
            <div class="form-group">
              <label>商品图片URL</label>
              <input v-model="productForm.image_url" type="url" placeholder="https://example.com/image.jpg">
            </div>
            
            <div class="form-group">
              <label>商品链接</label>
              <input v-model="productForm.product_url" type="url" placeholder="https://example.com/product">
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
              <button type="submit" class="btn btn-primary">保存</button>
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
import { addLiveProduct, getLiveProducts, updateLiveProduct, removeLiveProduct, promoteLiveProduct } from '../apis/live.js'

export default {
  name: 'LiveProductManager',
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
      showAddProduct: false,
      editingProduct: null,
      productForm: {
        name: '',
        description: '',
        price: 0,
        original_price: 0,
        stock: 0,
        image_url: '',
        product_url: ''
      }
    }
  },
  mounted() {
    this.loadProducts()
  },
  methods: {
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

    async saveProduct() {
      this.loading = true
      this.error = null
      
      try {
        if (this.editingProduct) {
          await updateLiveProduct(this.liveId, this.editingProduct.id, this.productForm)
          this.$message.success('商品更新成功')
        } else {
          await addLiveProduct(this.liveId, this.productForm)
          this.$message.success('商品添加成功')
        }
        
        this.closeModal()
        this.loadProducts()
      } catch (error) {
        this.error = '保存商品失败：' + (error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },

    editProduct(product) {
      this.editingProduct = product
      this.productForm = { ...product }
    },

    async removeProduct(productId) {
      if (!confirm('确定要删除这个商品吗？')) return
      
      this.loading = true
      try {
        await removeLiveProduct(this.liveId, productId)
        this.$message.success('商品删除成功')
        this.loadProducts()
      } catch (error) {
        this.error = '删除商品失败：' + (error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },

    async promoteProduct(productId) {
      this.loading = true
      try {
        await promoteLiveProduct(this.liveId, productId)
        this.$message.success('商品推广成功，已在聊天室展示')
      } catch (error) {
        this.error = '推广商品失败：' + (error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },

    closeModal() {
      this.showAddProduct = false
      this.editingProduct = null
      this.productForm = {
        name: '',
        description: '',
        price: 0,
        original_price: 0,
        stock: 0,
        image_url: '',
        product_url: ''
      }
    }
  }
}
</script>

<style scoped>
.live-product-manager {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.product-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.product-list {
  display: grid;
  gap: 16px;
}

.product-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: box-shadow 0.3s ease;
}

.product-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-item.out-of-stock {
  opacity: 0.6;
  background: #f5f5f5;
}

.product-image {
  width: 80px;
  height: 80px;
  margin-right: 16px;
  border-radius: 4px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.product-info h4 {
  margin: 0 0 8px 0;
  color: #333;
}

.product-description {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
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
  gap: 16px;
  font-size: 12px;
  color: #666;
}

.product-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
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

.product-modal {
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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