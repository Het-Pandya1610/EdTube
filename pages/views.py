from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from teacher.models import Teacher, Follower
from video.models import Video
from video.utils import save_to_history
import json, os, time
from django.http import JsonResponse
from django.contrib.auth.models import User
from video.utils import HISTORY_FILE, file_lock
from django.utils.html import escape
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import imghdr
from PIL import Image
from student.utils import get_quiz_heatmap

def index(request):
    videos = []

    if request.user.is_authenticated:
        videos = Video.objects.all().order_by('-created_at')

    context = {
        'videos': videos
    }
    return render(request, "EdTube.html", context)

def notifications(request):
    return render(request, "notifications.html")

def faqs(request):
    return render(request, "faqs.html")


def terms(request):
    return render(request, "terms.html")


def dashboard(request):
    return render(request, "dashboard.html")


def reviews(request):
    return render(request, "reviews.html")


def reportIssue(request):
    return render(request, "report-issue.html")


def privacyPolicy(request):
    return render(request, "privacy-policy.html")


def helpCenter(request):
    return render(request, "help-center.html")


def contact(request):
    return render(request, "contact.html")


def aboutUs(request):
    return render(request, "about-us.html")


def search(request):
    raw_query = request.GET.get("q", "").strip()
    query = escape(raw_query)
    
    videos = []
    teachers = []
    
    if query:
        if request.user.is_authenticated:
            save_to_history("search", request.user.email, query)
        
        # Check for "subject by teacher" pattern (e.g., "Math by John")
        if ' by ' in raw_query.lower():
            parts = raw_query.lower().split(' by ')
            if len(parts) == 2:
                subject_part = parts[0].strip()
                teacher_part = parts[1].strip()
                
                # Search for videos with subject and teacher name
                videos = Video.objects.filter(
                    Q(subject__icontains=subject_part) &
                    Q(teacher__name__icontains=teacher_part)
                ).select_related("teacher")
                teachers = Teacher.objects.filter(
                    Q(name__icontains=teacher_part) |
                    Q(username__icontains=teacher_part)
                )
            else:
                videos = Video.objects.filter(
                    Q(title__icontains=raw_query) |
                    Q(subject__icontains=raw_query) |
                    Q(description__icontains=raw_query)
                ).select_related("teacher")
                
                teachers = Teacher.objects.filter(
                    Q(name__icontains=raw_query) |
                    Q(username__icontains=raw_query)
                )
                
        elif raw_query.startswith('#'):
            tag_query = query[1:]

            videos = Video.objects.filter(
                Q(description__icontains=f" #{tag_query} ") |  # Hashtag with spaces around
                Q(description__icontains=f" #{tag_query}\n") |  # Hashtag followed by newline
                Q(description__icontains=f"\n#{tag_query} ") |  # Hashtag preceded by newline
                Q(description__icontains=f"#{tag_query},") |    # Hashtag followed by comma
                Q(description__icontains=f",#{tag_query}") |    # Hashtag preceded by comma
                Q(description__startswith=f"#{tag_query} ") |   # Hashtag at start of description
                Q(title__icontains=tag_query) |                # Also search in title
                Q(subject__icontains=tag_query)                # Also search in subject
            ).select_related("teacher")
            
            teachers = Teacher.objects.filter(
                Q(name__icontains=tag_query) |
                Q(username__icontains=tag_query)
            )
        else:
            # Normal search (existing logic)
            videos = Video.objects.filter(
                Q(title__icontains=raw_query) |
                Q(subject__icontains=raw_query) |
                Q(description__icontains=raw_query)
            ).select_related("teacher")

            teachers = Teacher.objects.filter(
                Q(name__icontains=raw_query) |
                Q(username__icontains=raw_query)
            )
    
    return render(request, "search_results.html", {
        "query": query,
        "videos": videos,
        "teachers": teachers,
    })
    
       
def get_search_suggestions(request):
    if not request.user.is_authenticated or not os.path.exists(HISTORY_FILE):
        return JsonResponse([], safe=False)

    try:
        with open(HISTORY_FILE, 'r') as f:
            content = json.load(f)
            
            # Filter searches for the logged-in user (Het or anyone else)
            user_history = [
                item['query'] for item in content.get("search_history", []) 
                if item['email'] == request.user.email
            ]
            
            # dict.fromkeys removes duplicates while keeping order
            # reversed() makes sure the most recent searches show up first
            unique_history = list(dict.fromkeys(reversed(user_history)))[:8]
            return JsonResponse(unique_history, safe=False)
    except (json.JSONDecodeError, IOError):
        return JsonResponse([], safe=False)


def delete_search_suggestion(request):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            query_to_delete = data.get("query")
            email = request.user.email #

            with file_lock: # Prevent corruption during write
                if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, 'r') as f:
                        content = json.load(f)
                    
                    # Filter out the specific query for this user
                    content["search_history"] = [
                        item for item in content.get("search_history", [])
                        if not (item['email'] == email and item['query'] == query_to_delete)
                    ]

                    with open(HISTORY_FILE, 'w') as f:
                        json.dump(content, f, indent=4)
                    
                    return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    return JsonResponse({"status": "unauthorized"}, status=401)
    

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_following = False
    is_owner = False
    if request.user.is_authenticated and request.user == profile_user:
        is_owner = True

    if request.user.is_authenticated and profile_user.profile.role == 'tutor':
        is_following = Follower.objects.filter(
            teacher=profile_user.teacher, 
            follower=request.user
        ).exists()    
    
    context = {
        'profile_user': profile_user, 
        'is_owner': is_owner, 
        'is_following': is_following,         
    }
    
    if profile_user.profile.role == 'student':
        student = profile_user.student
        context['quiz_heatmap'] = get_quiz_heatmap(student)
    
    return render(request, 'profile.html', context)

@require_POST
@csrf_exempt
def upload_profile_image(request):
    """
    Handle profile picture and banner uploads
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    
    try:
        # Get the uploaded image
        image_file = request.FILES.get('image')
        image_type = request.POST.get('type', 'pfp')  # 'pfp' or 'banner'
        
        if not image_file:
            return JsonResponse({
                'status': 'error',
                'message': 'No image provided'
            }, status=400)
        
        # Validate file type
        valid_image_types = ['jpeg', 'jpg', 'png', 'gif', 'bmp']
        file_type = imghdr.what(image_file)
        
        if file_type not in valid_image_types:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid image format. Allowed: {", ".join(valid_image_types)}'
            }, status=400)
        
        # Validate file size (max 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'status': 'error',
                'message': 'Image size must be less than 10MB'
            }, status=400)
        
        # Process the image based on type
        user = request.user
        
        # Generate unique filename
        timestamp = int(time.time())
        ext = image_file.name.split('.')[-1].lower()
        filename = f"{image_type}_{user.id}_{timestamp}.{ext}"
        
        # Save to appropriate model field based on user role
        if hasattr(user, 'profile'):
            if user.profile.role == 'tutor':
                teacher = user.teacher
                if image_type == 'pfp':
                    # Delete old profile picture if exists
                    if teacher.pfp:
                        teacher.pfp.delete(save=False)
                    teacher.pfp.save(filename, ContentFile(image_file.read()), save=True)
                    image_url = teacher.pfp.url
                elif image_type == 'banner':
                    # Delete old banner if exists
                    if teacher.banner_img:
                        teacher.banner_img.delete(save=False)
                    teacher.banner_img.save(filename, ContentFile(image_file.read()), save=True)
                    image_url = teacher.banner_img.url
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid image type'
                    }, status=400)
            elif user.profile.role == 'student':
                student = user.student
                if image_type == 'pfp':
                    # Delete old profile picture if exists
                    if student.pfp:
                        student.pfp.delete(save=False)
                    student.pfp.save(filename, ContentFile(image_file.read()), save=True)
                    image_url = student.pfp.url
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Students can only upload profile pictures'
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Unknown user role'
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'User profile not found'
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{image_type} updated successfully',
            'image_url': image_url
        })
        
    except Exception as e:
        import traceback
        print(f"Upload error: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)