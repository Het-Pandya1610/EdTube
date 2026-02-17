from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Video,Comment, CommentReply, Quiz, VideoHistory
from teacher.models import Teacher
from .utils import save_to_history
from django.utils.html import linebreaks, urlize
from .utils import HISTORY_FILE
import json, os
from django.db import transaction
import csv

@login_required
def videoUpload(request):
    if request.user.profile.role != "tutor":
        return HttpResponseForbidden("You are not allowed to upload videos")

    teacher = request.user.teacher

    if request.method == "POST":
        video_url = request.POST.get("video_url")
        video_file = request.FILES.get("video_file")
        video = Video.objects.create(
            teacher=teacher,
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            language=request.POST.get("language"),
            subject=request.POST.get("subject"),
            notes=request.FILES.get("notes"),
            quiz=request.FILES.get("quiz"),
        )
        if video_url:
            video.video_link = video_url
        if video_file:
            video.video_file = video_file
            video.thumbnail = request.FILES.get("thumbnail")

        video.save()
        teacher.nov += 1
        teacher.save()

        return redirect("index")

    return render(request, "video_upload.html")        
    
def upload_quiz_file_in_database(video, csv_file):

    try:
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        with transaction.atomic():

            quiz_objects = []

            for row in reader:

                # Validate correct option
                correct_option = row["correct_option"].upper()
                if correct_option not in ["A", "B", "C", "D"]:
                    raise ValueError("Invalid correct_option value")

                quiz_objects.append(
                    Quiz(
                        video=video,
                        question_id=row["question_id"],
                        question_text=row["question_text"],
                        option_a=row["option_a"],
                        option_b=row["option_b"],
                        option_c=row["option_c"],
                        option_d=row["option_d"],
                        correct_option=correct_option
                    )
                )

            Quiz.objects.bulk_create(quiz_objects)

        return True

    except Exception as e:
        print("CSV Quiz Upload Error:", e)
        return False

def watchVideo(request):
    video_id = request.GET.get('v') 
    
    if not video_id:
        return redirect('index')
        
    video = get_object_or_404(Video, video_id=video_id)

    if request.user.is_authenticated:
        save_to_history("video", request.user.email, video_id)
        
        session_key = f'viewed_video_{video_id}'
        if not request.session.get(session_key):
            video.views_count += 1
            video.save()
            request.session[session_key] = True
    
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("comment")

        if content and request.user.profile.role in ["student", "tutor"]:
            Comment.objects.create(
                video=video,
                author=request.user,
                content=content
            )
            video.comment_count+=1
            video.save(update_fields=["comment_count"])
            return redirect(request.path + f'?v={video_id}')
        
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)

            if data.get('action') == 'update_description':
                if video.teacher.user != request.user:
                    return JsonResponse(
                        {'status': 'error', 'message': 'Permission denied'},
                        status=403
                    )

                video.description = data.get('description', '')
                video.save()

                formatted_desc = linebreaks(urlize(video.description))

                return JsonResponse({
                    'status': 'success',
                    'formatted_description': formatted_desc
                })

            return JsonResponse(
                {'status': 'error', 'message': 'Invalid action'},
                status=400
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid JSON'},
                status=400
            )

    comments = Comment.objects.filter(
        video=video,
        is_reply=False
    ).select_related('author').prefetch_related('replies').order_by('-created_at')

    return render(request, 'video_player.html', {
        'video': video,
        'comments': comments
    })

@login_required
def add_reply(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == "POST":
        content = request.POST.get("reply")

        if content and request.user.profile.role in ["student", "tutor"]:
            CommentReply.objects.create(
                comment=comment,
                author=request.user,
                content=content
            )

    return redirect(request.META.get('HTTP_REFERER', '/'))

def searchVideos(request):
    query = request.GET.get('q')
    
    if query and request.user.is_authenticated:
        # Save the search query to the JSON file
        save_to_history("search", request.user.email, query)
        
    # Your search filtering logic here...
    videos = Video.objects.filter(title__icontains=query)
    return render(request, 'search_results.html', {'videos': videos, 'query': query})


@login_required
def toggle_video_like(request, video_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    video = get_object_or_404(Video, video_id=video_id)
    user = request.user

    if user in video.likes.all():
        # UNLIKE
        video.likes.remove(user)
        video.like_count = max(video.like_count - 1, 0)
        liked = False
    else:
        # LIKE
        video.likes.add(user)
        video.like_count += 1
        liked = True

    video.save(update_fields=["like_count"])

    return JsonResponse({
        "liked": liked,
        "like_count": video.like_count
    })

@login_required
def videoHistory(request):
    """View for video history page"""
    
    # Get user's video history with prefetched video data
    history_entries = VideoHistory.objects.filter(
        user=request.user
    ).select_related('video').order_by('-watched_at')[:20]
    
    # Extract unique videos (keeping order)
    seen_ids = set()
    watched_videos = []
    for entry in history_entries:
        if entry.video.video_id not in seen_ids:
            seen_ids.add(entry.video.video_id)
            watched_videos.append(entry.video)
    
    context = {
        'videos': watched_videos,
        'total_count': VideoHistory.objects.filter(user=request.user).count()
    }
    
    return render(request, 'video_history.html', context)

def quiz(request):
    return render(request, 'quiz.html')
