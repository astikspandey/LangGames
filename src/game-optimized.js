// ============================================================
// PERFORMANCE OPTIMIZATIONS
// ============================================================

// Object pool for particles to reduce garbage collection
const particlePool = {
    pool: [],
    get(x, y, color, type) {
        let particle;
        if (this.pool.length > 0) {
            particle = this.pool.pop();
            particle.reset(x, y, color, type);
        } else {
            particle = new Particle(x, y, color, type);
        }
        return particle;
    },
    return(particle) {
        this.pool.push(particle);
    }
};

// Cache for frequently used values
const cache = {
    sqrtCache: new Map(),
    getSqrt(dx, dy) {
        const key = `${dx.toFixed(2)},${dy.toFixed(2)}`;
        if (!this.sqrtCache.has(key)) {
            this.sqrtCache.set(key, Math.sqrt(dx * dx + dy * dy));
            // Limit cache size
            if (this.sqrtCache.size > 1000) {
                const firstKey = this.sqrtCache.keys().next().value;
                this.sqrtCache.delete(firstKey);
            }
        }
        return this.sqrtCache.get(key);
    }
};

// Optimized Tank class
class OptimizedTank {
    constructor(vocabulary, vehicleType) {
        this.vocabulary = vocabulary;
        this.vehicleType = vehicleType;
        this.waypointIndex = 0;
        this.progress = 0;
        this.x = pathWaypoints[0].x;
        this.y = pathWaypoints[0].y;

        // Pre-calculate these once
        this.color = vehicleType === 'tank' ? '#FF6B6B' :
                     vehicleType === 'blimp' ? '#9C27B0' : '#8BC34A';
        this.speed = vehicleType === 'tank' ? 1.2 :
                     vehicleType === 'blimp' ? 0.8 : 1.5;
        this.size = vehicleType === 'tank' ? {width: 50, height: 30} :
                    vehicleType === 'blimp' ? {width: 60, height: 40} :
                    {width: 45, height: 25};
    }

    update() {
        if (this.waypointIndex >= pathWaypoints.length - 1) {
            return false;
        }

        const currentWaypoint = pathWaypoints[this.waypointIndex];
        const nextWaypoint = pathWaypoints[this.waypointIndex + 1];

        const dx = nextWaypoint.x - currentWaypoint.x;
        const dy = nextWaypoint.y - currentWaypoint.y;

        // Use cached sqrt for performance
        const distance = cache.getSqrt(dx, dy);

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
        const halfWidth = this.size.width / 2;
        const halfHeight = this.size.height / 2;

        // Draw vehicle body
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x - halfWidth, this.y - halfHeight, this.size.width, this.size.height);

        // Draw border
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x - halfWidth, this.y - halfHeight, this.size.width, this.size.height);

        // Draw vehicle details (simplified for performance)
        if (this.vehicleType === 'tank') {
            ctx.fillStyle = '#D84315';
            ctx.fillRect(this.x - 10, this.y - 8, 20, 16);
            ctx.fillRect(this.x + 10, this.y - 3, 15, 6);
        } else if (this.vehicleType === 'blimp') {
            ctx.fillStyle = '#7B1FA2';
            ctx.fillRect(this.x - 15, this.y + 15, 30, 10);
        } else if (this.vehicleType === 'suv') {
            ctx.fillStyle = '#81C784';
            ctx.fillRect(this.x - 8, this.y - 6, 16, 12);
        }

        // Draw text (font properties set once globally)
        ctx.fillStyle = '#FFF';
        ctx.fillText(this.vocabulary.english, this.x, this.y, this.size.width - 8);
    }
}

// Optimized Particle class with reset method for pooling
class OptimizedParticle {
    constructor(x, y, color, type = 'correct') {
        this.reset(x, y, color, type);
    }

    reset(x, y, color, type) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.type = type;
        this.life = 1.0;
        this.size = type === 'correct' ? 8 : 15;

        if (type === 'correct') {
            const angle = Math.random() * Math.PI * 2;
            const speed = 2 + Math.random() * 3;
            this.vx = Math.cos(angle) * speed;
            this.vy = Math.sin(angle) * speed;
        } else {
            this.vx = 0;
            this.vy = 0;
        }
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.life -= 0.02;

        if (this.type === 'correct') {
            this.vy += 0.1;
        }

        return this.life > 0;
    }

    draw(ctx) {
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;

        if (this.type === 'correct') {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.strokeStyle = this.color;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(this.x - 10, this.y - 10);
            ctx.lineTo(this.x + 10, this.y + 10);
            ctx.moveTo(this.x + 10, this.y - 10);
            ctx.lineTo(this.x - 10, this.y + 10);
            ctx.stroke();
        }
    }
}

// Optimized game loop with delta time
let lastFrameTime = 0;
function optimizedGameLoop(timestamp) {
    const deltaTime = timestamp - lastFrameTime;
    lastFrameTime = timestamp;

    // Cap at 60 FPS minimum (don't process if too fast)
    if (deltaTime < 16) {
        if (!game.isGameOver) {
            game.animationFrame = requestAnimationFrame(optimizedGameLoop);
        }
        return;
    }

    const ctx = game.ctx;
    const canvas = game.canvas;

    // Clear canvas
    ctx.fillStyle = '#7CB342';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw path
    drawPath(ctx);

    // Set canvas context properties once
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Update and draw tanks (reverse iteration for safe removal)
    for (let i = game.tanks.length - 1; i >= 0; i--) {
        const tank = game.tanks[i];
        const alive = tank.update();

        if (!alive) {
            game.missedTanks.push({
                english: tank.vocabulary.english,
                kannada: tank.vocabulary.kannada
            });

            loseLife();
            updateUI();

            game.tanks.splice(i, 1);
            const activeIndex = game.activeTanks.indexOf(tank);
            if (activeIndex > -1) {
                game.activeTanks.splice(activeIndex, 1);
            }
        } else {
            tank.draw(ctx);
        }
    }

    // Reset alpha for particles
    ctx.globalAlpha = 1.0;

    // Update and draw particles
    for (let i = game.particles.length - 1; i >= 0; i--) {
        const particle = game.particles[i];
        const alive = particle.update();

        if (!alive) {
            particlePool.return(particle);
            game.particles.splice(i, 1);
        } else {
            particle.draw(ctx);
        }
    }

    // Reset alpha
    ctx.globalAlpha = 1.0;

    if (!game.isGameOver) {
        game.animationFrame = requestAnimationFrame(optimizedGameLoop);
    }
}

// Optimized draggable items rendering with incremental updates
const draggableItemsCache = new Map();

function renderDraggableItemsOptimized() {
    const container = document.getElementById('draggableItems');

    // Only update items that changed instead of recreating everything
    game.draggableItems.forEach((item, index) => {
        const cacheKey = `${item.english}_${index}`;
        const isMatched = game.fullyMatchedItems.has(item.english);

        let wrapper = draggableItemsCache.get(cacheKey);

        if (!wrapper) {
            // Create new element
            wrapper = createDraggableItem(item, index, isMatched);
            draggableItemsCache.set(cacheKey, wrapper);
            container.appendChild(wrapper);
        } else {
            // Update existing element
            const div = wrapper.querySelector('.draggable-item');
            if (isMatched && !div.classList.contains('matched')) {
                div.classList.add('matched');
                div.style.cursor = 'not-allowed';
            }
        }
    });
}

function createDraggableItem(item, index, isMatched) {
    const wrapper = document.createElement('div');
    wrapper.className = 'draggable-item-wrapper';
    wrapper.style.position = 'relative';

    const div = document.createElement('div');
    div.className = 'draggable-item';
    div.textContent = item.kannada;
    div.dataset.english = item.english;
    div.dataset.kannada = item.kannada;
    div.dataset.index = index;
    div.draggable = false;
    div.style.cursor = isMatched ? 'not-allowed' : 'pointer';

    if (isMatched) {
        div.classList.add('matched');
    }

    if (!isMatched) {
        div.addEventListener('click', () => {
            selectWord(item.english, item.kannada, div);
        });
    }

    // Create hint tooltip
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

    let hoverTimeout;
    div.addEventListener('mouseenter', () => {
        hoverTimeout = setTimeout(() => {
            hint.style.opacity = '1';
        }, 500);
    });

    div.addEventListener('mouseleave', () => {
        clearTimeout(hoverTimeout);
        hint.style.opacity = '0';
    });

    wrapper.appendChild(div);
    wrapper.appendChild(hint);
    return wrapper;
}

// Export optimizations
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        OptimizedTank,
        OptimizedParticle,
        optimizedGameLoop,
        renderDraggableItemsOptimized,
        particlePool,
        cache
    };
}
