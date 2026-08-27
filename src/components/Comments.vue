<template>
    <el-row>
        <el-form size="large"
                id="comment-form"
                 :model="commentForm" 
                 class="demo-form-inline"
                 label-position="top"
                 style="width: 100%;"
                 label-width="100px">
            <el-form-item label="评论">
                <el-input v-model="commentForm.body" placeholder="请输入评论" type="textarea" :rows="4"/>
            </el-form-item>
            <el-form-item style="float:left;">
                <el-button type="primary" @click="publishComment">发表</el-button>
            </el-form-item>
        </el-form>
    </el-row>

    <div v-for="(comment, i) in comments" :key="i" class="comment">
        <el-divider />
        <!-- 评论人信息 -->
        <el-row class="comment-username" :id="comment.id">
            {{ comment.user_name }} &nbsp;&nbsp; {{comment.time }}
            <el-button link style="position:absolute; right: 10%" @click="showReplyForm">回复</el-button>
        </el-row>
        <!-- 评论内容 -->
        <el-row class="comment-p" style="padding: 10px" >
            {{ comment.body }}
        </el-row>
        <!-- 回复框 -->
        <el-row class="comment-reply-form" style="display: none" :id="'reply-' + comment.id">
            <el-form  :model="replyComment" size="small" style="width: 100%;">
                <el-form-item label="">
                    <el-input v-model="replyComment.body" placeholder="回复:" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="replyCommentPost">回复</el-button>
                </el-form-item>
            </el-form>
        </el-row>
        <!-- 此评论的回复 -->
        <div v-for="(reply, j) in comment.replies" :key="j" class="comment-replay">
            <el-row class="comment-username" :id="reply.id">
                {{ reply.user_name }} &nbsp;回复&nbsp; {{reply.reply_user_name }} &nbsp;&nbsp; {{ reply.time }}
                <el-button link style="position:absolute; right: 10%" @click="showReplyForm">回复</el-button>
            </el-row>
            <el-row class="comment-p" style="padding: 10px" >{{ reply.body }}</el-row>
            <el-row class="comment-reply-form" style="display: none" :id="'reply-' + reply.id">
                <el-form  :model="replyComment" size="small" style="width: 100%;">
                    <el-form-item label="">
                      <el-input v-model="replyComment.body" placeholder="回复:" type="textarea" :rows="3" />
                    </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="replyCommentPost">回复</el-button>
                    </el-form-item>
                </el-form>
            </el-row>
        </div>
    </div>
    
</template>

<script>
import { reactive } from 'vue'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { publishComment, showVodComment, replyCommentPost } from '../apis/comments'

export default {
    // 评论组件
    name: 'Comment',
    setup() {
        const store = useStore()
        
        const commentForm = reactive({
                body: '',
                user_id: '',
            })

        const replyComment = reactive({
                body: '',
                user_id: ''
            })

        return {
            store,
            commentForm,
            replyComment
        }
    },

    props: {
        vod_id: String
    },

    data() {
        return {
            comments:  [],
        }
    },

    methods: {
        publishComment() {
            if (this.store.state.appStore.isLogining) {
                // 登录状态发布评论
                // 构建符合后端API的数据结构
                const commentData = {
                    content: this.commentForm.body,
                    video_id: parseInt(this.vod_id)
                }
                
                console.log('发表评论请求数据:', commentData)
                publishComment(commentData).then(
                    res => {
                        console.log('发表评论响应:', res)
                        if (res && res.data && res.data.code == 200) {
                            ElMessage({
                                message: '评论发布成功',
                                type: 'success',
                            })
                            this.showVodComment()
                            this.commentForm.body = ''
                        } else {
                            ElMessage({
                                message: res && res.data ? res.data.message : '评论发布失败',
                                type: 'warning',
                            })
                        }
                    }
                ).catch(error => {
                    console.error('评论发布错误:', error)
                    ElMessage({
                        message: '评论发布失败，请检查网络连接',
                        type: 'error',
                    })
                })
            } else {
                ElMessage({
                message: "请先登录",
                type: 'warning',
                })
            }
        },

        showVodComment() {
            showVodComment({video_id: this.vod_id}).then(
                res => {
                    console.log('获取评论列表响应:', res)
                    if (res && res.data && res.data.code == 200) {
                        this.comments = res.data.data
                    } else {
                        ElMessage({
                                    message: res && res.data ? res.data.message : '获取评论列表失败',
                                    type: 'warning',
                                    })}
                                }
                            )
                },

        showReplyForm(e) {
            this.replyComment.body = ''
            var forms = document.getElementsByClassName("comment-reply-form")
            for (var i in forms) {
                if (typeof(forms[i])=="object" && forms[i].style.display == "block") {
                    forms[i].style.display = "none"
                }
            }
            var comment_id = 'reply-' + e.currentTarget.parentElement.id
            document.getElementById(comment_id).style.display = "block"
        },

        replyCommentPost(e) {
            if (this.store.state.appStore.isLogining) {
                // 登录状态回复评论
                var comment_id = e.currentTarget.parentElement.parentElement.parentElement.parentElement.id.split('-')[1]
                
                // 构建符合后端API的数据结构
                const replyData = {
                    content: this.replyComment.body,
                    video_id: parseInt(this.vod_id),
                    parent_id: parseInt(comment_id)
                }
                
                console.log('回复评论数据:', replyData)
                replyCommentPost(replyData).then(
                    res => {
                        console.log('回复评论响应:', res)
                        if (res && res.data && res.data.code == 200) {
                            this.replyComment.body = ''
                            this.showVodComment()
                            // 隐藏回复框
                            var forms = document.getElementsByClassName("comment-reply-form")
                            for (var i in forms) {
                                if (typeof(forms[i])=="object" && forms[i].style.display == "block") {
                                    forms[i].style.display = "none"
                                }
                            }
                        } else {
                            ElMessage({
                                message: res && res.data ? res.data.message : '回复失败',
                                type: 'warning',
                            })
                        }
                    }
                ).catch(error => {
                    console.error('回复评论错误:', error)
                    ElMessage({
                        message: '回复失败，请检查网络连接',
                        type: 'error',
                    })
                })
            } else {
                ElMessage({
                message: "请先登录",
                type: 'warning',
                })
            }
        }
            
        },

    created() {
        this.showVodComment()
    }

   
}
</script>

<style>
#comment-form .el-form-item__label {
  font-size: 18px;
  font-weight: bold;
}


.el-row.comment-username {
    color: #777888;
}

div.comment-replay {
    padding-left: 3%;
}
</style>