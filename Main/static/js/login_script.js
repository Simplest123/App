document.addEventListener('DOMContentLoaded', () => {
            // 元素缓存
            const elements = {
                modals: {
                    login: document.getElementById('loginModal'),
                    register: document.getElementById('registerModal')
                },
                buttons: {
                    login: document.getElementById('loginButton'),
                    register: document.getElementById('goToRegister'),
                    goLogin: document.getElementById('goToLogin')
                },
                forms: {
                    login: document.getElementById('loginForm'),
                    register: document.getElementById('registerForm')
                }
            };
        
            // 状态管理
            const state = {
                currentModal: null,
                passwordVisible: false
            };
        
            // 通用方法
            const utils = {
                toggleModal: (modalType, show = true) => {
                    state.currentModal = show ? modalType : null;
                    elements.modals[modalType].style.display = show ? 'block' : 'none';
                    document.body.style.overflow = show ? 'hidden' : '';
                },
                
                showError: (input, message) => {
                    const group = input.closest('.input-group');
                    let error = group.querySelector('.error-message');
                    if (!error) {
                        error = document.createElement('div');
                        error.className = 'error-message';
                        group.appendChild(error);
                    }
                    error.textContent = message;
                    error.style.display = 'block';
                    input.style.borderColor = '#ef4444';
                    group.classList.add('error');
                },
        
                clearError: (input) => {
                    const group = input.closest('.input-group');
                    const error = group.querySelector('.error-message');
                    if (error) error.style.display = 'none';
                    input.style.borderColor = '';
                    group.classList.remove('error');
                },
        
                validateEmail: (email) => 
                    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
        
                validatePhone: (phone) => 
                    /^1[3-9]\d{9}$/.test(phone),
        
                checkPasswordMatch: (pass, confirm) => 
                    pass === confirm
            };
        
            // 事件处理器
            const handlers = {
                togglePassword: (e) => {
                    if (!e.target.classList.contains('password-toggle')) return;
                    const input = e.target.closest('.input-group').querySelector('input');
                    state.passwordVisible = !state.passwordVisible;
                    input.type = state.passwordVisible ? 'text' : 'password';
                    e.target.textContent = state.passwordVisible ? '👁️' : '👁';
                },
        
                handleInputValidation: (e) => {
                    const input = e.target;
                    if (!input.required) return;
                    
                    utils.clearError(input);
                    
                    if (input.id === 'regEmail' && !utils.validateEmail(input.value)) {
                        utils.showError(input, '邮箱格式不正确');
                    }
                    
                    if (input.id === 'regPhone' && !utils.validatePhone(input.value)) {
                        utils.showError(input, '手机号格式错误');
                    }
                },
        
                handleFormSubmit: {
                    login: (e) => {
                        e.preventDefault();
                        const formData = new FormData(e.target);
                        // 实际开发中这里发送登录请求
                        console.log('登录数据:', Object.fromEntries(formData));
                        utils.toggleModal('login', false);
                    },
        
                    register: (e) => {
                        e.preventDefault();
                        let isValid = true;
                        const inputs = e.target.querySelectorAll('input[required]');
        
                        // 基础验证
                        inputs.forEach(input => {
                            if (!input.value.trim()) {
                                utils.showError(input, '该字段不能为空');
                                isValid = false;
                            }
                        });
        
                        // 邮箱验证
                        const email = document.getElementById('regEmail');
                        if (!utils.validateEmail(email.value)) {
                            utils.showError(email, '请输入有效邮箱地址');
                            isValid = false;
                        }
        
                        // 手机号验证
                        const phone = document.getElementById('regPhone');
                        if (!utils.validatePhone(phone.value)) {
                            utils.showError(phone, '手机号格式不正确');
                            isValid = false;
                        }
        
                        // 密码匹配验证
                        const password = document.getElementById('regPassword');
                        const confirm = document.getElementById('regConfirm');
                        if (!utils.checkPasswordMatch(password.value, confirm.value)) {
                            utils.showError(confirm, '两次密码输入不一致');
                            isValid = false;
                        }
        
                        // 性别选择验证
                        const gender = document.querySelector('input[name="gender"]:checked');
                        if (!gender) {
                            const group = document.querySelector('.radio-group');
                            group.style.border = '2px solid #ef4444';
                            isValid = false;
                        }
        
                        if (isValid) {
                            // 实际开发中这里发送注册请求
                            console.log('注册数据:', {
                                username: document.getElementById('regUsername').value,
                                email: email.value,
                                name: document.getElementById('regName').value,
                                gender: gender.value,
                                phone: phone.value
                            });
                            alert('🎉 注册成功！');
                            utils.toggleModal('register', false);
                        }
                    }
                }
            };
        
            // 事件监听
            document.addEventListener('click', (e) => {
                // 模态框切换
                if (e.target === elements.buttons.login) {
                    utils.toggleModal('login');
                }
                if (e.target === elements.buttons.register) {
                    utils.toggleModal('login', false);
                    utils.toggleModal('register');
                }
                if (e.target === elements.buttons.goLogin) {
                    utils.toggleModal('register', false);
                    utils.toggleModal('login');
                }
        
                // 关闭操作
                if (e.target.classList.contains('close') || 
                    e.target.classList.contains('modal')) {
                    utils.toggleModal(state.currentModal, false);
                }
        
                // 密码可见切换
                handlers.togglePassword(e);
            });
        
            // 输入实时验证
            document.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', handlers.handleInputValidation);
            });
        
            // 表单提交
            elements.forms.login.addEventListener('submit', handlers.handleFormSubmit.login);
            elements.forms.register.addEventListener('submit', handlers.handleFormSubmit.register);
        
            // 密码强度实时检测
            document.getElementById('regPassword').addEventListener('input', function() {
                const strength = calculatePasswordStrength(this.value);
                updateStrengthIndicator(strength);
            });
        
            function calculatePasswordStrength(password) {
                let strength = 0;
                if (password.length >= 8) strength++;
                if (/[A-Z]/.test(password)) strength++;
                if (/[0-9]/.test(password)) strength++;
                if (/[^A-Za-z0-9]/.test(password)) strength++;
                return strength;
            }
        
            function updateStrengthIndicator(strength) {
                const indicator = document.querySelector('.strength-progress');
                const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'];
                indicator.style.width = `${strength * 25}%`;
                indicator.style.backgroundColor = colors[strength] || colors[0];
            }
        });
		