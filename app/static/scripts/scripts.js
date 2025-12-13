// Функция для получения cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Проверяем наличие токена
const token = getCookie('users_access_token');
if (!token) {
    console.warn('User not authenticated. Please login first.');
    // Можно показать сообщение пользователю
    // alert('Please login before connecting to chat');
}

// Используем тот же домен, что и текущая страница
// Это важно! localhost и 127.0.0.1 - разные домены для браузера
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const host = window.location.host; // Используем тот же host (localhost или 127.0.0.1)
const wsUrl = `${protocol}//${host}/ws/chat`;

console.log('Connecting to WebSocket:', wsUrl);
console.log('Current page origin:', window.location.origin);
console.log('Token in cookie:', token ? 'Found' : 'NOT FOUND');

// Создаем WebSocket с правильным URL (используем тот же домен)
var ws = new WebSocket(wsUrl);
var statusDiv = document.getElementById('status');
var messageInput = document.getElementById('messageText');
var sendButton = document.getElementById('sendButton');

ws.onopen = function(event) {
    console.log('WebSocket connected successfully');
    statusDiv.textContent = 'CONNECTED';
    statusDiv.className = 'connected';
    messageInput.disabled = false;
    sendButton.disabled = false;
};

ws.onclose = function(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    statusDiv.textContent = 'DISCONNECTED';
    statusDiv.className = 'disconnected';
    messageInput.disabled = true;
    sendButton.disabled = true;
    
    // Если закрыто из-за аутентификации
    if (event.code === 1008) { // Policy Violation
        console.error('Authentication failed:', event.reason);
        alert('Authentication failed. Please login again.');
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
    statusDiv.textContent = 'Connection error';
    statusDiv.className = 'disconnected';
};

ws.onmessage = function(event) {
    var messages = document.getElementById('messages');
    var message = document.createElement('li');
    message.className = 'received';
    
    try {
        var data = JSON.parse(event.data);
        var content = document.createTextNode(JSON.stringify(data, null, 2));
    } catch (e) {
        var content = document.createTextNode(event.data);
    }
    
    message.appendChild(content);
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
};

function sendMessage(event) {
    var input = document.getElementById("messageText");
    var messageText = input.value.trim();
    if (messageText && ws.readyState === WebSocket.OPEN) {
        var messages = document.getElementById('messages');
        var message = document.createElement('li');
        message.className = 'sent';
        var content = document.createTextNode(messageText);
        message.appendChild(content);
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
        
        var messageData = {"message": messageText};
        ws.send(JSON.stringify(messageData));
        input.value = '';
    }
    event.preventDefault();
}