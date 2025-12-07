
document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & DOM refs ---
    // Use relative URLs for Vercel deployment, fallback to localhost for local dev
    const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://127.0.0.1:5000' 
        : '';

    // Mobile and Desktop elements
    const startBtn = document.getElementById('start-btn');
    const startBtnDesktop = document.getElementById('start-btn-desktop');
    const statusIndicator = document.getElementById('status-indicator');
    const statusIndicatorDesktop = document.getElementById('status-indicator-desktop');
    const statusIcon = document.getElementById('status-icon');
    const statusIconDesktop = document.getElementById('status-icon-desktop');
    const backendStatus = document.getElementById('backend-status');
    const backendStatusDesktop = document.getElementById('backend-status-desktop');
    
    const userCommandEl = document.getElementById('user-command');
    const assistantResponseEl = document.getElementById('assistant-response');
    const unsupportedMessage = document.getElementById('unsupported-message');
    const remindersList = document.getElementById('reminders-list');
    const conversationLog = document.getElementById('conversation-log');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const addReminderBtn = document.getElementById('add-reminder-btn');
    const reminderTaskInput = document.getElementById('reminder-task-input');
    const reminderTimeInput = document.getElementById('reminder-time-input');
    const quickPromptButtons = document.querySelectorAll('[data-command]');
    const refreshWeatherBtn = document.getElementById('refresh-weather');
    const weatherContent = document.getElementById('weather-content');

    // --- Speech Recognition & Synthesis ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        startBtn.disabled = true;
        unsupportedMessage.classList.remove('hidden');
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    const utterance = new SpeechSynthesisUtterance();
    utterance.lang = 'en-US';

    // --- State management ---
    let isListening = false;
    let hasGreeted = false; // Track if initial greeting has been played
    let conversationHistory = [];
    const MAX_HISTORY = 18;
    const MAX_STORAGE_CONVERSATIONS = 50; // Prevent localStorage overflow
    let lastWeatherData = null;
    let backendAvailable = null; // null = unknown, true = online, false = offline
    
    // Safe localStorage access with error handling
    const safeGetLocalStorage = (key, defaultValue = '{}') => {
        try {
            return JSON.parse(localStorage.getItem(key) || defaultValue);
        } catch (e) {
            return JSON.parse(defaultValue);
        }
    };
    
    const knowledge = safeGetLocalStorage('nextor_knowledge', '{}');
    let reminders = safeGetLocalStorage('nextor_reminders', '[]');
    const activeTimeouts = new Map();

    // --- UI helpers ---
    function updateStatus(status) {
        // Update mobile status
        if (statusIndicator) {
            statusIndicator.classList.remove('listening', 'speaking');
            statusIcon.className = 'fas fa-microphone text-3xl text-white';

            switch (status) {
                case 'listening':
                    statusIndicator.classList.add('listening');
                    statusIcon.className = 'fas fa-waveform-lines text-3xl text-green-500';
                    break;
                case 'speaking':
                    statusIndicator.classList.add('speaking');
                    statusIcon.className = 'fas fa-volume-high text-3xl text-blue-500';
                    break;
                default:
                    statusIcon.className = 'fas fa-microphone text-3xl text-white';
            }
        }
        
        // Update desktop status
        if (statusIndicatorDesktop) {
            statusIndicatorDesktop.classList.remove('listening', 'speaking');
            statusIconDesktop.className = 'fas fa-microphone text-4xl text-white';

            switch (status) {
                case 'listening':
                    statusIndicatorDesktop.classList.add('listening');
                    statusIconDesktop.className = 'fas fa-waveform-lines text-4xl text-green-500';
                    break;
                case 'speaking':
                    statusIndicatorDesktop.classList.add('speaking');
                    statusIconDesktop.className = 'fas fa-volume-high text-4xl text-blue-500';
                    break;
                default:
                    statusIconDesktop.className = 'fas fa-microphone text-4xl text-white';
            }
        }
    }

    function addMessage(role, text) {
        const timestamp = new Date().toISOString();
        conversationHistory.push({ role, text, time: timestamp });
        if (conversationHistory.length > MAX_HISTORY) {
            conversationHistory = conversationHistory.slice(-MAX_HISTORY);
        }
        renderConversation();
        saveConversationHistory();
    }

    function saveConversationHistory() {
        try {
            // Keep only last 50 conversations to prevent localStorage overflow
            const toSave = conversationHistory.slice(-MAX_STORAGE_CONVERSATIONS);
            localStorage.setItem('nextor_conversations', JSON.stringify(toSave));
        } catch (error) {
            // If quota exceeded, clear old data and retry
            if (error.name === 'QuotaExceededError') {
                localStorage.removeItem('nextor_conversations');
                conversationHistory = conversationHistory.slice(-MAX_HISTORY);
                try {
                    localStorage.setItem('nextor_conversations', JSON.stringify(conversationHistory));
                } catch (e) {
                    // Still failing, give up silently
                }
            }
        }
    }

    function loadConversationHistory() {
        try {
            const saved = localStorage.getItem('nextor_conversations');
            if (saved) {
                conversationHistory = JSON.parse(saved);
            }
        } catch (error) {
            // Invalid data or storage disabled
            conversationHistory = [];
        }
    }

    function renderConversation() {
        if (!conversationLog) return;
        conversationLog.innerHTML = '';
        const recent = conversationHistory.slice(-12);
        recent.forEach((entry) => {
            const wrapper = document.createElement('div');
            wrapper.className = entry.role === 'user' 
                ? 'glass-effect rounded-2xl p-4 border-l-4 border-green-500 animate-slide-up'
                : 'glass-effect rounded-2xl p-4 border-l-4 border-blue-500 animate-slide-up';

            const header = document.createElement('div');
            header.className = 'flex items-center gap-2 mb-2';
            
            const icon = document.createElement('i');
            icon.className = entry.role === 'user'
                ? 'fas fa-user-circle text-green-500'
                : 'fas fa-robot text-blue-500';
            
            const label = document.createElement('span');
            label.className = 'text-xs font-bold text-gray-400';
            label.textContent = entry.role === 'user' ? 'You' : 'Nextor';
            
            const timeEl = document.createElement('time');
            timeEl.className = 'text-xs text-gray-500 ml-auto';
            timeEl.dateTime = entry.time;
            timeEl.textContent = new Date(entry.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            header.appendChild(icon);
            header.appendChild(label);
            header.appendChild(timeEl);

            const message = document.createElement('p');
            message.className = 'text-white text-sm leading-relaxed';
            message.textContent = entry.text;

            wrapper.appendChild(header);
            wrapper.appendChild(message);
            conversationLog.appendChild(wrapper);
        });
        conversationLog.scrollTop = conversationLog.scrollHeight;
    }

    function speak(text, options = {}) {
        const { onend, log = true } = options;
        assistantResponseEl.textContent = text;
        if (log) {
            addMessage('assistant', text);
        }
        
        const synth = window.speechSynthesis;
        
        // Force cancel any ongoing speech and clear queue
        if (synth.speaking || synth.pending) {
            synth.cancel();
        }
        
        utterance.text = text;
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        utterance.onstart = () => updateStatus('speaking');
        utterance.onend = () => {
            updateStatus('idle');
            if (typeof onend === 'function') {
                onend();
            }
        };
        utterance.onerror = (event) => {
            updateStatus('idle');
            // Only retry on recoverable errors
            if (event.error === 'network' || event.error === 'synthesis-unavailable') {
                setTimeout(() => synth.speak(utterance), 500);
            }
        };
        
        // Ensure clean state before speaking
        setTimeout(() => {
            if (!synth.speaking) {
                synth.speak(utterance);
            }
        }, 150);
    }

    function openWebsite(url, speakText) {
        speak(speakText);
        window.open(url, '_blank');
    }

    function saveKnowledge() {
        localStorage.setItem('nextor_knowledge', JSON.stringify(knowledge));
    }

    function saveReminders() {
        localStorage.setItem('nextor_reminders', JSON.stringify(reminders));
    }

    function parseTimeToDate(timeStr) {
        const safeTime = timeStr?.toLowerCase() || '';
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        if (safeTime.includes('minute')) {
            const minutes = parseInt(safeTime.match(/(\d+)/)?.[1] || '5', 10);
            return new Date(now.getTime() + minutes * 60000);
        }

        if (safeTime.includes('hour')) {
            const hours = parseInt(safeTime.match(/(\d+)/)?.[1] || '1', 10);
            return new Date(now.getTime() + hours * 3600000);
        }

        if (safeTime.includes('tomorrow')) {
            const tomorrow = new Date(today.getTime() + 24 * 3600000);
            const timeMatch = safeTime.match(/(\d{1,2})(:(\d{2}))?\s*(am|pm)?/i);
            if (timeMatch) {
                let hour = parseInt(timeMatch[1], 10);
                const minute = parseInt(timeMatch[3] || '0', 10);
                const ampm = timeMatch[4]?.toLowerCase();
                if (ampm === 'pm' && hour !== 12) hour += 12;
                if (ampm === 'am' && hour === 12) hour = 0;
                tomorrow.setHours(hour, minute, 0, 0);
                return tomorrow;
            }
            tomorrow.setHours(9, 0, 0, 0);
            return tomorrow;
        }

        const timeMatch = safeTime.match(/(\d{1,2})(:(\d{2}))?\s*(am|pm)?/i);
        if (timeMatch) {
            let hour = parseInt(timeMatch[1], 10);
            const minute = parseInt(timeMatch[3] || '0', 10);
            const ampm = timeMatch[4]?.toLowerCase();
            if (ampm === 'pm' && hour !== 12) hour += 12;
            if (ampm === 'am' && hour === 12) hour = 0;

            const target = new Date(today);
            target.setHours(hour, minute, 0, 0);
            if (target <= now) {
                target.setDate(target.getDate() + 1);
            }
            return target;
        }

        return null;
    }

    async function requestNotificationPermission() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                if (permission === 'granted') {
                    console.log('✅ Notification permission granted');
                } else {
                    console.warn('⚠️ Notification permission denied');
                    alert('Please enable notifications to receive reminders!');
                }
            } else if (Notification.permission === 'denied') {
                alert('Notifications are blocked. Please enable them in browser settings: Settings > Site Settings > Notifications');
            }
        } else {
            console.warn('⚠️ Notifications not supported on this device');
        }
    }

    function showNotification(title, body) {
        console.log('🔔 Showing notification:', title, body);
        
        // Try browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            try {
                const notification = new Notification(title, {
                    body,
                    icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="%2310b981"/><text x="50" y="60" text-anchor="middle" font-family="Arial" font-size="40" fill="white">N</text></svg>',
                    badge: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="%2310b981"/></svg>',
                    vibrate: [200, 100, 200], // Vibration pattern
                    requireInteraction: true, // Keep notification visible
                    tag: 'nextor-reminder' // Replace old notifications
                });
                
                notification.onclick = () => {
                    window.focus();
                    notification.close();
                };
                
                setTimeout(() => notification.close(), 10000);
            } catch (err) {
                console.error('Notification error:', err);
            }
        } else {
            console.warn('⚠️ Notifications not available:', 
                'Notification' in window ? `Permission: ${Notification.permission}` : 'Not supported');
        }
        
        // Vibrate device if supported
        if ('vibrate' in navigator) {
            navigator.vibrate([200, 100, 200, 100, 200]);
        }
        
        // Play sound alert
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0fPTgjMGHm7A7+OZSA0PVqzn77BdGAg+l9n0yXksBSd+zPDajjwKElyx6OyrWBUIQ6Hn88BwJAU1kdXzzn0pBSx6xu/blUELElyx6OyrWBUIQ6Hn88BwJAU1kdXzzn0pBSx6xu/blUELE1mw5PDTqVQVCEOh5/PAcCQFNZHV885/KQUre8bv25VBC');
            audio.volume = 0.5;
            audio.play().catch(() => console.log('Audio play blocked'));
        } catch (err) {
            console.log('Audio not available');
        }
        
        // Visual alert in page
        const alertDiv = document.createElement('div');
        alertDiv.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);z-index:9999;background:#f59e0b;color:white;padding:16px 24px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.3);font-weight:600;max-width:90%;text-align:center;animation:slideDown 0.3s ease-out;';
        alertDiv.innerHTML = `⏰ <strong>Reminder for:</strong><br>${body}`;
        document.body.appendChild(alertDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            alertDiv.style.animation = 'slideUp 0.3s ease-out';
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
        
        // Try to speak the reminder
        try {
            speak(`Reminder: ${body}`);
        } catch (err) {
            console.log('Speech synthesis blocked');
        }
    }

    function scheduleReminder(reminder, index) {
        if (!reminder.scheduledTime) return;
        const now = new Date();
        const delay = reminder.scheduledTime - now.getTime();
        
        // Clean up expired reminder immediately
        if (delay <= 0) {
            reminders.splice(index, 1);
            saveReminders();
            return;
        }

        // Clear existing timeout if already scheduled
        if (activeTimeouts.has(reminder.id)) {
            clearTimeout(activeTimeouts.get(reminder.id));
        }

        const timeoutId = setTimeout(() => {
            showNotification('Nextor Reminder', reminder.text);
            // Find current index (might have changed)
            const currentIndex = reminders.findIndex(r => r.id === reminder.id);
            if (currentIndex !== -1) {
                reminders.splice(currentIndex, 1);
                saveReminders();
                renderReminders();
            }
            activeTimeouts.delete(reminder.id);
        }, delay);

        activeTimeouts.set(reminder.id, timeoutId);
    }

    // Check reminders periodically (every 10 seconds) to handle mobile background states
    function startReminderWatcher() {
        console.log('🔔 Starting reminder watcher');
        setInterval(() => {
            const now = new Date().getTime();
            // Iterate backwards to safely remove items
            for (let i = reminders.length - 1; i >= 0; i--) {
                const reminder = reminders[i];
                if (reminder.scheduledTime && reminder.scheduledTime <= now && reminder.scheduledTime > (now - 120000)) {
                    // Reminder is due (within last 2 minutes)
                    console.log('⏰ Reminder triggered:', reminder.text);
                    showNotification('⏰ Nextor Reminder', reminder.text);
                    reminders.splice(i, 1);
                    saveReminders();
                    renderReminders();
                }
            }
        }, 10000); // Check every 10 seconds for better responsiveness
    }

    function cleanupExpiredReminders() {
        const now = new Date().getTime();
        const before = reminders.length;
        reminders = reminders.filter(r => {
            if (r.scheduledTime && r.scheduledTime < now) {
                // Clear timeout if exists
                if (activeTimeouts.has(r.id)) {
                    clearTimeout(activeTimeouts.get(r.id));
                    activeTimeouts.delete(r.id);
                }
                return false; // Remove expired
            }
            return true; // Keep active
        });
        
        if (before !== reminders.length) {
            saveReminders();
            renderReminders();
        }
    }

    function renderReminders() {
        remindersList.innerHTML = '';
        if (reminders.length === 0) {
            remindersList.innerHTML = '<li class="text-slate-400 text-sm italic p-3 text-center">No reminders set</li>';
            return;
        }

        reminders.forEach((reminder, idx) => {
            const li = document.createElement('li');
            li.className = 'glass-effect rounded-xl p-3 border-l-4 border-red-500 flex items-start justify-between gap-3 animate-slide-up';

            let timeDisplay = reminder.time || 'no time';
            if (reminder.scheduledTime) {
                const scheduledDate = new Date(reminder.scheduledTime);
                const now = new Date();
                const diffMinutes = Math.round((scheduledDate - now) / 60000);
                if (diffMinutes > 0) {
                    if (diffMinutes < 60) {
                        timeDisplay = `in ${diffMinutes} min`;
                    } else if (diffMinutes < 1440) {
                        timeDisplay = `in ${Math.round(diffMinutes / 60)} hr`;
                    } else {
                        timeDisplay = scheduledDate.toLocaleDateString() + ' ' + scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    }
                } else {
                    timeDisplay = 'overdue';
                }
            }

            const textContainer = document.createElement('div');
            textContainer.className = 'flex-1';
            
            const taskText = document.createElement('p');
            taskText.className = 'text-white text-sm font-medium';
            taskText.textContent = reminder.text;
            
            const timeText = document.createElement('p');
            timeText.className = 'text-red-400 text-xs mt-1 flex items-center gap-1';
            timeText.innerHTML = `<i class="fas fa-clock"></i> ${timeDisplay}`;
            
            textContainer.appendChild(taskText);
            textContainer.appendChild(timeText);

            const delBtn = document.createElement('button');
            delBtn.className = 'px-3 py-1.5 rounded-lg bg-red-600/80 hover:bg-red-600 border border-red-500/50 hover:border-red-500 text-white hover:text-white text-xs font-bold transition-all hover:scale-105 flex items-center gap-1';
            delBtn.innerHTML = '<i class="fas fa-trash"></i>';
            delBtn.addEventListener('click', () => {
                if (activeTimeouts.has(reminder.id)) {
                    clearTimeout(activeTimeouts.get(reminder.id));
                    activeTimeouts.delete(reminder.id);
                }
                reminders.splice(idx, 1);
                saveReminders();
                renderReminders();
                speak('Reminder deleted');
            });

            li.appendChild(textContainer);
            li.appendChild(delBtn);
            remindersList.appendChild(li);
        });
    }

    // --- Weather helpers ---
    function showWeatherStatus(message) {
        if (weatherContent) {
            weatherContent.innerHTML = `<p class="text-slate-300 text-sm">${message}</p>`;
        }
    }

    function getCurrentPosition() {
        return new Promise((resolve, reject) => {
            console.log('🌍 Requesting location...');
            
            // Check if geolocation is supported
            if (!('geolocation' in navigator)) {
                reject(new Error('Geolocation not supported by your browser'));
                return;
            }

            // Check if we're on HTTPS (required for geolocation on mobile)
            const isSecure = window.location.protocol === 'https:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            console.log('🔒 Secure context:', isSecure, 'Protocol:', window.location.protocol);
            
            if (!isSecure) {
                reject(new Error('Geolocation requires HTTPS connection. Please access this site via HTTPS.'));
                return;
            }

            // Try to get location directly (works better on mobile)
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log('✅ Location acquired:', position.coords.latitude, position.coords.longitude);
                    resolve(position);
                },
                (error) => {
                    console.error('❌ Geolocation error:', error.code, error.message);
                    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
                    const isAndroid = /Android/.test(navigator.userAgent);
                    let errorMessage = 'LOCATION_ERROR: ';
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            if (isIOS) {
                                errorMessage += 'iPhone/iPad: Settings > Safari > Location > While Using App. Then close and reopen browser.';
                            } else if (isAndroid) {
                                errorMessage += 'Android: Settings > Site Settings > Location > Allow. Enable device GPS in Quick Settings.';
                            } else {
                                errorMessage += 'Click "Allow" when browser asks for location permission. Then refresh.';
                            }
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage += 'GPS signal unavailable. Move to an open area or enable High Accuracy mode in Settings.';
                            break;
                        case error.TIMEOUT:
                            errorMessage += 'Location request timed out. Check GPS is enabled and try again.';
                            break;
                        default:
                            errorMessage += 'Unknown error (code: ' + error.code + '). Restart your browser and try again.';
                    }
                    reject(new Error(errorMessage));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000, // Increased timeout for mobile
                    maximumAge: 30000 // Allow cached position up to 30s old
                }
            );
        });
    }

    async function fetchWeather(lat, lon) {
        const params = new URLSearchParams({ lat, lon });
        console.log('🌤️ Fetching weather:', `${API_BASE_URL}/api/weather?${params.toString()}`);
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000); // 8s timeout
        
        const response = await fetch(`${API_BASE_URL}/api/weather?${params.toString()}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        console.log('🌤️ Weather API response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Weather API error:', response.status, errorText);
            throw new Error(`Weather request failed: ${response.status}`);
        }
        const data = await response.json();
        console.log('✅ Weather data received:', data);
        return data;
    }

    function renderWeather(data) {
        lastWeatherData = data;
        const locationLabel = [data.location.name, data.location.region].filter(Boolean).join(', ') || 'Your location';
        const countryLabel = data.location.country ? ` • ${data.location.country}` : '';
        const temp = Math.round(data.current.temperature);
        const feelsLike = Math.round(data.current.apparent_temperature);
        const humidity = data.current.humidity;
        const wind = data.current.wind_speed;
        const condition = data.current.condition;
        const updatedAt = new Date(data.current.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const advice = data.advice || '';

        weatherContent.innerHTML = `
            <div class="space-y-3">
                <!-- Main Temperature Display -->
                <div class="main-temp text-center">
                    <p class="text-xs text-slate-400 mb-2 flex items-center justify-center gap-1">
                        <i class="fas fa-map-marker-alt text-blue-400 text-xs"></i>
                        <span class="text-xs">${locationLabel}${countryLabel}</span>
                    </p>
                    <div class="flex items-center justify-center gap-3 my-3">
                        <i class="fas fa-cloud-sun text-yellow-400 text-4xl"></i>
                        <div>
                            <div class="text-5xl font-bold text-white">${temp}<span class="text-2xl text-blue-400">&deg;C</span></div>
                        </div>
                    </div>
                    <p class="text-lg font-semibold text-white mb-1">${condition}</p>
                    <div class="flex items-center justify-center gap-2 text-xs text-slate-500">
                        <i class="fas fa-clock text-blue-400 text-xs"></i>
                        <span class="text-xs">Updated at ${updatedAt}</span>
                    </div>
                </div>
                
                <!-- Weather Stats Grid -->
                <div class="grid grid-cols-2 gap-4">
                    <div class="weather-stat">
                        <i class="fas fa-temperature-high"></i>
                        <span class="value">${feelsLike}&deg;C</span>
                        <span class="label">Feels Like</span>
                    </div>
                    <div class="weather-stat">
                        <i class="fas fa-droplet"></i>
                        <span class="value">${humidity}%</span>
                        <span class="label">Humidity</span>
                    </div>
                    <div class="weather-stat">
                        <i class="fas fa-wind"></i>
                        <span class="value">${wind} km/h</span>
                        <span class="label">Wind Speed</span>
                    </div>
                    <div class="weather-stat">
                        <i class="fas fa-gauge-high"></i>
                        <span class="value">${Math.abs(temp - feelsLike)}&deg;</span>
                        <span class="label">Temp Diff</span>
                    </div>
                </div>
                
                ${advice ? `<div class="mt-5 p-4 bg-slate-900/50 border border-blue-500/30 rounded-xl backdrop-blur-sm">
                    <div class="flex items-start gap-3">
                        <i class="fas fa-lightbulb text-yellow-400 text-xl mt-0.5"></i>
                        <p class="text-sm text-slate-300 leading-relaxed">${advice}</p>
                    </div>
                </div>` : ''}
            </div>
        `;
    }

    function buildWeatherSpeech(data) {
        const name = data.location.name || 'your area';
        const temp = Math.round(data.current.temperature);
        const feelsLike = Math.round(data.current.apparent_temperature);
        const condition = data.current.condition.toLowerCase();
        return `Right now in ${name}, it's ${temp} degrees and ${condition}. It feels like ${feelsLike} degrees, with humidity at ${data.current.humidity} percent.`;
    }

    async function requestWeatherForCurrentLocation({ speakResponse = false } = {}) {
        try {
            // Check backend availability first
            const isAvailable = await checkBackendAvailability();
            if (!isAvailable) {
                const message = 'Weather service is offline. Backend server not running.';
                showWeatherStatus(message);
                if (speakResponse) {
                    speak(message);
                }
                return;
            }

            if (refreshWeatherBtn) refreshWeatherBtn.disabled = true;
            showWeatherStatus('Requesting your location...');
            const position = await getCurrentPosition();
            showWeatherStatus('Fetching live weather data...');
            const { latitude, longitude } = position.coords;
            const data = await fetchWeather(latitude, longitude);
            renderWeather(data);
            if (speakResponse) {
                speak(buildWeatherSpeech(data));
            } else {
                addMessage('assistant', `Weather updated for ${data.location.name || 'your location'}.`);
            }
        } catch (error) {
            console.error('Weather error', error);
            const errorMsg = error.message || String(error);
            const denied = errorMsg.includes('DENIED') || errorMsg.includes('denied');
            const httpsRequired = errorMsg.includes('HTTPS');
            const isNetworkError = error.name === 'AbortError' || errorMsg.includes('fetch') || errorMsg.includes('Failed to fetch');
            
            let message;
            let htmlMessage;
            
            if (httpsRequired) {
                message = 'Location requires HTTPS. Please use https:// to access this site.';
                htmlMessage = `<div class="text-amber-400 font-semibold mb-2">🔒 HTTPS Required</div><div class="text-sm">Location access needs a secure connection. Use <strong>https://</strong> instead of http://</div>`;
            } else if (denied) {
                // Extract the detailed instructions from error message
                const instructionMatch = errorMsg.match(/LOCATION_(?:DENIED|ERROR):\s*(.+)/);
                const instructions = instructionMatch ? instructionMatch[1] : 'Enable location in browser settings';
                message = `Location blocked. ${instructions}`;
                htmlMessage = `<div class="text-amber-400 font-semibold mb-2">📍 Location Access Blocked</div><div class="text-sm text-left" style="line-height: 1.6;">${instructions}<br><br><strong>Then:</strong> Close browser completely and reopen this page.</div>`;
            } else if (isNetworkError) {
                message = 'Weather service is currently offline. The backend server may not be running.';
                htmlMessage = `<div class="text-red-400 font-semibold mb-2">⚠️ Service Offline</div><div class="text-sm">Backend server not running. Check terminal for errors.</div>`;
                backendAvailable = false;
            } else {
                message = errorMsg || 'Unable to fetch weather data. Please try again.';
                htmlMessage = `<div class="text-slate-300 text-sm">${message}</div>`;
            }
            
            if (weatherContent && htmlMessage) {
                weatherContent.innerHTML = htmlMessage;
            } else {
                showWeatherStatus(`⚠️ ${message}`);
            }
            
            if (speakResponse) {
                speak(message);
            }
        } finally {
            if (refreshWeatherBtn) refreshWeatherBtn.disabled = false;
        }
    }

    // --- Conversational intelligence ---
    async function checkBackendAvailability() {
        // Always check fresh to detect if server comes online
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000); // Reduced to 2s
            const response = await fetch(`${API_BASE_URL}/api/health`, {
                method: 'GET',
                signal: controller.signal,
                cache: 'no-cache'
            });
            clearTimeout(timeoutId);
            backendAvailable = response.ok;
            return backendAvailable;
        } catch (error) {
            backendAvailable = false;
            return false;
        }
    }

    async function fetchChatReply(message) {
        // Check backend availability first
        const isAvailable = await checkBackendAvailability();
        if (!isAvailable) {
            console.warn('Chat backend is offline, skipping AI chat');
            return null;
        }

        try {
            const payload = {
                message,
                history: conversationHistory.slice(-8).map(({ role, text }) => ({ role, text }))
            };
            console.log('📤 Sending to chat API:', `${API_BASE_URL}/api/chat`, payload);
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
            
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            console.log('📥 Chat API response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Chat API error:', response.status, errorText);
                backendAvailable = false;
                throw new Error(`Chat service error: ${response.status}`);
            }
            const data = await response.json();
            console.log('✅ Chat API reply:', data.reply);
            backendAvailable = true;
            return data.reply;
        } catch (error) {
            console.error('❌ Chat backend error:', error);
            backendAvailable = false;
            return null;
        }
    }

    // --- Core command handling ---
    const websiteMap = {
        youtube: 'https://www.youtube.com',
        whatsapp: 'https://www.whatsapp.com',
        instagram: 'https://www.instagram.com',
        facebook: 'https://www.facebook.com',
        google: 'https://www.google.com',
        w3schools: 'https://www.w3schools.com',
        twitter: 'https://www.twitter.com',
        linkedin: 'https://www.linkedin.com',
        netflix: 'https://www.netflix.com',
        amazon: 'https://www.amazon.com',
        ebay: 'https://www.ebay.com',
        reddit: 'https://www.reddit.com',
        github: 'https://www.github.com',
        stackoverflow: 'https://stackoverflow.com',
        gmail: 'https://mail.google.com',
        outlook: 'https://outlook.live.com',
        spotify: 'https://open.spotify.com',
        twitch: 'https://www.twitch.tv'
    };

    const tips = [
        'Break your work into focused 25 minute sprints, then rest for 5 minutes.',
        'Write down tomorrow’s priorities before you finish today.',
        'See if you can teach the concept to a friend; it locks the knowledge in.',
        'Turn distracting notifications off for one deep work block.',
        'Use a short walk or stretch to reset before starting creative work.'
    ];

    const funFacts = [
        'The Eiffel Tower can be six inches taller during the summer because metal expands when it gets hot.',
        'A teaspoon of honey is the life’s work of 12 bees.',
        'Bananas glow blue under black lights due to chlorophyll breakdown.',
        'Octopuses have three hearts and their blood is blue.',
        'Caffeine took almost 600 years to reach Europe after coffee was first brewed.'
    ];

    const jokes = [
        "Why don’t programmers trust stairs? Because they’re always up to something.",
        "I told my computer I needed a break, and it said: 'No problem, I’ll go to sleep.'",
        "Why was the math book sad? Because it had too many problems.",
        "Parallel lines have so much in common. It’s a shame they’ll never meet.",
        "I tried to catch fog yesterday. Mist."
    ];

    // Popular Hindi songs for random selection
    const hindiSongs = [
        'Tum Hi Ho Aashiqui 2',
        'Channa Mereya Ae Dil Hai Mushkil',
        'Kesariya Brahmastra',
        'Tera Ban Jaunga Akhil Sachdeva',
        'Raataan Lambiyan Shershaah',
        'Mann Meri Jaan King',
        'Apna Bana Le Bhediya',
        'Tum Se Hi Jab We Met',
        'Tere Hawaale Laal Singh Chaddha',
        'Ae Watan Ae Watan Raazi',
        'Kalank Title Track',
        'Tera Yaar Hoon Main Sonu Ke Titu Ki Sweety',
        'Dil Diyan Gallan Tiger Zinda Hai',
        'Tera Ban Jaunga',
        'Ae Dil Hai Mushkil Title Track',
        'Gerua Dilwale',
        'Janam Janam Dilwale',
        'Tum Hi Aana Jubin Nautiyal',
        'Mere Rashke Qamar Baadshaho',
        'Tera Hone Laga Hoon Atif Aslam'
    ];

    // Popular Bengali songs for random selection
    const bengaliSongs = [
        'Tumi Jake Bhalobaso Kishore Kumar',
        'Ei Meghla Dine Ekla Rabindra Sangeet',
        'Tomake Chai Arijit Singh',
        'Haay Re Meri Moto Kishore Kumar',
        'Chokher Bali Arijit Singh',
        'Tomar Khola Hawa Shaan',
        'Aamake Aamar Moto Arijit Singh',
        'Mithe Alo Shaan',
        'Prithibi Ta Naki Anupam Roy',
        'Boba Tunnel Anupam Roy',
        'Amake Amar Moto Thakte Dao Anupam Roy',
        'Tumi Robe Nirobe Rabindranath Tagore',
        'Ekla Chalo Re Rabindra Sangeet',
        'Moner Manush Lalon Fakir',
        'Bondhu Tin Din Tor Nachiketa',
        'Ore Grihabashi Kishore Kumar',
        'Jodi Tor Dak Sune Keu Na Ase Rabindra Sangeet',
        'Cholo Bodle Jai Arnob',
        'Shey Je Boshe Ache Rabindra Sangeet',
        'Amar Sonar Bangla Rabindranath Tagore'
    ];

    // Popular English songs for random selection
    const englishSongs = [
        'Shape of You Ed Sheeran',
        'Blinding Lights The Weeknd',
        'Someone Like You Adele',
        'Bohemian Rhapsody Queen',
        'Imagine John Lennon',
        'Perfect Ed Sheeran',
        'Hello Adele',
        'All of Me John Legend',
        'Let It Be The Beatles',
        'Levitating Dua Lipa',
        'Stay The Kid LAROI Justin Bieber',
        'Drivers License Olivia Rodrigo',
        'As It Was Harry Styles',
        'Anti Hero Taylor Swift',
        'Flowers Miley Cyrus',
        'Heat Waves Glass Animals',
        'Happier Than Ever Billie Eilish',
        'Circles Post Malone',
        'Watermelon Sugar Harry Styles',
        'Dance Monkey Tones and I'
    ];

    function playRandomHindiSong() {
        const randomSong = hindiSongs[Math.floor(Math.random() * hindiSongs.length)];
        const searchQuery = `${randomSong}`;
        const youtubeUrl = `https://music.youtube.com/search?q=${encodeURIComponent(searchQuery)}`;
        speak(`Playing ${randomSong}!`);
        window.open(youtubeUrl, '_blank');
    }

    function playRandomBengaliSong() {
        const randomSong = bengaliSongs[Math.floor(Math.random() * bengaliSongs.length)];
        const searchQuery = `${randomSong}`;
        const youtubeUrl = `https://music.youtube.com/search?q=${encodeURIComponent(searchQuery)}`;
        speak(`Playing ${randomSong}!`);
        window.open(youtubeUrl, '_blank');
    }

    function playRandomEnglishSong() {
        const randomSong = englishSongs[Math.floor(Math.random() * englishSongs.length)];
        const searchQuery = `${randomSong}`;
        const youtubeUrl = `https://music.youtube.com/search?q=${encodeURIComponent(searchQuery)}`;
        speak(`Playing ${randomSong}!`);
        window.open(youtubeUrl, '_blank');
    }

    const commands = {
        'what time is it': () => {
            const time = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });
            speak(`It's ${time}.`);
        },
        "what is today's date": () => {
            const date = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            speak(`Today is ${date}.`);
        },
        'what day is it': () => {
            const day = new Date().toLocaleDateString('en-US', { weekday: 'long' });
            speak(`Today is ${day}.`);
        },
        'what month is it': () => {
            const month = new Date().toLocaleDateString('en-US', { month: 'long' });
            speak(`It's ${month}.`);
        },
        'what year is it': () => {
            const year = new Date().getFullYear();
            speak(`It's ${year}.`);
        },
        'flip a coin': () => {
            const result = Math.random() < 0.5 ? 'heads' : 'tails';
            speak(`The coin landed on ${result}.`);
        },
        'roll a dice': () => {
            const result = Math.floor(Math.random() * 6) + 1;
            speak(`You rolled a ${result}.`);
        },
        'pick a number': () => {
            const result = Math.floor(Math.random() * 100) + 1;
            speak(`I picked the number ${result}.`);
        },
        'tell me a quote': () => {
            const quotes = [
                'The only way to do great work is to love what you do. - Steve Jobs',
                'Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill',
                'Believe you can and you\'re halfway there. - Theodore Roosevelt',
                'The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt',
                'It does not matter how slowly you go as long as you do not stop. - Confucius'
            ];
            speak(quotes[Math.floor(Math.random() * quotes.length)]);
        },
        'give me a tip': () => {
            const tip = tips[Math.floor(Math.random() * tips.length)];
            speak(`Here's a productivity tip: ${tip}`);
        },
        'give me a productivity tip': () => {
            const tip = tips[Math.floor(Math.random() * tips.length)];
            speak(`Try this: ${tip}`);
        },
        'tell me a fun fact': () => {
            const fact = funFacts[Math.floor(Math.random() * funFacts.length)];
            speak(`Here's something interesting: ${fact}`);
        },
        'tell me a joke': () => {
            const joke = jokes[Math.floor(Math.random() * jokes.length)];
            speak(joke);
        },
        'motivate me for work': () => {
            const message = [
                'Picture the reward waiting on the other side of this task. Let\'s make progress one small win at a time.',
                'Your future self will thank you for getting started today. What\'s the first five-minute step?',
                'You already have the skill. All that\'s left is focused time. Let\'s build momentum together.'
            ];
            speak(message[Math.floor(Math.random() * message.length)]);
        },
        'how are you': () => {
            speak("I'm feeling fully charged and ready to help. How can I support you right now?");
        },
        'thank you': () => {
            speak('Anytime! I\'m always here when you need me.');
        },
        'who are you': () => {
            speak("I'm Nextor, your AI voice assistant. I'm here to help you with tasks, answer questions, and make your day easier.");
        },
        'who created you': () => {
            speak("I was created by Mister Avik Ghosh.");
        },
        'who made you': () => {
            speak("I was created by Mister Avik Ghosh.");
        },
        'who is your creator': () => {
            speak("My creator is Mister Avik Ghosh.");
        },
        'who built you': () => {
            speak("I was built by Mister Avik Ghosh.");
        },
        'what can you do': () => {
            speak("I can play music, tell the time and date, check weather, set reminders, open websites, search the web, do calculations, tell jokes and facts, and much more. Just ask me!");
        },
        'hello': () => {
            const greetings = ['Hello! How can I help you?', 'Hi there! What can I do for you?', 'Hey! Ready to assist you.'];
            speak(greetings[Math.floor(Math.random() * greetings.length)]);
        },
        'hi': () => {
            const greetings = ['Hi! What do you need?', 'Hello! How may I assist you?', 'Hey! What\'s up?'];
            speak(greetings[Math.floor(Math.random() * greetings.length)]);
        },
        'good morning': () => {
            speak('Good morning! I hope you have a wonderful day ahead. How can I help you get started?');
        },
        'good night': () => {
            speak('Good night! Rest well and see you tomorrow.');
        },
        'goodbye': () => {
            speak('Goodbye! Come back anytime you need help.');
        }
    };

    async function handleCommands(rawCommand) {
        const command = rawCommand.toLowerCase().trim();
        userCommandEl.textContent = rawCommand;
        addMessage('user', rawCommand);

        let handled = false;
        let response = '';

        // Handle music/song commands
        if ((command.includes('play') || command.includes('start')) && (command.includes('song') || command.includes('music') || command.includes('songs'))) {
            if (command.includes('hindi') && !command.match(/\b(tum|kesariya|channa|raataan|mann|apna|kalank|gerua|janam)\b/i)) {
                // Only random if no specific song mentioned
                playRandomHindiSong();
                handled = true;
            } else if (command.includes('bengali') || command.includes('bangla')) {
                playRandomBengaliSong();
                handled = true;
            } else if (command.includes('english') && !command.match(/\b(shape|blinding|someone|perfect|hello|imagine)\b/i)) {
                playRandomEnglishSong();
                handled = true;
            } else {
                // Extract song name - improved extraction
                let songName = command
                    .replace(/^(play|start)\s+/i, '')
                    .replace(/\s+(song|music|songs)$/i, '')
                    .replace(/\ba\b/gi, '')
                    .replace(/\bthe\b/gi, '')
                    .trim();
                
                if (songName && songName.length > 2) {
                    const searchQuery = encodeURIComponent(songName);
                    const youtubeUrl = `https://music.youtube.com/search?q=${searchQuery}`;
                    speak(`Playing ${songName} on YouTube Music!`);
                    const newWindow = window.open(youtubeUrl, '_blank');
                    if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                        speak('Please allow popups for this site to play music');
                    }
                } else {
                    // Default to Hindi if no language specified
                    playRandomHindiSong();
                }
                handled = true;
            }
        }
        
        // Special case: direct Hindi/Bengali song command without 'play'
        if (!handled && (command.includes('hindi song') || command.includes('hindi songs'))) {
            playRandomHindiSong();
            handled = true;
        }
        
        if (!handled && (command.includes('bengali song') || command.includes('bengali songs'))) {
            playRandomBengaliSong();
            handled = true;
        }

        // Check exact command matches first
        if (commands[command]) {
            commands[command]();
            handled = true;
        }
        // Check for partial matches if exact match not found
        // Only match if the key is a complete word or phrase within the command
        else if (!handled) {
            for (const [key, func] of Object.entries(commands)) {
                // Create regex for whole word/phrase matching
                const keyRegex = new RegExp(`\\b${key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
                if (keyRegex.test(command)) {
                    func();
                    handled = true;
                    break;
                }
            }
        }
        
        // Check if user wants to open a website
        if (!handled && (command.includes('open') || command.includes('launch') || command.includes('go to'))) {
            // Try to extract site name after "open", "launch", or "go to"
            let siteName = '';
            if (command.includes('open')) {
                siteName = command.substring(command.indexOf('open') + 4).trim();
            } else if (command.includes('launch')) {
                siteName = command.substring(command.indexOf('launch') + 6).trim();
            } else if (command.includes('go to')) {
                siteName = command.substring(command.indexOf('go to') + 5).trim();
            }
            
            // Clean up the site name
            siteName = siteName.toLowerCase().replace(/[,\.!\?]/g, '').trim();
            
            // Check if it's a known website
            if (siteName && siteName.length > 0) {
                const url = websiteMap[siteName] || (siteName.includes('.') ? (siteName.startsWith('http') ? siteName : `https://${siteName}`) : `https://www.${siteName}.com`);
                openWebsite(url, `Opening ${siteName}...`);
                handled = true;
            }
        } 
        
        if (!handled && (command.startsWith('search for') || command.includes('google'))) {
            let query = '';
            if (command.startsWith('search for')) {
                query = command.substring('search for'.length).trim();
            } else if (command.includes('search')) {
                query = command.substring(command.indexOf('search') + 6).trim();
            } else if (command.includes('google')) {
                query = command.replace('google', '').trim();
            }
            
            if (query && query.length > 0) {
                openWebsite(`https://www.google.com/search?q=${encodeURIComponent(query)}`, `Searching Google for ${query}`);
                handled = true;
            }
        } 
        
        if (!handled && command.includes('weather')) {
            await requestWeatherForCurrentLocation({ speakResponse: true });
            handled = true;
        } else if (command.startsWith('remind me to')) {
            const payload = command.substring('remind me to'.length).trim();
            let time = null;
            let text = payload;
            let scheduledTime = null;

            const timeIndicators = [' at ', ' in ', ' tomorrow'];
            let timeIndex = -1;
            let indicator = '';

            for (const ind of timeIndicators) {
                const idx = payload.toLowerCase().lastIndexOf(ind);
                if (idx > timeIndex) {
                    timeIndex = idx;
                    indicator = ind;
                }
            }

            if (timeIndex !== -1) {
                text = payload.substring(0, timeIndex).trim();
                time = payload.substring(timeIndex + indicator.length).trim();
                if (indicator === ' tomorrow') {
                    time = `tomorrow ${time}`;
                }
                const parsedDate = parseTimeToDate(time);
                if (parsedDate) {
                    scheduledTime = parsedDate.getTime();
                }
            }

            const reminder = {
                id: Date.now() + Math.random(),
                text,
                time,
                scheduledTime
            };

            reminders.push(reminder);
            saveReminders();
            renderReminders();

            if (scheduledTime) {
                scheduleReminder(reminder, reminders.length - 1);
                const scheduledDate = new Date(scheduledTime);
                speak(`Got it. I’ll remind you to ${text} at ${scheduledDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}.`);
            } else {
                speak(`I noted the reminder to ${text}. I couldn't understand the time, but it's saved in your list.`);
            }
            handled = true;
        }
        
        // Math calculation - handle both "calculate X" and direct math expressions
        if (!handled) {
            let mathExpression = null;
            let originalCommand = command;
            
            if (command.startsWith('calculate')) {
                // Extract expression after "calculate"
                mathExpression = command
                    .replace(/^calculate\s*/i, '')
                    .trim();
            } else if (command.startsWith('what is') || command.startsWith('what\'s') || command.startsWith('whats')) {
                // Only treat as math if it contains numbers AND math keywords
                const afterWhatIs = command.replace(/^(what is|what's|whats)\s*/i, '').trim();
                const hasMathKeywords = /\b(plus|minus|times|multiplied|divided|divide|over|into)\b/i.test(afterWhatIs);
                const hasNumbers = /\d/.test(afterWhatIs);
                
                // MUST have BOTH numbers AND math keywords to be treated as math
                // This prevents "what is machine learning" from being treated as math
                if (hasNumbers && hasMathKeywords) {
                    mathExpression = afterWhatIs;
                }
            } else {
                // Check if command is a direct math expression (e.g., "5+7", "3*2", "12 divided by 4")
                const testMath = command
                    .replace(/plus/gi, '+')
                    .replace(/minus/gi, '-')
                    .replace(/times/gi, '*')
                    .replace(/multiplied\s*by/gi, '*')
                    .replace(/divided\s*by/gi, '/')
                    .replace(/divide\s*by/gi, '/')
                    .replace(/\s+/g, '');
                
                if (/^[\d+\-*/.()]+$/.test(testMath) && /[+\-*\/]/.test(testMath)) {
                    mathExpression = command;
                }
            }
            
            if (mathExpression) {
                // Convert common spoken math to operators
                mathExpression = mathExpression
                    .replace(/\s+/g, ' ')
                    .replace(/x/gi, '*')
                    .replace(/plus/gi, '+')
                    .replace(/minus/gi, '-')
                    .replace(/times/gi, '*')
                    .replace(/multiplied\s*by/gi, '*')
                    .replace(/into/gi, '*')
                    .replace(/divided\s*by/gi, '/')
                    .replace(/divide\s*by/gi, '/')
                    .replace(/over/gi, '/')
                    .replace(/\s+/g, '');
                
                try {
                    // Safer calculation: only allow numbers and basic math operators
                    if (!/^[\d+\-*/.()\s]+$/.test(mathExpression)) {
                        throw new Error('Invalid characters in expression');
                    }
                    const result = Function('"use strict"; return (' + mathExpression + ')')();
                    
                    // Round to 2 decimal places if needed
                    const finalResult = Number.isInteger(result) ? result : Math.round(result * 100) / 100;
                    
                    speak(`The answer is ${finalResult}.`);
                    handled = true;
                } catch (error) {
                    // If it fails, it's not a math expression - let it fall through to AI
                    console.log('Math evaluation failed, will send to AI:', error.message);
                }
            }
        }
        
        if (!handled && knowledge[command]) {
            speak(knowledge[command]);
            handled = true;
        }

        if (!handled) {
            const reply = await fetchChatReply(rawCommand);
            if (reply) {
                speak(reply);
                handled = true;
            }
        }

        if (!handled) {
            openWebsite(`https://www.google.com/search?q=${encodeURIComponent(rawCommand)}`, `I'm not sure about that. Let me search the web for ${rawCommand}.`);
        }
    }

    // --- Event listeners ---
    // Mobile button
    if (startBtn) {
        startBtn.addEventListener('click', handleStartClick);
    }
    
    // Desktop button
    if (startBtnDesktop) {
        startBtnDesktop.addEventListener('click', handleStartClick);
    }
    
    function handleStartClick() {
        if (isListening) {
            recognition.stop();
            isListening = false;
            updateButtonText('activate');
            updateStatus('idle');
            return;
        }
        
        // Only greet on first activation, then just start listening
        if (!hasGreeted) {
            hasGreeted = true;
            speak("Hi, I'm Nextor. What can I help you today?", {
                onend: () => {
                    if (!isListening) {
                        recognition.start();
                    }
                }
            });
        } else {
            // Subsequent activations - just start listening immediately
            recognition.start();
        }
    }
    
    function updateButtonText(state) {
        const activateHTML = '<span class="flex items-center gap-2"><i class="fas fa-play"></i><span>Activate</span></span><small class="block text-xs uppercase tracking-wider opacity-90 mt-1">Click & Speak</small>';
        const listeningHTML = '<span class="flex items-center gap-2"><i class="fas fa-ear-listen"></i><span>Listening...</span></span><small class="block text-xs uppercase tracking-wider opacity-90 mt-1">Click to Stop</small>';
        
        if (state === 'activate') {
            if (startBtn) startBtn.innerHTML = activateHTML;
            if (startBtnDesktop) startBtnDesktop.innerHTML = activateHTML;
        } else if (state === 'listening') {
            if (startBtn) startBtn.innerHTML = listeningHTML;
            if (startBtnDesktop) startBtnDesktop.innerHTML = listeningHTML;
        }
    }

    recognition.onstart = () => {
        isListening = true;
        if (startBtn) startBtn.disabled = false;
        if (startBtnDesktop) startBtnDesktop.disabled = false;
        updateButtonText('listening');
        updateStatus('listening');
    };

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript.trim();
        if (transcript) {
            await handleCommands(transcript);
        }
    };

    recognition.onend = () => {
        isListening = false;
        updateButtonText('activate');
        updateStatus('idle');
    };

    recognition.onerror = (event) => {
        isListening = false;
        let message = 'Sorry, something went wrong while listening.';
        
        if (event.error === 'no-speech') {
            message = "I didn't catch that. Click the button and try speaking again.";
        } else if (event.error === 'audio-capture') {
            message = "I can't hear you. Please check your microphone and try again.";
        } else if (event.error === 'not-allowed') {
            message = 'Microphone access denied. Please enable microphone permissions in your browser settings.';
            if (startBtn) startBtn.disabled = true;
            if (startBtnDesktop) startBtnDesktop.disabled = true;
            setTimeout(() => { 
                if (startBtn) startBtn.disabled = false;
                if (startBtnDesktop) startBtnDesktop.disabled = false;
            }, 3000);
        } else if (event.error === 'network') {
            message = 'Network error. Please check your internet connection.';
        } else if (event.error === 'aborted') {
            return; // Don't show error for manual stops
        }
        
        speak(message);
        updateStatus('idle');
        updateButtonText('activate');
    };

    // Clear chat history button
    clearHistoryBtn.addEventListener('click', () => {
        conversationHistory = [];
        saveConversationHistory();
        renderConversation();
        
        // Clear the visible command and response displays
        if (userCommandEl) {
            userCommandEl.textContent = 'Waiting for your command...';
        }
        if (assistantResponseEl) {
            assistantResponseEl.textContent = 'Click activate and speak to me!';
        }
        
        speak('Chat history cleared successfully. Click activate and speak to me!');
    });

    // Add reminder button
    addReminderBtn.addEventListener('click', () => {
        const task = reminderTaskInput.value.trim();
        const time = reminderTimeInput.value.trim();
        
        // Enhanced input validation
        if (!task || task.length < 2) {
            speak('Please enter a valid task description');
            return;
        }
        
        if (task.length > 200) {
            speak('Task description is too long. Please keep it under 200 characters');
            return;
        }
        
        if (!time) {
            speak('Please specify when you want to be reminded');
            return;
        }
        
        const scheduledTime = parseTimeToDate(time);
        if (!scheduledTime) {
            speak("I couldn't understand the time. Try formats like 5pm, in 30 minutes, or tomorrow at 9am");
            return;
        }
        
        const newReminder = {
            id: Date.now(),
            text: task,
            time: time,
            scheduledTime: scheduledTime.getTime()
        };
        
        reminders.push(newReminder);
        saveReminders();
        scheduleReminder(newReminder, reminders.length - 1);
        renderReminders();
        
        // Clear inputs
        reminderTaskInput.value = '';
        reminderTimeInput.value = '';
        
        const timeStr = scheduledTime.toLocaleString([], { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        speak(`Reminder set for ${task} at ${timeStr}`);
    });

    quickPromptButtons.forEach((button) => {
        button.addEventListener('click', async () => {
            const command = button.dataset.command;
            await handleCommands(command);
        });
    });

    if (refreshWeatherBtn) {
        refreshWeatherBtn.addEventListener('click', () => {
            requestWeatherForCurrentLocation({ speakResponse: true });
        });
    }

    // --- Initialization ---
    loadConversationHistory();
    renderReminders();
    cleanupExpiredReminders(); // Remove old reminders on startup
    requestNotificationPermission();
    
    // Reschedule active reminders
    reminders.forEach((reminder, idx) => {
        if (reminder.scheduledTime) {
            scheduleReminder(reminder, idx);
        }
    });

    // Start background reminder watcher for mobile devices
    startReminderWatcher();

    // Check backend availability in background and update UI
    checkBackendAvailability().then(available => {
        if (available) {
            console.log('✅ Backend server is online');
            if (backendStatus) {
                backendStatus.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 status-online';
                backendStatus.innerHTML = '<div class="w-2 h-2 bg-white rounded-full"></div><span class="hidden sm:inline">Online</span>';
            }
            if (backendStatusDesktop) {
                backendStatusDesktop.className = 'px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 status-online';
                backendStatusDesktop.innerHTML = '<div class="w-2.5 h-2.5 bg-white rounded-full"></div><span>Server Online</span>';
            }
        } else {
            console.warn('❌ Backend server is offline. Weather and AI chat features will be unavailable.');
            if (backendStatus) {
                backendStatus.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 status-offline';
                backendStatus.innerHTML = '<div class="w-2 h-2 bg-white rounded-full animate-pulse"></div><span class="hidden sm:inline">Offline</span>';
            }
            if (backendStatusDesktop) {
                backendStatusDesktop.className = 'px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 status-offline';
                backendStatusDesktop.innerHTML = '<div class="w-2.5 h-2.5 bg-white rounded-full animate-pulse"></div><span>Server Offline</span>';
            }
        }
    });

    // Initial greeting
    addMessage('assistant', '👋 Welcome! I\'m Nextor, your AI voice assistant. Click "Activate Nextor" to get started.');
    showWeatherStatus('📍 Click refresh to fetch live weather (location permission required)');

    // Preload voices and use the default system voice
    if ('speechSynthesis' in window) {
        // Load voices
        const loadVoices = () => {
            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {
                // Use default voice (usually the best quality)
                // Or find a preferred English voice
                const defaultVoice = voices.find((v) => v.default) || voices[0];
                const englishVoice = voices.find((v) => v.lang.startsWith('en-US') || v.lang.startsWith('en-GB'));
                
                utterance.voice = englishVoice || defaultVoice;
                console.log('Voice selected:', utterance.voice?.name || 'Default system voice');
            }
        };
        
        // Try to load voices immediately
        loadVoices();
        
        // Also listen for voices changed event (for browsers that load voices asynchronously)
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = loadVoices;
        }
    }
    
    // Log successful initialization
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Space to toggle listening (when not typing in input fields)
        if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            e.preventDefault();
            handleStartClick();
        }
        
        // Escape to stop listening
        if (e.code === 'Escape' && isListening) {
            e.preventDefault();
            handleStartClick();
        }
    });

    // ========================================
    // Chat Functionality (Disabled - Chat panel removed)
    // ========================================
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat');
    const chatMessages = document.getElementById('chat-messages');
    const clearChatBtn = document.getElementById('clear-chat');
    
    // Only initialize if elements exist
    if (chatInput && sendChatBtn && chatMessages && clearChatBtn) {
        let chatHistory = [];

        function addChatMessage(message, isUser = true) {
            // Remove welcome message if exists
            const welcome = chatMessages.querySelector('.text-center');
            if (welcome) welcome.remove();

            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
            
            if (isUser) {
                messageDiv.innerHTML = `
                    <div class="message-bubble user">
                        ${message}
                    </div>
                `;
            } else {
                messageDiv.innerHTML = `
                    <div class="message-bubble bot">
                        <i class="fas fa-robot bot-icon"></i>${message}
                    </div>
                `;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        async function sendChatMessage() {
            const message = chatInput.value.trim();
            if (!message) return;

            // Add user message
            addChatMessage(message, true);
            chatInput.value = '';

            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'chat-message bot';
            typingDiv.id = 'typing-indicator';
            typingDiv.innerHTML = `
                <div class="message-bubble bot">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const reply = await fetchChatReply(message, chatHistory);
                
                // Remove typing indicator
                document.getElementById('typing-indicator')?.remove();
                
                // Add bot response
                addChatMessage(reply, false);
                
                // Update history
                chatHistory.push({ role: 'user', message });
                chatHistory.push({ role: 'assistant', message: reply });
                
                // Keep only last 10 messages in history
                if (chatHistory.length > 20) {
                    chatHistory = chatHistory.slice(-20);
                }
            } catch (error) {
                document.getElementById('typing-indicator')?.remove();
                addChatMessage('Sorry, I encountered an error. Please try again.', false);
            }
        }

        sendChatBtn.addEventListener('click', sendChatMessage);
        
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });

        clearChatBtn.addEventListener('click', () => {
            chatHistory = [];
            chatMessages.innerHTML = `
                <div class="text-center py-8">
                    <div class="w-12 h-12 mx-auto mb-3 rounded-full bg-purple-500/20 flex items-center justify-center">
                        <i class="fas fa-robot text-purple-400 text-xl"></i>
                    </div>
                    <p class="text-gray-400 text-sm font-medium">Start chatting with Nextor</p>
                    <p class="text-gray-500 text-xs mt-1">Type your message below</p>
                </div>
            `;
        });
    }

    // Debug logging (only in development)
    const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isDev) {
        console.log('✅ Nextor initialized successfully');
        console.log('📡 Backend URL:', API_BASE_URL);
        console.log('🎤 Speech recognition:', SpeechRecognition ? 'Available' : 'Not supported');
    }
});