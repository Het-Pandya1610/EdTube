# EduNex

🎓 EduNex — Learn. Grow. Evolve.

EduNex is a modern, responsive, and user-friendly e-learning platform designed to empower students and educators through interactive tools, adaptive insights, and seamless connectivity.
It combines elegant UI/UX design, secure authentication, and scalability — making it ideal for institutions, tutoring platforms, or self-paced learners.

🚀 Features
🧭 Core Functionalities

Smart Authentication:
Secure registration and login system with password hashing and input validation.

Mobile-Responsive Interface:
Adaptive layout with hamburger navigation and modern gradient visuals.

Dynamic Footer & Navigation:
Professional footer with Quick Links, Support, and Contact sections across all pages.

Dedicated Pages:

Home

Courses

Events

Blog

About Us

Contact

Help Center

FAQs

Privacy Policy

Terms & Conditions

Report an Issue

Animated Backgrounds:
Smooth gradient transitions for a dynamic user experience.

Social Media Integration:
WhatsApp, Instagram, LinkedIn, Facebook, and direct call links.

🔐 Authentication Flow
Page	Description
`register.html`	User registration form with Google/Facebook options
`login.html`	Login form for existing users


🗄️ Database Setup

Database Name: edunex_db

```
CREATE DATABASE IF NOT EXISTS edunex_db;
USE edunex_db;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  fullname VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

🧱 Project Structure

```
EduNex/
│
├── EduNex.html              # Homepage
├── login.html               # Login Page
├── register.html            # Registration Page
├── login.php                # Handles login logic
├── register.php             # Handles registration logic
│
├── courses.html             # Course listings
├── events.html              # Upcoming events
├── blog.html                # Articles and updates
├── about.html               # About EduNex
├── contact.html             # Contact page
│
├── help-center.html         # Support and resources
├── faqs.html                # Frequently Asked Questions
├── privacy-policy.html      # Privacy Policy
├── terms.html               # Terms & Conditions
├── report-issue.html        # Bug or issue report page
│
├── footer.css               # Footer styling
├── EduNex.png               # Logo
└── assets/                  # Images, icons, and media
```
⚙️ Technologies Used

```
Frontend: HTML5, CSS3, JavaScript (vanilla)

Backend: PHP (procedural)

Database: MySQL

Icons: Font Awesome 6.5

Fonts: Poppins / Lucida Sans

Hosting: XAMPP / Apache (local dev)
```

🧠 Design Philosophy

EduNex was built around three core values:

Simplicity: Clean interface for effortless navigation.

Consistency: Unified design across all pages.

Accessibility: Works flawlessly on both desktop and mobile.

💡 Future Enhancements

Implement a personalized dashboard with course progress tracking

Add real-time chat between students and mentors

Integrate Groq API for AI-driven study insights

Enable video lectures and downloadable resources

Add admin panel for content management


“Empowering every learner — one click at a time.”

📄 License

© 2025 EduNex. All Rights Reserved.
Unauthorized duplication or redistribution of any content is prohibited without written permission.
