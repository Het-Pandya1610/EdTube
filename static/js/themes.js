document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;

  const toggles = document.querySelectorAll(".theme-toggle");
  const suns = document.querySelectorAll(".sun");
  const moons = document.querySelectorAll(".moon");

  const logo = document.getElementById("theme-logo");

  const applyTheme = (isDark) => {
    body.classList.toggle("dark-mode", isDark);

    toggles.forEach(toggle => {
      toggle.className = isDark
        ? "bi bi-toggle-on theme-toggle"
        : "bi bi-toggle-off theme-toggle";
    });


    suns.forEach(sun => sun.classList.toggle("d-none", !isDark));
    moons.forEach(moon => moon.classList.toggle("d-none", isDark));

    if (logo) {
      logo.src = isDark
        ? "/static/assets/EdTube logo dark copy.png"
        : "/static/assets/EdTube logo light.png";
    }
    localStorage.setItem("theme", isDark ? "dark" : "light");
  };

  const savedTheme = localStorage.getItem("theme");
  applyTheme(savedTheme === "dark");

  toggles.forEach(toggle => {
    toggle.addEventListener("click", () => {
      const isDark = !body.classList.contains("dark-mode");
      applyTheme(isDark);
    });
  });
});
