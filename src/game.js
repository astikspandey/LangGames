// ============================================================
// CONFIGURATION - Easy to modify
// ============================================================
// Use current domain (works for both localhost and production)
const SERVER_URL = window.location.origin;
// ============================================================

// Data persistence module (Supabase with localStorage fallback)
const DataManager = {
    apiUrl: `${SERVER_URL}/api`,
    autoSaveInterval: null,
    isOfflineMode: false,
    offlineModeIndicator: null,

    // LocalStorage fallback functions
    saveToLocalStorage(gameData) {
        try {
            localStorage.setItem('langfight_gamedata', JSON.stringify(gameData));
            console.log('✓ Game data saved to localStorage (offline mode)');
            return true;
        } catch (error) {
            console.error('✗ Failed to save to localStorage:', error);
            return false;
        }
    },

    loadFromLocalStorage() {
        try {
            const data = localStorage.getItem('langfight_gamedata');
            if (data) {
                const gameData = JSON.parse(data);
                console.log('✓ Game data loaded from localStorage (offline mode)');
                return gameData;
            }
            return null;
        } catch (error) {
            console.error('✗ Failed to load from localStorage:', error);
            return null;
        }
    },

    showOfflineIndicator() {
        if (!this.offlineModeIndicator) {
            this.offlineModeIndicator = document.createElement('div');
            this.offlineModeIndicator.id = 'offlineIndicator';
            this.offlineModeIndicator.innerHTML = '📵 Offline Mode - Saving Locally';
            this.offlineModeIndicator.style.cssText = `
                position: fixed;
                top: 50px;
                right: 10px;
                background: rgba(255, 152, 0, 0.95);
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                z-index: 1000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                animation: slideIn 0.3s ease-out;
            `;
            document.body.appendChild(this.offlineModeIndicator);
        }
    },

    hideOfflineIndicator() {
        if (this.offlineModeIndicator) {
            this.offlineModeIndicator.remove();
            this.offlineModeIndicator = null;
        }
    },

    async saveGameData() {
        // Get user_id from localStorage (WalkerAuth) or use default
        const userEmail = localStorage.getItem('user_email');
        const userId = userEmail || localStorage.getItem('user_id') || 'default_user';

        const gameData = {
            user_id: userId,
            level: game.level,
            score: game.score,
            highScore: this.getHighScore(),
            gamesPlayed: this.getGamesPlayed(),
            lastPlayed: new Date().toISOString(),
            stats: {
                totalScore: this.getTotalScore(),
                levelsCompleted: game.level > 1 ? game.level - 1 : 0
            }
        };

        // Try Supabase first
        try {
            const response = await fetch(`${this.apiUrl}/data/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(gameData)
            });

            if (response.ok) {
                console.log('✓ Game data saved to Supabase');
                // If we were in offline mode, we're back online now
                if (this.isOfflineMode) {
                    this.isOfflineMode = false;
                    this.hideOfflineIndicator();
                    console.log('✓ Back online - Supabase connection restored');
                }
                return true;
            } else {
                throw new Error('Server responded with error');
            }
        } catch (error) {
            // Supabase failed, fallback to localStorage
            console.error('✗ Supabase unavailable, using localStorage fallback:', error);

            if (!this.isOfflineMode) {
                this.isOfflineMode = true;
                this.showOfflineIndicator();
            }

            return this.saveToLocalStorage(gameData);
        }
    },

    async loadGameData() {
        // Get user_id from localStorage (WalkerAuth) or use default
        const userEmail = localStorage.getItem('user_email');
        const userId = userEmail || localStorage.getItem('user_id') || 'default_user';

        // Try Supabase first
        try {
            const response = await fetch(`${this.apiUrl}/data/load?user_id=${encodeURIComponent(userId)}`);

            if (response.ok) {
                const data = await response.json();
                if (data && Object.keys(data).length > 0) {
                    console.log('✓ Game data loaded from Supabase');
                    // If we were in offline mode, we're back online now
                    if (this.isOfflineMode) {
                        this.isOfflineMode = false;
                        this.hideOfflineIndicator();
                        console.log('✓ Back online - Supabase connection restored');
                    }
                    return data;
                } else {
                    console.log('ℹ No saved game data found in Supabase');
                    // Try localStorage as fallback
                    return this.loadFromLocalStorage();
                }
            } else {
                throw new Error('Server responded with error');
            }
        } catch (error) {
            // Supabase failed, fallback to localStorage
            console.error('✗ Supabase unavailable, using localStorage fallback:', error);

            if (!this.isOfflineMode) {
                this.isOfflineMode = true;
                this.showOfflineIndicator();
            }

            return this.loadFromLocalStorage();
        }
    },

    startAutoSave() {
        // Auto-save every 30 seconds
        this.autoSaveInterval = setInterval(() => {
            if (!game.isGameOver) {
                this.saveGameData();
            }
        }, 30000);
    },

    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    },

    getHighScore() {
        const saved = localStorage.getItem('highScore');
        return saved ? parseInt(saved) : 0;
    },

    getGamesPlayed() {
        const saved = localStorage.getItem('gamesPlayed');
        return saved ? parseInt(saved) : 0;
    },

    getTotalScore() {
        const saved = localStorage.getItem('totalScore');
        return saved ? parseInt(saved) : 0;
    },

    updateStats() {
        const gamesPlayed = this.getGamesPlayed() + 1;
        const totalScore = this.getTotalScore() + game.score;

        localStorage.setItem('gamesPlayed', gamesPlayed.toString());
        localStorage.setItem('totalScore', totalScore.toString());

        if (game.score > this.getHighScore()) {
            localStorage.setItem('highScore', game.score.toString());
        }
    }
};

// Game state
const game = {
    canvas: null,
    ctx: null,
    score: 0,
    lives: 3,
    level: 1,
    tanks: [],
    activeTanks: [], // Tanks currently on screen
    draggableItems: [], // Available items to drag
    matchedCounts: {}, // Count of how many times each item has been matched
    fullyMatchedItems: new Set(), // Items that have ALL instances destroyed
    mistakes: [], // Track mistakes {english, kannada, attempted}
    missedTanks: [], // Track tanks that reached the end
    isGameOver: false,
    spawnInterval: null,
    baseSpawnRate: 3000,
    animationFrame: null,
    draggedElement: null,
    canvasRect: null,
    speedMultiplier: 1,
    savedLevel: 1, // Level to return to if player loses immediately after skip
    hasPlayedCurrentLevel: false, // Track if player has played current level
    particles: [], // Visual feedback particles
    audioContext: null, // Audio context for sound effects
    selectedWord: null // Currently selected word for click mode (levels 1-3)
};

// Path waypoints based on the map image
const pathWaypoints = [
    { x: 50, y: 140 },
    { x: 180, y: 140 },
    { x: 180, y: 110 },
    { x: 315, y: 110 },
    { x: 315, y: 140 },
    { x: 475, y: 140 },
    { x: 475, y: 360 },
    { x: 515, y: 360 },
    { x: 515, y: 480 },
    { x: 610, y: 480 },
    { x: 610, y: 520 },
    { x: 730, y: 520 },
    { x: 730, y: 590 },
    { x: 945, y: 590 },
    { x: 945, y: 640 },
    { x: 730, y: 640 },
    { x: 730, y: 750 },
    { x: 515, y: 750 },
    { x: 515, y: 640 },
    { x: 210, y: 640 },
    { x: 210, y: 920 },
    { x: 250, y: 920 }
];

// Tank class
class Tank {
    constructor(vocabulary, vehicleType) {
        this.vocabulary = vocabulary;
        this.vehicleType = vehicleType; // 'suv', 'tank', or 'blimp'
        this.waypointIndex = 0;
        this.x = pathWaypoints[0].x;
        this.y = pathWaypoints[0].y;
        this.speed = this.getSpeed();
        this.size = this.getSize();
        this.color = this.getColor();
        this.progress = 0;
        this.spawnTime = Date.now(); // Track when tank was spawned
    }

    getSpeed() {
        // First 3 levels are much slower for learning
        let baseSpeed;
        if (game.level === 1) {
            baseSpeed = 0.3; // Very slow for first level
        } else if (game.level === 2) {
            baseSpeed = 0.5; // Slow for second level
        } else if (game.level === 3) {
            baseSpeed = 0.7; // Still slow for third level
        } else {
            baseSpeed = 1 + (game.level * 0.15); // Normal progression after level 3
        }

        switch (this.vehicleType) {
            case 'suv': return baseSpeed * 1.8;
            case 'tank': return baseSpeed * 1.2;
            case 'blimp': return baseSpeed * 0.7;
            default: return baseSpeed;
        }
    }

    getSize() {
        switch (this.vehicleType) {
            case 'suv': return { width: 35, height: 25 };
            case 'tank': return { width: 50, height: 35 };
            case 'blimp': return { width: 80, height: 50 };
            default: return { width: 50, height: 35 };
        }
    }

    getColor() {
        switch (this.vehicleType) {
            case 'suv': return '#4CAF50';
            case 'tank': return '#FF9800';
            case 'blimp': return '#9C27B0';
            default: return '#FF9800';
        }
    }

    update() {
        if (this.waypointIndex >= pathWaypoints.length - 1) {
            return false;
        }

        const currentWaypoint = pathWaypoints[this.waypointIndex];
        const nextWaypoint = pathWaypoints[this.waypointIndex + 1];

        const dx = nextWaypoint.x - currentWaypoint.x;
        const dy = nextWaypoint.y - currentWaypoint.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Apply speed multiplier
        this.progress += this.speed * game.speedMultiplier;

        if (this.progress >= distance) {
            this.waypointIndex++;
            this.progress = 0;
            if (this.waypointIndex >= pathWaypoints.length - 1) {
                return false;
            }
        } else {
            const ratio = this.progress / distance;
            this.x = currentWaypoint.x + dx * ratio;
            this.y = currentWaypoint.y + dy * ratio;
        }

        return true;
    }

    draw(ctx) {
        // Draw vehicle body
        ctx.fillStyle = this.color;
        ctx.fillRect(
            this.x - this.size.width / 2,
            this.y - this.size.height / 2,
            this.size.width,
            this.size.height
        );

        // Draw border
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(
            this.x - this.size.width / 2,
            this.y - this.size.height / 2,
            this.size.width,
            this.size.height
        );

        // Draw vehicle details based on type
        if (this.vehicleType === 'tank') {
            // Tank turret
            ctx.fillStyle = '#D84315';
            ctx.fillRect(this.x - 10, this.y - 8, 20, 16);
            // Tank barrel
            ctx.fillRect(this.x + 10, this.y - 3, 15, 6);
        } else if (this.vehicleType === 'blimp') {
            // Blimp gondola
            ctx.fillStyle = '#7B1FA2';
            ctx.fillRect(this.x - 15, this.y + 15, 30, 10);
        } else if (this.vehicleType === 'suv') {
            // SUV windows
            ctx.fillStyle = '#81C784';
            ctx.fillRect(this.x - 8, this.y - 6, 16, 12);
        }

        // Draw English text on vehicle
        ctx.fillStyle = '#FFF';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        const maxWidth = this.size.width - 8;
        const text = this.vocabulary.english;

        ctx.fillText(text, this.x, this.y, maxWidth);
    }
}

// Particle class for visual feedback
class Particle {
    constructor(x, y, color, type = 'correct') {
        this.x = x;
        this.y = y;
        this.color = color;
        this.type = type;
        this.life = 1.0;
        this.size = type === 'correct' ? 8 : 15;

        if (type === 'correct') {
            // Explosion particles for correct match
            const angle = Math.random() * Math.PI * 2;
            const speed = 2 + Math.random() * 3;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
        } else {
            // Wrong match - just fades in place
            this.vx = 0;
            this.vy = 0;
        }
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.02;

        if (this.type === 'correct') {
            this.vy += 0.1; // Gravity for correct particles
        }

        return this.life > 0;
    }

    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;

        if (this.type === 'correct') {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        } else {
            // Wrong match - draw X
            ctx.strokeStyle = this.color;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(this.x - this.size, this.y - this.size);
            ctx.lineTo(this.x + this.size, this.y + this.size);
            ctx.moveTo(this.x + this.size, this.y - this.size);
            ctx.lineTo(this.x - this.size, this.y + this.size);
            ctx.stroke();
        }

        ctx.restore();
    }
}

// Audio functions
function initAudio() {
    if (!game.audioContext) {
        try {
            game.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.log('Web Audio API not supported');
        }
    }
}

function playSound(frequency, duration, type = 'sine') {
    if (!game.audioContext) return;

    const oscillator = game.audioContext.createOscillator();
    const gainNode = game.audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(game.audioContext.destination);

    oscillator.frequency.value = frequency;
    oscillator.type = type;

    gainNode.gain.setValueAtTime(0.3, game.audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, game.audioContext.currentTime + duration);

    oscillator.start(game.audioContext.currentTime);
    oscillator.stop(game.audioContext.currentTime + duration);
}

function playCorrectSound() {
    // Happy ascending tone
    playSound(523.25, 0.1, 'sine'); // C5
    setTimeout(() => playSound(659.25, 0.15, 'sine'), 50); // E5
}

function playWrongSound() {
    // Descending error tone
    playSound(200, 0.2, 'sawtooth');
}

function createParticles(x, y, color, type, count = 10) {
    for (let i = 0; i < count; i++) {
        game.particles.push(new Particle(x, y, color, type));
    }
}

function showWelcomeBackMessage() {
    const canvas = game.canvas;
    const ctx = game.ctx;

    // Store game state temporarily
    const tempGameOver = game.isGameOver;
    game.isGameOver = true; // Pause game loop

    // Draw welcome message
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#4CAF50';
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Welcome Back!', canvas.width / 2, canvas.height / 2 - 50);
    ctx.fillStyle = '#FFF';
    ctx.font = 'bold 28px Arial';
    ctx.fillText(`Level ${game.level} • Score: ${game.score}`, canvas.width / 2, canvas.height / 2 + 10);
    ctx.font = '18px Arial';
    ctx.fillStyle = '#CCC';
    ctx.fillText('Continuing from your last save...', canvas.width / 2, canvas.height / 2 + 50);

    // Resume game after 2 seconds
    setTimeout(() => {
        game.isGameOver = tempGameOver;
    }, 2000);
}

// Device detection
const DeviceInfo = {
    isMobile() {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        // Check for mobile devices
        return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());
    },

    isTablet() {
        const userAgent = navigator.userAgent.toLowerCase();
        return /(ipad|tablet|playbook|silk)|(android(?!.*mobile))/i.test(userAgent);
    },

    getDeviceType() {
        if (this.isMobile() && !this.isTablet()) return 'mobile';
        if (this.isTablet()) return 'tablet';
        return 'desktop';
    },

    applyMobileStyles() {
        const deviceType = this.getDeviceType();
        document.body.classList.add(`device-${deviceType}`);

        if (deviceType === 'mobile') {
            // Apply mobile-specific adjustments
            const canvas = document.getElementById('gameCanvas');
            if (canvas) {
                canvas.width = 800;
                canvas.height = 800;
            }
        }
    }
};

// Tutorial management
const Tutorial = {
    currentStep: 0,
    totalSteps: 4,

    show() {
        document.getElementById('tutorialOverlay').style.display = 'flex';
        game.isGameOver = true; // Pause game during tutorial
        this.currentStep = 0; // Reset to first step
        this.updateStep(); // Update display
    },

    hide() {
        document.getElementById('tutorialOverlay').style.display = 'none';
        game.isGameOver = false; // Resume game
        localStorage.setItem('tutorialCompleted', 'true');
    },

    nextStep() {
        if (this.currentStep < this.totalSteps - 1) {
            this.currentStep++;
            this.updateStep();
        } else {
            this.hide();
        }
    },

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateStep();
        }
    },

    updateStep() {
        // Update steps visibility
        const steps = document.querySelectorAll('.tutorial-step');
        steps.forEach((step, index) => {
            step.classList.toggle('active', index === this.currentStep);
        });

        // Update dots
        const dots = document.querySelectorAll('.tutorial-dots .dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === this.currentStep);
        });

        // Update buttons
        const prevBtn = document.getElementById('tutorialPrev');
        const nextBtn = document.getElementById('tutorialNext');

        prevBtn.disabled = this.currentStep === 0;
        nextBtn.textContent = this.currentStep === this.totalSteps - 1 ? 'Start Playing!' : 'Next →';
    },

    init() {
        // Previous button
        document.getElementById('tutorialPrev').addEventListener('click', () => {
            this.prevStep();
        });

        // Next button
        document.getElementById('tutorialNext').addEventListener('click', () => {
            this.nextStep();
        });

        // Skip button
        document.getElementById('tutorialSkip').addEventListener('click', () => {
            this.hide();
        });

        // Tutorial reopen button
        const tutorialBtn = document.getElementById('tutorialBtn');
        if (tutorialBtn) {
            tutorialBtn.addEventListener('click', () => {
                this.show();
            });
        }
    }
};

// Initialize game
async function initGame() {
    game.canvas = document.getElementById('gameCanvas');
    game.ctx = game.canvas.getContext('2d');
    game.canvasRect = game.canvas.getBoundingClientRect();

    initAudio();

    // Load saved data if available
    let hasRestoredData = false;
    const savedData = await DataManager.loadGameData();
    if (savedData && savedData.level) {
        console.log('✓ Previous save found - continuing from level', savedData.level);

        // Restore game state
        game.level = savedData.level || 1;
        game.score = savedData.score || 0;
        game.savedLevel = savedData.level || 1;
        hasRestoredData = true;
    }

    resetGame(hasRestoredData); // Pass true to skip level/score reset if restoring
    initializeDraggableItems();
    startSpawning();
    gameLoop();
    setupEventListeners();

    // Detect device and apply mobile styles
    DeviceInfo.applyMobileStyles();

    // Initialize tutorial
    Tutorial.init();

    // Show tutorial if no saved data and first time user
    if (!hasRestoredData && !localStorage.getItem('tutorialCompleted')) {
        setTimeout(() => {
            Tutorial.show();
        }, 500);
    }

    // Show welcome back message AFTER game loop starts (if data was restored)
    if (hasRestoredData) {
        setTimeout(() => {
            showWelcomeBackMessage();
        }, 300);
    }

    // Start auto-save
    DataManager.startAutoSave();

    // Save on window close
    window.addEventListener('beforeunload', () => {
        DataManager.saveGameData();
    });
}

// Reset game state
function resetGame(skipLevelReset = false) {
    // Only reset score/lives, keep level if skipLevelReset is true
    if (!skipLevelReset) {
        game.score = 0;
        // Keep current level - don't reset to 1
        // game.level = 1; // REMOVED - now retries current level
    }

    game.lives = 3;
    game.tanks = [];
    game.activeTanks = [];
    game.matchedCounts = {};
    game.fullyMatchedItems.clear();
    game.mistakes = [];
    game.missedTanks = [];
    game.isGameOver = false;

    updateUI();
    hideGameOver();
}

// Initialize draggable items based on level
function initializeDraggableItems() {
    const vocabulary = getVocabularyForLevel(game.level);
    game.draggableItems = [...vocabulary];

    renderDraggableItems();
}

// Render draggable items in sidebar
function renderDraggableItems() {
    const container = document.getElementById('draggableItems');
    container.innerHTML = '';

    game.draggableItems.forEach((item, index) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'draggable-item-wrapper';
        wrapper.style.position = 'relative';

        const div = document.createElement('div');
        div.className = 'draggable-item';
        div.textContent = item.kannada;
        div.dataset.english = item.english;
        div.dataset.kannada = item.kannada;
        div.dataset.index = index;

        // All levels use click mode now
        const isMatched = game.fullyMatchedItems.has(item.english);

        div.draggable = false; // No drag and drop
        div.style.cursor = isMatched ? 'not-allowed' : 'pointer';

        // Only mark as matched if ALL instances have been destroyed
        if (isMatched) {
            div.classList.add('matched');
        }

        // Add click handler for all levels
        if (!isMatched) {
            div.addEventListener('click', () => {
                selectWord(item.english, item.kannada, div);
            });
        }

        // Create hint element
        const hint = document.createElement('div');
        hint.className = 'hint-tooltip';
        hint.textContent = item.english;
        hint.style.cssText = `
            position: absolute;
            left: 100%;
            top: 50%;
            transform: translateY(-50%);
            margin-left: 10px;
            background: rgba(0, 0, 0, 0.9);
            color: #FFD700;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s;
            z-index: 1000;
        `;

        // Add hover functionality with 0.5s delay
        let hoverTimeout;
        div.addEventListener('mouseenter', () => {
            hoverTimeout = setTimeout(() => {
                hint.style.opacity = '1';
            }, 500); // 0.5 seconds = 500ms
        });

        div.addEventListener('mouseleave', () => {
            clearTimeout(hoverTimeout);
            hint.style.opacity = '0';
        });

        wrapper.appendChild(div);
        wrapper.appendChild(hint);
        container.appendChild(wrapper);
    });
}

// Click word to match with first vehicle on path
function selectWord(english, kannada, element) {
    // Find the first vehicle on the path (earliest spawned, furthest along)
    if (game.activeTanks.length === 0) {
        // No vehicles to match
        return;
    }

    // Get the first tank (index 0 is the oldest/furthest along)
    const firstTank = game.activeTanks[0];

    // Check if it matches
    if (firstTank.vocabulary.english === english) {
        // Correct match!
        handleCorrectMatch(firstTank, english);
    } else {
        // Wrong match
        createParticles(firstTank.x, firstTank.y, '#F44336', 'wrong', 1);
        playWrongSound();

        game.mistakes.push({
            attempted: kannada,
            correct: firstTank.vocabulary.kannada,
            english: firstTank.vocabulary.english
        });
        loseLife();
    }
}

// Start spawning tanks
function startSpawning() {
    if (game.spawnInterval) {
        clearInterval(game.spawnInterval);
    }

    let baseRate;
    // First 3 levels spawn much slower for learning
    if (game.level === 1) {
        baseRate = 5000; // 5 seconds for level 1
    } else if (game.level === 2) {
        baseRate = 4000; // 4 seconds for level 2
    } else if (game.level === 3) {
        baseRate = 3500; // 3.5 seconds for level 3
    } else {
        baseRate = Math.max(1000, game.baseSpawnRate - (game.level * 200)); // Normal progression
    }

    const spawnRate = baseRate / game.speedMultiplier;

    game.spawnInterval = setInterval(() => {
        if (!game.isGameOver) {
            spawnTank();
        }
    }, spawnRate);
}

// Spawn a new tank
function spawnTank() {
    // Only spawn tanks for items that haven't been fully matched yet
    const unmatchedItems = game.draggableItems.filter(item => !game.fullyMatchedItems.has(item.english));

    if (unmatchedItems.length === 0) {
        // All items fully matched - level up!
        levelUp();
        return;
    }

    // Select random unmatched item, ensuring variety
    let vocabulary;

    // Try to pick an item that's different from recent spawns
    if (game.tanks.length > 0) {
        const recentEnglish = game.tanks.slice(-3).map(t => t.vocabulary.english);
        const differentItems = unmatchedItems.filter(item => !recentEnglish.includes(item.english));

        if (differentItems.length > 0) {
            vocabulary = differentItems[Math.floor(Math.random() * differentItems.length)];
        } else {
            vocabulary = unmatchedItems[Math.floor(Math.random() * unmatchedItems.length)];
        }
    } else {
        vocabulary = unmatchedItems[Math.floor(Math.random() * unmatchedItems.length)];
    }

    // Determine vehicle type based on vocabulary difficulty, not level
    let vehicleType;
    if (vocabulary.difficulty === 'letter') {
        vehicleType = 'suv';      // Letters always get SUV (green, fast)
    } else if (vocabulary.difficulty === 'word') {
        vehicleType = 'tank';     // Words always get tank (orange, medium)
    } else {
        vehicleType = 'blimp';    // Sentences always get blimp (purple, slow)
    }

    const tank = new Tank(vocabulary, vehicleType);
    game.tanks.push(tank);
    game.activeTanks.push(tank);
}

// Check if dropped item matches a tank
function checkMatch(kannada, english, dropX, dropY) {
    // Convert canvas coordinates
    const canvasRect = game.canvas.getBoundingClientRect();

    let closestTank = null;
    let closestDistance = Infinity;

    // Find the closest tank
    for (let i = 0; i < game.activeTanks.length; i++) {
        const tank = game.activeTanks[i];

        // Calculate tank position on screen
        const tankScreenX = tank.x * (canvasRect.width / game.canvas.width) + canvasRect.left;
        const tankScreenY = tank.y * (canvasRect.height / game.canvas.height) + canvasRect.top;

        // Check distance to this tank
        const distance = Math.sqrt(
            Math.pow(dropX - tankScreenX, 2) +
            Math.pow(dropY - tankScreenY, 2)
        );

        if (distance < 100 && distance < closestDistance) {
            closestDistance = distance;
            closestTank = tank;
        }
    }

    // Check if we found a close tank
    if (closestTank) {
        // Check if the English text matches
        if (closestTank.vocabulary.english === english) {
            // Correct match!
            handleCorrectMatch(closestTank, english);
            return true;
        } else {
            // Wrong match - dragged wrong item to tank
            // Visual feedback - red X particles
            createParticles(closestTank.x, closestTank.y, '#F44336', 'wrong', 1);

            // Audio feedback - error sound
            playWrongSound();

            game.mistakes.push({
                attempted: kannada,
                correct: closestTank.vocabulary.kannada,
                english: closestTank.vocabulary.english
            });
            loseLife();
            return false;
        }
    }

    // Not close enough to any tank
    loseLife();
    return false;
}

// Handle correct match
function handleCorrectMatch(tank, english) {
    game.score += 10 * game.level;

    // Visual feedback - green particles explosion
    createParticles(tank.x, tank.y, '#4CAF50', 'correct', 15);

    // Audio feedback - happy sound
    playCorrectSound();

    // Increment match count
    if (!game.matchedCounts[english]) {
        game.matchedCounts[english] = 0;
    }
    game.matchedCounts[english]++;

    // Remove tank
    const tankIndex = game.tanks.indexOf(tank);
    if (tankIndex > -1) {
        game.tanks.splice(tankIndex, 1);
    }

    const activeTankIndex = game.activeTanks.indexOf(tank);
    if (activeTankIndex > -1) {
        game.activeTanks.splice(activeTankIndex, 1);
    }

    // Check if there are any more tanks with this word on screen or in queue
    const remainingTanksWithWord = game.tanks.filter(t => t.vocabulary.english === english).length;

    // If no more tanks with this word exist, mark as fully matched
    if (remainingTanksWithWord === 0) {
        game.fullyMatchedItems.add(english);
        // Update draggable items display to show green
        renderDraggableItems();
    }

    updateUI();
}

// Level up
function levelUp() {
    game.level++;
    game.matchedCounts = {};
    game.fullyMatchedItems.clear();
    game.tanks = [];
    game.activeTanks = [];

    // Save level and mark as played when naturally leveling up
    game.savedLevel = game.level;
    game.hasPlayedCurrentLevel = false;

    // Load new vocabulary for new level
    initializeDraggableItems();

    updateUI();
    startSpawning(); // Update spawn rate

    // Show level up message briefly
    const canvas = game.canvas;
    const ctx = game.ctx;

    setTimeout(() => {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#FFD700';
        ctx.font = 'bold 48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('LEVEL UP!', canvas.width / 2, canvas.height / 2);
    }, 100);
}

// Lose a life
function loseLife() {
    game.lives--;

    // Mark that player has played this level
    game.hasPlayedCurrentLevel = true;

    if (game.lives <= 0) {
        gameOver();
    }
}

// Game over
function gameOver() {
    game.isGameOver = true;
    clearInterval(game.spawnInterval);

    // If player hasn't played current level (lost immediately after skip), revert to saved level
    if (!game.hasPlayedCurrentLevel) {
        game.level = game.savedLevel;
    }

    // Save game data and update stats
    DataManager.updateStats();
    DataManager.saveGameData();

    document.getElementById('finalScore').textContent = game.score;
    document.getElementById('finalLevel').textContent = game.level;

    // Update restart button text to show current level
    const restartBtn = document.getElementById('restartBtn');
    restartBtn.textContent = `Retry Level ${game.level}`;

    // Display mistakes
    displayMistakes();

    document.getElementById('gameOverScreen').style.display = 'flex';
}

// Display mistakes on game over screen
function displayMistakes() {
    const mistakesContainer = document.getElementById('mistakesContainer');
    mistakesContainer.innerHTML = '';

    if (game.mistakes.length === 0 && game.missedTanks.length === 0) {
        mistakesContainer.innerHTML = '<p class="no-mistakes">Perfect! No mistakes!</p>';
        return;
    }

    // Show wrong matches
    if (game.mistakes.length > 0) {
        const wrongSection = document.createElement('div');
        wrongSection.className = 'mistake-section';
        wrongSection.innerHTML = '<h3>Wrong Matches:</h3>';

        const mistakeList = document.createElement('div');
        mistakeList.className = 'mistake-list';

        game.mistakes.forEach(mistake => {
            const item = document.createElement('div');
            item.className = 'mistake-item';
            item.innerHTML = `
                <div class="mistake-row">
                    <span class="label">English:</span>
                    <span class="value">${mistake.english}</span>
                </div>
                <div class="mistake-row error">
                    <span class="label">You used:</span>
                    <span class="value kannada">${mistake.attempted}</span>
                </div>
                <div class="mistake-row correct">
                    <span class="label">Correct:</span>
                    <span class="value kannada">${mistake.correct}</span>
                </div>
            `;
            mistakeList.appendChild(item);
        });

        wrongSection.appendChild(mistakeList);
        mistakesContainer.appendChild(wrongSection);
    }

    // Show missed tanks
    if (game.missedTanks.length > 0) {
        const missedSection = document.createElement('div');
        missedSection.className = 'mistake-section';
        missedSection.innerHTML = '<h3>Missed Vehicles:</h3>';

        const missedList = document.createElement('div');
        missedList.className = 'mistake-list';

        game.missedTanks.forEach(missed => {
            const item = document.createElement('div');
            item.className = 'mistake-item';
            item.innerHTML = `
                <div class="mistake-row">
                    <span class="label">English:</span>
                    <span class="value">${missed.english}</span>
                </div>
                <div class="mistake-row correct">
                    <span class="label">Should be:</span>
                    <span class="value kannada">${missed.kannada}</span>
                </div>
            `;
            missedList.appendChild(item);
        });

        missedSection.appendChild(missedList);
        mistakesContainer.appendChild(missedSection);
    }
}

// Hide game over screen
function hideGameOver() {
    document.getElementById('gameOverScreen').style.display = 'none';
}

// Update UI elements
function updateUI() {
    document.getElementById('score').textContent = game.score;
    document.getElementById('level').textContent = game.level;

    const heartsDisplay = '❤️'.repeat(Math.max(0, game.lives));
    document.getElementById('lives').textContent = heartsDisplay || '💀';

    // Update sliders
    const levelSlider = document.getElementById('levelSlider');
    if (levelSlider) {
        levelSlider.value = game.level;
        document.getElementById('levelStatus').textContent = game.level;
    }

    // Sidebar title is always "Click to Match" now
}

// Draw the path
function drawPath(ctx) {
    ctx.strokeStyle = '#999';
    ctx.lineWidth = 80;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    ctx.moveTo(pathWaypoints[0].x, pathWaypoints[0].y);

    for (let i = 1; i < pathWaypoints.length; i++) {
        ctx.lineTo(pathWaypoints[i].x, pathWaypoints[i].y);
    }

    ctx.stroke();
}

// Main game loop
function gameLoop() {
    const ctx = game.ctx;
    const canvas = game.canvas;

    // Clear canvas
    ctx.fillStyle = '#7CB342';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw path
    drawPath(ctx);

    // Update and draw tanks
    for (let i = game.tanks.length - 1; i >= 0; i--) {
        const tank = game.tanks[i];
        const alive = tank.update();

        if (!alive) {
            // Tank reached the end - track as missed
            game.missedTanks.push({
                english: tank.vocabulary.english,
                kannada: tank.vocabulary.kannada
            });

            // Player loses a life
            loseLife();
            updateUI();

            // Remove from both arrays
            game.tanks.splice(i, 1);
            const activeIndex = game.activeTanks.indexOf(tank);
            if (activeIndex > -1) {
                game.activeTanks.splice(activeIndex, 1);
            }
        } else {
            tank.draw(ctx);
        }
    }

    // Update and draw particles
    for (let i = game.particles.length - 1; i >= 0; i--) {
        const particle = game.particles[i];
        const alive = particle.update();

        if (!alive) {
            game.particles.splice(i, 1);
        } else {
            particle.draw(ctx);
        }
    }

    if (!game.isGameOver) {
        game.animationFrame = requestAnimationFrame(gameLoop);
    }
}

// Toggle fullscreen
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.log(`Error attempting to enable fullscreen: ${err.message}`);
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Speed control function
function setSpeed(speed) {
    if (!isNaN(speed) && speed >= 1) {
        game.speedMultiplier = speed;
        document.getElementById('speedStatus').textContent = speed + 'x';

        // Restart spawning with new speed
        if (!game.isGameOver) {
            startSpawning();
        }
    }
}

// Skip to level function
function skipToLevel(targetLevel) {
    if (!isNaN(targetLevel) && targetLevel >= 1) {
        // Don't save if skipping to same or lower level
        if (targetLevel > game.savedLevel) {
            // Only update saved level if not skipping
            game.savedLevel = game.level;
        }

        game.level = targetLevel;
        game.hasPlayedCurrentLevel = false;
        game.matchedCounts = {};
        game.fullyMatchedItems.clear();
        game.tanks = [];
        game.activeTanks = [];
        game.lives = 3;

        // Load new vocabulary for target level
        initializeDraggableItems();

        updateUI();

        // Restart spawning if game is active
        if (!game.isGameOver) {
            startSpawning();
        }
    }
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('restartBtn').addEventListener('click', () => {
        resetGame(true); // Keep current level when restarting
        initializeDraggableItems();
        startSpawning();
        gameLoop();
    });

    // Speed slider
    document.getElementById('speedSlider').addEventListener('input', (e) => {
        const speed = parseFloat(e.target.value);
        setSpeed(speed);
    });

    // Level slider
    document.getElementById('levelSlider').addEventListener('input', (e) => {
        const level = parseInt(e.target.value);
        document.getElementById('levelStatus').textContent = level;
    });

    document.getElementById('levelSlider').addEventListener('change', (e) => {
        const level = parseInt(e.target.value);
        skipToLevel(level);
    });

    // Listen for * key to toggle fullscreen
    document.addEventListener('keydown', (event) => {
        if (event.key === '*') {
            toggleFullscreen();
        }
    });

    // No drag and drop - all interaction happens via click on sidebar words

}

// WalkerAuth Integration
function initAuth() {
    const token = localStorage.getItem('walkerauth_token');
    const userName = localStorage.getItem('user_name');
    const userEmail = localStorage.getItem('user_email');
    const userAvatar = localStorage.getItem('user_avatar');

    const loginBtn = document.getElementById('loginBtn');
    const userProfile = document.getElementById('userProfile');
    const userNameEl = document.getElementById('userName');
    const userAvatarEl = document.getElementById('userAvatar');
    const logoutBtn = document.getElementById('logoutBtn');

    if (token && userName) {
        // User is logged in
        loginBtn.style.display = 'none';
        userProfile.style.display = 'flex';
        userNameEl.textContent = userName;

        if (userAvatar) {
            userAvatarEl.src = userAvatar;
            userAvatarEl.style.display = 'block';
        } else {
            userAvatarEl.style.display = 'none';
        }
    } else {
        // User is not logged in
        loginBtn.style.display = 'block';
        userProfile.style.display = 'none';
    }

    // Login button handler
    loginBtn.addEventListener('click', () => {
        window.location.href = 'https://walkerauth.walkerco.co/?id=LangGames&presync=1';
    });

    // Logout button handler
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('walkerauth_token');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_email');
        localStorage.removeItem('user_avatar');
        window.location.reload();
    });
}

// Start game when page loads
window.addEventListener('load', () => {
    initAuth();
    initGame();
});
