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
pip install django pillow python-dotenv
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
├── accounts/                 # User authentication
│   ├── models.py            # User & Profile models
│   ├── views.py             # Auth views
│   └── urls.py              # Auth URLs
├── video/                   # Video functionality
│   ├── models.py            # Video model
│   ├── views.py             # Video views
│   ├── urls.py              # Video URLs
│   └── templatetags/        # Custom template tags
├── teacher/                 # Teacher features
│   ├── models.py            # Teacher model
│   └── views.py             # Teacher views
├── student/                 # Student features
│   ├── models.py            # Student model
│   └── views.py             # Student views
├── courses/                 # Course management
│   ├── models.py            # Course model
│   └── views.py             # Course views
├── blog/                    # Educational blog
│   ├── models.py            # Blog model
│   └── views.py             # Blog views
├── pages/                   # Static pages
│   └── views.py             # Static page views
├── templates/               # HTML templates
│   ├── video_player.html    # Video player template
│   ├── search_results.html  # Search results template
│   ├── login.html           # Login template
│   ├── register.html        # Register template
│   └── dashboard.html       # Dashboard template
├── static/                  # Static files
│   ├── assets/              # Images and logos
│   ├── js/                  # JavaScript files
│   └── css/                 # CSS files
├── media/                   # User uploads
│   ├── teacher_profiles/    # Teacher profile pictures
│   ├── videos/              # Uploaded videos
│   ├── video_thumbnails/    # Video thumbnails
│   ├── video_notes/         # Video notes
│   └── video_quizzes/       # Video quizzes
├── EdTube/                  # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URLs
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Optional Settings
# YOUTUBE_API_KEY=your-youtube-api-key
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

## 🚢 Deployment

### Preparation
1. Set `DEBUG=False` in production
2. Generate a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` with your domain
4. Use PostgreSQL for production database
5. Set up proper static file serving

### Deployment Options

#### Option 1: Render (Recommended)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Add environment variables:
   - `DATABASE_URL` (from Render PostgreSQL)
   - `SECRET_KEY` (generate a strong one)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-render-url.onrender.com`

#### Option 2: Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway up
```

#### Option 3: Heroku
```bash
# Install Heroku CLI
# Create Procfile with:
web: gunicorn EdTube.wsgi:application

# Deploy
git push heroku main
heroku run python manage.py migrate
```

### Production Checklist
- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY`
- [ ] Configured `ALLOWED_HOSTS`
- [ ] PostgreSQL database
- [ ] Static files served via CDN/Whitenoise
- [ ] Media files served via cloud storage
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Error logging setup

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
- **Last Updated**: January 2026

## 🔗 Links

- [Repository](https://github.com/Het-Pandya1610/EdTube)
- [Issue Tracker](https://github.com/Het-Pandya1610/EdTube/issues)
- [Releases](https://github.com/Het-Pandya1610/EdTube/releases)

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/Het-Pandya1610">Het Pandya</a><br>
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
