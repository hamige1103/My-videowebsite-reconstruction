export default {
    ADD_ACOUNTVUEX(state, countVuex) {
        state.countVuex = countVuex
    },
    SET_USER_INFO(state, userInfo) {
        state.user = userInfo
    },
    SET_LOGIN_STATUS(state, status) {
        state.isLogining = status
    }
}