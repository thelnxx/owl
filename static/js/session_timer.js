document.addEventListener("DOMContentLoaded", function () {
    const config = window.SESSION_CONFIG;
    if (!config) return;

    const countdownEl = document.getElementById("sessionCountdown");
    const badgeEl = document.getElementById("sessionTimerBadge");
    const iconEl = document.getElementById("sessionTimerIcon");
    const modalEl = document.getElementById("sessionExpiredModal");
    const statusEl = document.getElementById("sessionLogoutStatus");

    const STORAGE_KEY = "lnx_session_expires_at";
    const timeoutMs = (config.timeoutSeconds || 14400) * 1000;
    let logoutTriggered = false;

    // Reset expiry timestamp on every server page load (matches SESSION_SAVE_EVERY_REQUEST = True)
    function resetSessionExpiry() {
        const expiresAt = Date.now() + timeoutMs;
        localStorage.setItem(STORAGE_KEY, expiresAt.toString());
        return expiresAt;
    }

    resetSessionExpiry();

    function formatDuration(totalSeconds) {
        const hrs = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        return [hrs, mins, secs]
            .map((unit) => String(unit).padStart(2, "0"))
            .join(":");
    }

    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    function triggerServerLogout() {
        if (logoutTriggered) return;
        logoutTriggered = true;

        localStorage.removeItem(STORAGE_KEY);

        if (modalEl) {
            const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
            modalInstance.show();
        }

        const csrfToken = getCsrfToken();

        fetch(config.logoutUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json"
            }
        })
            .then((response) => {
                if (statusEl) {
                    statusEl.textContent = response.ok
                        ? "Server session terminated successfully."
                        : "Session ended. Please log in again.";
                }
            })
            .catch(() => {
                if (statusEl) {
                    statusEl.textContent = "Session expired. Please log in again.";
                }
            });
    }

    const timerInterval = setInterval(function () {
        const storedExpiry = parseInt(localStorage.getItem(STORAGE_KEY) || "0", 10);
        const remainingMs = storedExpiry - Date.now();
        const remainingSec = Math.max(0, Math.floor(remainingMs / 1000));

        if (countdownEl) {
            countdownEl.textContent = formatDuration(remainingSec);
        }

        // Visual warning under 5 minutes
        if (remainingSec <= 300 && badgeEl) {
            badgeEl.classList.remove("bg-body-secondary", "border-secondary");
            badgeEl.classList.add("bg-danger", "border-danger");
            if (iconEl) {
                iconEl.classList.remove("text-info");
                iconEl.classList.add("text-white");
            }
        }

        if (remainingSec <= 0) {
            clearInterval(timerInterval);
            triggerServerLogout();
        }
    }, 1000);
});