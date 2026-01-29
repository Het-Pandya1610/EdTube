from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .models import Video,Comment, CommentReply
from teacher.models import Teacher
from .utils import save_to_history 
from .utils import HISTORY_FILE
import json, os

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


def watchVideo(request):
    video_id = request.GET.get('v') 
    
    if not video_id:
        return redirect('home')
        
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
            video.save(update_field=["comment_count"])
            return redirect(request.path + f'?v={video_id}')
        
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            
            # Check if it's a description update request
            if data.get('action') == 'update_description':
                # Verify user owns the video
                if video.teacher.user != request.user:
                    return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
                
                # Update description
                video.description = data.get('description', '')
                video.save()
                
                # Return formatted description
                from django.utils.html import linebreaks, urlize
                formatted_desc = linebreaks(urlize(video.description))
                
                return JsonResponse({
                    'status': 'success',
                    'formatted_description': formatted_desc
                })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

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


def videoHistory(request):
    watched_videos = []
    if request.user.is_authenticated:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    content = json.load(f)
                    # Filter history for current user and get video IDs
                    history_entries = [
                        item for item in content.get("video_history", []) 
                        if item['email'] == request.user.email
                    ]
                    
                    # Sort by most recent (timestamp) and get unique IDs
                    history_entries.sort(key=lambda x: x['timestamp'], reverse=True)
                    video_ids = []
                    for entry in history_entries:
                        if entry['video_id'] not in video_ids:
                            video_ids.append(entry['video_id'])
                    
                    # Fetch Video objects from DB in the correct order
                    # Using a list to maintain the 'most recent' order
                    unordered_videos = Video.objects.filter(video_id__in=video_ids[:20])
                    video_map = {v.video_id: v for v in unordered_videos}
                    watched_videos = [video_map[vid] for vid in video_ids if vid in video_map]
            except (json.JSONDecodeError, IOError):
                pass

    return render(request, 'video_history.html', {'videos': watched_videos})
