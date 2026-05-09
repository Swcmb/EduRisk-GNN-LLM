document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    const heroCard = document.querySelector('.hero-card');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.feature-card, .stat-item, .model-card, .content-card');
        
        elements.forEach(element => {
            const position = element.getBoundingClientRect();
            
            if (position.top < window.innerHeight * 0.85 && position.bottom > 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    document.querySelectorAll('.feature-card, .model-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    document.querySelectorAll('.stat-item').forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'scale(0.9)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });

    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll();

    document.querySelectorAll('.footer-links a').forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(8px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });

    document.querySelectorAll('.feature-icon').forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.15) rotate(10deg)';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    });

    const tabs = document.querySelectorAll('.nav-pills .nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    if (heroCard) {
        let angle = 0;
        setInterval(() => {
            angle += 0.5;
            heroCard.style.transform = `translateY(${Math.sin(angle * 0.02) * 10}px)`;
        }, 50);
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});