document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;

  // All toggle buttons (PC + Mobile)
  const toggles = document.querySelectorAll(".theme-toggle");

  // All icons
  const suns = document.querySelectorAll(".sun");
  const moons = document.querySelectorAll(".moon");

  // Apply theme function
  const applyTheme = (isDark) => {
    body.classList.toggle("dark-mode", isDark);

    toggles.forEach(toggle => {
      toggle.className = isDark
        ? "bi bi-toggle-on theme-toggle"
        : "bi bi-toggle-off theme-toggle";
    });

    suns.forEach(sun => sun.classList.toggle("d-none", !isDark));
    moons.forEach(moon => moon.classList.toggle("d-none", isDark));

    localStorage.setItem("theme", isDark ? "dark" : "light");
  };

  // Load saved theme
  const savedTheme = localStorage.getItem("theme");
  applyTheme(savedTheme === "dark");

  // Add click event to ALL toggles
  toggles.forEach(toggle => {
    toggle.addEventListener("click", () => {
      const isDark = !body.classList.contains("dark-mode");
      applyTheme(isDark);
    });
  });
});
