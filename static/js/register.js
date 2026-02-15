document.querySelector("form").addEventListener("submit", function () {
    const btn = document.getElementById("registerBtn");
    btn.disabled = true;
    btn.style.opacity = "0.7";
    btn.innerText = "Please wait...";
});