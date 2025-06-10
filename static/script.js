// Grab UI elements
const startBtn = document.getElementById("startBtn");
const stopBtn  = document.getElementById("stopBtn");
const cmdDisp  = document.getElementById("commandDisplay");
const respArea = document.getElementById("responseArea");
const welcome  = document.getElementById("welcomeMessage").innerText;

// Set up Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;
if (recognition) {
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = false;
}

// Speak via Web Speech Synthesis
function speak(text) {
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'en-US';
  window.speechSynthesis.speak(utter);
}

// Greet on load
window.addEventListener('DOMContentLoaded', () => {
  speak(welcome);
});

// Start / Stop buttons
startBtn.onclick = () => {
  if (!recognition) return alert("SpeechRecognition not supported");
  cmdDisp.innerText = "Listening...";
  startBtn.disabled = true;
  stopBtn.disabled = false;
  recognition.start();
};
stopBtn.onclick = () => {
  recognition.stop();
  startBtn.disabled = false;
  stopBtn.disabled = true;
};

// Recognition events
if (recognition) {
  recognition.onresult = e => {
    const text = Array.from(e.results)
      .map(r => r[0].transcript)
      .join('');
    cmdDisp.innerText = "You said: " + text;
  };
  recognition.onend = () => {
    startBtn.disabled = false;
    stopBtn.disabled = true;
    const spoken = cmdDisp.innerText.replace("You said: ", "").trim();
    if (spoken) sendCommand(spoken);
  };
}

// Send command to Flask
function sendCommand(cmd) {
  fetch('/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({command: cmd})
  })
  .then(r => r.json())
  .then(data => {
    respArea.innerHTML = `<div class="alert alert-info">${data.response}</div>`;
    speak(data.response);
    if (data.url) window.open(data.url, '_blank');
  })
  .catch(err => {
    respArea.innerHTML = `<div class="alert alert-danger">Error: ${err}</div>`;
  });
}
