# EdTube - Educational Video Platform

A Django-based platform for sharing and watching educational videos with YouTube-like interface.

## 📋 Table of Contents
- Features
- Installation
- Project Structure
- Usage
- Configuration
- Development
- Deployment
- Contributing
- License
- Contact

## ✨ Features

### 🎥 Video Features
- YouTube-like video player with custom controls
- Video embedding and playback
- Hashtag support in descriptions
- Search functionality with multiple patterns
- Responsive video player for all devices

### 👤 User Features
- Separate Teacher and Student roles
- User authentication system
- Profile management
- Dark/Light theme toggle
- Responsive design

### 🔍 Search Features
- Regular text search
- Hashtag search (#python, #math)
- "Subject by Teacher" search pattern
- Real-time search suggestions

## 🚀 Installation

### Prerequisites
- Python 3.10+
- pip package manager

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/Het-Pandya1610/EdTube.git
cd EdTube
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install django pillow

# Some requirements may not download by themselves because the version differs from person to person
# According to your version, download those requirements

pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env file with your settings
```

5. **Setup database**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
Open browser and visit: `http://localhost:8000`

## 📁 Project Structure

```
EdTube/
│
├── manage.py                    # Django's command-line utility for administrative tasks
├── Requirements.txt             # Project dependencies list
├── pytest.ini                   # Pytest configuration settings
├── factories.py                 # Test factories for generating test data
├── test_search.py               # Search functionality tests
├── README.md                    # Project documentation and setup instructions
├── .gitignore                   # Specifies intentionally untracked files to ignore
│
├── EdTube/                       # Project configuration directory
│   ├── __init__.py              # Marks directory as Python package
│   ├── settings.py              # Project settings and configuration
│   ├── urls.py                  # Main URL routing configuration
│   ├── wsgi.py                   # WSGI configuration for deployment
│   ├── asgi.py                   # ASGI configuration for async support
│   ├── test_runner.py            # Custom test runner configuration
│   └── migrations/               # Database migrations directory
│
├── accounts/                      # User account management app
│   ├── __init__.py               # Marks directory as Python package
│   ├── admin.py                   # Admin interface configurations
│   ├── apps.py                    # App configuration class
│   ├── models.py                  # User profile and account models
│   ├── views.py                   # Account-related views (login, register, profile)
│   ├── urls.py                    # Account-specific URL patterns
│   ├── utils.py                   # Helper functions for accounts
│   ├── mail_utils.py              # Email sending utilities
│   ├── signals.py                  # Django signals for account events
│   ├── tests.py                    # Account app tests
│   ├── data/                       # Static data files
│   │   └── surnames.csv            # CSV file containing surnames for testing
│   └── migrations/                  # Database migrations directory
│
├── video/                           # Video management app
│   ├── __init__.py                 # Marks directory as Python package
│   ├── admin.py                     # Admin interface for video management
│   ├── apps.py                      # App configuration class
│   ├── models.py                    # Video, comment, quiz models
│   ├── views.py                     # Video playback and management views
│   ├── urls.py                      # Video-specific URL patterns
│   ├── utils.py                     # Video processing utilities
│   ├── analytics.py                  # Video analytics and tracking
│   ├── tests.py                      # Video app tests
│   ├── templatetags/                 # Custom template tags
│   │   ├── __init__.py
│   │   └── hashtag_helper.py         # Template tags for hashtag processing
│   ├── management/                    # Custom management commands
│   │   └── commands/
│   │       └── migrate_history.py     # Command to migrate video history
│   └── migrations/                    # Database migrations directory
│
├── teacher/                          # Teacher functionality app
│   ├── __init__.py                   # Marks directory as Python package
│   ├── admin.py                       # Admin interface for teachers
│   ├── apps.py                        # App configuration class
│   ├── models.py                      # Teacher profile and content models
│   ├── views.py                       # Teacher dashboard and content management
│   ├── urls.py                        # Teacher-specific URL patterns
│   ├── utils.py                       # Teacher helper functions
│   ├── tests.py                       # Teacher app tests
│   ├── templatetags/                   # Custom template tags for teachers
│   │   ├── __init__.py
│   │   └── teacher_tags.py             # Template tags for teacher features
│   └── migrations/                      # Database migrations directory
│
├── student/                           # Student functionality app
│   ├── __init__.py                    # Marks directory as Python package
│   ├── admin.py                        # Admin interface for students
│   ├── apps.py                         # App configuration class
│   ├── models.py                       # Student profile and progress models
│   ├── views.py                        # Student dashboard and learning views
│   ├── utils.py                        # Student helper functions
│   ├── tests.py                        # Student app tests
│   └── migrations/                      # Database migrations directory
│
├── notifications/                      # Notification system app
│   ├── __init__.py                     # Marks directory as Python package
│   ├── admin.py                         # Admin interface for notifications
│   ├── apps.py                          # App configuration class
│   ├── models.py                        # Notification models
│   ├── views.py                         # Notification views
│   ├── context_processors.py             # Context processor for notifications
│   ├── tests.py                         # Notification app tests
│   └── migrations/                       # Database migrations directory
│
├── pages/                              # Static pages app
│   ├── __init__.py                     # Marks directory as Python package
│   ├── admin.py                         # Admin interface for pages
│   ├── apps.py                          # App configuration class
│   ├── models.py                        # Page models (if dynamic content)
│   ├── views.py                         # Static page views
│   ├── urls.py                          # Page-specific URL patterns
│   ├── tests.py                         # Pages app tests
│   └── migrations/                       # Database migrations directory
│
├── security_tests/                      # Security testing module
│   ├── __init__.py                      # Marks directory as Python package
│   ├── security_summary.py               # Security test summary generator
│   ├── test_api_security.py              # API security tests
│   ├── test_authentication.py            # Authentication security tests
│   ├── test_configuration.py             # Configuration security tests
│   ├── test_csrf.py                      # CSRF protection tests
│   ├── test_data_exposure.py             # Data exposure tests
│   ├── test_file_upload.py                # File upload security tests
│   ├── test_sql_injection.py              # SQL injection tests
│   └── test_xss.py                        # XSS vulnerability tests
│
├── static/                               # Static files directory
│   ├── assets/                           # Images, icons, and media assets
│   │
│   ├── css/                              # Stylesheet files
│   │   ├── EdTube.css
│   │   ├── about-us.css
│   │   ├── account_settings.css
│   │   ├── advanced_settings.css
│   │   ├── coins.css
│   │   ├── contact.css
│   │   ├── cropper.css
│   │   ├── dashboard.css
│   │   ├── delete_account.css
│   │   ├── edit_video.css
│   │   ├── faqs.css
│   │   ├── footer.css
│   │   ├── help-center.css
│   │   ├── login.css
│   │   ├── navbar.css
│   │   ├── notifications.css
│   │   ├── privacy-policy.css
│   │   ├── profile.css
│   │   ├── quiz.css
│   │   ├── register.css
│   │   ├── report-issue.css
│   │   ├── reviews.css
│   │   ├── search_results.css
│   │   ├── share_modal.css
│   │   ├── terms.css
│   │   ├── verify_email.css
│   │   ├── video_history.css
│   │   ├── video_player.css
│   │   ├── video_upload.css
│   │   └── watch_later.css
│   ├── js/                               # JavaScript files
│   │   ├── advanced_settings.js
│   │   ├── cropper.js
│   │   ├── edit_video.js
│   │   ├── loader.js
│   │   ├── navbar.js
│   │   ├── password-toggle.js
│   │   ├── profile.js
│   │   ├── quiz.js
│   │   ├── register.js
│   │   ├── reviews.js
│   │   ├── share_modal.js
│   │   ├── themes.js
│   │   ├── toggle_option_menu.js
│   │   ├── verify_email.js
│   │   ├── video_player.js
│   │   ├── video_upload.js
│   │   └── watch_later.js
│   ├── sample/                            # Sample data files
│   │   └── quiz_sample.csv                 # Sample quiz data
│   └── sounds/                             # Sound effects
│       ├── mic-error.mp3
│       ├── mic-off.mp3
│       └── mic-on.mp3
│
└── templates/                             # HTML templates directory
    ├── EdTube.html
    ├── about-us.html
    ├── account_settings.html
    ├── advanced_settings.html
    ├── coins.html
    ├── contact.html
    ├── dashboard.html
    ├── delete_account.html
    ├── edit_video.html
    ├── faqs.html
    ├── footer.html
    ├── forgot_password.html
    ├── help-center.html
    ├── login.html
    ├── navbar.html
    ├── notifications.html
    ├── privacy-policy.html
    ├── profile.html
    ├── quiz.html
    ├── register.html
    ├── report-issue.html
    ├── reviews.html
    ├── search_results.html
    ├── set_new_password.html
    ├── terms.html
    ├── verify_email.html
    ├── verify_reset_otp.html
    ├── video_history.html
    ├── video_player.html
    ├── video_upload.html
    ├── watch_later.html
    └── components/                          # Reusable template components
        └── share_modal.html
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY = your_secret_key
DEBUG = True
DB_NAME= your_db_name
DB_USER= your_db_user
DB_PASS = your_db_pass
DB_HOST= your_db_host
DB_PORT= your_db_port
EMAIL_HOST_USER= your_email_host_user
EMAIL_HOST_PASSWORD = your_email_host_password
CLOUDINARY_CLOUD_NAME = your_cloudinary_cloud_name
CLOUDINARY_API_KEY = your_cloudinary_api_key
CLOUDINARY_API_SECRET = your_cloudinary_api_secret

# Database (SQLite for development)
DATABASE_URL= your_db_url

# Optional Settings
# YOUTUBE_API_KEY=your_youtube_api_key
```

### Settings Overview
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Use a strong secret key
- `ALLOWED_HOSTS`: Add your domain in production
- `MEDIA_ROOT`: Path for uploaded files
- `STATIC_ROOT`: Path for collected static files

## 📖 Usage

### For Teachers
1. Register as a Teacher
2. Upload educational videos
3. Add video descriptions with hashtags
4. Manage your video library
5. View analytics (if implemented)

### For Students
1. Register as a Student
2. Browse available videos
3. Use search to find specific content
4. Save favorite videos
5. Track learning progress

### Search Examples
```
#python                    # Search by hashtag
Math by John              # Search subject by teacher
programming tutorial      # Regular search
science videos            # Category search
```

## 🔧 Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test video
python manage.py test accounts

# Run with verbose output
python manage.py test --verbosity=2
```

### Security Test
```bash
python manage.py test --testrunner=EdTube.test_runner.SecurityTestRunner
```

### Creating Migrations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Database Management
```bash
# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Check database tables
python manage.py dbshell
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py clear_cache
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues
1. Check if the issue already exists
2. Create a new issue with clear description
3. Include steps to reproduce
4. Add screenshots if applicable

### Feature Requests
1. Check if feature already exists
2. Explain the use case
3. Suggest implementation approach
4. Discuss in issues before coding

### Pull Requests
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Update documentation
6. Submit pull request

### Code Guidelines
- Follow Django coding style
- Write meaningful commit messages
- Add comments for complex logic
- Update requirements.txt if adding packages
- Test changes before submitting

### Development Setup
```bash
# Fork and clone
git clone https://github.com/your-username/EdTube.git
cd EdTube

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add: your feature description"

# Push and create PR
git push origin feature/your-feature-name
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Het Pandya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Contact

**Het Pandya**
- GitHub: [@Het-Pandya1610](https://github.com/Het-Pandya1610)
- Email: hetpandya1610@gmail.com

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework used
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icons used in the project
- [YouTube IFrame API](https://developers.google.com/youtube/iframe_api_reference) - Video embedding
- All contributors and testers who helped improve this project

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Active Development
- **Last Updated**: February 2026

## 🔗 Links

- [Repository](https://github.com/Het-Pandya1610/EdTube)
- [Issue Tracker](https://github.com/Het-Pandya1610/EdTube/issues)
- [Releases](https://github.com/Het-Pandya1610/EdTube/releases)

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/Het-Pandya1610">Het Pandya</a>, <a href="https://github.com/dakshgadhiya0">Daksh Gadhiya</a> and <a href="https://github.com/priyaldholakiya21">Priyal Dholakiya</a><br>
  If you find this project useful, please give it a ⭐
</div>
```

**To use this README:**

1. **Copy the entire content above**
2. **Create a file** named `README.md` in your project root
3. **Paste the content**
4. **Save the file**
5. **Commit to GitHub:**
```bash
git add README.md
git commit -m "Add comprehensive README.md"
git push origin main
```
