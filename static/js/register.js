document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");
    const btn = document.getElementById("registerBtn");

    let isSubmitting = false;

    form.addEventListener("submit", function (e) {

        if (isSubmitting) {
            e.preventDefault();
            return;
        }

        isSubmitting = true;

        // Disable button
        btn.disabled = true;
        btn.innerText = "Please wait...";
        btn.style.opacity = "0.7";

        // Create full page overlay
        const overlay = document.createElement("div");
        overlay.id = "pageBlocker";

        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100%";
        overlay.style.height = "100%";
        overlay.style.background = "rgba(255,255,255,0.6)";
        overlay.style.backdropFilter = "blur(3px)";
        overlay.style.zIndex = "9999";
        overlay.style.cursor = "not-allowed";

        document.body.appendChild(overlay);
    });

});
