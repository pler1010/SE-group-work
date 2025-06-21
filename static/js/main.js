// 全局变量
let notificationQueue = [];
let isShowingNotification = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 添加平滑滚动
    addSmoothScrolling();
    
    // 初始化工具提示
    initializeTooltips();
    
    // 添加键盘快捷键
    addKeyboardShortcuts();
    
    // 初始化拖拽上传
    initializeDragAndDrop();
    
    // 添加页面过渡动画
    addPageTransitions();
    
    console.log('🚗 智能车载AI助手已启动');
}

// 添加平滑滚动
function addSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 初始化工具提示
function initializeTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', showTooltip);
        tooltip.addEventListener('mouseleave', hideTooltip);
    });
}

// 显示工具提示
function showTooltip(e) {
    const tooltipText = e.target.querySelector('.tooltiptext');
    if (tooltipText) {
        tooltipText.style.visibility = 'visible';
        tooltipText.style.opacity = '1';
    }
}

// 隐藏工具提示
function hideTooltip(e) {
    const tooltipText = e.target.querySelector('.tooltiptext');
    if (tooltipText) {
        tooltipText.style.visibility = 'hidden';
        tooltipText.style.opacity = '0';
    }
}

// 添加键盘快捷键
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Space: 播放/暂停视频
        if ((e.ctrlKey || e.metaKey) && e.code === 'Space') {
            e.preventDefault();
            const playBtn = document.getElementById('play-pause-btn');
            if (playBtn && !playBtn.disabled) {
                playBtn.click();
            }
        }
        
        // Escape: 关闭警告弹窗
        if (e.code === 'Escape') {
            const alertPanel = document.getElementById('alert-panel');
            if (alertPanel && alertPanel.classList.contains('show')) {
                alertPanel.classList.remove('show');
            }
        }
        
        // Ctrl/Cmd + R: 重新分析
        if ((e.ctrlKey || e.metaKey) && e.code === 'KeyR') {
            e.preventDefault();
            const analyzeBtn = document.getElementById('analyze-btn');
            if (analyzeBtn && !analyzeBtn.disabled) {
                analyzeBtn.click();
            }
        }
    });
}

// 初始化拖拽上传
function initializeDragAndDrop() {
    const uploadArea = document.getElementById('upload-area');
    const videoFile = document.getElementById('video-file');
    
    if (!uploadArea || !videoFile) return;
    
    // 防止默认拖拽行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // 高亮拖拽区域
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    // 处理文件拖拽
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        uploadArea.style.borderColor = '#0984e3';
        uploadArea.style.background = 'rgba(116, 185, 255, 0.2)';
        uploadArea.style.transform = 'scale(1.02)';
    }
    
    function unhighlight(e) {
        uploadArea.style.borderColor = '#74b9ff';
        uploadArea.style.background = 'rgba(116, 185, 255, 0.05)';
        uploadArea.style.transform = 'scale(1)';
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('video/')) {
                videoFile.files = files;
                // 触发change事件
                const event = new Event('change', { bubbles: true });
                videoFile.dispatchEvent(event);
                showNotification('📁 文件上传成功', 'success');
            } else {
                showNotification('❌ 请选择视频文件', 'error');
            }
        }
    }
}

// 添加页面过渡动画
function addPageTransitions() {
    // 为新添加的元素添加淡入动画
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1 && node.classList) {
                    node.classList.add('fade-in');
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// 显示通知
function showNotification(message, type = 'info', duration = 3000) {
    const notification = {
        id: Date.now(),
        message,
        type,
        duration
    };
    
    notificationQueue.push(notification);
    
    if (!isShowingNotification) {
        processNotificationQueue();
    }
}

// 处理通知队列
function processNotificationQueue() {
    if (notificationQueue.length === 0) {
        isShowingNotification = false;
        return;
    }
    
    isShowingNotification = true;
    const notification = notificationQueue.shift();
    
    displayNotification(notification);
}

// 显示通知元素
function displayNotification(notification) {
    const notificationEl = document.createElement('div');
    notificationEl.className = `notification notification-${notification.type}`;
    notificationEl.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${notification.message}</span>
            <button class="notification-close" onclick="closeNotification(this)">×</button>
        </div>
    `;
    
    // 添加样式
    notificationEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 500;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        backdrop-filter: blur(10px);
    `;
    
    // 设置背景颜色
    switch (notification.type) {
        case 'success':
            notificationEl.style.background = 'linear-gradient(135deg, #00b894 0%, #00a085 100%)';
            break;
        case 'error':
            notificationEl.style.background = 'linear-gradient(135deg, #fd79a8 0%, #e84393 100%)';
            break;
        case 'warning':
            notificationEl.style.background = 'linear-gradient(135deg, #fdcb6e 0%, #e17055 100%)';
            break;
        default:
            notificationEl.style.background = 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)';
    }
    
    document.body.appendChild(notificationEl);
    
    // 显示动画
    setTimeout(() => {
        notificationEl.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动关闭
    setTimeout(() => {
        closeNotification(notificationEl);
    }, notification.duration);
}

// 关闭通知
function closeNotification(element) {
    const notificationEl = element.closest ? element.closest('.notification') : element;
    
    notificationEl.style.transform = 'translateX(100%)';
    
    setTimeout(() => {
        if (notificationEl.parentNode) {
            notificationEl.parentNode.removeChild(notificationEl);
        }
        processNotificationQueue();
    }, 300);
}

// 格式化时间
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 检测浏览器支持
function checkBrowserSupport() {
    const features = {
        video: !!document.createElement('video').canPlayType,
        fileAPI: !!(window.File && window.FileReader && window.FileList && window.Blob),
        dragDrop: 'draggable' in document.createElement('span'),
        localStorage: !!window.localStorage
    };
    
    const unsupported = Object.keys(features).filter(key => !features[key]);
    
    if (unsupported.length > 0) {
        showNotification(`⚠️ 浏览器不支持以下功能: ${unsupported.join(', ')}`, 'warning', 5000);
    }
    
    return features;
}

// 性能监控
function monitorPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log(`📊 页面加载时间: ${loadTime}ms`);
            
            if (loadTime > 3000) {
                showNotification('⚡ 页面加载较慢，建议检查网络连接', 'warning');
            }
        });
    }
}

// 错误处理
window.addEventListener('error', function(e) {
    console.error('JavaScript错误:', e.error);
    showNotification('❌ 发生未知错误，请刷新页面重试', 'error');
});

// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', function(e) {
    console.error('未处理的Promise拒绝:', e.reason);
    showNotification('❌ 请求处理失败，请重试', 'error');
});

// 添加CSS样式（如果不存在）
function addNotificationStyles() {
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                margin-left: 15px;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                opacity: 0.8;
                transition: opacity 0.2s ease;
            }
            
            .notification-close:hover {
                opacity: 1;
                background: rgba(255, 255, 255, 0.2);
            }
        `;
        document.head.appendChild(style);
    }
}

// 初始化通知样式和性能监控
addNotificationStyles();
monitorPerformance();
checkBrowserSupport();

// 导出函数供全局使用
window.showNotification = showNotification;
window.formatTime = formatTime;
window.formatFileSize = formatFileSize;