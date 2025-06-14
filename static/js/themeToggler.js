function setupThemeToggler() {
    const body = document.body;
    const themeToggler = document.querySelector('.theme-toggler');
    if (!themeToggler) return;

    const darkIcon = themeToggler.querySelector('.material-symbols-outlined:nth-child(2)');
    const lightIcon = themeToggler.querySelector('.material-symbols-outlined:nth-child(1)');

    // Apply saved theme
    if (localStorage.getItem('theme') === 'dark') {
        body.classList.add('dark-theme-variables');
        darkIcon.classList.add('active');
        lightIcon.classList.remove('active');
    }

    themeToggler.addEventListener('click', function () {
        body.classList.toggle('dark-theme-variables');
        darkIcon.classList.toggle('active');
        lightIcon.classList.toggle('active');
        localStorage.setItem('theme', body.classList.contains('dark-theme-variables') ? 'dark' : 'light');
    });
}

// Auto-run on initial load
document.addEventListener('DOMContentLoaded', setupThemeToggler);

// Expose to global so sidebar can re-run it on module load
window.setupThemeToggler = setupThemeToggler;
