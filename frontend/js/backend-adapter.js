console.log('🔧 后端适配器加载中...');

// 全局变量初始化
window.DEEPSEEK_API_KEY = 'your_api_key';
window.isStreaming = false;

// 确保对话数据结构
if (!window.conversations) {
    try {
        window.conversations = JSON.parse(localStorage.getItem('deepseek_multi_bubble_conversations') || '[]');
    } catch (e) {
        window.conversations = [];
    }
}

if (!window.currentConversationId && window.conversations.length > 0) {
    window.currentConversationId = window.conversations[0].id;
}

// 测试后端连接
async function testBackendConnection() {
    try {
        const response = await fetch('http://localhost:8001/api/qa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: '测试连接',
                system_prompt: '',
                conversation_history: []
            })
        });
        
        if (response.ok) {
            console.log('✅ 后端连接正常');
            return true;
        } else {
            console.error('❌ 后端连接失败:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ 后端连接测试失败:', error);
        return false;
    }
}

// 核心发送消息函数
async function sendMessageToBackend(messageText = null) {
    console.log('🚀 开始发送消息...');
    
    if (window.isStreaming) {
        console.log('⚠️ 正在发送中，请稍候');
        return;
    }
    
    // 获取消息内容
    const chatInput = document.getElementById('chatInput');
    const message = messageText || (chatInput ? chatInput.value.trim() : '');
    
    if (!message) {
        console.log('⚠️ 消息为空');
        return;
    }
    
    console.log('📝 发送消息:', message);
    
    // 清空输入框
    if (chatInput) {
        chatInput.value = '';
    }
    
    // 设置发送状态
    window.isStreaming = true;
    
    // 显示用户消息
    if (window.displayMessage) {
        window.displayMessage(message, 'user');
    }
    
    // 显示加载状态
    if (window.showLoading) {
        window.showLoading();
    }
    
    try {
        // 准备对话历史
        let conversationHistory = [];
        if (window.conversations && window.currentConversationId) {
            const currentConv = window.conversations.find(c => c.id === window.currentConversationId);
            if (currentConv && currentConv.messages) {
                // 只保留最近3轮对话作为上下文，避免内容混杂
                const recentMessages = currentConv.messages.slice(-6); // 最多6条消息（3轮对话）
                conversationHistory = recentMessages;
            }
        }
        
        // 构建请求数据
        const requestData = {
            message: message,
            system_prompt: window.SYSTEM_PROMPT || '你是一个智能AI助手，请专注回答当前用户的问题，提供准确、简洁的回答。',
            conversation_history: conversationHistory
        };
        
        console.log('📤 发送请求到后端:', requestData);
        
        // 发送流式请求
        const response = await fetch('http://localhost:8001/api/qa/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
        
        // 隐藏加载状态
        if (window.hideLoading) {
            window.hideLoading();
        }
        
        // 创建AI消息元素
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="streaming-text"></div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        
        if (chatMessages) {
            chatMessages.appendChild(messageDiv);
        }
        
        const streamingText = messageDiv.querySelector('.streaming-text');
        let fullResponse = '';
        
        // 处理流式响应
        const reader = response.body.getReader();
        
        while (true) {
            const result = await reader.read();
            if (result.done) break;
            
            const chunk = new TextDecoder().decode(result.value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.type === 'triplets' && data.triplets) {
                            // 处理三元组数据
                            console.log('📊 收到三元组数据:', data.triplets);
                            if (window.generateGraphFromTriplets) {
                                try {
                                    window.generateGraphFromTriplets(data.triplets);
                                } catch (e) {
                                    console.error('图形生成失败:', e);
                                }
                            }
                        } else if (data.content !== undefined) {
                            // 处理文本内容
                            fullResponse += data.content;
                            if (streamingText) {
                                streamingText.textContent = fullResponse;
                            }
                            
                            // 滚动到底部
                            if (window.scrollToBottom) {
                                window.scrollToBottom();
                            }
                        }
                    } catch (e) {
                        console.error('解析数据错误:', e);
                    }
                }
            }
        }
        
        console.log('✅ AI回复完成:', fullResponse.length, '字符');
        
        // 渲染Markdown
        if (fullResponse && window.renderMarkdown && streamingText) {
            streamingText.innerHTML = window.renderMarkdown(fullResponse);
        }
        
        // 添加拖拽功能
        if (fullResponse && messageDiv) {
            const messageContent = messageDiv.querySelector('.message-content');
            if (messageContent) {
                messageContent.dataset.originalContent = fullResponse;
                messageContent.draggable = true;
                messageContent.style.cursor = 'grab';
                messageContent.title = '拖拽到右侧生成动态关系图';
                
                // 添加拖拽事件监听器
                if (window.handleDragStart) {
                    messageContent.addEventListener('dragstart', window.handleDragStart);
                }
                if (window.handleDragEnd) {
                    messageContent.addEventListener('dragend', window.handleDragEnd);
                }
                
                console.log('✅ 已为AI消息添加拖拽功能');
            }
        }
        
        // 保存对话历史
        saveConversationHistory(message, fullResponse);
        
    } catch (error) {
        console.error('❌ 发送失败:', error);
        
        if (window.hideLoading) {
            window.hideLoading();
        }
        
        if (window.displayMessage) {
            window.displayMessage('发送失败: ' + error.message, 'assistant');
        }
    } finally {
        window.isStreaming = false;
    }
}

// 保存对话历史
function saveConversationHistory(userMessage, aiResponse) {
    try {
        if (!window.conversations) {
            window.conversations = [];
        }
        
        // 如果没有当前对话，创建一个
        if (!window.currentConversationId || !window.conversations.find(c => c.id === window.currentConversationId)) {
            const newConversation = {
                id: 'conv_' + Date.now(),
                title: userMessage.length > 20 ? userMessage.substring(0, 20) + '...' : userMessage,
                messages: [],
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString()
            };
            window.conversations.unshift(newConversation);
            window.currentConversationId = newConversation.id;
        }
        
        // 添加消息到当前对话
        const conversation = window.conversations.find(c => c.id === window.currentConversationId);
        if (conversation) {
            const timestamp = new Date().toISOString();
            
            conversation.messages.push({
                role: 'user',
                content: userMessage,
                timestamp: timestamp
            });
            
            conversation.messages.push({
                role: 'assistant',
                content: aiResponse,
                timestamp: timestamp
            });
            
            conversation.updatedAt = timestamp;
            
            // 保存到localStorage
            localStorage.setItem('deepseek_multi_bubble_conversations', JSON.stringify(window.conversations));
            
            // 更新对话列表
            if (window.loadConversations) {
                window.loadConversations();
            }
        }
    } catch (e) {
        console.error('保存对话失败:', e);
    }
}

// 绑定事件的函数
function bindEvents() {
    console.log('🔗 绑定发送事件...');
    
    // 绑定发送按钮
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
        // 清除所有旧事件
        sendBtn.onclick = null;
        sendBtn.removeEventListener('click', sendMessageToBackend);
        
        // 添加新事件
        sendBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🖱️ 发送按钮被点击');
            sendMessageToBackend();
        });
        
        console.log('✅ 发送按钮事件已绑定');
    } else {
        console.error('❌ 找不到发送按钮');
    }
    
    // 绑定输入框回车事件
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        // 清除所有旧事件
        chatInput.onkeypress = null;
        chatInput.removeEventListener('keypress', handleKeyPress);
        
        // 添加新事件
        chatInput.addEventListener('keypress', handleKeyPress);
        
        console.log('✅ 输入框回车事件已绑定');
    } else {
        console.error('❌ 找不到输入框');
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        console.log('⌨️ 回车键被按下');
        sendMessageToBackend();
    }
}

// 强制覆盖sendMessage函数
function overrideSendMessage() {
    window.sendMessage = sendMessageToBackend;
    console.log('✅ sendMessage函数已覆盖');
}

// 测试函数
window.testSend = function() {
    console.log('🧪 测试发送功能');
    sendMessageToBackend('测试消息 ' + new Date().toLocaleTimeString());
};

window.fixSend = function() {
    console.log('🔧 修复发送功能');
    bindEvents();
    overrideSendMessage();
    return '✅ 发送功能已修复';
};

// 初始化
function initialize() {
    console.log('🚀 初始化后端适配器...');
    
    // 立即覆盖函数
    overrideSendMessage();
    
    // 绑定事件
    bindEvents();
    
    // 测试后端连接
    testBackendConnection();
    
    console.log('✅ 后端适配器初始化完成');
}

// 立即执行初始化
initialize();

// DOM加载完成后再次确保绑定
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        console.log('📱 DOM加载完成，重新绑定事件');
        bindEvents();
        overrideSendMessage();
    }, 1000);
});

// 再次确保绑定
setTimeout(() => {
    console.log('⏰ 延时绑定事件');
    bindEvents();
    overrideSendMessage();
}, 3000);

console.log('✅ 后端适配器脚本加载完成');
