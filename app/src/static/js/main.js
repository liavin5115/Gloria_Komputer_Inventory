// Main JavaScript file for Gloria Komputer Inventory
document.addEventListener('DOMContentLoaded', function() {    // Animate counter values
    const animateCounter = (element) => {
        // Get the original value
        const target = parseInt(element.dataset.originalValue || element.textContent);
        if (isNaN(target)) return;

        // Animation settings
        const duration = 1500; // Slower animation
        const startValue = 0;
        const increment = target / (duration / 16);
        let currentValue = startValue;

        const updateCounter = () => {
            currentValue += increment;
            if (currentValue < target) {
                element.textContent = Math.round(currentValue);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        };

        // Start the animation
        updateCounter();
    };

    // Initialize counter animations when elements are visible
    const counterElements = document.querySelectorAll('.counter-value');
    const observerOptions = {
        root: null,
        threshold: 0.1,
        rootMargin: '0px'
    };

    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);    counterElements.forEach(counter => {
        // Store the original value immediately
        const originalValue = counter.textContent;
        if (!isNaN(parseInt(originalValue))) {
            counter.dataset.originalValue = originalValue;
            
            // Start observing
            counterObserver.observe(counter);
            
            // Additional safeguard
            counter.addEventListener('animationend', () => {
                if (isNaN(parseInt(counter.textContent))) {
                    counter.textContent = counter.dataset.originalValue;
                }
            });
        }
    });
    
    // Auto-hide flash messages
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.3s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 3000);
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle form submissions with loading states
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
                submitBtn.disabled = true;

                // Re-enable button if form submission fails
                setTimeout(() => {
                    if (submitBtn.disabled) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 10000);
            }
        });
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
