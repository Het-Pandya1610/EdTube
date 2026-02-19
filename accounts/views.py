from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from teacher.models import Teacher
from student.models import Student
from teacher.utils import generate_teacher_id
from student.utils import generate_student_id
from .utils import generate_suggestions_by_name, generate_suggestions_by_username
from django.contrib.auth.hashers import make_password

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
    
    if parts[0].lower() not in SURNAME_SET:
        for i, part in enumerate(parts):
            if part.lower() in SURNAME_SET:
                return " ".join(parts[:i]), " ".join(parts[i:])

    if parts[-1].lower() not in SURNAME_SET:
        for i, part in enumerate(parts):
            if part.lower() in SURNAME_SET:
                if i == 0 and len(parts) > 1:
                    remaining_parts = parts[1:]
                    remaining_are_names = all(p.lower() not in SURNAME_SET for p in remaining_parts)
                    if remaining_are_names:
                        return " ".join(parts[1:]), parts[0]
                    
    for i in range(len(parts) - 1, 0, -1):
        if parts[i].lower() in SURNAME_SET:
            preceding_parts = parts[:i]
            preceding_are_names = all(p.lower() not in SURNAME_SET for p in preceding_parts)
            if preceding_are_names:
                return " ".join(parts[:i]), " ".join(parts[i:])
            
    for i in range(len(parts)):
        if parts[i].lower() in SURNAME_SET:
            following_parts = parts[i+1:]
            following_are_names = all(p.lower() not in SURNAME_SET for p in following_parts)
            if following_are_names:
                return " ".join(parts[i+1:]), parts[i]
    
    for i in range(1, len(parts) - 1):
        if parts[i].lower() in SURNAME_SET:
            return " ".join(parts[:i]), " ".join(parts[i:])

    return " ".join(parts[:-1]), parts[-1]


def register_view(request):
    return reg(request) 

@transaction.atomic
def reg(request):
    
    if request.method == "POST":

        # ================= OTP VERIFY =================
        if "verify_otp" in request.POST:

            email = request.session.get("pending_email")
            purpose = request.session.get("otp_purpose")
            user_id = request.session.get("pending_user_id")
            otp_entered = request.POST.get("otp")

            # Debug prints (remove in production)
            print(f"🔍 VERIFY DEBUG - Email: {email}, Purpose: {purpose}, User ID: {user_id}, OTP: {otp_entered}")
            print(f"🔍 VERIFY DEBUG - Session data: {dict(request.session.items())}")

            if not email:
                messages.error(request, "Session expired. Email not found. Please try again.")
                return redirect("login")
            
            if not purpose:
                messages.error(request, "Session expired. Purpose not found. Please try again.")
                return redirect("login")

            # Try to get user by email first
            user = User.objects.filter(email=email).first()
            
            # If not found by email and we have user_id, try by ID
            if not user and user_id:
                user = User.objects.filter(id=user_id).first()
                print(f"🔍 VERIFY DEBUG - Found user by ID: {user.username if user else 'None'}")

            if not user:
                messages.error(request, "User not found. Please register again.")
                return redirect("register")

            print(f"🔍 VERIFY DEBUG - User found: {user.username} (ID: {user.id})")

            # Get the most recent unused OTP for this user and purpose
            verification = EmailVerification.objects.filter(
                user=user,
                is_used=False,
                otp_purpose=purpose
            ).order_by("-created_at").first()

            if not verification:
                print(f"🔍 VERIFY DEBUG - No OTP found for user {user.id} with purpose '{purpose}'")
                return render(request, "verify_email.html", {
                    "email": email,
                    "error": "No OTP found. Please request a new one.",
                    "purpose": purpose
                })

            print(f"🔍 VERIFY DEBUG - OTP found: {verification.otp}, Created: {verification.created_at}")
            print(f"🔍 VERIFY DEBUG - OTP expired: {verification.is_expired()}")

            # Check if OTP is expired
            if verification.is_expired():
                return render(request, "verify_email.html", {
                    "email": email,
                    "error": "OTP has expired. Please request a new one.",
                    "purpose": purpose
                })

            # Check if OTP matches
            if verification.otp != otp_entered:
                return render(request, "verify_email.html", {
                    "email": email,
                    "error": "Invalid OTP. Please try again.",
                    "purpose": purpose
                })

            # Mark OTP as used
            verification.is_used = True
            verification.save()
            print(f"🔍 VERIFY DEBUG - OTP marked as used")

            # Mark email as verified (if not already)
            if not user.profile.is_email_verified:
                profile = user.profile
                profile.is_email_verified = True
                profile.save()
                print(f"🔍 VERIFY DEBUG - Email verified for user {user.id}")

            # ================= HANDLE BASED ON PURPOSE =================
            
            # LOGIN PURPOSE
            if purpose == "login":
                print(f"🔍 VERIFY DEBUG - Processing LOGIN purpose")

                # Log the user in
                auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                # Clean up session
                for key in ['pending_user_id', 'pending_email', 'otp_purpose']:
                    if key in request.session:
                        del request.session[key]

                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect("index")

            # REGISTRATION PURPOSE
            elif purpose == "registration" or purpose == "registeration":  # Handle typo
                print(f"🔍 VERIFY DEBUG - Processing REGISTRATION purpose")

                # Log the user in
                auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                # Clean up session
                for key in ['pending_email', 'otp_purpose']:
                    if key in request.session:
                        del request.session[key]

                messages.success(request, "Email verified successfully! Welcome to EdTube!")
                return redirect("index")

            # PASSWORD RESET PURPOSE
            elif purpose == "password_reset":
                print(f"🔍 VERIFY DEBUG - Processing PASSWORD RESET purpose")

                # Store in session for password reset
                request.session["reset_user_id"] = user.id
                request.session["reset_email"] = email
                request.session.set_expiry(900)  # 15 minutes

                # Clean up pending session data
                for key in ['pending_user_id', 'pending_email', 'otp_purpose']:
                    if key in request.session:
                        del request.session[key]

                messages.success(request, "OTP verified. Please set your new password.")
                return redirect("set_new_password")

            # UNKNOWN PURPOSE
            else:
                print(f"🔍 VERIFY DEBUG - Unknown purpose: {purpose}")
                messages.error(request, "Invalid verification purpose.")
                return redirect("login")

        # ================= REGISTER (New Registration) =================
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role = request.POST.get("role")

        print(f"🔍 REGISTER DEBUG - New registration attempt: {email}, role: {role}")

        if not all([fullname, email, password, confirm_password, role]):
            return render(request, "register.html", {"error": "All fields required"})

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "Email already exists"})

        # Split name into first and last
        first_name, last_name = split_name(fullname)
        username = email.split("@")[0]

        # Create base username and ensure uniqueness
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        print(f"🔍 REGISTER DEBUG - Creating user: {username}")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Create profile
        profile = user.profile
        profile.role = role
        profile.is_email_verified = False  # Explicitly set to False
        profile.save()

        # Create teacher or student profile
        if role == "tutor":
            Teacher.objects.create(
                teacher_id=generate_teacher_id(fullname),
                user=user,
                name=fullname,
                username=username
            )
            print(f"🔍 REGISTER DEBUG - Teacher profile created")
        else:
            Student.objects.create(
                student_id=generate_student_id(fullname),
                user=user,
                name=fullname,
                username=username
            )
            print(f"🔍 REGISTER DEBUG - Student profile created")

        # Generate and send OTP
        otp = EmailVerification.generate_otp()
        print(f"🔍 REGISTER DEBUG - OTP generated: {otp}")

        # Save OTP to database
        EmailVerification.objects.create(
            user=user,
            otp=otp,
            otp_purpose="registration"  # Fixed typo: was "registeration"
        )

        # Send OTP email
        send_otp_email(email, otp, "registration")

        # Clear any existing session data
        for key in ['pending_email', 'pending_user_id', 'otp_purpose']:
            if key in request.session:
                del request.session[key]

        # Set new session data
        request.session["pending_email"] = email
        request.session["otp_purpose"] = "registration"  # Fixed typo
        request.session.set_expiry(900)  # 15 minutes expiry
        request.session.modified = True

        print(f"🔍 REGISTER DEBUG - Session set: {dict(request.session.items())}")

        return render(request, "verify_email.html", {
            "email": email,
            "success": "OTP sent to your email. Please verify to complete registration.",
            "purpose": "registration"
        })

    # GET request - show registration form
    return render(request, "register.html")


def resend_otp(request):
    if request.method == "POST":

        email = request.POST.get("email")
        purpose = request.POST.get("purpose")   # no default

        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "User not found")
            return redirect("reg")

        # deactivate old OTPs for THIS purpose only
        EmailVerification.objects.filter(
            user=user,
            otp_purpose=purpose,
            is_used=False
        ).update(is_used=True)

        otp = EmailVerification.generate_otp()

        EmailVerification.objects.create(
            user=user,
            otp=otp,
            otp_purpose=purpose   # ✅ required
        )

        send_otp_email(email, otp, purpose)

        request.session["pending_email"] = email
        request.session["otp_purpose"] = purpose   # ✅ correct key

        return render(request, "verify_email.html", {
            "email": email,
            "purpose": purpose,
            "success": "New OTP sent"
        })

    return redirect("reg")


def login_view(request):
    
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if not email or not password:
            return render(request, "login.html", {
                "error": "Email and password are required"
            })

        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, "login.html", {"error": "Email not found"})

        auth_user = authenticate(request, username=user.username, password=password)

        if not auth_user:
            return render(request, "login.html", {"error": "Invalid password"})

        # ================= EMAIL NOT VERIFIED =================
        if not user.profile.is_email_verified:
            
            # Clear any existing OTP-related session data first
            for key in ['pending_email', 'pending_user_id', 'otp_purpose']:
                if key in request.session:
                    del request.session[key]
            
            # Mark old unused OTPs as used
            EmailVerification.objects.filter(
                user=user,
                is_used=False,
                otp_purpose="login"
            ).update(is_used=True)

            # Generate and save new OTP
            otp = EmailVerification.generate_otp()
            
            EmailVerification.objects.create(
                user=user,
                otp=otp,
                otp_purpose="login"
            )

            # Send OTP email
            send_otp_email(email, otp, "login")

            # Set session variables with explicit expiry
            request.session["pending_email"] = email
            request.session["pending_user_id"] = user.id
            request.session["otp_purpose"] = "login"
            request.session.set_expiry(900)  # 15 minutes expiry
            
            # Force session save
            request.session.modified = True

            # Debug print (remove in production)
            print(f"DEBUG - Login OTP sent - Session: {request.session.items()}")

            return render(request, "verify_email.html", {
                "email": email,
                "error": "Please verify your email",
                "purpose": "login"
            })

        # ================= NORMAL LOGIN =================
        auth_login(request, auth_user)
        return redirect("index")

    return render(request, "login.html")


def logout_view(request):
    auth_logout(request)
    return redirect('login')

@transaction.atomic
def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not found.")
            return redirect("forgot_password")

        # ❗ Invalidate old unused password reset OTPs
        EmailVerification.objects.filter(
            user=user,
            otp_purpose="password_reset",
            is_used=False
        ).update(is_used=True)

        # ✅ Generate new OTP
        otp = EmailVerification.generate_otp()

        EmailVerification.objects.create(
            user=user,
            otp=otp,
            otp_purpose="password_reset"
        )

        send_otp_email(email, otp, "password_reset")

        # store in session for verification step
        request.session["reset_email"] = email

        messages.success(request, "OTP sent to your email for password reset.")
        return redirect("verify_reset_otp")   # 🔥 IMPORTANT

    return render(request, "forgot_password.html")

def verify_reset_otp(request):
    
    email = request.session.get("reset_email")

    if not email:
        return redirect("forgot_password")

    user = User.objects.filter(email=email).first()

    if not user:
        return redirect("forgot_password")

    if request.method == "POST":

        otp_entered = request.POST.get("otp")

        verification = EmailVerification.objects.filter(
            user=user,
            otp_purpose="password_reset",
            is_used=False
        ).order_by("-created_at").first()

        if not verification or verification.is_expired() or verification.otp != otp_entered:
            return render(request, "verify_reset_otp.html", {
                "email": email,
                "error": "Invalid or expired OTP",
                "purpose": "password_reset"
            })

        verification.is_used = True
        verification.save()

        request.session["reset_user_id"] = user.id

        return redirect("set_new_password")

    return render(request, "verify_reset_otp.html", {"email": email})

def set_new_password(request):
    
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "set_new_password.html", {
                "error": "Passwords do not match"
            })

        user.password = make_password(password)
        user.save()

        # cleanup session
        del request.session["reset_user_id"]
        del request.session["reset_email"]

        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "set_new_password.html")

@login_required
def account_settings(request):

    # user = request.user
    # profile = user.profile
    
    # teacher = None
    # student = None
    
    # try:
    #     if hasattr(user, 'teacher'):
    #         teacher = user.teacher
    # except Teacher.DoesNotExist:
    #     teacher = None
        
    # try:
    #     if hasattr(user, 'student'):
    #         student = user.student
    # except Student.DoesNotExist:
    #     student = None
    
    # suggestions = None

    # if request.method == 'POST':
    #     new_username = request.POST.get('username').strip().lower()
    #     if new_username != user.username:
    #         if User.objects.filter(username=new_username).exists():
    #             full_name = f"{user.first_name} {user.last_name}"
    #             suggestions = generate_suggestions_by_name(full_name)
    #             messages.error(request, f"The username @{new_username} is already taken.")
    #             return render(request, 'account_settings.html', {'suggestions': suggestions})
    #         else:
    #             user.username = new_username
                
    #     user.first_name = request.POST.get('first_name')
    #     user.last_name = request.POST.get('last_name')
    #     user.email = request.POST.get('email')

    #     new_pass = request.POST.get('new_password')
    #     confirm_pass = request.POST.get('confirm_password')
    #     if new_pass:
    #         if new_pass == confirm_pass:
    #             user.set_password(new_pass)
    #             update_session_auth_hash(request, user) # Don't log out
    #         else:
    #             messages.error(request, "Passwords do not match!")
    #             return redirect('account_settings')

    #     user.save()

    #     profile.bio = request.POST.get('bio')
    #     teacher.center_address = request.POST.get('center_address')
    #     teacher.degree_pursued = request.POST.get('degree_pursued')
    #     teacher.experience_years = request.POST.get('experience_years') or 0
    #     teacher.save()

        
    #     messages.success(request, "Your settings have been updated successfully!")
    #     return redirect('account_settings')

    return render(request, 'account_settings.html')

@login_required
def advanced_settings(request):
    """Advanced settings page"""
    user = request.user
    profile = Profile.objects.get(user=user)
    
    # Get teacher or student
    teacher = None
    student = None
    
    if profile.role == 'tutor':
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            # Create teacher if doesn't exist
            from teacher.utils import generate_teacher_id
            teacher = Teacher.objects.create(
                teacher_id=generate_teacher_id(f"{user.first_name} {user.last_name}"),
                user=user,
                name=f"{user.first_name} {user.last_name}",
                username=user.username
            )
    else:
        try:
            student = Student.objects.get(user=user)
        except Student.DoesNotExist:
            from student.utils import generate_student_id
            student = Student.objects.create(
                student_id=generate_student_id(f"{user.first_name} {user.last_name}"),
                user=user,
                name=f"{user.first_name} {user.last_name}",
                username=user.username
            )
    
    # Generate username suggestions
    full_name = f"{user.first_name} {user.last_name}".strip()
    if full_name:
        suggestions = generate_suggestions_by_name(full_name)
    else:
        suggestions = generate_suggestions_by_username(user.username)
    
    # Get suggestions from session if any
    session_suggestions = request.session.pop('username_suggestions', None)
    if session_suggestions:
        suggestions = session_suggestions

    context = {
        'suggestions': suggestions[:5] if suggestions else [],
        'teacher': teacher,
        'student': student,
        'profile': profile,
    }
    
    return render(request, 'advanced_settings.html', context)

@login_required
@require_POST
def update_bio(request):
    bio = request.POST.get("bio","").strip()
    
    if len(bio) > 1000:
        messages.error(request, "Bio cannot exceed 1000 characters.")
        return redirect("advanced_settings")

    user = request.user
    profile = Profile.objects.get(user=user)

    if profile.bio == bio:
        messages.info(request, "No changes detected in bio.")
        return redirect("advanced_settings")

    profile.bio = bio
    profile.save()
    
    messages.success(request, "Bio updated successfully!")
    return redirect("user_profile")

@login_required
@require_POST
def update_username(request):
    """Handle username update"""
    user = request.user
    new_username = request.POST.get('username', '').strip().lower()
    
    # Validation
    if not new_username:
        messages.error(request, "Username cannot be empty.")
        return redirect('advanced_settings')
    
    if len(new_username) < 3:
        messages.error(request, "Username must be at least 3 characters long.")
        return redirect('advanced_settings')
    
    if not new_username.replace('_', '').isalnum():
        messages.error(request, "Username can only contain letters, numbers, and underscores.")
        return redirect('advanced_settings')
    
    # Check if username is taken
    if new_username != user.username:
        if User.objects.filter(username=new_username).exists():
            full_name = f"{user.first_name} {user.last_name}".strip()
            suggestions = generate_suggestions_by_name(full_name) if full_name else generate_suggestions_by_username(user.username)
            
            # Store suggestions in session
            request.session['username_suggestions'] = suggestions[:5]
            
            messages.error(request, f"The username @{new_username} is already taken.")
            return redirect('advanced_settings')
        else:
            # Update username
            old_username = user.username
            user.username = new_username
            user.save()
            update_session_auth_hash(request, user)
            # Update teacher/student username
            try:
                teacher = Teacher.objects.get(user=user)
                teacher.username = new_username
                teacher.save()
            except Teacher.DoesNotExist:
                try:
                    student = Student.objects.get(user=user)
                    student.username = new_username
                    student.save()
                except Student.DoesNotExist:
                    pass
            
            messages.success(request, f"Username updated to @{new_username}!")
    
    return redirect('advanced_settings')

@login_required
@require_POST
def update_name_appearance(request):
    """Update name display format"""
    try:
        user = request.user
        profile = Profile.objects.get(user=user)
        
        name_format = request.POST.get('name_format', 'full')
        
        # Validate format
        valid_formats = ['full', 'first_last', 'first_only', 'last_only', 'username']
        if name_format not in valid_formats:
            return JsonResponse({
                'success': False,
                'error': 'Invalid name format.'
            }, status=400)
        
        # Update profile
        profile.name_format = name_format
        profile.save()
        
        # Get formatted name
        formatted_name = get_formatted_name(user, name_format)
        
        return JsonResponse({
            'success': True,
            'message': 'Name display format updated!',
            'formatted_name': formatted_name,
            'format': name_format
        })
        
    except Profile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Profile not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def update_teacher_info(request):
    """Update teacher professional information"""
    user = request.user
    profile = Profile.objects.get(user=user)
    
    # Check if user is a teacher
    if profile.role != 'tutor':
        messages.error(request, "Only teachers can update professional information.")
        return redirect('advanced_settings')
    
    try:
        teacher = Teacher.objects.get(user=user)
        
        # Update degree
        degree = request.POST.get('degree_pursued', '').strip()
        if degree:
            teacher.degree_pursued = degree
        
        # Update experience years
        experience = request.POST.get('experience_years', '').strip()
        if experience:
            try:
                teacher.experience_years = int(experience)
            except ValueError:
                messages.error(request, "Please enter a valid number for experience.")
                return redirect('advanced_settings')
        
        # Update address
        address = request.POST.get('center_address', '').strip()
        if address:
            teacher.center_address = address
        
        teacher.save()
        
        # Check for verification eligibility
        if teacher.degree_pursued and teacher.experience_years and teacher.experience_years >= 2:
            teacher.verification_requested = True
            teacher.save()
            messages.success(request, "Professional info updated! Verification requested.")
        else:
            messages.success(request, "Professional information updated successfully!")
        
    except Teacher.DoesNotExist:
        messages.error(request, "Teacher profile not found.")
    
    return redirect('advanced_settings')

@login_required
@require_http_methods(["GET", "POST"])  # Allow both GET and POST
def check_username(request):
    """AJAX endpoint to check username availability"""
    # Get username from GET or POST
    if request.method == 'GET':
        username = request.GET.get('username', '').strip().lower()
    else:  # POST
        username = request.POST.get('username', '').strip().lower()
    
    print(f"Checking username: {username}")  # Debug print
    
    if not username:
        return JsonResponse({
            'available': False,
            'error': 'Username is required'
        }, status=400)
    
    if len(username) < 3:
        return JsonResponse({
            'available': False,
            'error': 'Username must be at least 3 characters'
        })
    
    if not username.replace('_', '').isalnum():
        return JsonResponse({
            'available': False,
            'error': 'Username can only contain letters, numbers, and underscores'
        })
    
    # Check if username exists and is not current user
    is_taken = User.objects.filter(username=username).exists()
    is_current = username == request.user.username
    
    available = not is_taken or is_current
    
    suggestions = []
    if is_taken and not is_current:
        full_name = f"{request.user.first_name} {request.user.last_name}".strip()
        if full_name:
            suggestions = generate_suggestions_by_name(full_name)
        else:
            suggestions = generate_suggestions_by_username(username)
    
    response_data = {
        'available': available,
        'is_current': is_current,
        'suggestions': suggestions[:5] if suggestions else [],
        'message': f"@{username} is {'available' if available else 'taken'}!"
    }
    
    print(f"Response: {response_data}")  # Debug print
    
    return JsonResponse(response_data)

@login_required
def suggest_usernames(request):
    """Generate username suggestions"""
    user = request.user
    
    full_name = f"{user.first_name} {user.last_name}".strip()
    
    if full_name:
        suggestions = generate_suggestions_by_name(full_name)
    else:
        suggestions = generate_suggestions_by_username(user.username)
    
    # Filter out taken usernames and current username
    filtered = []
    for suggestion in suggestions:
        if not User.objects.filter(username=suggestion).exists() and suggestion != user.username:
            filtered.append(suggestion)
            if len(filtered) >= 10:  # Get more suggestions
                break
    
    print(f"Generated suggestions: {filtered}")  # Debug print
    
    return JsonResponse({
        'suggestions': filtered
    })

@login_required
def get_name_preview(request):
    """Get name preview for selected format"""
    user = request.user
    format_code = request.GET.get('format', 'full')
    
    formatted_name = get_formatted_name(user, format_code)
    
    return JsonResponse({
        'formatted_name': formatted_name,
        'username': f"@{user.username}",
        'format': format_code
    })

# ==================== HELPER FUNCTIONS ====================

def get_formatted_name(user, format_code):
    """Return user's name in specified format"""
    first_name = user.first_name or "User"
    last_name = user.last_name or ""
    username = user.username
    
    if format_code == 'full':
        return f"{first_name} {last_name}".strip()
    elif format_code == 'first_last':
        return f"{first_name} {last_name[0]}." if last_name else first_name
    elif format_code == 'first_only':
        return first_name
    elif format_code == 'last_only':
        return last_name if last_name else first_name
    elif format_code == 'username':
        return f"@{username}"
    else:
        return f"{first_name} {last_name}".strip()


@login_required
@require_POST
def upgrade_to_teacher(request):
    user = request.user   # ✅ get logged-in user properly

    profile = Profile.objects.get(user=user)
    profile.role = 'tutor'
    profile.save()

    from teacher.utils import generate_teacher_id
    teacher, created = Teacher.objects.get_or_create(
        teacher_id=generate_teacher_id(f"{user.first_name} {user.last_name}"),
        user=user,
        name=f"{user.first_name} {user.last_name}",
        username=user.username
    )

    try:
        student = Student.objects.get(user=user)
        student.delete()
    except Student.DoesNotExist:
        pass

    return redirect('index')

@login_required
@transaction.atomic
def delete_account(request):

    if request.method == "POST":

        password = request.POST.get("password")

        if not request.user.check_password(password):
            messages.error(request, "Incorrect password.")
            return redirect("account_settings")

        user = request.user

        # Optional: delete Teacher / Student profile explicitly
        if hasattr(user, "teacher"):
            user.teacher.delete()

        if hasattr(user, "student"):
            user.student.delete()

        user.delete()

        auth_logout(request)

        messages.success(request, "Your account has been deleted successfully.")
        return redirect("index")

    return render(request, "delete_account.html")
