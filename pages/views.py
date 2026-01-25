from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from teacher.models import Teacher, Follower
from video.models import Video
from video.utils import save_to_history
import json, os
from django.http import JsonResponse
from django.contrib.auth.models import User
from video.utils import HISTORY_FILE, file_lock

def index(request):
    return render(request, "EdTube.html")


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
    query = request.GET.get("q", "").strip()
    
    videos = []
    teachers = []
    
    if query:
        if request.user.is_authenticated:
            save_to_history("search", request.user.email, query)
        
        # Check if query starts with # (hashtag search)
        if query.startswith('#'):
            # Remove the # for the search
            tag_query = query[1:]  # Remove the # character
            
            # Search for hashtags in description
            # Using regex for more accurate hashtag matching
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
                Q(title__icontains=query) |
                Q(subject__icontains=query) |
                Q(description__icontains=query)
            ).select_related("teacher")

            teachers = Teacher.objects.filter(
                Q(name__icontains=query) |
                Q(username__icontains=query)
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

    return render(request, 'profile.html', context)