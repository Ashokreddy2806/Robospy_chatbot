/*
// ==== DOM ELEMENTS ====
const chatoutput = document.getElementById("chat_output");
const userinput = document.getElementById("user_input");
const sendbutton = document.getElementById("send_button");
const inputform = document.getElementById("input_form");
const modelmarker = document.getElementById("model_marker");
const menu_output = document.getElementById("menu_output");

// ==== GLOBAL STATE ====
let chatHistory = [];
let isStreaming = false;

let promptFiles = [];
let selectedModel = "";
let selectedPrompt = "";
let selectedLanguage = "";
let modelSelected = false;
let promptSelected = false;

// ==== OPTIONAL ====
let promptSelection = false;

// ==== TTS ====
const synth = window.speechSynthesis;
let speaking = false;
let ttsQueue = [];
let ttsEnabled = false;

// ==== UTILS ====
function getTimestamp() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function highlightSelection(text) {
  chatoutput.innerHTML = "";
  const highlight = document.createElement("div");
  highlight.className = "chat-line system";
  highlight.innerHTML = `<span style="color: #00ff00;">>>> ${text} SELECTED</span><span class="typing"><span>.</span><span>.</span><span>.</span></span>`;
  chatoutput.appendChild(highlight);
}

// ==== PROMPT LOADING ====
async function loadPromptOptions() {
  const res = await fetch("/list_prompts/");
  const data = await res.json();

  const fileNameToLabel = {
    "promptsheet_robopsy_eng.txt": "ENGLISH",
    "promptsheet_robopsy_ger.txt": "GERMAN"
  };

  promptFiles = data.files.map(file => ({
    filename: file,
    label: fileNameToLabel[file] || file
  }));
}

// ==== UI INSTRUCTIONS ====
function showPromptSelectionInstructions() {
  chatoutput.innerHTML = "";
  const instructions = document.createElement("div");
  instructions.className = "chat-line system";
  instructions.innerHTML = `
    Model <strong>${selectedModel}</strong> selected.<br>
    Now choose a LANGUAGE:<br>
    ${promptFiles.map((f, i) => `>>> ${i + 1} ${f.label}`).join("<br>")}
  `;
  chatoutput.appendChild(instructions);
}

function showModelSelectionInstructions() {
  chatoutput.innerHTML = "";
  const instructions = document.createElement("div");
  instructions.className = "chat-line system";
  // still not loaded dynamically, could be done via config file for final App
  instructions.innerHTML = `
    Choose the Large Language Model you want to use:<br>
    >>> 1 openai/gpt-4o
    >>> 2 openai/gpt-4o-mini
    >>> 3 mistral/mistral-large-latest
    >>> 4 deepseek/deepseek-chat
    >>> 5 groq/llama-3.1-8b-instant
  `;
  chatoutput.appendChild(instructions);
}

// ==== MESSAGE SENDING ====
async function sendMessage(message) {
  if (isStreaming) return;
  isStreaming = true;

  const response = await fetch("/answer/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history: chatHistory, model: selectedModel, prompt: selectedPrompt }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let output = "";
  let { value, done } = await reader.read();

  if (message.trim()) {
    chatHistory.push({ role: "user", content: message });

    const userDiv = document.createElement("div");
    userDiv.className = "chat-line user";
    userDiv.innerHTML = `<strong>USER:</strong> ${message}`;
    chatoutput.appendChild(userDiv);
    chatoutput.appendChild(document.createElement("br"));
    chatoutput.scrollTop = chatoutput.scrollHeight;
  }

  const assistantLine = document.createElement("div");
  assistantLine.className = "chat-line assistant";
  assistantLine.innerHTML = `<strong>ROBOPSY:</strong> `;
  chatoutput.appendChild(assistantLine);

  while (!done) {
    const chunk = decoder.decode(value, { stream: true });

    let buffer = "";
    for (let char of chunk) {
      output += char;
      buffer += char;
      assistantLine.innerHTML += char;
      chatoutput.scrollTop = chatoutput.scrollHeight;

      if (buffer.endsWith(".") || buffer.endsWith("?") || buffer.length > 100) {
        ttsQueue.push(buffer.trim());
        if (!speaking) speakText(ttsQueue.shift());
        buffer = "";
      }

      await new Promise(r => requestAnimationFrame(r));
    }

    ({ value, done } = await reader.read());
  }

  chatoutput.appendChild(document.createElement("br"));
  chatHistory.push({ role: "assistant", content: output });
  isStreaming = false;
}

// ==== TTS SPEAK ====
function speakText(text) {
  if (!ttsEnabled || !text.trim()) return;

  function speak() {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1;
    utterance.pitch = 1;

    const voices = synth.getVoices();
    const matchingVoice = voices.find(voice => voice.lang === 'en-US');
    if (matchingVoice) utterance.voice = matchingVoice;

    speaking = true;
    utterance.onend = () => {
      speaking = false;
      if (ttsQueue.length > 0) speakText(ttsQueue.shift());
    };

    synth.speak(utterance);
  }

  // If voices are not loaded yet, wait and retry
  if (synth.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = () => {
      speak();
    };
  } else {
    speak();
  }
}

// ==== EVENT LISTENERS ====
window.onload = async function () {
  await loadPromptOptions();
  showModelSelectionInstructions();
  document.addEventListener("keydown", handleKeyPress);
};
async function handleKeyPress(event) {
  const key = event.key;

  if (!modelSelected) {
    const modelMap = {
      l: "openai/gpt-4o",
      k: "openai/gpt-4o-mini",
      j: "mistral/mistral-large-latest",
      h: "deepseek/deepseek-chat",
      g: "groq/llama3.1-8b"
    };

    if (key in modelMap) {
      selectedModel = modelMap[key];
      modelSelected = true;
      modelmarker.innerHTML = selectedModel;
      highlightSelection(`MODEL: ${selectedModel}`);
      await new Promise(r => setTimeout(r, 1000));
      if (promptSelection) {
        showPromptSelectionInstructions(); // Now select prompt next
      } else {
        promptSelected = true;
        selectedPrompt = promptFiles[0]["filename"];
        console.log(`Prompt Auto selected: ${selectedPrompt}`)
        chatoutput.innerHTML = "";
        menu_output.innerHTML = "OUTPUT";
        sendMessage(""); // Start conversation
      }
    }
    return; // Always return after handling model selection
  }

  if (!promptSelected && promptSelection) {
    const keyMap = { l: 1, k: 2, j: 3, h: 4, g: 5 }; // adjust as needed

    if (key in keyMap && promptFiles[keyMap[key] - 1]) {
      const prompt = promptFiles[keyMap[key] - 1];
      selectedPrompt = prompt.filename;
      promptSelected = true;
      selectedLanguage = prompt.label;
      highlightSelection(`LANGUAGE: ${selectedLanguage}`);
      await new Promise(r => setTimeout(r, 1000));

      chatoutput.innerHTML = "";
      menu_output.innerHTML = "OUTPUT";
      sendMessage(""); // Start conversation
    }
    return; // Always return after handling prompt selection
  }

  // Message handling - only reached if both model and prompt are selected
  if (isStreaming) return;

  if (['l', 'k', 'j', 'h'].includes(key)) {
    event.preventDefault();
    userinput.value = key;
    sendMessage({ l: '1', k: '2', j: '3', h: '4' }[key]);
  } else if (key === 'g') {
    // Save and reset
    const messages = [`=== MODEL USED: ${selectedModel} === \n=== LANGUAGE: ${selectedLanguage} ===\n`];

    document.querySelectorAll('.chat-line').forEach(div => {
      const role = div.classList.contains("user") ? "USER" : "ROBOPSY";
      const content = div.textContent.replace(/^USER: |^ROBOPSY: /, "").trim();
      messages.push(`${role}: ${content}`);
    });

    const joinedText = messages.join("\n\n");

    fetch("/reset_chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ html: joinedText })
    }).then(() => {
      chatoutput.innerHTML = "";
      window.location.replace("http://127.0.0.1:8000/");
    });
  }
}

// ==== BUTTON SEND HANDLER ====
sendbutton.addEventListener("click", async (e) => {
  e.preventDefault();
  const message = userinput.value.trim();
  if (!message) return;
  userinput.value = "";
  await sendMessage(message);
});


//Ashok : Adding image generation and reset game functionality

// ==== IMAGE GENERATION ====
// ...existing code...

function generateSceneImage(prompt, imageUrl) {
    fetch('/generate_image/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `prompt=${encodeURIComponent(prompt)}&image_url=${encodeURIComponent(imageUrl)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.image) {
            // Display image in a div with id="scene-image"
            document.getElementById('scene-image').src = 'data:image/png;base64,' + data.image;
        } else if (data.error) {
            alert(data.error);
        }
    });
}

function resetGame() {
    fetch('/reset_game/', {method: 'POST'})
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('scene-image').src = '';
        }
    });
}

// Example usage after each scene:
// generateSceneImage("Add a hat to the cat", "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png");

// Example usage when resetting:
// resetGame();
*/






// static/js/script.js
document.addEventListener('DOMContentLoaded', function () {
    const chatoutput = document.getElementById("chat_output");
    const userinput = document.getElementById("user_input");
    const modelmarker = document.getElementById("model_marker");
    const menu_output = document.getElementById("menu_output");

    let chatHistory = [];
    let modelSelected = false;
    let selectedModel = "";
    let selectedPrompt = "";
    let isTyping = false; // Prevents user input while the bot is "typing"

    function showModelSelectionInstructions() {
        chatoutput.innerHTML = "";
        const instructions = document.createElement("div");
        instructions.className = "chat-line system";
        instructions.innerHTML = `
            Choose the Large Language Model you want to use:<br>
            >>> 1 openai/gpt-4o<br>
            >>> 2 openai/gpt-4o-mini<br>
            >>> 3 mistral/mistral-large-latest<br>
            >>> 4 deepseek/deepseek-chat<br>
            >>> 5 groq/llama-3.1-8b-instant
        `;
        chatoutput.appendChild(instructions);
    }

    function highlightSelection(text) {
        chatoutput.innerHTML = "";
        const highlight = document.createElement("div");
        highlight.className = "chat-line system";
        highlight.innerHTML = `<span style="color: #00ff00;">>>> ${text} SELECTED</span><span class="typing"><span>.</span><span>.</span><span>.</span></span>`;
        chatoutput.appendChild(highlight);
    }

    // --- NEW displayMessage function that renders HTML and simulates line-by-line output ---
    function displayMessage(sender, message) {
        const messageContainer = document.createElement("div");
        messageContainer.className = `chat-line ${sender.toLowerCase()}`;
        
        // ** JAVASCRIPT CSS OVERRIDE **
        // This forces the browser to render HTML tags correctly, ignoring the CSS file.
        messageContainer.style.whiteSpace = 'normal';

        messageContainer.innerHTML = `<strong>${sender}:</strong> `;
        chatoutput.appendChild(messageContainer);
        
        const textSpan = document.createElement('span');
        messageContainer.appendChild(textSpan);

        if (sender.toLowerCase() === 'robopsy') {
            isTyping = true;
            // Split the message into paragraphs (or lines separated by double newlines)
            const lines = message.split(/\n\s*\n/);
            let lineIndex = 0;

            function showNextLine() {
                if (lineIndex < lines.length) {
                    const line = lines[lineIndex];
                    if (line.trim() !== '') {
                        // Convert markdown for the current line to HTML and add it
                        textSpan.innerHTML += marked.parse(line);
                        chatoutput.scrollTop = chatoutput.scrollHeight;
                    }
                    lineIndex++;
                    // Wait before showing the next line to create the effect
                    setTimeout(showNextLine, 400); // Adjust delay in milliseconds
                } else {
                    isTyping = false; // Finished displaying
                    chatoutput.appendChild(document.createElement("br"));
                }
            }
            showNextLine();

        } else {
            // For user and system messages, display instantly
            textSpan.innerHTML = marked.parse(message);
            chatoutput.scrollTop = chatoutput.scrollHeight;
            chatoutput.appendChild(document.createElement("br"));
        }
    }

    async function sendMessage(message) {
        if (isTyping) return;

        if (message.trim()) {
            displayMessage('USER', message);
            chatHistory.push({ role: 'user', content: message });
        }

        try {
            const response = await fetch("/answer/", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    message: message,
                    history: chatHistory,
                    model: selectedModel,
                    prompt: selectedPrompt
                }),
            });

            const data = await response.json();

            if (data.error) {
                displayMessage('ERROR', data.error);
            } else {
                const botMessage = data.response;
                displayMessage('ROBOPSY', botMessage);
                chatHistory.push({ role: 'assistant', content: botMessage });
            }
        } catch (error) {
            console.error("Error sending message:", error);
            displayMessage('ERROR', 'Failed to get response from server.');
        }
    }

    async function handleKeyPress(event) {
        if (isTyping) return;
        const key = event.key;

        if (!modelSelected) {
            const modelMap = {
                '1': "openai/gpt-4o",
                '2': "openai/gpt-4o-mini",
                '3': "mistral/mistral-large-latest",
                '4': "deepseek/deepseek-chat",
                '5': "groq/llama-3.1-8b-instant",
            };

            if (key in modelMap) {
                selectedModel = modelMap[key];
                modelSelected = true;
                if(modelmarker) modelmarker.innerHTML = selectedModel;
                highlightSelection(`MODEL: ${selectedModel}`);
                await new Promise(r => setTimeout(r, 1000));
                
                selectedPrompt = "promptsheet_robopsy_eng.txt"; 
                chatoutput.innerHTML = "";
                if(menu_output) menu_output.innerHTML = "OUTPUT";
                sendMessage("");
            }
            return;
        }
        
        if (['1', '2', '3', '4'].includes(key)) {
            event.preventDefault();
            if(userinput) userinput.value = "";
            sendMessage(key);
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    window.onload = function () {
        showModelSelectionInstructions();
        document.addEventListener("keydown", handleKeyPress);
    };
});