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

    for i, part in enumerate([p.lower() for p in parts]):
        if part in SURNAME_SET:
            return " ".join(parts[:i]), " ".join(parts[i:])
    return parts[0], parts[-1]


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

            if not email or not purpose:
                messages.error(request, "Session expired. Please try again.")
                return redirect("login")

            user = User.objects.filter(email=email).first()

            verification = EmailVerification.objects.filter(
                user=user,
                is_used=False,
                purpose=purpose
            ).order_by("-created_at").first()

            if not verification or verification.is_expired() or verification.otp != otp_entered:
                return render(request, "verify_email.html", {
                    "email": email,
                    "error": "Invalid or expired OTP"
                })

            # mark used
            verification.is_used = True
            verification.save()

            # mark email verified
            profile = user.profile
            profile.is_email_verified = True
            profile.save()

            # ================= LOGIN PURPOSE =================
            if purpose == "login":

                if not user_id:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("login")

                auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

                # cleanup session
                request.session.pop("pending_user_id", None)
                request.session.pop("pending_email", None)
                request.session.pop("otp_purpose", None)

                return redirect("index")

            # ================= REGISTER PURPOSE =================
            auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            request.session.pop("pending_email", None)
            request.session.pop("otp_purpose", None)

            messages.success(request, "Email verified successfully!")
            return redirect("index")

        # ================= REGISTER =================
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

        # send OTP
        otp = EmailVerification.generate_otp()

        EmailVerification.objects.create(
            user=user,
            otp=otp,
            purpose="register"
        )

        send_otp_email(email, otp, "registration")

        request.session["pending_email"] = email
        request.session["otp_purpose"] = "register"

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
            return render(request, "login.html", {
                "error": "Email and password are required"
            })

        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, "login.html", {"error": "Email not found"})

        username = email.split("@")[0]

        auth_user = authenticate(request, username=username, password=password)

        if not auth_user:
            return render(request, "login.html", {"error": "Invalid password"})

        # ================= EMAIL NOT VERIFIED =================
        if not user.profile.is_email_verified:

            EmailVerification.objects.filter(
                user=user,
                is_used=False,
                purpose="login"
            ).update(is_used=True)

            otp = EmailVerification.generate_otp()

            EmailVerification.objects.create(
                user=user,
                otp=otp,
                purpose="login"
            )

            send_otp_email(email, otp, "login")

            request.session["pending_email"] = email
            request.session["pending_user_id"] = user.id
            request.session["otp_purpose"] = "login"

            return render(request, "verify_email.html", {
                "email": email,
                "error": "Please verify your email"
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
                "error": "Invalid or expired OTP"
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
    
    profile = request.user.profile
    if profile.bio == bio:
        messages.info(request, "No changes detected in bio.")
        return redirect("advanced_settings")
    
    profile.bio = bio
    profile.save()
    
    messages.success(request, "Bio updated successfully!")
    return redirect("advanced_settings")

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
