// static/js/auth.js
const AuthManager = {
    // 同步检查登录状态
    async checkLogin() {
        try {
            const response = await fetch('/sessions');
            const data = await response.json();

            if (data.re_code === RET.OK) {
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userAvatar', data.user?.avatar || 'static/img/default_avatar.jpg');
                return true;
            }
            localStorage.clear();
            return false;
        } catch (error) {
            console.error('Session检查失败:', error);
            localStorage.clear();
            return false;
        }
    },

    // 更新所有页面UI
    updateUI() {
        const loginButton = document.getElementById('login-button');
        const userAvatar = document.getElementById('user-avatar');
        const avatar_url = document.getElementById('user-avatar_url');

        if (localStorage.getItem('isLoggedIn') === 'true') {
            loginButton?.style?.setProperty('display', 'none', 'important');
            userAvatar?.style?.setProperty('display', 'inline-block', 'important');
            if (avatar_url) {
                avatar_url.src = localStorage.getItem('userAvatar') || 'static/img/default_avatar.jpg';
            }
        } else {
            loginButton?.style?.setProperty('display', 'inline-block', 'important');
            userAvatar?.style?.setProperty('display', 'none', 'important');
        }
    },

    // 路由守卫
    async routeGuard() {
        const isLoggedIn = await this.checkLogin();
        const protectedRoutes = ['/article', '/article-single', '/center', '/service_photo', '/service_video'];

        const currentPath = window.location.pathname;
        if (protectedRoutes.some(route => currentPath.startsWith(route)) {
            if (!isLoggedIn) {
                window.location.href = '/';
                return false;
            }
        }
        return true;
    }
};