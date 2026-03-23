function qsGet(name) {
    return new URLSearchParams(window.location.search).get(name);
}

function setChatIdInUrl(chatId) {
    const url = new URL(window.location.href);
    if (chatId === null || chatId === undefined || chatId === "") {
        url.searchParams.delete("chat_id");
    } else {
        url.searchParams.set("chat_id", String(chatId));
    }
    window.history.pushState({}, "", url.toString());
}

function wsUrlForChat(chatId) {
    // Важно: cookies/origin одинаковые, поэтому WS под тем же хостом.
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const base = `${protocol}//${host}/ws/chat`;
    if (chatId === null || chatId === undefined) return base;
    return `${base}?chat_id=${encodeURIComponent(chatId)}`;
}

async function apiJson(path, init) {
    const res = await fetch(path, {
        credentials: "include",
        ...init,
    });

    const data = await res.json().catch(() => null);
    if (!res.ok) {
        const msg = data && data.detail ? data.detail : `HTTP ${res.status}`;
        throw new Error(msg);
    }
    return data;
}

function liCreateMessage(kind, text) {
    const li = document.createElement("li");
    li.className = kind; // sent | received
    li.appendChild(document.createTextNode(text ?? ""));
    return li;
}

const statusDiv = document.getElementById("status");
const messageInput = document.getElementById("messageText");
const sendButton = document.getElementById("sendButton");
const chatForm = document.getElementById("chatForm");
const messagesEl = document.getElementById("messages");

const chatListEl = document.getElementById("chatList");
const sidebarHintEl = document.getElementById("sidebarHint");
const newChatButton = document.getElementById("newChatButton");

let ws = null;
let selectedChatId = null;

function setConnectedUi(connected) {
    statusDiv.textContent = connected ? "CONNECTED" : "DISCONNECTED";
    statusDiv.className = connected ? "connected" : "disconnected";
    messageInput.disabled = !connected;
    sendButton.disabled = !connected;
}

function closeWsIfAny() {
    if (ws) {
        try {
            ws.close();
        } catch (_) {
            // ignore
        }
        ws = null;
    }
}

function clearMessages() {
    messagesEl.innerHTML = "";
}

function renderHistory(messages) {
    clearMessages();
    const list = Array.isArray(messages) ? messages.slice() : [];

    // Старые -> новые
    list.sort((a, b) => (a.id ?? 0) - (b.id ?? 0));

    for (const m of list) {
        const kind = m.is_bot ? "received" : "sent";
        const text = m.context ?? "";
        messagesEl.appendChild(liCreateMessage(kind, text));
    }

    messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function loadChatsList() {
    const payload = await apiJson("/chats/", { method: "GET" });
    const chats = payload.chat_list || [];

    // Сверху вниз: от более нового created_at к более старому
    chats.sort((a, b) => {
        const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
        const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
        return bTime - aTime;
    });

    chatListEl.innerHTML = "";

    for (const chat of chats) {
        const li = document.createElement("li");
        li.className = "chat-item";
        li.dataset.chatId = String(chat.id);

        const row = document.createElement("div");
        row.className = "chat-item-row";

        const titleLink = document.createElement("a");
        titleLink.className = "chat-item-link";
        titleLink.href = "#";
        titleLink.textContent = chat.title || `Chat ${chat.id}`;

        titleLink.addEventListener("click", async (event) => {
            event.preventDefault();
            const nextId = li.dataset.chatId;
            await openChatById(nextId, true);
        });

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "chat-delete-btn";
        deleteBtn.type = "button";
        deleteBtn.textContent = "delete";

        deleteBtn.addEventListener("click", async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const chatIdToDelete = li.dataset.chatId;
            const deletedId = String(chatIdToDelete);
            const wasCurrent = String(selectedChatId) === deletedId;

            const ok = confirm(`Delete chat #${deletedId}?`);
            if (!ok) return;

            await apiJson(`/chats/${encodeURIComponent(chatIdToDelete)}`, {
                method: "DELETE",
            });

            const remainingChats = await loadChatsList();

            if (!remainingChats.length) {
                closeWsIfAny();
                setConnectedUi(false);
                clearMessages();
                sidebarHintEl.textContent = "У вас больше нет чатов.";
                selectedChatId = null;
                return;
            }

            if (wasCurrent) {
                await openChatById(remainingChats[0].id, true);
            } else {
                markActiveChat(selectedChatId);
            }
        });

        row.appendChild(titleLink);
        row.appendChild(deleteBtn);
        li.appendChild(row);

        chatListEl.appendChild(li);
    }

    return chats;
}

function markActiveChat(chatId) {
    const items = chatListEl.querySelectorAll(".chat-item");
    for (const el of items) {
        const isActive = String(el.dataset.chatId) === String(chatId);
        el.classList.toggle("active", isActive);
    }
}

async function loadChatHistory(chatId) {
    const chat = await apiJson(`/chats/${encodeURIComponent(chatId)}`, { method: "GET" });
    renderHistory(chat.messages || []);
}

function connectWs(chatId) {
    return new Promise((resolve) => {
        const url = wsUrlForChat(chatId);
        ws = new WebSocket(url);

        ws.onopen = () => {
            setConnectedUi(true);
            resolve(true);
        };

        ws.onclose = (event) => {
            setConnectedUi(false);
            if (event && event.code === 1008) {
                alert(event.reason || "Authentication failed. Please login again.");
            }
        };

        ws.onerror = (err) => {
            console.error("ws error:", err);
            setConnectedUi(false);
        };

        ws.onmessage = (event) => {
            let data = null;
            try {
                data = JSON.parse(event.data);
            } catch (_) {
                data = null;
            }

            if (!data || !data.message_type) {
                // fallback
                messagesEl.appendChild(liCreateMessage("received", event.data));
                messagesEl.scrollTop = messagesEl.scrollHeight;
                return;
            }

            const mt = data.message_type;
            const text = data.message ?? "";

            if (mt === "assistant" || mt === "welcome") {
                messagesEl.appendChild(liCreateMessage("received", text));
            } else if (mt === "user") {
                messagesEl.appendChild(liCreateMessage("sent", text));
            } else {
                messagesEl.appendChild(liCreateMessage("received", text));
            }

            messagesEl.scrollTop = messagesEl.scrollHeight;
        };
    });
}

async function openChatById(chatId, updateUrl) {
    selectedChatId = String(chatId);
    markActiveChat(selectedChatId);

    if (updateUrl) {
        setChatIdInUrl(selectedChatId);
    }

    closeWsIfAny();
    setConnectedUi(false);

    await loadChatHistory(selectedChatId);
    await connectWs(selectedChatId);
}

newChatButton.addEventListener("click", async () => {
    sidebarHintEl.textContent = "";

    try {
        const created = await apiJson("/chats/", { method: "POST" });
        const newId = created.id;

        // Перерисуем список, чтобы появился новый чат.
        await loadChatsList();

        await openChatById(newId, true);
    } catch (e) {
        console.error(e);
        sidebarHintEl.textContent = String(e.message || e);
    }
});

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const text = (messageInput.value || "").trim();
    if (!text) return;

    // Оптимистично добавляем сообщение пользователя (сервер user обратно не шлёт).
    messagesEl.appendChild(liCreateMessage("sent", text));
    messagesEl.scrollTop = messagesEl.scrollHeight;

    ws.send(JSON.stringify({ message: text }));
    messageInput.value = "";
});

async function init() {
    setConnectedUi(false);
    sidebarHintEl.textContent = "";
    clearMessages();

    const chats = await loadChatsList();
    if (!chats.length) {
        sidebarHintEl.textContent = "У вас пока нет чатов. Нажмите New chat.";
        return;
    }

    const chatIdFromUrl = qsGet("chat_id");
    const initialChatId = chatIdFromUrl ? chatIdFromUrl : chats[0].id;

    // Если chatId в URL не совпадает с существующими — fallback на первый.
    const exists = chats.some((c) => String(c.id) === String(initialChatId));
    const safeChatId = exists ? initialChatId : chats[0].id;

    await openChatById(safeChatId, false);
}

init().catch((e) => {
    console.error("init error:", e);
    sidebarHintEl.textContent = String(e.message || e);
});