// 语音控制模块
const voiceControl = {
    init() {
        this.startVoiceButton = document.getElementById('start-voice');
        this.voiceOutput = document.getElementById('voice-output');
        
        if (this.startVoiceButton) {
            this.startVoiceButton.addEventListener('click', () => this.startVoiceRecognition());
        }
    },
    
    startVoiceRecognition() {
        // 检查浏览器是否支持语音识别
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('您的浏览器不支持语音识别功能');
            return;
        }
        
        // 使用浏览器内置的语音识别API
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        
        recognition.onstart = () => {
            this.voiceOutput.textContent = '正在听取指令...';
            this.startVoiceButton.disabled = true;
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.voiceOutput.textContent = `您说: ${transcript}`;
            
            // 发送到服务器处理
            this.processVoiceCommand(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('语音识别错误:', event.error);
            this.voiceOutput.textContent = `错误: ${event.error}`;
            this.startVoiceButton.disabled = false;
        };
        
        recognition.onend = () => {
            this.startVoiceButton.disabled = false;
        };
        
        recognition.start();
    },
    
    processVoiceCommand(transcript) {
        fetch('/process_voice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `text=${encodeURIComponent(transcript)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.voiceOutput.textContent += `\n${data.message}`;
                this.executeAction(data.action);
            } else {
                this.voiceOutput.textContent += `\n${data.message}`;
            }
        })
        .catch(error => {
            console.error('处理语音命令出错:', error);
            this.voiceOutput.textContent += '\n处理命令时出错';
        });
    },
    
    executeAction(action) {
        // 实际执行相应的操作
        console.log(`执行动作: ${action}`);
        // 这里添加实际的功能实现，如控制音乐、空调等
    }
};

// 交互控制模块（整合手势和视觉交互）
const interactionControl = {
    init() {
        this.videoElement = document.getElementById('camera-video');
        this.startCameraButton = document.getElementById('start-camera');
        this.captureGestureButton = document.getElementById('capture-gesture');
        this.captureVisualButton = document.getElementById('capture-visual');
        this.outputElement = document.getElementById('interaction-output');
        
        // 绑定页面上的摄像头控件，无论在哪个页面
        this.bindCameraControls();
        
        // 初始化摄像头状态
        this.cameraActive = false;
        this.stream = null;
    },
    
    bindCameraControls() {
        // 找到所有需要绑定的摄像头按钮
        const startButtons = document.querySelectorAll('[id^="start-camera"], [id="start-visual-camera"]');
        const gestureButtons = document.querySelectorAll('[id^="capture-gesture"]');
        const visualButtons = document.querySelectorAll('[id^="capture-"], [id="capture-head"], [id="capture-gaze"]');
        
        // 绑定启动摄像头按钮
        startButtons.forEach(button => {
            if (button) {
                button.addEventListener('click', () => this.startCamera());
            }
        });
        
        // 绑定手势捕捉按钮
        gestureButtons.forEach(button => {
            if (button) {
                button.addEventListener('click', () => this.captureGesture());
            }
        });
        
        // 绑定视觉捕捉相关按钮
        visualButtons.forEach(button => {
            if (button && button.id.includes('visual')) {
                button.addEventListener('click', () => this.captureVisual());
            }
            if (button && button.id.includes('head')) {
                button.addEventListener('click', () => this.captureHeadPose());
            }
            if (button && button.id.includes('gaze')) {
                button.addEventListener('click', () => this.captureGaze());
            }
        });
    },
    
    startCamera() {
        // 寻找页面上的视频元素
        const videoElements = document.querySelectorAll('video');
        if (videoElements.length === 0) return;
        
        // 使用第一个找到的视频元素
        const videoElement = videoElements[0];
        
        // 如果摄像头已经启动，不做任何操作
        if (this.cameraActive) return;
        
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                videoElement.srcObject = stream;
                videoElement.style.display = 'block';
                this.stream = stream;
                this.cameraActive = true;
                
                // 启用所有捕捉按钮
                document.querySelectorAll('[id^="capture-"], [id="capture-head"], [id="capture-gaze"]').forEach(btn => {
                    if (btn) btn.disabled = false;
                });
                
                // 禁用所有启动摄像头按钮
                document.querySelectorAll('[id^="start-camera"], [id="start-visual-camera"]').forEach(btn => {
                    if (btn) btn.disabled = true;
                });
                
                // 更新输出信息
                const outputElements = document.querySelectorAll('.output');
                outputElements.forEach(output => {
                    if (output && !output.id.includes('voice')) {
                        output.textContent = '摄像头已启动，准备就绪';
                    }
                });
            })
            .catch(error => {
                console.error('获取摄像头失败:', error);
                const outputElements = document.querySelectorAll('.output');
                outputElements.forEach(output => {
                    if (output && !output.id.includes('voice')) {
                        output.textContent = '无法访问摄像头';
                    }
                });
            });
    },
    
    captureGesture() {
        this.captureFrame('/process_gesture', '手势');
    },
    
    captureVisual() {
        this.captureFrame('/process_visual', '视觉信息');
    },
    
    captureHeadPose() {
        this.captureFrame('/process_head_pose', '头部姿态');
    },
    
    captureGaze() {
        this.captureFrame('/process_gaze', '目光方向');
    },
    
    captureFrame(endpoint, type) {
        // 查找活跃的视频元素
        const videoElements = document.querySelectorAll('video');
        if (videoElements.length === 0 || !this.cameraActive) {
            alert('请先启动摄像头');
            return;
        }
        
        const videoElement = videoElements[0];
        if (!videoElement.srcObject) {
            alert('请先启动摄像头');
            return;
        }
        
        // 输出元素可能在不同页面有不同ID
        let outputElement;
        if (type.includes('手势')) {
            outputElement = document.getElementById('gesture-output') || document.getElementById('interaction-output');
        } else if (type.includes('头部') || type.includes('目光') || type.includes('视觉')) {
            outputElement = document.getElementById('visual-output') || document.getElementById('interaction-output');
        } else {
            outputElement = document.getElementById('interaction-output');
        }
        
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0);
        
        canvas.toBlob(blob => {
            const formData = new FormData();
            formData.append('image', blob);
            
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (outputElement) {
                        outputElement.textContent = `${type}捕捉成功: ${data.message}`;
                    }
                } else {
                    if (outputElement) {
                        outputElement.textContent = `${type}捕捉失败: ${data.message}`;
                    }
                }
            })
            .catch(error => {
                console.error(`${type}处理出错:`, error);
                if (outputElement) {
                    outputElement.textContent = `${type}处理时出错`;
                }
            });
        });
    }
};

// 系统设置模块
const systemSettings = {
    init() {
        this.preferenceForm = document.getElementById('preference-form');
        this.permissionForm = document.getElementById('permission-form');
        
        if (this.preferenceForm) {
            this.preferenceForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.savePreference();
            });
        }
        
        if (this.permissionForm) {
            this.permissionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.updatePermissions();
            });
        }
    },
    
    savePreference() {
        const formData = new FormData(this.preferenceForm);
        
        fetch('/save_preference', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('偏好设置已保存');
                location.reload(); // 刷新页面以显示更新后的偏好
            } else {
                alert('保存偏好设置失败');
            }
        })
        .catch(error => {
            console.error('保存偏好设置出错:', error);
            alert('保存偏好设置时出错');
        });
    },
    
    updatePermissions() {
        const formData = new FormData(this.permissionForm);
        
        fetch('/update_permissions', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('权限设置已更新');
            } else {
                alert(data.message || '更新权限设置失败');
            }
        })
        .catch(error => {
            console.error('更新权限设置出错:', error);
            alert('更新权限设置时出错');
        });
    }
};

// 干扰处理模块
const distractionHandler = {
    init() {
        this.statusBar = document.getElementById('status-bar');
        this.videoElement = document.getElementById('distraction-video');
        this.simulateButton = document.getElementById('simulate-distraction');

        if (this.simulateButton) {
            this.simulateButton.addEventListener('click', () => this.simulateDistraction());
        }
    },

    simulateDistraction() {
        this.statusBar.textContent = '警告! 请目视前方';
        this.statusBar.style.color = 'red';

        // 模拟视觉检测分心状态
        setTimeout(() => {
            this.triggerVoiceWarning();
        }, 3000);
    },

    triggerVoiceWarning() {
        this.statusBar.textContent = '请立即目视前方!';
        fetch('/process_voice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'text=已注意道路'
        }).then(response => response.json())
          .then(data => {
              if (data.success) {
                  this.statusBar.textContent = '状态栏: 正常驾驶';
                  this.statusBar.style.color = 'green';
              }
          });
    }
};

// 多模态交互控制器
const multimodalController = {
    init() {
        // 初始化所有子控制器
        voiceControl.init();
        
        // 摄像头相关初始化
        this.videoElement = document.getElementById('camera-video');
        this.startCameraButton = document.getElementById('start-camera');
        this.captureGestureButton = document.getElementById('capture-gesture');
        this.captureHeadButton = document.getElementById('capture-head');
        this.captureGazeButton = document.getElementById('capture-gaze');
        
        // 输出元素
        this.gestureOutput = document.getElementById('gesture-output');
        this.visualOutput = document.getElementById('visual-output');
        
        // 状态显示元素
        this.statusAction = document.getElementById('status-action');
        this.statusInteraction = document.getElementById('status-interaction');
        this.statusState = document.getElementById('status-state');
        
        // 初始化摄像头状态
        this.cameraActive = false;
        this.stream = null;
        
        // 绑定摄像头按钮事件
        if (this.startCameraButton) {
            this.startCameraButton.addEventListener('click', () => this.startCamera());
        }
        
        // 绑定手势捕捉按钮事件
        if (this.captureGestureButton) {
            this.captureGestureButton.addEventListener('click', () => this.captureGesture());
        }
        
        // 绑定视觉捕捉按钮事件
        if (this.captureHeadButton) {
            this.captureHeadButton.addEventListener('click', () => this.captureHeadPose());
        }
        
        if (this.captureGazeButton) {
            this.captureGazeButton.addEventListener('click', () => this.captureGaze());
        }
    },
    
    startCamera() {
        if (!this.videoElement) return;
        
        // 如果摄像头已经启动，不执行任何操作
        if (this.cameraActive) return;
        
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                this.videoElement.srcObject = stream;
                this.videoElement.style.display = 'block';
                this.stream = stream;
                this.cameraActive = true;
                
                // 启用所有捕捉按钮
                if (this.captureGestureButton) this.captureGestureButton.disabled = false;
                if (this.captureHeadButton) this.captureHeadButton.disabled = false;
                if (this.captureGazeButton) this.captureGazeButton.disabled = false;
                
                // 禁用启动摄像头按钮
                if (this.startCameraButton) this.startCameraButton.disabled = true;
                
                // 更新状态
                this.updateStatus('状态', '摄像头已启动');
            })
            .catch(error => {
                console.error('获取摄像头失败:', error);
                this.updateStatus('状态', '无法访问摄像头');
                alert('无法访问摄像头，请确保允许浏览器使用摄像头权限');
            });
    },
    
    captureGesture() {
        if (!this.cameraActive) {
            this.updateStatus('状态', '请先启动摄像头');
            return;
        }
        
        this.updateStatus('状态', '正在捕捉手势...');
        this.captureFrame('/process_gesture', '手势', this.gestureOutput);
    },
    
    captureHeadPose() {
        if (!this.cameraActive) {
            this.updateStatus('状态', '请先启动摄像头');
            return;
        }
        
        this.updateStatus('状态', '正在捕捉头部姿态...');
        this.captureFrame('/process_head_pose', '头部姿态', this.visualOutput);
    },
    
    captureGaze() {
        if (!this.cameraActive) {
            this.updateStatus('状态', '请先启动摄像头');
            return;
        }
        
        this.updateStatus('状态', '正在捕捉目光方向...');
        this.captureFrame('/process_gaze', '目光方向', this.visualOutput);
    },
    
    captureFrame(endpoint, type, outputElement) {
        if (!this.videoElement || !this.cameraActive) return;
        
        // 创建canvas并截取视频帧
        const canvas = document.createElement('canvas');
        canvas.width = this.videoElement.videoWidth;
        canvas.height = this.videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(this.videoElement, 0, 0);
        
        // 将canvas内容转换为blob并发送到服务器
        canvas.toBlob(blob => {
            const formData = new FormData();
            formData.append('image', blob);
            
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (outputElement) {
                        outputElement.textContent = `检测到${type}: ${data.message}`;
                    }
                    this.updateStatus('操作结果', data.message);
                    this.updateStatus('最近交互', type);
                    this.updateStatus('状态', '识别成功');
                } else {
                    if (outputElement) {
                        outputElement.textContent = `${type}识别失败: ${data.message}`;
                    }
                    this.updateStatus('状态', '识别失败');
                }
            })
            .catch(error => {
                console.error(`${type}处理出错:`, error);
                if (outputElement) {
                    outputElement.textContent = `${type}处理时出错`;
                }
                this.updateStatus('状态', '处理出错');
            });
        });
    },
    
    updateStatus(type, message) {
        // 根据状态类型更新对应的状态显示
        switch (type) {
            case '操作结果':
                if (this.statusAction) this.statusAction.textContent = message;
                break;
            case '最近交互':
                if (this.statusInteraction) this.statusInteraction.textContent = message;
                break;
            case '状态':
                if (this.statusState) this.statusState.textContent = message;
                break;
        }
    }
};

// 增强语音控制模块
voiceControl.originalProcessVoiceCommand = voiceControl.processVoiceCommand;
voiceControl.processVoiceCommand = function(transcript) {
    fetch('/process_voice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `text=${encodeURIComponent(transcript)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            this.voiceOutput.textContent += `\n${data.message}`;
            this.executeAction(data.action);
            
            // 更新状态（如果在多模态界面中）
            if (multimodalController.updateStatus) {
                multimodalController.updateStatus('操作结果', data.message);
                multimodalController.updateStatus('最近交互', '语音');
                multimodalController.updateStatus('状态', '识别成功');
            }
        } else {
            this.voiceOutput.textContent += `\n${data.message}`;
            
            // 更新状态（如果在多模态界面中）
            if (multimodalController.updateStatus) {
                multimodalController.updateStatus('状态', '识别失败');
            }
        }
    })
    .catch(error => {
        console.error('处理语音命令出错:', error);
        this.voiceOutput.textContent += '\n处理命令时出错';
        
        // 更新状态（如果在多模态界面中）
        if (multimodalController.updateStatus) {
            multimodalController.updateStatus('状态', '处理出错');
        }
    });
};

// 初始化所有模块
document.addEventListener('DOMContentLoaded', () => {
    // 判断当前页面
    if (document.getElementById('camera-video') && document.getElementById('start-voice')) {
        // 多模态整合界面
        multimodalController.init();
    } else {
        // 单独的功能页面
        voiceControl.init();
        interactionControl.init();
    }
});
