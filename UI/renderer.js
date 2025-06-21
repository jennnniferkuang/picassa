const messages = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");

// Backend URL - adjust this to match your Flask server
const BACKEND_URL = 'http://localhost:5000';

function addMessage(text, sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  messageElement.textContent = text;
  messages.appendChild(messageElement);
  messages.scrollTop = messages.scrollHeight;
  return messageElement;
}

function addStreamingMessage(sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  messageElement.textContent = "";
  messages.appendChild(messageElement);
  messages.scrollTop = messages.scrollHeight;
  return messageElement;
}

async function analyzeLatestImage() {
  try {
    // Show analyzing message
    const analyzingMsg = addMessage("Analyzing your latest drawing...", "bot");
    
    // Call the backend endpoint
    const response = await fetch(`${BACKEND_URL}/critique/latest/stream`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Create streaming message
    const streamingMsg = addStreamingMessage("bot");
    
    // Read the streaming response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.error) {
              streamingMsg.textContent = `Error: ${data.error}`;
              break;
            } else if (data.content) {
              streamingMsg.textContent += data.content;
              messages.scrollTop = messages.scrollHeight;
            } else if (data.done) {
              break;
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
    
    // Remove the analyzing message
    analyzingMsg.remove();
    
  } catch (error) {
    console.error('Error:', error);
    addMessage(`Error: ${error.message}`, "bot");
  }
}

function handleSend() {
  const text = messageInput.value.trim();
  if (text) {
    addMessage(text, "user");
    messageInput.value = "";
    
    // Trigger the analyze function
    analyzeLatestImage();
  }
}

sendButton.addEventListener("click", handleSend);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleSend();
  }
}); 