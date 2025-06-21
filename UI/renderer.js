const messages = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

const { ipcRenderer } = require('electron');

document.getElementById("close-btn").addEventListener("click", () => {
  ipcRenderer.send("app-close");
});

function addMessage(text, sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  messageElement.textContent = text;
  messages.appendChild(messageElement);
  messages.scrollTop = messages.scrollHeight;
}

function handleSend() {
  const text = messageInput.value.trim();
  if (text) {
    addMessage(text, "user");
    messageInput.value = "";

    setTimeout(() => {
      addMessage("I am a bot, how can I help you?", "bot");
    }, 1000);
  }
}

sendButton.addEventListener("click", handleSend);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleSend();
  }
}); 