<template>
  <div class="admin-comments">
    <div class="page-header">
      <h2>评论管理</h2>
      <p>管理系统用户评论</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filters">
      <div class="search-box">
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索评论内容..."
          @input="handleSearch"
        />
        <button @click="handleSearch" class="search-btn">🔍</button>
      </div>
      
      <div class="filter-group">
        <select v-model="filterStatus" @change="loadComments">
          <option value="">所有状态</option>
          <option value="active">正常</option>
          <option value="deleted">已删除</option>
        </select>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comments-table">
      <div class="table-header">
        <div class="table-row">
          <div class="table-cell">ID</div>
          <div class="table-cell">用户</div>
          <div class="table-cell">视频ID</div>
          <div class="table-cell">评论内容</div>
          <div class="table-cell">状态</div>
          <div class="table-cell">创建时间</div>
          <div class="table-cell">操作</div>
        </div>
      </div>
      
      <div class="table-body">
        <div 
          v-for="comment in comments" 
          :key="comment.id" 
          class="table-row"
        >
          <div class="table-cell">{{ comment.id }}</div>
          <div class="table-cell">{{ comment.user_name }}</div>
          <div class="table-cell">{{ comment.video_id }}</div>
          <div class="table-cell comment-content">
            {{ comment.body || comment.content }}
          </div>
          <div class="table-cell">
            <span :class="['status-badge', comment.reviewed ? 'active' : 'deleted']">
              {{ comment.reviewed ? '正常' : '待审核' }}
            </span>
          </div>
          <div class="table-cell">{{ formatDate(comment.timestamp) }}</div>
          <div class="table-cell">
            <button 
              v-if="comment.reviewed"
              @click="deleteComment(comment.id)" 
              class="btn btn-delete"
            >
              删除
            </button>
            <button 
              v-if="!comment.reviewed"
              @click="reviewComment(comment.id, true)" 
              class="btn btn-restore"
            >
              审核通过
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1"
        class="page-btn"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页，共 {{ totalPages }} 页
      </span>
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import service from '../request/index'

export default {
  name: 'AdminComments',
  setup() {
    const comments = ref([])
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalPages = ref(1)
    const searchKeyword = ref('')
    const filterStatus = ref('')

    // 加载评论列表
    const loadComments = async () => {
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value
        }
        
        if (searchKeyword.value) {
          params.search = searchKeyword.value
        }
        
        const response = await service.get('/v1/admin/comments', { params })
        comments.value = response.data
        
        // 简单分页处理
        totalPages.value = Math.ceil(comments.value.length / pageSize.value)
        
      } catch (error) {
        console.error('获取评论列表失败:', error)
        // 设置默认数据用于测试
        comments.value = [
          { id: 1, content: '这个视频很好看', user_id: 53, video_id: 86699, status: 'active' },
          { id: 2, content: '感谢分享', user_id: 54, video_id: 86700, status: 'active' }
        ]
        totalPages.value = 1
      }
    }

    // 搜索评论
    const handleSearch = () => {
      currentPage.value = 1
      loadComments()
    }

    // 分页操作
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        loadComments()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        loadComments()
      }
    }

    // 删除评论
    const deleteComment = async (commentId) => {
      if (!confirm('确定要删除这条评论吗？')) {
        return
      }
      
      try {
        await service.delete(`/v1/admin/comments/${commentId}`)
        loadComments()
        
      } catch (error) {
        console.error('删除评论失败:', error)
        alert('删除评论失败，请重试')
      }
    }

    // 审核评论
    const reviewComment = async (commentId, reviewed) => {
      if (!confirm(`确定要${reviewed ? '审核通过' : '标记为待审核'}这条评论吗？`)) {
        return
      }
      
      try {
        await service.put(`/v1/admin/comments/${commentId}/review`, {
          reviewed: reviewed
        })
        loadComments()
        
      } catch (error) {
        console.error('审核评论失败:', error)
        alert('审核评论失败，请重试')
      }
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadComments()
    })

    return {
      comments,
      currentPage,
      totalPages,
      searchKeyword,
      filterStatus,
      loadComments,
      handleSearch,
      prevPage,
      nextPage,
      deleteComment,
      reviewComment,
      formatDate
    }
  }
}
</script>

<style scoped>
.admin-comments {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 16px;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-box input {
  border: none;
  padding: 10px 15px;
  outline: none;
  flex: 1;
  min-width: 200px;
}

.search-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
}

.filter-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
}

.comments-table {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.table-header {
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 120px 80px 2fr 100px 150px 120px;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 5px 0;
}

.comment-content {
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #28a745;
  color: white;
}

.status-badge.deleted {
  background: #dc3545;
  color: white;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
  font-size: 12px;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-restore {
  background: #17a2b8;
  color: white;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}
</style>