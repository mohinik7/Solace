// Create a star animation in the background
document.addEventListener('DOMContentLoaded', function() {
    const starsContainer = document.querySelector('.stars');
    const numStars = 100;
    
    // Create stars
    for (let i = 0; i < numStars; i++) {
        createStar(starsContainer);
    }
});

function createStar(container) {
    const star = document.createElement('div');
    star.classList.add('star');
    
    // Random position
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    
    // Random size
    const size = Math.random() * 3;
    
    // Random animation duration and delay
    const duration = 3 + Math.random() * 7;
    const delay = Math.random() * 5;
    
    // Random opacity
    const opacity = 0.2 + Math.random() * 0.8;
    
    // Set star styles
    star.style.left = `${x}%`;
    star.style.top = `${y}%`;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    star.style.setProperty('--duration', `${duration}s`);
    star.style.setProperty('--opacity', opacity);
    star.style.animationDelay = `${delay}s`;
    
    container.appendChild(star);
} 