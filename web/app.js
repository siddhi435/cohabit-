const setupForm = document.querySelector("#setupForm");
const prevStepButton = document.querySelector("#prevStep");
const nextStepButton = document.querySelector("#nextStep");
const progressFill = document.querySelector("#progressFill");
const progressPercent = document.querySelector("#progressPercent");
const wizardStepper = document.querySelector("#wizardStepper");
const wizardSteps = Array.from(document.querySelectorAll(".wizard-step"));
const aiScreen = document.querySelector("#aiScreen");
const resultsPanel = document.querySelector("#resultsPanel");
const profileCard = document.querySelector("#profileCard");
const likedGrid = document.querySelector("#likedGrid");
const savedGrid = document.querySelector("#savedGrid");
const matchesGrid = document.querySelector("#matchesGrid");
const matchesTitle = document.querySelector("#matchesTitle");
const matchCount = document.querySelector("#matchCount");
const likedCount = document.querySelector("#likedCount");
const savedCount = document.querySelector("#savedCount");
const heroMatchesFound = document.querySelector("#heroMatchesFound");
const heroLikedCount = document.querySelector("#heroLikedCount");
const heroSavedCount = document.querySelector("#heroSavedCount");
const heroAverageCompatibility = document.querySelector("#heroAverageCompatibility");
const heroPanel = document.querySelector("#heroPanel");
const wizardPanel = document.querySelector(".wizard-panel");
const contentPanel = document.querySelector("#contentPanel");
const navItems = Array.from(document.querySelectorAll(".nav-item"));
const aiProgress = document.querySelector("#aiProgress");
const energySlider = setupForm.querySelector('input[name="social_energy_rating"]');
const energyValueLabel = document.querySelector("#energyValue");
let currentUserId = 0;
let currentMatches = [];
let likedMatches = [];
let savedMatches = [];
let activeStep = 0;

// --- Phone OTP login state ---
const loginPhoneLink = document.getElementById('loginPhone');
const phoneModal = document.getElementById('phoneLoginModal');
const sendOtpBtn = () => document.getElementById('sendOtpBtn');

function openPhoneModal() {
  const m = document.getElementById('phoneLoginModal');
  if (!m) return;
  m.classList.remove('hidden');
  m.setAttribute('aria-hidden','false');
  const phoneInput = document.getElementById('phoneNumber');
  if (phoneInput && !phoneInput.value) {
    phoneInput.focus();
  }
}

function closePhoneModal() {
  const m = document.getElementById('phoneLoginModal');
  if (!m) return;
  m.classList.add('hidden');
  m.setAttribute('aria-hidden','true');
  const phoneStep = document.getElementById('phoneStep');
  const otpStep = document.getElementById('otpStep');
  if (phoneStep) phoneStep.style.display = 'block';
  if (otpStep) otpStep.style.display = 'none';
  const phoneInput = document.getElementById('phoneNumber');
  const otpInput = document.getElementById('otpInput');
  if (phoneInput) phoneInput.value = '';
  if (otpInput) otpInput.value = '';
  const demoOtp = document.getElementById('demoOtp');
  const demoOtpCode = document.getElementById('demoOtpCode');
  if (demoOtp) demoOtp.style.display = 'none';
  if (demoOtpCode) demoOtpCode.textContent = '000000';
}

function updateDemoOtp(code) {
  const demoOtp = document.getElementById('demoOtp');
  const demoOtpCode = document.getElementById('demoOtpCode');
  if (demoOtp && demoOtpCode) {
    demoOtpCode.textContent = code;
    demoOtp.style.display = 'block';
  }
}

function maskPhone(p) {
  // simple mask: keep last 4
  return p ? p.replace(/\s+/g,'').replace(/(.{0,})(\d{4})$/, '••• $2') : '';
}

function setLoggedIn(phone) {
  sessionStorage.setItem('cohabit_user_phone', phone);
  // update avatar button text
  const avatarBtn = document.getElementById('avatarBtn');
  if (avatarBtn) {
    avatarBtn.textContent = maskPhone(phone);
  }
  showToast('Signed in as ' + maskPhone(phone));
}

function clearLoggedIn() {
  sessionStorage.removeItem('cohabit_user_phone');
  const avatarBtn = document.getElementById('avatarBtn');
  if (avatarBtn) {
    avatarBtn.innerHTML = '👤';
  }
}

// Restore session if present
if (sessionStorage.getItem('cohabit_user_phone')) {
  const p = sessionStorage.getItem('cohabit_user_phone');
  setLoggedIn(p);
}


// Simple non-blocking toast helper
function showToast(message, timeout = 4000) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    Object.assign(container.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    });
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast';
  Object.assign(toast.style, {
    background: 'rgba(10,12,20,0.95)',
    color: '#e6f3ff',
    padding: '12px 16px',
    borderRadius: '8px',
    boxShadow: '0 6px 18px rgba(0,0,0,0.5)',
    maxWidth: '320px',
    fontSize: '14px',
  });
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity 250ms ease, transform 250ms ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-8px)';
    setTimeout(() => toast.remove(), 300);
  }, timeout);
}

function buildStepLabels() {
  if (wizardStepper) {
    wizardStepper.setAttribute("aria-hidden", "true");
    wizardStepper.innerHTML = "";
  }
}

function updateWizard() {
  wizardSteps.forEach((step, index) => {
    step.classList.toggle("active", index === activeStep);
  });

  if (wizardStepper) {
    const pills = wizardStepper.querySelectorAll(".step-pill");
    pills.forEach((pill, index) => {
      pill.classList.toggle("active", index === activeStep);
    });
  }

  prevStepButton.disabled = activeStep === 0;
  nextStepButton.textContent = activeStep === wizardSteps.length - 1 ? "See matches" : "Continue";
}

function goToStep(index) {
  if (index < 0 || index >= wizardSteps.length) return;
  activeStep = index;
  updateWizard();
}

function getFormPayload() {
  const formData = new FormData(setupForm);
  const payload = {};

  for (const [key, value] of formData.entries()) {
    payload[key] = value;
  }

  return payload;
}

function validateGenderPreference() {
  const gender = setupForm.querySelector('input[name="gender"]:checked')?.value;
  const preferredGender = setupForm.querySelector('input[name="preferred_gender"]:checked')?.value;
  const femaleMismatchNote = document.querySelector("#genderMismatchNote");
  const maleMismatchNote = document.querySelector("#maleMismatchNote");

  // Show warning if female user selected male as preferred
  if (gender === "Female" && preferredGender === "Male") {
    if (femaleMismatchNote) {
      femaleMismatchNote.style.display = "block";
    }
  } else {
    if (femaleMismatchNote) {
      femaleMismatchNote.style.display = "none";
    }
  }

  // Show warning if male user selected female as preferred
  if (gender === "Male" && preferredGender === "Female") {
    if (maleMismatchNote) {
      maleMismatchNote.style.display = "block";
    }
  } else {
    if (maleMismatchNote) {
      maleMismatchNote.style.display = "none";
    }
  }
}

// Add event listeners for gender validation
document.addEventListener("DOMContentLoaded", () => {
  const genderInputs = setupForm.querySelectorAll('input[name="gender"]');
  const preferredGenderInputs = setupForm.querySelectorAll('input[name="preferred_gender"]');

  genderInputs.forEach((input) => {
    input.addEventListener("change", validateGenderPreference);
  });

  preferredGenderInputs.forEach((input) => {
    input.addEventListener("change", validateGenderPreference);
  });

  // Phone login handlers
  const loginPhone = document.getElementById('loginPhone');
  if (loginPhone) {
    loginPhone.addEventListener('click', (e) => {
      e.preventDefault();
      openPhoneModal();
    });
  }

  const cancelOtpBtn = document.getElementById('cancelOtpBtn');
  if (cancelOtpBtn) cancelOtpBtn.addEventListener('click', (e) => { e.preventDefault(); closePhoneModal(); });

  const sendOtp = document.getElementById('sendOtpBtn');
  if (sendOtp) {
    sendOtp.addEventListener('click', async (e) => {
      e.preventDefault();
      const phone = (document.getElementById('phoneNumber')||{}).value || '';
      if (!phone || phone.length < 6) { showToast('Please enter a valid phone number'); return; }
      // create a fake OTP and store it in sessionStorage for demo
      const code = Math.floor(100000 + Math.random() * 900000).toString();
      sessionStorage.setItem('cohabit_otp', code);
      sessionStorage.setItem('cohabit_otp_phone', phone);
      // In a real app, call backend to send SMS here.
      console.log('DEBUG OTP for', phone, code);
      updateDemoOtp(code);
      showToast('OTP sent to ' + phone + ' (demo)');
      // switch to otp step
      document.getElementById('phoneStep').style.display = 'none';
      document.getElementById('otpStep').style.display = 'block';
    });
  }

  const resendBtn = document.getElementById('resendOtpBtn');
  if (resendBtn) {
    resendBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const phone = sessionStorage.getItem('cohabit_otp_phone') || (document.getElementById('phoneNumber')||{}).value;
      if (!phone) { showToast('Phone not found'); return; }
      const code = Math.floor(100000 + Math.random() * 900000).toString();
      sessionStorage.setItem('cohabit_otp', code);
      updateDemoOtp(code);
      console.log('DEBUG RESEND OTP for', phone, code);
      showToast('OTP resent (demo)');
    });
  }

  const verifyBtn = document.getElementById('verifyOtpBtn');
  if (verifyBtn) {
    verifyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const entered = (document.getElementById('otpInput')||{}).value || '';
      const stored = sessionStorage.getItem('cohabit_otp');
      const phone = sessionStorage.getItem('cohabit_otp_phone') || (document.getElementById('phoneNumber')||{}).value;
      if (entered === stored) {
        setLoggedIn(phone);
        // clear temp otp
        sessionStorage.removeItem('cohabit_otp');
        sessionStorage.removeItem('cohabit_otp_phone');
        closePhoneModal();
      } else {
        showToast('Incorrect OTP');
      }
    });
  }

  const signOut = document.getElementById('signOut');
  if (signOut) {
    signOut.addEventListener('click', (e) => {
      e.preventDefault();
      closePhoneModal();
      clearLoggedIn();
      showToast('Signed out');
    });
  }

});

function validateStep(stepIndex) {
  const step = wizardSteps[stepIndex];
  const requiredFields = {
    1: ["name", "profession", "gender"],
    2: ["work_shift", "personality"],
    3: ["bedtime", "wake_time", "noise_preference"],
    4: ["room_type_preference", "cleanliness", "privacy_importance"],
    5: ["pets", "smoking_drinking", "dietary_restrictions"],
  };

  const fieldsToCheck = requiredFields[stepIndex + 1] || [];

  for (const fieldName of fieldsToCheck) {
    const field = step.querySelector(`input[name="${fieldName}"]`);
    if (!field) continue;

    if (field.type === "radio") {
      const checked = step.querySelector(`input[name="${fieldName}"]:checked`);
      if (!checked) {
        showToast(`Please select ${fieldName.replace(/_/g, " ")}`);
        return false;
      }
    } else if (field.type === "text") {
      if (!field.value.trim()) {
        showToast(`Please fill in ${fieldName.replace(/_/g, " ")}`);
        return false;
      }
    }
  }

  return true;
}

function chipList(user) {
  return [
    user.gender,
    user.work_shift,
    user.personality,
    user.cleanliness,
    user.sleep_type,
    user.noise_preference,
    user.room_type_preference,
    user.privacy_importance,
    user.pets,
    user.dietary_restrictions,
  ].filter(Boolean);
}

function renderProfile(user) {
  profileCard.innerHTML = `
    <div class="summary-top">
      <div>
        <p class="eyebrow">Active profile</p>
        <h2>${user.name || "Guest"}</h2>
      </div>
      <span>${user.profession || "Your lifestyle"}</span>
    </div>
    <div class="chip-list">
      ${chipList(user).map((chip) => `<span class="chip">${chip}</span>`).join("")}
    </div>
    <p>${user.bio || "Your roommate summary will appear here once you generate recommendations."}</p>
  `;
}

function renderMatchCard(match, index, showActions = false) {
  const traits = match && Array.isArray(match.traits) ? match.traits : [];
  const persona = match && match.persona ? match.persona : "Balanced";
  const coach = match && match.coach ? match.coach : (match && match.explanation ? match.explanation : "A thoughtful fit for your routine.");
  const explanation = match && match.explanation ? match.explanation : "A strong fit for your routine.";
  const name = match && match.name ? match.name : "Candidate";
  const score = match && match.score != null ? match.score : 0;
  const id = match && match.id != null ? match.id : index + 1;
  const status = match && match.status ? match.status : null;
  const coachParagraph = coach !== explanation ? `<p>${coach}</p>` : "";
  const likeLabel = status === "like" ? "Liked" : "Like";
  const saveLabel = status === "save" ? "Saved" : "Save";
  const isLiked = status === "like";
  const isSaved = status === "save";

  return `
    <article class="match-card" data-candidate-id="${id}">
      <div class="rank">#${index + 1}</div>
      <div class="match-main">
        <div class="match-head">
          <h3>${name}</h3>
          <span class="score">${score}%</span>
        </div>
        <div class="match-summary">
          <button class="detail-toggle" data-candidate-id="${id}" type="button">View preferences</button>
        </div>
        <div class="match-details" id="details-${id}">
          <div class="match-meta">
            <span class="meta-pill">${persona}</span>
            ${traits.slice(0, 3).map((trait) => `<span class="meta-pill">${trait}</span>`).join("")}
          </div>
          <p>${explanation}</p>
          ${coachParagraph}
        </div>
        ${showActions ? `
          <div class="match-actions">
            <button class="${isLiked ? "active" : ""}" data-action="like" data-candidate-id="${id}" type="button">${likeLabel}</button>
            <button data-action="skip" data-candidate-id="${id}" type="button">Skip</button>
            <button class="${isSaved ? "active" : ""}" data-action="save" data-candidate-id="${id}" type="button">${saveLabel}</button>
          </div>
        ` : ""}
      </div>
    </article>
  `;
}

function renderMatches(matches) {
  matchCount.textContent = `${matches.length} shown`;
  if (!matches.length) {
    matchesGrid.innerHTML = `<div class="empty-state">No matches found.</div>`;
    return;
  }
  matchesGrid.innerHTML = matches.map((match, index) => renderMatchCard(match, index, true)).join("");
}

function renderInteractionSection(container, items, countElement, emptyText) {
  countElement.textContent = `${items.length}`;
  if (!items.length) {
    container.innerHTML = `<div class="empty-state">${emptyText}</div>`;
    return;
  }
  container.innerHTML = items.map((match, index) => renderMatchCard(match, index, false)).join("");
}

function installDetailToggles() {
  const toggleButtons = document.querySelectorAll(".detail-toggle");
  toggleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const candidateId = button.dataset.candidateId;
      const details = document.querySelector(`#details-${candidateId}`);
      if (!details) return;
      const expanded = details.classList.toggle("expanded");
      button.textContent = expanded ? "Hide preferences" : "View preferences";
    });
  });
}

function setLoadingState() {
  if (aiScreen) {
    aiScreen.classList.remove("hidden");
  }
  if (resultsPanel) {
    resultsPanel.classList.add("hidden");
  }
  if (aiProgress) {
    aiProgress.style.width = "0";
    window.requestAnimationFrame(() => {
      aiProgress.style.width = "50%";
    });
  }
}

function showPanel(panel) {
  if (!wizardPanel) return;

  if (panel === "dashboard" || panel === "saved" || panel === "settings") {
    wizardPanel.classList.add("hidden");
    if (aiScreen) {
      aiScreen.classList.add("hidden");
    }
    if (resultsPanel) {
      resultsPanel.classList.remove("hidden");
    }
    if (contentPanel) {
      contentPanel.classList.remove("hidden");
      contentPanel.classList.add("active");
    }
    if (heroPanel) {
      heroPanel.classList.toggle("hidden", panel === "settings");
    }
    return;
  }

  if (panel === "find-roommates") {
    wizardPanel.classList.remove("hidden");
    if (resultsPanel) {
      resultsPanel.classList.add("hidden");
    }
    if (aiScreen) {
      aiScreen.classList.add("hidden");
    }
    if (contentPanel) {
      contentPanel.classList.add("hidden");
    }
    if (heroPanel) {
      heroPanel.classList.add("hidden");
    }
    return;
  }
}

function showResultsSection() {
  if (aiScreen) {
    aiScreen.classList.add("hidden");
  }
  if (resultsPanel) {
    resultsPanel.classList.remove("hidden");
  }
  if (contentPanel) {
    contentPanel.classList.remove("hidden");
    contentPanel.classList.add("active");
  }
  if (aiProgress) {
    aiProgress.style.width = "100%";
  }
}

async function findMatches() {
  const payload = getFormPayload();
  setLoadingState();
  if (matchesGrid) {
    matchesGrid.innerHTML = `<div class="empty-state">Preparing your match feed...</div>`;
  }

  try {
    const response = await fetch("/api/custom-matches", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const data = await response.json();
  currentUserId = data.user.id || 0;
  currentMatches = Array.isArray(data.matches) ? data.matches : [];
  likedMatches = Array.isArray(data.liked) ? data.liked : [];
  savedMatches = Array.isArray(data.saved) ? data.saved : [];

  renderProfile(data.user);
  renderInteractionSection(likedGrid, likedMatches, likedCount, "No liked profiles yet.");
  renderInteractionSection(savedGrid, savedMatches, savedCount, "No saved profiles yet.");
  renderMatches(currentMatches);
  installDetailToggles();
  matchesTitle.textContent = `Best matches for ${data.user.name || "your profile"}`;
  heroMatchesFound.textContent = currentMatches.length;
  heroLikedCount.textContent = likedMatches.length;
  heroSavedCount.textContent = savedMatches.length;
  const avgScore = currentMatches.length
    ? Math.round(currentMatches.reduce((sum, match) => sum + (match.score || 0), 0) / currentMatches.length)
    : 0;
  heroAverageCompatibility.textContent = `${avgScore}%`;
  const contentPanel = document.querySelector("#contentPanel");
  if (contentPanel) {
    contentPanel.classList.remove("hidden");
    contentPanel.classList.add("active");
  }
  if (heroPanel) {
    heroPanel.classList.remove("hidden");
    heroPanel.classList.add("slide-in");
  }
  showResultsSection();
} catch (error) {
  if (aiScreen) {
    aiScreen.classList.add("hidden");
  }
  if (resultsPanel) {
    resultsPanel.classList.remove("hidden");
  }
  if (matchesGrid) {
    matchesGrid.innerHTML = `<div class="empty-state">Unable to load recommendations. ${error.message}</div>`;
  }
  console.error(error);
}
}

async function recordInteraction(candidateId, action) {
  if (!currentUserId || !candidateId) {
    return null;
  }

  const response = await fetch("/api/interactions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: currentUserId, candidate_id: candidateId, action }),
  });

  return response.ok ? response.json() : null;
}

prevStepButton.addEventListener("click", (event) => {
  event.preventDefault();
  if (activeStep > 0) {
    goToStep(activeStep - 1);
  }
});

nextStepButton.addEventListener("click", (event) => {
  event.preventDefault();
  if (!validateStep(activeStep)) {
    return;
  }
  if (activeStep < wizardSteps.length - 1) {
    goToStep(activeStep + 1);
  } else {
    findMatches();
  }
});

if (energySlider && energyValueLabel) {
  energySlider.addEventListener("input", (event) => {
    energyValueLabel.textContent = event.target.value;
  });
}

setupForm.addEventListener("submit", (event) => {
  event.preventDefault();
  findMatches();
});

navItems.forEach((item) => {
  item.addEventListener("click", (event) => {
    event.preventDefault();
    navItems.forEach((nav) => nav.classList.remove("active"));
    item.classList.add("active");
    const panel = item.dataset.panel || item.textContent.trim().toLowerCase().replace(/\s+/g, "-");
    showPanel(panel);
  });
});

matchesGrid.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;

  const action = button.dataset.action;
  const candidateId = Number(button.dataset.candidateId);
  const result = await recordInteraction(candidateId, action);

  if (action === "skip") {
    currentMatches = currentMatches.filter((match) => match.id !== candidateId);
    likedMatches = likedMatches.filter((match) => match.id !== candidateId);
    savedMatches = savedMatches.filter((match) => match.id !== candidateId);
    renderInteractionSection(likedGrid, likedMatches, likedCount, "No liked profiles yet.");
    renderInteractionSection(savedGrid, savedMatches, savedCount, "No saved profiles yet.");
    renderMatches(currentMatches);
    return;
  }

  const match = currentMatches.find((item) => item.id === candidateId);
  if (match) {
    match.status = action;
    currentMatches = currentMatches.filter((item) => item.id !== candidateId);

    if (action === "like") {
      likedMatches = [
        ...likedMatches.filter((item) => item.id !== candidateId),
        { ...match },
      ];
      savedMatches = savedMatches.filter((item) => item.id !== candidateId);
    }

    if (action === "save") {
      savedMatches = [
        ...savedMatches.filter((item) => item.id !== candidateId),
        { ...match },
      ];
      likedMatches = likedMatches.filter((item) => item.id !== candidateId);
    }

    renderInteractionSection(likedGrid, likedMatches, likedCount, "No liked profiles yet.");
    renderInteractionSection(savedGrid, savedMatches, savedCount, "No saved profiles yet.");
    renderMatches(currentMatches);
  }

  if (result && result.action) {
    button.textContent = `${result.action.charAt(0).toUpperCase()}${result.action.slice(1)}d`;
  }
});

buildStepLabels();
goToStep(0);
showPanel("find-roommates");
// Header button wiring
const bellBtn = document.querySelector('#bellBtn');
const avatarBtn = document.querySelector('#avatarBtn');
const bellPanel = document.querySelector('#bellPanel');
const avatarPanel = document.querySelector('#avatarPanel');

function togglePanel(panel, btn) {
  const isHidden = panel.getAttribute('aria-hidden') === 'true';
  // close both first
  bellPanel.setAttribute('aria-hidden', 'true');
  bellPanel.style.display = 'none';
  avatarPanel.setAttribute('aria-hidden', 'true');
  avatarPanel.style.display = 'none';

  if (isHidden) {
    panel.setAttribute('aria-hidden', 'false');
    panel.style.display = 'block';
    btn.setAttribute('aria-expanded', 'true');
  } else {
    panel.setAttribute('aria-hidden', 'true');
    panel.style.display = 'none';
    btn.setAttribute('aria-expanded', 'false');
  }
}

if (bellBtn && bellPanel) {
  bellBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    togglePanel(bellPanel, bellBtn);
  });
}

if (avatarBtn && avatarPanel) {
  avatarBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    togglePanel(avatarPanel, avatarBtn);
  });
}

// Close panels when clicking outside
document.addEventListener('click', () => {
  if (bellPanel) {
    bellPanel.setAttribute('aria-hidden', 'true');
    bellPanel.style.display = 'none';
  }
  if (avatarPanel) {
    avatarPanel.setAttribute('aria-hidden', 'true');
    avatarPanel.style.display = 'none';
  }
  if (bellBtn) bellBtn.setAttribute('aria-expanded', 'false');
  if (avatarBtn) avatarBtn.setAttribute('aria-expanded', 'false');
});
// Header menu item actions
const viewProfileLink = document.querySelector('#viewProfile');
const savedProfilesLink = document.querySelector('#savedProfiles');
const settingsLink = document.querySelector('#settingsLink');
const signOutLink = document.querySelector('#signOut');

if (viewProfileLink) {
  viewProfileLink.addEventListener('click', (e) => {
    e.preventDefault();
    togglePanel(avatarPanel, avatarBtn);
    showPanel('dashboard');
  });
}

if (savedProfilesLink) {
  savedProfilesLink.addEventListener('click', (e) => {
    e.preventDefault();
    togglePanel(avatarPanel, avatarBtn);
    showPanel('saved');
  });
}

if (settingsLink) {
  settingsLink.addEventListener('click', (e) => {
    e.preventDefault();
    togglePanel(avatarPanel, avatarBtn);
    showPanel('settings');
  });
}

if (signOutLink) {
  signOutLink.addEventListener('click', async (e) => {
    e.preventDefault();
    togglePanel(avatarPanel, avatarBtn);
    try {
      await fetch('/api/logout', { method: 'POST' });
    } catch (err) {
      console.warn('Logout failed', err);
    }
    // clear local UI state
    currentUserId = 0;
    currentMatches = [];
    likedMatches = [];
    savedMatches = [];
    renderInteractionSection(likedGrid, likedMatches, likedCount, "No liked profiles yet.");
    renderInteractionSection(savedGrid, savedMatches, savedCount, "No saved profiles yet.");
    renderMatches(currentMatches);
    await refreshSession();
    showToast('Signed out');
    showPanel('find-roommates');
  });
}

// Update UI based on session presence by fetching /api/session (optional)
async function refreshSession() {
  try {
    const resp = await fetch('/api/session');
    if (!resp.ok) return;
    const data = await resp.json();
    const user = data.user;
    const avatarBtn = document.querySelector('#avatarBtn');
    if (user && avatarBtn) {
      avatarBtn.textContent = user.name ? user.name.charAt(0).toUpperCase() : '👤';
      avatarBtn.title = user.name;
    }
  } catch (err) {
    // ignore
  }
}

refreshSession();
// Connect to the FastAPI WebSocket server
const socket = new WebSocket('ws://127.0.0.1:8000/ws/notifications/');
socket.onopen = function(e) {
    console.log("🚀 Connected to CoHabit Real-Time Server via WebSockets!");
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Real-time event received:", data);
    
    if (data.type === "NEW_MATCH") {
  // Show a non-blocking toast notification
  showToast(data.message);

  // Add to notification list panel
  const list = document.querySelector('#notificationsList');
  if (list) {
    const entry = document.createElement('div');
    entry.className = 'notification-item';
    entry.textContent = data.message;
    entry.style.padding = '8px 6px';
    entry.style.borderBottom = '1px dashed rgba(255,255,255,0.03)';
    entry.style.color = 'var(--text)';
    const empty = list.querySelector('.empty');
    if (empty) empty.remove();
    list.prepend(entry);
  }
    }
};

socket.onclose = function(e) {
    console.warn("WebSocket connection dropped.");
};
