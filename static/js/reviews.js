const defaultReviews = [
    { name: "Aarav Patel", rating: "★★★★★", message: "EdTube helped me build a consistent study habit. My scores improved faster than I expected!"},
    { name: "Meera Sharma", rating: "★★★★☆", message: "The quizzes actually adapt to your progress — it feels like having a personal tutor!" },
    { name: "Rohan Mehta", rating: "★★★★★", message: "Clean UI, smooth performance, and tracking features that keep you motivated every day." },
    { name: "Priya Nair", rating: "★★★★★", message: "One of the best educational platforms I’ve used — simple, modern, and effective." },
    { name: "Aditya Singh", rating: "★★★★☆", message: "The scheduling and reminders make studying easier and more organized than ever." },
    { name: "Diya Kapoor", rating: "★★★★★", message: "EdTube keeps learning exciting! I can track everything I do — progress feels visible." }
];

// Load from localStorage OR default
let reviews = JSON.parse(localStorage.getItem("reviews")) || defaultReviews;

// Fix old EduNex references automatically
reviews = reviews.map(r => ({
  ...r,
  message: r.message.replace(/EduNex/g, "EdTube")
}));

function displayReviews() {
    const container = document.getElementById("reviewsList");
    container.innerHTML = "<h2>What Students Say</h2>";

    reviews.forEach(r => {
    container.innerHTML += `
        <div class="review">
        <div class="stars">${r.rating}</div>
        <p>${r.message}</p>
        <h4>— ${r.name}</h4>
        </div>
    `;
    });

    localStorage.setItem("reviews", JSON.stringify(reviews));
}

function addReview() {
    const name = document.getElementById("nameInput").value.trim();
    const rating = document.getElementById("ratingInput").value;
    const message = document.getElementById("messageInput").value.trim();

    if (!name || !rating || !message) {
    alert("All fields are required.");
    return;
    }

    reviews.push({
    name,
    rating: generateStarString(rating),
    message
    });

    displayReviews();

    document.getElementById("nameInput").value = "";
    document.getElementById("ratingInput").value = "";
    document.getElementById("messageInput").value = "";
}

function generateStarString(rating) {
    if (rating == 5) return "★★★★★";
    if (rating == 4.5) return "★★★★\u2BEA";
    if (rating == 4) return "★★★★☆";
    return "★★★★★";
}

displayReviews();

const stars = document.querySelectorAll("#starRating span");
const ratingInput = document.getElementById("ratingInput");

stars.forEach(star => {
    star.addEventListener("click", () => {
    const rating = star.getAttribute("data-value");
    ratingInput.value = rating;

    stars.forEach(s => s.classList.remove("selected"));
    star.classList.add("selected");
    let next = star.nextElementSibling;
    while (next) {
        next.classList.add("selected");
        next = next.nextElementSibling;
    }
    });
});
