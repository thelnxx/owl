document.addEventListener("DOMContentLoaded", function () {
    const scriptTag = document.getElementById('session-tracker-script');
    if (!scriptTag) return;

    // Data attributelarından verileri oku
    const isAuthenticated = scriptTag.dataset.isAuthenticated === 'true';
    const sessionTimeout = parseInt(scriptTag.dataset.sessionTimeout, 10) * 1000;

    // 1. Manuel 'Çıkış Yap' tıklamasını yakala
    document.addEventListener('click', function(e) {
        const logoutTarget = e.target.closest('a[href*="logout"], button[formaction*="logout"], input[type="submit"]');
        if (logoutTarget && logoutTarget.getAttribute('href')?.includes('logout')) {
            localStorage.removeItem('wasLoggedIn');
            localStorage.removeItem('lastActivity');
        }
    });

    const expiredModalEl = document.getElementById('sessionExpiredModal');
    let expiredModal;
    if (expiredModalEl && typeof bootstrap !== 'undefined') {
        expiredModal = new bootstrap.Modal(expiredModalEl);
    }

    if (isAuthenticated) {
        // Kullanıcı aktif: Oturum bayrağını ve son hareket zamanını kaydet
        localStorage.setItem('wasLoggedIn', 'true');
        localStorage.setItem('lastActivity', Date.now().toString());

        function updateActivity() {
            localStorage.setItem('lastActivity', Date.now().toString());
        }

        ['mousemove', 'keydown', 'click', 'scroll'].forEach(evt => {
            document.addEventListener(evt, updateActivity);
        });

        // Sekme açıkken pasiflik süresi dolarsa sayfayı yenile
        setInterval(() => {
            const lastAct = parseInt(localStorage.getItem('lastActivity') || '0', 10);
            if (Date.now() - lastAct > sessionTimeout) {
                window.location.reload();
            }
        }, 5000);

    } else {
        // Kullanıcı oturumu kapalı: Sadece pasiflikten dolayı düştüyse popup göster
        if (localStorage.getItem('wasLoggedIn') === 'true') {
            if (expiredModal) {
                expiredModal.show();
            }
            localStorage.removeItem('wasLoggedIn');
            localStorage.removeItem('lastActivity');
        }
    }
});