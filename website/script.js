// Bruno AI Website JavaScript

// Smooth scrolling for navigation links
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Enhanced navbar behavior on scroll
function handleNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    const scrolled = window.scrollY > 50;
    
    if (scrolled) {
        navbar.style.background = 'rgba(255, 248, 231, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(139, 69, 19, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 248, 231, 0.95)';
        navbar.style.boxShadow = 'none';
    }
}

// Form submission handler
function handleSignup(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    const familySize = form.querySelector('select').value;
    
    if (!email || !familySize) {
        showMessage('Please fill in all fields!', 'error');
        return;
    }
    
    // Simulate form submission
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    submitButton.textContent = 'Processing Request...';
    submitButton.disabled = true;
    
    setTimeout(() => {
        submitButton.textContent = '✅ Request Received!';
        submitButton.style.background = 'var(--instacart-green)';
        
        // Show success message
        showMessage(`Welcome! I've added ${email} to our early access list. You'll be among the first to experience our strategic meal planning approach for families of ${familySize}.`, 'success');
        
        // Reset form after delay
        setTimeout(() => {
            form.reset();
            submitButton.textContent = originalText;
            submitButton.disabled = false;
            submitButton.style.background = '';
        }, 3000);
    }, 1500);
}

// Message display function
function showMessage(text, type) {
    // Remove existing messages
    const existingMessage = document.querySelector('.notification-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const message = document.createElement('div');
    message.className = `notification-message ${type}`;
    message.textContent = text;
    
    // Style the message
    message.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? 'var(--instacart-green)' : '#dc3545'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        z-index: 10000;
        max-width: 400px;
        font-weight: 500;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(message);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        message.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => message.remove(), 300);
    }, 5000);
}

// Intersection Observer for animations
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate
    const animatedElements = document.querySelectorAll('.section-header, .problem-card, .feature-card, .testimonial, .step');
    animatedElements.forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
}

// Bruno character interactions
function setupBrunoInteractions() {
    const brunoCharacter = document.querySelector('.bruno-character');
    const speechBubble = document.querySelector('.speech-bubble p');
    
    if (!brunoCharacter || !speechBubble) return;
    
    const brunoQuotes = [
        "I'm here to help you create an effective meal planning strategy.",
        "Let's analyze your budget and optimize your grocery spending.",
        "I've identified several cost-effective meal options for your family.",
        "Based on current market data, I can suggest better alternatives.",
        "Excellent work! This approach is clearly working well.",
        "I want to make sure I give you the best recommendation.",
        "This strategic approach delivers measurable results.",
        "I specialize in data-driven budget optimization.",
        "Let's focus on solutions that work in real life.",
        "I've analyzed the options and found optimal choices."
    ];
    
    let currentQuoteIndex = 0;
    
    // Click interaction
    brunoCharacter.addEventListener('click', () => {
        // Animate Bruno
        brunoCharacter.style.transform = 'scale(1.1)';
        setTimeout(() => {
            brunoCharacter.style.transform = '';
        }, 200);
        
        // Change quote
        currentQuoteIndex = (currentQuoteIndex + 1) % brunoQuotes.length;
        speechBubble.textContent = `"${brunoQuotes[currentQuoteIndex]}"`;
        
        // Add sparkle effect
        createSparkles(brunoCharacter);
    });
    
    // Auto-change quotes periodically
    setInterval(() => {
        currentQuoteIndex = (currentQuoteIndex + 1) % brunoQuotes.length;
        speechBubble.textContent = `"${brunoQuotes[currentQuoteIndex]}"`;
    }, 8000);
}

// Create sparkle effect
function createSparkles(element) {
    for (let i = 0; i < 6; i++) {
        const sparkle = document.createElement('div');
        sparkle.textContent = '✨';
        sparkle.style.cssText = `
            position: absolute;
            font-size: 1.5rem;
            pointer-events: none;
            animation: sparkle 1s ease-out forwards;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
        `;
        
        element.appendChild(sparkle);
        
        setTimeout(() => sparkle.remove(), 1000);
    }
}

// Statistics counter animation
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const finalValue = stat.textContent;
        const isNumber = /^\d+/.test(finalValue);
        
        if (isNumber) {
            const numValue = parseInt(finalValue.replace(/\D/g, ''));
            let currentValue = 0;
            const increment = numValue / 50;
            const suffix = finalValue.replace(/[\d,]/g, '');
            
            const counter = setInterval(() => {
                currentValue += increment;
                if (currentValue >= numValue) {
                    stat.textContent = finalValue;
                    clearInterval(counter);
                } else {
                    const displayValue = Math.floor(currentValue);
                    stat.textContent = displayValue.toLocaleString() + suffix;
                }
            }, 40);
        }
    });
}

// Setup stats animation on scroll
function setupStatsAnimation() {
    const statsSection = document.querySelector('.stats-banner');
    if (!statsSection) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
                entry.target.classList.add('animated');
                animateStats();
            }
        });
    }, { threshold: 0.5 });
    
    observer.observe(statsSection);
}

// Floating icons interaction
function setupFloatingIcons() {
    const floatingIcons = document.querySelectorAll('.floating-icons .icon');
    
    floatingIcons.forEach((icon, index) => {
        icon.addEventListener('mouseenter', () => {
            icon.style.transform = 'scale(1.5) rotate(360deg)';
            icon.style.zIndex = '10';
        });
        
        icon.addEventListener('mouseleave', () => {
            icon.style.transform = '';
            icon.style.zIndex = '';
        });
        
        // Add click interaction
        icon.addEventListener('click', () => {
            // Create ripple effect
            const ripple = document.createElement('div');
            ripple.style.cssText = `
                position: absolute;
                width: 20px;
                height: 20px;
                background: radial-gradient(circle, rgba(255,215,0,0.6) 0%, transparent 70%);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
                top: 50%;
                left: 50%;
            `;
            
            icon.style.position = 'relative';
            icon.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// Mobile menu toggle
function setupMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (!mobileMenuToggle || !navMenu) return;
    
    // Toggle mobile menu
    mobileMenuToggle.addEventListener('click', () => {
        mobileMenuToggle.classList.toggle('active');
        navMenu.classList.toggle('active');
        document.body.classList.toggle('menu-open');
    });
    
    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                mobileMenuToggle.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    });
    
    // Close menu on window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            mobileMenuToggle.classList.remove('active');
            navMenu.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    });
}

// Preload images and optimize performance
function preloadCriticalAssets() {
    // Preload any images that might be added later
    const criticalImages = [
        // Add any image URLs here when images are added
    ];
    
    criticalImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

// Add CSS animations dynamically
function addCustomAnimations() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        @keyframes sparkle {
            0% {
                transform: translateY(0) scale(0);
                opacity: 1;
            }
            50% {
                transform: translateY(-20px) scale(1);
                opacity: 1;
            }
            100% {
                transform: translateY(-40px) scale(0);
                opacity: 0;
            }
        }
        
        @keyframes ripple {
            from {
                transform: translate(-50%, -50%) scale(0);
                opacity: 1;
            }
            to {
                transform: translate(-50%, -50%) scale(4);
                opacity: 0;
            }
        }
        
        .animate-in {
            animation-play-state: running !important;
        }
    `;
    document.head.appendChild(style);
}

// Performance optimization
function optimizePerformance() {
    // Debounce scroll events
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        scrollTimeout = setTimeout(handleNavbarScroll, 10);
    });
    
    // Lazy load images (when added)
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🐻 Bruno AI website loaded!');
    
    // Initialize all functionality
    addCustomAnimations();
    setupScrollAnimations();
    setupBrunoInteractions();
    setupStatsAnimation();
    setupFloatingIcons();
    setupMobileMenu();
    preloadCriticalAssets();
    optimizePerformance();
    
    // Add smooth scrolling to navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.problem-card, .feature-card, .testimonial, .step');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Add click tracking for analytics (placeholder)
    function trackEvent(action, element) {
        console.log(`🐻 Bruno tracked: ${action} on ${element}`);
        // Here you would integrate with analytics like Google Analytics
        // gtag('event', action, { element_clicked: element });
    }
    
    // Track button clicks
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.addEventListener('click', () => {
            trackEvent('button_click', btn.textContent.trim());
        });
    });
    
    // Track form submissions
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            trackEvent('form_submit', 'early_access');
        });
    });
    
    // Welcome message in console
    console.log(`
    🐻 Welcome to Bruno AI! 
    
    Smart meals, happy families!
    
    This website was built with love and a focus on:
    - Performance optimization
    - Accessibility
    - Mobile-first design
    - Bruno's friendly personality
    
    Found a bug? Bruno would love to help fix it!
    `);
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        document.title = '🐻 Come back to Bruno AI!';
    } else {
        document.title = 'Bruno AI - Your Friendly Budget Meal Planning Bear';
    }
});

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    if (resizeTimeout) {
        clearTimeout(resizeTimeout);
    }
    resizeTimeout = setTimeout(() => {
        // Recalculate any layout-dependent functionality
        const brunoCharacter = document.querySelector('.bruno-character');
        if (brunoCharacter && window.innerWidth < 480) {
            brunoCharacter.style.transform = 'scale(0.7)';
        } else if (brunoCharacter && window.innerWidth < 768) {
            brunoCharacter.style.transform = 'scale(0.8)';
        } else if (brunoCharacter) {
            brunoCharacter.style.transform = '';
        }
    }, 250);
});

// Service Worker registration (for future PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('🐻 Bruno SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}

// Export functions for testing or external use
window.BrunoAI = {
    scrollToSection,
    handleSignup,
    showMessage,
    trackEvent: (action, element) => console.log(`🐻 ${action}: ${element}`)
};
