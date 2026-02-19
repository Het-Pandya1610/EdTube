// navbar.js
document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.getElementById("hamburgerBtn");
  const searchToggle = document.getElementById("searchToggleBtn");
  const voiceBtn = document.getElementById("voiceSearchBtn");
  const searchInput = document.getElementById("searchInput");
  const suggestionsBox = document.getElementById("suggestionsBox");

  hamburger?.addEventListener("click", toggleMenu);
  searchToggle?.addEventListener("click", toggleSearch);
  voiceBtn?.addEventListener("click", openVoiceSearch);
  
  // UPDATED: Load search history from database
  if (searchInput) {
    searchInput.addEventListener("focus", loadSearchHistory);
    searchInput.addEventListener("input", handleSearchInput);
    searchInput.addEventListener("blur", () => {
      setTimeout(() => {
        suggestionsBox.style.display = "none";
      }, 200);
    });
  }

  // Logo click handler
  const logo = document.getElementById("theme-logo");
  if (logo) {
    logo.addEventListener("click", () => {
      window.location.href = "/";
    });
  }

  // Following dropdown
  const toggle = document.querySelector(".following-toggle");
  const list = document.querySelector(".following-list");
  if (toggle && list) {
    toggle.addEventListener("click", function() {
      list.classList.toggle("d-none");
    });
  }
});

const toggle = document.getElementById("pfpToggle");
const menu = document.getElementById("accountDropdown");

toggle.addEventListener("click", () => {
  menu.style.display =
    menu.style.display === "block" ? "none" : "block";
});

window.addEventListener("click", (e) => {
  if (!toggle.contains(e.target) && !menu.contains(e.target)) {
    menu.style.display = "none";
  }
});

// UPDATED: Load search history from database
function loadSearchHistory() {
  const suggestionsBox = document.getElementById("suggestionsBox");
  const searchInput = document.getElementById("searchInput");
  
  if (!searchInput.value) {
    fetch('/get-search-suggestions/')
      .then(response => response.json())
      .then(searches => {
        if (searches.length > 0) {
          suggestionsBox.style.display = "block";
          const isDark = window.isDarkMode ? window.isDarkMode() : document.body.classList.contains('dark-mode');
          const mode = isDark ? 'dark' : 'light';
          suggestionsBox.innerHTML = `
            <div class="suggestions-header">
              <span>Recent searches</span>
              <button class="clear-history-btn" onclick="clearSearchHistory()">
                Clear
              </button>
            </div>
            ${searches.map(query => `
              <div class="suggestion-item" onclick="selectSuggestion('${query}')">
                <img src="/static/assets/history ${mode}.png" alt="History Icon" class="history-icon" style="width: 16px !important; height: 16px !important; object-fit: contain;">
                <span>${query}</span>
                <button class="delete-suggestion" onclick="deleteSearch('${query}', event)">
                  <i class="bi bi-x-lg"></i>
                </button>
              </div>
            `).join('')}
          `;
        }
      })
      .catch(error => console.error('Error loading search history:', error));
  }
}

// UPDATED: Delete single search
function deleteSearch(query, event) {
  event.stopPropagation();
  
  fetch('/delete-search-suggestion/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ query: query })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      loadSearchHistory(); // Reload suggestions
    }
  })
  .catch(error => console.error('Error deleting search:', error));
}

// UPDATED: Clear all search history
function clearSearchHistory() {
  fetch('/clear-search-history/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      document.getElementById("suggestionsBox").style.display = "none";
    }
  })
  .catch(error => console.error('Error clearing history:', error));
}

// Helper to get CSRF token
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

function selectSuggestion(query) {
  document.getElementById("searchInput").value = query;
  document.getElementById("suggestionsBox").style.display = "none";
  // Submit search
  document.querySelector(".search-bar form").submit();
}

function handleSearchInput(e) {
  const query = e.target.value;
  const suggestionsBox = document.getElementById("suggestionsBox");
  
  if (query.length > 1) {
    fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        if (data.length > 0) {
          suggestionsBox.style.display = "block";
          suggestionsBox.innerHTML = data.map(item => `
            <div class="suggestion-item" onclick="selectSuggestion('${item}')">
              <i class="bi bi-search"></i>
              <span>${item}</span>
            </div>
          `).join('');
        } else {
          suggestionsBox.style.display = "none";
        }
      });
  } else {
    loadSearchHistory();
  }
}

function toggleMenu() {
  const nav = document.getElementById('mobileNav');
  const hamburger = document.getElementById('hamburgerBtn');
  
  nav.classList.toggle('active');
  hamburger.classList.toggle('active');

  if (window.innerWidth >= 992) {
    const isNowOpen = nav.classList.contains('active');
    document.body.classList.toggle('nav-open', isNowOpen);
  }
}

function toggleSearch() {
  document.body.classList.toggle('mobile-search-active');
}

/* ================= VOICE SEARCH (unchanged) ================= */
let recognition;
const micOnSound = document.getElementById("micOnSound");
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
    // Submit search automatically
    document.querySelector(".search-bar form").submit();
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

// Mic visualizer (unchanged)
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

  try {
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
  } catch (err) {
    console.error('Microphone error:', err);
  }
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
    ctx.fillStyle = "rgb(0, 207, 255)"; // Your theme color
    ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    x += barWidth + 1;
  }
}