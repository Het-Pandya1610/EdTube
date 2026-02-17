document.addEventListener("DOMContentLoaded", () => {

  const hamburger = document.getElementById("hamburgerBtn");
  const searchToggle = document.getElementById("searchToggleBtn");
  const voiceBtn = document.getElementById("voiceSearchBtn");

  hamburger?.addEventListener("click", toggleMenu);
  searchToggle?.addEventListener("click", toggleSearch);
  voiceBtn?.addEventListener("click", openVoiceSearch);

});

document.addEventListener("DOMContentLoaded", () => {
  const logo = document.getElementById("theme-logo");

  if (logo) {
    logo.addEventListener("click", () => {
      window.location.href = "/";
    });
  }
});


function toggleMenu() {
  const nav = document.getElementById('mobileNav');
  const hamburger = document.getElementById('hamburgerBtn');
  
  // Toggle the 'active' class to trigger the CSS transition
  nav.classList.toggle('active');
  hamburger.classList.toggle('active');

  // Logic for shifting page content if on desktop
  if (window.innerWidth >= 992) {
    const isNowOpen = nav.classList.contains('active');
    document.body.classList.toggle('nav-open', isNowOpen);
  }
}

document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.querySelector(".following-toggle");
    const list = document.querySelector(".following-list");

    if (toggle && list) {
        toggle.addEventListener("click", function() {
            list.classList.toggle("d-none");
        });
    }
});

function toggleSearch() {
  document.body.classList.toggle('mobile-search-active');
}

/* ================= VOICE SEARCH ================= */

let recognition;
const micOnSound  = document.getElementById("micOnSound");
const micOffSound = document.getElementById("micOffSound");
const micErrorSound = document.getElementById("micErrorSound");

function playSound(audio) {
  audio.currentTime = 0;
  audio.play().catch(() => {});
}

function openVoiceSearch() {
  playSound(micOnSound);

  const overlay = document.getElementById("voiceOverlay");
  const input = document.querySelector(".search-bar input");

  overlay.classList.remove("d-none");

  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
    playSound(micErrorSound);
    return;
  }

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.interimResults = false;

  recognition.start();

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    closeVoiceSearch();
  };

  recognition.onerror = () => {
    playSound(micErrorSound);
  };

  recognition.onend = () => {
    playSound(micOffSound);
  };
}

function closeVoiceSearch() {
  document.getElementById("voiceOverlay").classList.add("d-none");
  if (recognition) recognition.stop();
}

document.getElementById("voiceOverlay")?.addEventListener("click", (e) => {
  if (e.target.id === "voiceOverlay") {
    playSound(micOffSound);
    closeVoiceSearch();
  }
});

/* ================= MIC VISUALIZER ================= */

const voiceMic = document.getElementById("voiceMic");
const canvas = document.getElementById("voiceCanvas");
const ctx = canvas?.getContext("2d");

let audioContext, analyser, dataArray, source;
let isListening = false;

voiceMic && (voiceMic.onclick = async () => {
  if (isListening) {
    audioContext.close();
    canvas.style.display = "none";
    isListening = false;
    return;
  }

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

  audioContext = new AudioContext();
  analyser = audioContext.createAnalyser();
  source = audioContext.createMediaStreamSource(stream);

  source.connect(analyser);
  analyser.fftSize = 256;

  dataArray = new Uint8Array(analyser.frequencyBinCount);

  canvas.width = 300;
  canvas.height = 80;
  canvas.style.display = "block";
  isListening = true;

  draw();
});

function draw() {
  if (!isListening) return;

  requestAnimationFrame(draw);
  analyser.getByteFrequencyData(dataArray);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const barWidth = canvas.width / dataArray.length;
  let x = 0;

  for (let i = 0; i < dataArray.length; i++) {
    const barHeight = dataArray[i] / 2;
    ctx.fillStyle = "rgb(0,0,255)";
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    x += barWidth + 1;
  }
}
