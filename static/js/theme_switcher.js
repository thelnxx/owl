document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("themeToggleBtn");
    const toggleIcon = document.getElementById("themeToggleIcon");
    const STORAGE_KEY = "lnx_theme";

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-bs-theme", theme);
        localStorage.setItem(STORAGE_KEY, theme);

        if (toggleIcon) {
            if (theme === "dark") {
                toggleIcon.className = "fa-solid fa-sun text-warning";
                if (toggleBtn) toggleBtn.setAttribute("title", "Switch to Light Mode");
            } else {
                toggleIcon.className = "fa-solid fa-moon text-info";
                if (toggleBtn) toggleBtn.setAttribute("title", "Switch to Dark Mode");
            }
        }
    }

    const currentTheme = document.documentElement.getAttribute("data-bs-theme") || "dark";
    applyTheme(currentTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            const active = document.documentElement.getAttribute("data-bs-theme");
            const nextTheme = active === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
        });
    }
});