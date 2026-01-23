document.addEventListener('DOMContentLoaded', () => {
    // Mobile menu toggle logic
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('.main-nav');

    if (toggle && nav) {
        toggle.addEventListener('click', () => {
            const isVisible = nav.style.display === 'block';
            nav.style.display = isVisible ? 'none' : 'block';
            
            // Basic absolute positioning for mobile menu override
            if (!isVisible) {
                nav.style.position = 'absolute';
                nav.style.top = '100%';
                nav.style.left = '0';
                nav.style.width = '100%';
                nav.style.backgroundColor = 'white';
                nav.style.padding = '1rem';
                nav.style.borderBottom = '1px solid #eee';
                nav.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)';
            } else {
                nav.style = ''; // Reset inline styles
            }
        });
    }
});
