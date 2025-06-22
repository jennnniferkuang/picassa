const messages = document.getElementById("messages");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const closeIcon = document.getElementById("close-icon");
const blankContainer = document.getElementById("blank-container");

// Backend URL - adjust this to match your Flask server
const BACKEND_URL = 'http://localhost:5001';

// Close app functionality
closeIcon.addEventListener("click", () => {
  window.electronAPI.closeApp();
});

/**
 * Parses a complete string with markdown and converts it to HTML.
 * @param {string} text - The text to parse.
 * @returns {string} - HTML string.
 */
function parseMarkdown(text) {
  // Headers (h1, h2, h3)
  text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');

  // Bold
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');

  // Italic
  text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
  text = text.replace(/_(.*?)_/g, '<em>$1</em>');
  
  // Inline code
  text = text.replace(/`(.*?)`/g, '<code>$1</code>');

  // New lines
  text = text.replace(/\n/g, '<br>');

  return text;
}

function addMessage(text, sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  // Use innerHTML to render markdown
  messageElement.innerHTML = parseMarkdown(text); 
  messages.appendChild(messageElement);
  messages.scrollTop = messages.scrollHeight;
  return messageElement;
}

function addStreamingMessage(sender) {
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", sender);
  messageElement.innerHTML = ""; // Start with empty innerHTML
  messages.appendChild(messageElement);
  messages.scrollTop = messages.scrollHeight;
  return messageElement;
}

async function analyzeLatestImage() {
  try {
    const analyzingMsg = addMessage("Analyzing your latest drawing...", "bot");
    
    const response = await fetch(`${BACKEND_URL}/critique/latest/stream`);
    
    if (!response.ok) {
      const err = await response.json();
      throw new Error(`Error ${response.status}: ${err.error.message}`);
    }
    
    const streamingMsg = addStreamingMessage("bot");
    let currentText = "";
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.error) {
              streamingMsg.innerHTML = parseMarkdown(`**Error:** ${data.error}`);
              return;
            } else if (data.content) {
              currentText += data.content;
              // For streaming, we just update the text content directly for performance
              // and to avoid layout shifts. We'll parse markdown at the end.
              streamingMsg.innerHTML = parseMarkdown(currentText); // Live parsing
              messages.scrollTop = messages.scrollHeight;
            } else if (data.done) {
              // Final parse when streaming is complete
              streamingMsg.innerHTML = parseMarkdown(currentText);
              analyzingMsg.remove();
              return; // Exit loop
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, "Line:", line);
          }
        }
      }

      if (done) {
        // Final parse in case the stream ends without a 'done' message
        streamingMsg.innerHTML = parseMarkdown(currentText);
        analyzingMsg.remove();
        break;
      }
    }
    
  } catch (error) {
    console.error('Error:', error);
    addMessage(`**Error:** ${error.message}`, "bot");
  }
}

function handleSend() {
  const text = messageInput.value.trim();
  if (text) {
    addMessage(text, "user");
    messageInput.value = "";
    analyzeLatestImage();
  } else {
    // If no text, just analyze
    analyzeLatestImage();
  }
}

sendButton.addEventListener("click", handleSend);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleSend();
  }
}); 

blankContainer.addEventListener("click", async () => {
  const pngFiles = await window.electronAPI.selectDirectory();
  if (pngFiles.length === 0) {
    addMessage("No PNG files found in the selected directory.", "bot");
    return;
  }

  addMessage(`Found ${pngFiles.length} PNG files:`, "bot");
  pngFiles.forEach(file => {
    addMessage(`${file}`, "bot");
  });

  // You can also pass the file list to the backend if needed
});