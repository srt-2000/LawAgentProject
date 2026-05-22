/** WebSocket close code: policy violation (auth), matches backend WebSocketException. */
const WS_CLOSE_POLICY_VIOLATION = 1008;

/** Serialized refresh to avoid rotating refresh twice (backend revokes old refresh). */
let refreshInFlight = null;

/** Skip reactive reconnect when closing the socket on purpose (switch chat / unload). */
let intentionalWsClose = false;

/**
 * Rotate access/refresh cookies via POST /user/refresh.
 *
 * @returns {Promise<void>}
 */
async function refreshSession() {
    if (refreshInFlight) {
        await refreshInFlight;
        return;
    }
    refreshInFlight = (async () => {
        const res = await fetch("/user/refresh", {
            method: "POST",
            credentials: "include",
        });
        if (!res.ok) {
            window.location.href = "/login";
            throw new Error("Session expired. Redirecting to login.");
        }
        await res.json().catch(() => null);
    })();
    try {
        await refreshInFlight;
    } finally {
        refreshInFlight = null;
    }
}

/**
 * JSON fetch with credentials; on 401, refresh once and retry the same request.
 *
 * @param {string} path
 * @param {RequestInit} [init]
 * @param {boolean} [afterRefresh]
 * @returns {Promise<any>}
 */
async function apiJson(path, init = {}, afterRefresh = false) {
    const res = await fetch(path, {
        credentials: "include",
        ...init,
    });

    const data = await res.json().catch(() => null);

    if (res.status === 401 && path !== "/user/refresh" && !afterRefresh) {
        await refreshSession();
        return apiJson(path, init, true);
    }

    if (!res.ok) {
        let msg = `HTTP ${res.status}`;
        if (data && data.detail !== undefined) {
            msg =
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail);
        }
        throw new Error(msg);
    }
    return data;
}

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
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const base = `${protocol}//${host}/ws/chat/`;
    if (chatId === null || chatId === undefined) return base;
    return `${base}?chat_id=${encodeURIComponent(chatId)}`;
}

function liCreateMessage(kind, text) {
    const li = document.createElement("li");
    li.className = kind;
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

/**
 * Show reconnecting state while refreshing session before WS retry.
 *
 * @param {boolean} active
 */
function setReconnectingUi(active) {
    if (active) {
        statusDiv.textContent = "REFRESHING SESSION…";
        statusDiv.className = "reconnecting";
        messageInput.disabled = true;
        sendButton.disabled = true;
    } else {
        setConnectedUi(false);
    }
}

function closeWsIfAny() {
    if (!ws) return;
    intentionalWsClose = true;
    try {
        ws.close();
    } catch (_) {
        // ignore
    }
    ws = null;
}

function clearMessages() {
    messagesEl.innerHTML = "";
}

function renderHistory(messages) {
    clearMessages();
    const list = Array.isArray(messages) ? messages.slice() : [];

    list.sort((a, b) => (a.id ?? 0) - (b.id ?? 0));

    for (const m of list) {
        const kind = m.is_bot ? "received" : "sent";
        const text = m.context ?? "";
        messagesEl.appendChild(liCreateMessage(kind, text));
    }

    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function attachWsMessageHandler(socket) {
    socket.onmessage = (event) => {
        let data = null;
        try {
            data = JSON.parse(event.data);
        } catch (_) {
            data = null;
        }

        if (!data || !data.message_type) {
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
}

/**
 * Wait for WebSocket open or fail; used for reactive auth refresh on 1008.
 *
 * @param {string | number} chatId
 * @returns {Promise<void>}
 */
function waitForWebSocketOpened(chatId) {
    const url = wsUrlForChat(chatId);
    const socket = new WebSocket(url);
    ws = socket;

    return new Promise((resolve, reject) => {
        let opened = false;

        socket.onopen = () => {
            opened = true;
            setConnectedUi(true);
            resolve(undefined);
        };

        attachWsMessageHandler(socket);

        socket.onerror = () => {
            console.error("WebSocket error");
            if (!opened) {
                setConnectedUi(false);
            }
        };

        socket.onclose = (event) => {
            setConnectedUi(false);
            if (intentionalWsClose) {
                intentionalWsClose = false;
                return;
            }
            if (!opened) {
                const err = new Error(event.reason || `WebSocket closed (${event.code})`);
                err.wsCloseCode = event.code;
                reject(err);
            }
        };
    });
}

/**
 * Open WebSocket for chat. On 1008 (auth), refresh session once and retry (reactive path).
 *
 * @param {string | number} chatId
 * @param {boolean} [allowAuthRefreshRetry]
 * @returns {Promise<void>}
 */
async function connectWs(chatId, allowAuthRefreshRetry = true) {
    intentionalWsClose = false;
    setConnectedUi(false);

    try {
        await waitForWebSocketOpened(chatId);
    } catch (err) {
        if (
            allowAuthRefreshRetry &&
            err &&
            typeof err.wsCloseCode === "number" &&
            err.wsCloseCode === WS_CLOSE_POLICY_VIOLATION
        ) {
            setReconnectingUi(true);
            try {
                await refreshSession();
            } finally {
                setReconnectingUi(false);
            }
            await connectWs(chatId, false);
            return;
        }
        throw err;
    }
}

async function loadChatsList() {
    const payload = await apiJson("/chats/", { method: "GET" });
    const chats = payload.chat_list || [];

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
                sidebarHintEl.textContent = "You don't have any chats.";
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
        sidebarHintEl.textContent = "You have no chats yet. Click New chat.";
        return;
    }

    const chatIdFromUrl = qsGet("chat_id");
    const initialChatId = chatIdFromUrl ? chatIdFromUrl : chats[0].id;

    const exists = chats.some((c) => String(c.id) === String(initialChatId));
    const safeChatId = exists ? initialChatId : chats[0].id;

    await openChatById(safeChatId, false);
}

init().catch((e) => {
    console.error("init error:", e);
    sidebarHintEl.textContent = String(e.message || e);
});

const logoutTopBtn = document.getElementById("logoutTopBtn");
if (logoutTopBtn) {
    logoutTopBtn.addEventListener("click", async () => {
        try {
            await fetch("/user/logout", {
                method: "POST",
                credentials: "include",
            });
        } finally {
            window.location.href = "/login";
        }
    });
}
