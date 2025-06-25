(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    select('#navbar').classList.toggle('navbar-mobile')
    this.classList.toggle('bi-list')
    this.classList.toggle('bi-x')
  })

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav dropdowns activate
   */
  on('click', '.navbar .dropdown > a', function(e) {
    if (select('#navbar').classList.contains('navbar-mobile')) {
      e.preventDefault()
      this.nextElementSibling.classList.toggle('dropdown-active')
    }
  }, true)

  /**
   * Testimonials slider
   */
  new Swiper('.testimonials-slider', {
    speed: 600,
    loop: true,
    autoplay: {
      delay: 5000,
      disableOnInteraction: false
    },
    slidesPerView: 'auto',
    pagination: {
      el: '.swiper-pagination',
      type: 'bullets',
      clickable: true
    }
  });

  /**
   * Animation on scroll
   */
  window.addEventListener('load', () => {
    AOS.init({
      duration: 1000,
      easing: 'ease-in-out',
      once: true,
      mirror: false
    })
  });

})()


 // 获取导航栏元素
const header = document.getElementById('header');

// 页面加载完成后显示导航栏
window.addEventListener('load', function () {
  // 添加 visible 类，触发淡入效果
  header.classList.add('visible');
});

// 页面刷新前隐藏导航栏
window.addEventListener('beforeunload', function () {
  // 移除 visible 类，触发淡出效果
  header.classList.remove('visible');
});
const RET = {
    OK: "0", // 成功
    DBERR: "4001", // 数据库错误
    NODATA: "4002", // 无数据
    DATAEXIST: "4003", // 数据已存在
    DATAERR: "4004", // 数据错误
    SESSIONERR: "4101", // 用户未登录
    LOGINERR: "4102", // 登录失败
    PARAMERR: "4103", // 参数错误
    USERERR: "4104", // 用户不存在或未激活
    ROLEERR: "4105", // 用户身份错误
    PWDERR: "4106", // 密码错误
    REQERR: "4201", // 非法请求
    IPERR: "4202", // IP受限
    THIRDERR: "4301", // 第三方系统错误
    IOERR: "4302", // 文件读写错误
    SERVERERR: "4500", // 内部错误
    UNKOWNERR: "4501", // 未知错误
    REGISTERERR: "4503" // 注册失败
};

// 获取错误信息
function getErrorMessage(re_code) {
    switch (re_code) {
        case RET.DBERR: return '数据库错误，请稍后重试';
        case RET.NODATA: return '无数据';
        case RET.DATAEXIST: return '数据已存在';
        case RET.DATAERR: return '数据错误';
        case RET.SESSIONERR: return '用户未登录，请先登录';
        case RET.LOGINERR: return '登录失败，请检查用户名和密码';
        case RET.PARAMERR: return '参数错误，请检查输入';
        case RET.USERERR: return '用户不存在或未激活';
        case RET.ROLEERR: return '用户身份错误';
        case RET.PWDERR: return '密码错误';
        case RET.REQERR: return '非法请求';
        case RET.IPERR: return 'IP受限';
        case RET.THIRDERR: return '第三方系统错误';
        case RET.IOERR: return '文件读写错误';
        case RET.SERVERERR: return '服务器内部错误';
        case RET.UNKOWNERR: return '未知错误';
        case RET.REGISTERERR: return '注册失败';
        default: return '未知错误';
    }
}

// 获取 CSRF Token
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrf_token='))
        ?.split('=')[1] || '';
}

async function sendRequest(url, method, data = null) {
    const csrfToken = getCSRFToken();
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrfToken
            }
        };

        // 如果是 GET 请求，不添加 body
        if (method.toUpperCase() !== 'GET' && data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('请求错误:', error);
        throw error;
    }
}

// 页面加载时检查登录状态
window.onload = function () {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userAvatar = localStorage.getItem('userAvatar');
    const username = localStorage.getItem('username');

    const loginButton = document.getElementById('login-button');
    const userAvatarElement = document.getElementById('user-avatar');
    const avatar_url = document.getElementById('user-avatar_url');

    if (isLoggedIn) {
        if (loginButton) loginButton.style.display = 'none';
        if (userAvatarElement) {
            userAvatarElement.style.display = 'inline-block';
            avatar_url.src = userAvatar || 'https://remote-sensing-system.oss-cn-beijing.aliyuncs.com/images/default%20avatar.jpg';
        }
        console.log('用户已登录，用户名:', username);
    } else {
        console.log('用户未登录');
    }
};


/**
 * 自定义弹窗函数
 * @param {string} title - 弹窗标题
 * @param {string} content - 弹窗内容
 * @param {'success'|'error'|'warning'|'info'|'question'} [iconType='info'] - 图标类型
 */
function showAlert(title, content, iconType = 'info') {
  Swal.fire({
    title: title,
    text: content,
    icon: iconType,
    confirmButtonText: '确定',
    confirmButtonColor: '#3085d6',
    customClass: {
      popup: 'custom-swal-popup'
    }
  });
}