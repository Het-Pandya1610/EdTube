from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.contrib.auth.decorators import login_required
from teacher.models import Teacher
from student.models import Student
from teacher.utils import generate_teacher_id
from student.utils import generate_student_id
from .utils import generate_suggestions_by_name

import csv
from pathlib import Path

from .models import Profile, EmailVerification
from .mail_utils import send_otp_email


# ================= SURNAME DATA =================
SURNAME_FILE = Path(__file__).resolve().parent / "data" / "surnames.csv"
SURNAME_SET = set()

with open(SURNAME_FILE, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if row:
            SURNAME_SET.add(row[0].strip().lower())


def split_name(fullname):
    parts = fullname.strip().split()
    if len(parts) == 1:
        return parts[0], ""

    for i, part in enumerate([p.lower() for p in parts]):
        if part in SURNAME_SET:
            return " ".join(parts[:i]), " ".join(parts[i:])
    return parts[0], parts[-1]


def register_view(request):
    return reg(request) 

@transaction.atomic
def reg(request):
    if request.method == "POST":
        
        # ---------- OTP VERIFY ----------
        if "verify_otp" in request.POST:
            email = request.session.get("pending_email")
            purpose = request.session.get("pending_purpose", "registration")
            otp_entered = request.POST.get("otp")
            
            if not email:
                messages.error(request, "Session expired. Please try again.")
                return redirect("register")
            
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "User not found")
                return redirect("register")
            
            # Get the latest unused OTP
            verification = EmailVerification.objects.filter(
                user=user, is_used=False
            ).order_by("-created_at").first()
            
            # Validate OTP
            if not verification:
                return render(request, "verify_email.html", {
                    "email": email,
                    "purpose": purpose,
                    "error": "No valid OTP found. Please request a new one."
                })
            
            if verification.is_expired():
                return render(request, "verify_email.html", {
                    "email": email,
                    "purpose": purpose,
                    "error": "OTP has expired. Please request a new one."
                })
            
            if verification.otp != otp_entered:
                return render(request, "verify_email.html", {
                    "email": email,
                    "purpose": purpose,
                    "error": "Invalid OTP. Please try again."
                })
            
            # Mark OTP as used
            verification.is_used = True
            verification.save()
            
            # Mark email as verified
            profile = user.profile
            profile.is_email_verified = True
            profile.save()
            
            # Clear session data
            if "pending_email" in request.session:
                del request.session["pending_email"]
            if "pending_purpose" in request.session:
                del request.session["pending_purpose"]
            
            # Handle based on purpose
            if purpose == "login":
                # For login, log the user in
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, "Email verified successfully! You're now logged in.")
                return redirect("index")
            else:
                # For registration, log the user in and welcome them
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"Welcome to EdTube, {user.first_name}! Your account has been verified.")
                return redirect("index")

        # ---------- REGISTER ----------
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        if not all([fullname, email, password, confirm_password, role]):
            return render(request, "register.html", {"error": "All fields required"})

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Email already exists"})

        first_name, last_name = split_name(fullname)
        username = email.split("@")[0]
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        profile = user.profile
        profile.role = role
        profile.save()

        if role == "tutor":
            Teacher.objects.create(
                teacher_id=generate_teacher_id(fullname),
                user=user,
                name=fullname,
                username=username
            )
        else:
            Student.objects.create(
                student_id=generate_student_id(fullname),
                user=user,
                name=fullname,
                username=username
            )

        otp = EmailVerification.generate_otp()
        EmailVerification.objects.create(user=user, otp=otp)

        send_otp_email(email, otp, "registration")
        request.session["pending_email"] = email

        return render(request, "verify_email.html", {
            "email": email,
            "success": "OTP sent to your email"
        })

    return render(request, "register.html")


def resend_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        purpose = request.POST.get("purpose", "registration")
        
        user = User.objects.filter(email=email).first()
        
        if not user:
            messages.error(request, "User not found")
            return redirect("reg")
        
        # Mark old OTPs as used
        EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate new OTP
        otp = EmailVerification.generate_otp()
        EmailVerification.objects.create(user=user, otp=otp)
        
        # Send OTP with correct purpose
        send_otp_email(email, otp, purpose)
        
        # Update session
        request.session["pending_email"] = email
        request.session["pending_purpose"] = purpose
        
        # Prepare response context
        context = {
            "email": email,
            "purpose": purpose,
            "success": "New OTP has been sent to your email"
        }
        
        # Add appropriate message based on purpose
        if purpose == "login":
            context["message"] = "Please verify your email to login"
        else:
            context["message"] = "Please verify your email to complete registration"
        
        return render(request, "verify_email.html", context)
    
    return redirect("reg")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if not email or not password:
            return render(request, "login.html", {"error": "Email and password are required"})
        
        user = User.objects.filter(email=email).first()
        if not user:
            return render(request, "login.html", {"error": "Email not found"})

        username = email.split("@")[0]
        
        # Authenticate to check password first
        user = authenticate(request, username=username, password=password)
        if not user:
            return render(request, "login.html", {"error": "Invalid password"})
        
        # Check if email is verified
        profile = user.profile
        if not profile.is_email_verified:
            # Mark old OTPs as used
            EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Generate new OTP for LOGIN purpose
            otp = EmailVerification.generate_otp()
            EmailVerification.objects.create(user=user, otp=otp)
            
            # Send LOGIN OTP
            send_otp_email(email, otp, "login")
            
            # Store both email and purpose in session
            request.session["pending_email"] = email
            request.session["pending_purpose"] = "login"
            request.session["pending_user_id"] = user.id  # Store user ID for later login
            
            return render(request, "verify_email.html", {
                "email": email,
                "purpose": "login",
                "message": "Please verify your email to complete login"
            })

        # If email is already verified, log them in directly
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("index")

    return render(request, "login.html")


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
def account_settings(request):
    user = request.user
    profile = user.profile
    teacher = user.teacher
    if hasattr(user, 'student'):
        student = user.student
    else:
        student=None
    suggestions = None

    if request.method == 'POST':
        new_username = request.POST.get('username').strip().lower()
        if new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                full_name = f"{user.first_name} {user.last_name}"
                suggestions = generate_suggestions_by_name(full_name)
                messages.error(request, f"The username @{new_username} is already taken.")
                return render(request, 'account_settings.html', {'suggestions': suggestions})
            else:
                user.username = new_username
                
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        if new_pass:
            if new_pass == confirm_pass:
                user.set_password(new_pass)
                update_session_auth_hash(request, user) # Don't log out
            else:
                messages.error(request, "Passwords do not match!")
                return redirect('account_settings')

        user.save()

        if profile.role=="tutor":
            teacher.bio = request.POST.get('bio')
        else:
            student.bio = request.POST.get('bio')
        teacher.center_address = request.POST.get('center_address')
        teacher.degree_pursued = request.POST.get('degree_pursued')
        teacher.experience_years = request.POST.get('experience_years') or 0
        teacher.save()

        
        messages.success(request, "Your settings have been updated successfully!")
        return redirect('account_settings')

    return render(request, 'account_settings.html')
