// 模拟前端调用智能搜索API
const axios = require('axios');

// 模拟前端axios配置
const service = axios.create({
    baseURL: 'http://localhost:8000/api',
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
    },
});

async function testSmartSearch() {
    try {
        console.log('=== 测试前端API调用 ===');
        
        // 测试智能搜索
        const response = await service.post('/v1/smart-search', {
            question: '动作电影'
        });
        
        console.log('API响应状态:', response.status);
        console.log('API响应数据:', JSON.stringify(response.data, null, 2));
        
        if (response.data.code === 200) {
            console.log('✅ 智能搜索API调用成功');
            console.log('生成的SQL:', response.data.data.generated_sql);
            console.log('结果数量:', response.data.data.total);
        } else {
            console.log('❌ 智能搜索API调用失败:', response.data.message);
        }
        
    } catch (error) {
        console.error('❌ API调用异常:', error.message);
        if (error.response) {
            console.error('响应状态:', error.response.status);
            console.error('响应数据:', error.response.data);
        }
    }
}

testSmartSearch();