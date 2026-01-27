document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".password-box .toggle").forEach(icon => {
    icon.addEventListener("click", () => {
      const inputId = icon.dataset.target;
      const input = document.getElementById(inputId);

      if (!input) return;

      if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
      } else {
        input.type = "password";
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
      }
    });
  });
});
