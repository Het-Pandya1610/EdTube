from pathlib import Path
import subprocess
import uuid
from django.core.files.base import ContentFile
from notifications.models import Notification
from teacher.models import Follower
from EdTube import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from .models import Video,Comment, CommentReply, Quiz, VideoHistory, WatchLater
from teacher.models import Teacher
from .utils import save_to_history
from django.contrib import messages
from django.utils.html import linebreaks, urlize
from .utils import HISTORY_FILE
import json, os
import random
from django.db import transaction
import csv
from django.db.models import F
from student.models import Student, QuizAttempt, CoinTransaction
import cloudinary.api

@login_required
def videoUpload(request):
    if request.user.profile.role != "tutor":
        return HttpResponseForbidden("You are not allowed to upload videos")

    teacher = request.user.teacher

    if request.method == "POST":
        video_url = request.POST.get("video_url")
        video_file = request.FILES.get("video_file")
        thumbnail_file = request.FILES.get("thumbnail")
        notes_file = request.FILES.get("notes")
        quiz_file = request.FILES.get("quiz")

        try:
            with transaction.atomic():
                # ✅ Create video object WITHOUT saving to DB yet
                video = Video(
                    teacher=teacher,
                    title=request.POST.get("title"),
                    description=request.POST.get("description"),
                    language=request.POST.get("language"),
                    subject=request.POST.get("subject"),
                )

                # ✅ Assign ALL fields BEFORE first save
                if video_url:
                    video.video_link = video_url
                if video_file:
                    video.video_file = video_file
                if thumbnail_file:
                    video.thumbnail = thumbnail_file
                if notes_file:
                    video.notes = notes_file
                if quiz_file:
                    video.quiz = quiz_file
                
                # ✅ NOW save once with everything populated
                video.save()  # This will trigger duration fetch

                if quiz_file:
                    success, message = upload_quiz_file_in_database(video, quiz_file)
                    if not success:
                        messages.warning(request, f"Quiz upload issue: {message}")
                    else:
                        messages.success(request, message)

                followers = Follower.objects.filter(teacher=teacher).select_related("follower")

                notification_list = []

                for f in followers:
                    if f.follower.profile.role == "student":
                        notification_list.append(
                            Notification(
                                user=f.follower,
                                message=f"{teacher.user.username} uploaded a new video: {video.title}",
                                link=f"/watch/?v={video.video_id}"
                            )
                        )

                Notification.objects.bulk_create(notification_list)

                teacher.nov += 1
                teacher.save()

            messages.success(request, "Video uploaded successfully!")
            return redirect("index")

        except Exception as e:
            print("Video Upload Error:", e)
            messages.error(request, f"Video upload failed: {e}")
            return redirect("videoUpload")

    return render(request, "video_upload.html")

def upload_quiz_file_in_database(video, csv_file):
    try:
        csv_file.seek(0)
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        required_columns = {
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
        }

        if not required_columns.issubset(reader.fieldnames):
            missing = required_columns - set(reader.fieldnames)
            raise ValueError(f"Missing columns: {', '.join(missing)}")

        quiz_objects = []

        # Make sure quiz_id exists
        if not video.quiz_id:
            video.quiz_id = f"{video.video_id}-QUIZ"
            video.save(update_fields=["quiz_id"])

        with transaction.atomic():
            # Delete old quiz for this video
            Quiz.objects.filter(video=video).delete()

            for idx, row in enumerate(reader, start=1):
                correct_option = row.get("correct_option", "").strip().upper()
                if correct_option not in ["A", "B", "C", "D"]:
                    raise ValueError(f"Invalid correct_option at row {idx}")

                # Auto-generate question_id using quiz_id + question number
                question_number = str(idx).zfill(4)  # 0001, 0002, ...
                question_id = f"{video.quiz_id}-{question_number}"  # Changed to use quiz_id

                quiz_objects.append(
                    Quiz(
                        video=video,
                        question_id=question_id,
                        question_text=row.get("question_text", "").strip(),
                        option_a=row.get("option_a", "").strip(),
                        option_b=row.get("option_b", "").strip(),
                        option_c=row.get("option_c", "").strip(),
                        option_d=row.get("option_d", "").strip(),
                        correct_option=correct_option,
                    )
                )

            Quiz.objects.bulk_create(quiz_objects)

        return True, f"{len(quiz_objects)} questions uploaded successfully."

    except Exception as e:
        print("CSV Quiz Upload Error:", e)
        return False, str(e)

def submit_quiz(request, quiz_id):
    if request.method != "POST":
        return redirect("quiz", quiz_id=quiz_id)

    video = get_object_or_404(Video, quiz_id=quiz_id)
    student = get_object_or_404(Student, user=request.user)

    # Prevent multiple attempts early
    if QuizAttempt.objects.filter(student=student, quiz_id=quiz_id).exists():
        messages.error(request, "You have already attempted this quiz.")
        return redirect("watch_video") + f"?v={video.video_id}"

    # Quiz questions stored in session
    questions = request.session.get("quiz_questions", [])
    if not questions:
        messages.error(request, "No quiz questions found in session.")
        return redirect("quiz", quiz_id=quiz_id)

    total_questions = len(questions)
    correct_answers = 0

    # Calculate score
    for idx, q in enumerate(questions, start=1):
        selected_option = request.POST.get(f"q{idx}")
        correct_option = q.get("correct")

        if selected_option and correct_option and selected_option.upper() == correct_option.upper():
            correct_answers += 1

    if total_questions > 0:
        percentage = round((correct_answers / total_questions) * 100, 2)  # 2 digits after decimal
    else:
        percentage = 0.0

    # Total points earned
    total_points = correct_answers  # 1 point per correct answer
    accuracy = correct_answers / total_questions if total_questions else 0

    # Coins calculation
    base_coins = total_points * 2
    accuracy_bonus = round(base_coins * accuracy)
    total_coins = base_coins + accuracy_bonus
    # Save **single QuizAttempt**
    QuizAttempt.objects.create(
        student=student,
        quiz_id=quiz_id,
        score=total_points,
        total_questions=total_questions,
        percentage = percentage
    )

    # Update student stats
    student.no_of_quiz_given += 1
    student.no_of_points_earned += total_points
    student.coins += total_coins
    student.save()

    # Record coin transaction
    CoinTransaction.objects.create(
        student=student,
        amount=total_coins,
        transaction_type="credit",
        title=f"Coins earned from quiz '{video.title}'"
    )

    # Clear session to prevent resubmission
    if "quiz_questions" in request.session:
        del request.session["quiz_questions"]

    messages.success(
        request,
        f"Quiz submitted! You scored {total_points}/{total_questions} "
        f"and earned {total_coins} coins "
        f"(Base: {base_coins}, Accuracy Bonus: {accuracy_bonus})."
    )

    return redirect("index")

@login_required
def save_to_watch_later(request, video_id):
    """Save a video to watch later playlist"""
    video = get_object_or_404(Video, pk=video_id)
    
    # Save to watch later
    WatchLater.objects.get_or_create(
        user=request.user,
        video=video
    )
    
    messages.success(request, f"'{video.title}' saved to Watch Later!")
    
    # Redirect back to the page user came from
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def watch_later_playlist(request):
    """Display user's watch later playlist"""
    saved_videos = WatchLater.objects.filter(
        user=request.user
    ).select_related('video__teacher').order_by('-added_at')
    
    context = {
        'saved_videos': saved_videos,
        'total_videos': saved_videos.count()
    }
    return render(request, 'watch_later.html', context)

@login_required
def remove_from_watch_later(request, video_id):
    """Remove a video from watch later playlist"""
    if request.method == 'POST':
        video = get_object_or_404(Video, pk=video_id)
        WatchLater.objects.filter(
            user=request.user,
            video=video
        ).delete()
        messages.success(request, "Removed from Watch Later")
    
    return redirect('watch_later_playlist')

def watchVideo(request):
    video_id = request.GET.get('v')

    if not video_id:
        return redirect('index')

    video = get_object_or_404(Video, video_id=video_id)

    if request.user.is_authenticated:
        save_to_history("video", request.user, video_id)

        session_key = f'viewed_video_{video_id}'
        if not request.session.get(session_key):
            Video.objects.filter(pk=video.pk).update(
                views_count=F("views_count") + 1
            )
            request.session[session_key] = True

    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("comment")

        if content and request.user.profile.role in ["student", "tutor"]:
            Comment.objects.create(
                video=video,
                author=request.user,
                content=content
            )

            Video.objects.filter(pk=video.pk).update(
                comment_count=F("comment_count") + 1
            )

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
                video.save(update_fields=["description"])  # safe

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
    is_owner = request.user.is_authenticated and request.user == video.teacher.user

    comments = Comment.objects.filter(
        video=video,
        is_reply=False
    ).select_related('author').prefetch_related('replies').order_by('-created_at')

    return render(request, 'video_player.html', {
        'video': video,
        'comments': comments,
        'is_owner': is_owner
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
        save_to_history("search", request.user, query)
        
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



def quiz(request, quiz_id):
    video = get_object_or_404(Video, quiz_id=quiz_id)

    # Fetch all quiz questions from the DB for this video
    db_questions = Quiz.objects.filter(video=video)

    if not db_questions.exists():
        return render(request, "quiz.html", {
            "video": video,
            "questions": [],
            "error": "No quiz available for this video."
        })

    questions = []

    for q in db_questions:
        options = [
            ("A", q.option_a),
            ("B", q.option_b),
            ("C", q.option_c),
            ("D", q.option_d),
        ]

        random.shuffle(options)  # Shuffle options per question

        questions.append({
            "question": q.question_text,
            "options": options,
            "correct": q.correct_option
        })

    random.shuffle(questions)  # Shuffle question order

    # Store in session for user's attempt tracking
    request.session["quiz_questions"] = questions

    return render(request, "quiz.html", {
        "video": video,
        "questions": questions
    })


def edit_video(request, video_id):
    """
    Edit video details including title, description, subject, language,
    thumbnail, and video file replacement/trimming.
    """
    video = get_object_or_404(Video, video_id=video_id)
    
    # Check if user is owner
    if request.user != video.teacher.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        return redirect('profile')
    
    if request.method == 'POST':
        try:
            # Handle different actions
            action = request.POST.get('action', 'update')
            
            if action == 'trim':
                return handle_video_trim(request, video)
            elif action == 'update':
                return handle_video_update(request, video)  # This will now work
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
            return render(request, 'edit_video.html', {
                'video': video,
                'error': str(e)
            })
    
    # GET request - show edit form
    return render(request, 'edit_video.html', {'video': video})

def handle_video_update(request, video):
    """Handle video metadata update"""
    try:
        print("=" * 60)
        print("HANDLE VIDEO UPDATE CALLED")
        print("=" * 60)
        
        # Print ALL POST data
        print("POST data keys:", list(request.POST.keys()))
        for key, value in request.POST.items():
            print(f"POST[{key}] = '{value}'")
        
        # Print ALL FILES data
        print("FILES data keys:", list(request.FILES.keys()))
        for key, file in request.FILES.items():
            print(f"FILES[{key}] = {file.name} ({file.size} bytes)")
        
        # Before update - print current values
        print(f"BEFORE UPDATE - Title: '{video.title}'")
        print(f"BEFORE UPDATE - Description: '{video.description[:50]}...'")
        print(f"BEFORE UPDATE - Subject: '{video.subject}'")
        print(f"BEFORE UPDATE - Language: '{video.language}'")
        
        # Update basic fields - with fallbacks
        new_title = request.POST.get('title')
        if new_title:
            print(f"Updating title from '{video.title}' to '{new_title}'")
            video.title = new_title
        else:
            print("No title in POST data")
        
        new_description = request.POST.get('description')
        if new_description is not None:
            print(f"Updating description from '{video.description[:50]}...' to '{new_description[:50]}...'")
            video.description = new_description
        else:
            print("No description in POST data")
        
        new_subject = request.POST.get('subject')
        if new_subject:
            print(f"Updating subject from '{video.subject}' to '{new_subject}'")
            video.subject = new_subject
        else:
            print("No subject in POST data")
        
        new_language = request.POST.get('language')
        if new_language:
            print(f"Updating language from '{video.language}' to '{new_language}'")
            video.language = new_language
        else:
            print("No language in POST data")
        
        # Handle thumbnail upload
        if request.FILES.get('thumbnail'):
            print(f"Updating thumbnail with: {request.FILES['thumbnail'].name}")
            if video.thumbnail:
                video.thumbnail.delete(save=False)
            video.thumbnail = request.FILES.get('thumbnail')
        else:
            print("No thumbnail file in request")
        
        # Handle video file replacement
        if request.FILES.get('video_file'):
            print(f"Updating video file with: {request.FILES['video_file'].name}")
            if video.video_file:
                video.video_file.delete(save=False)
            video.video_file = request.FILES.get('video_file')
        else:
            print("No video file in request")
        
        print("Saving video...")
        video.save()
        print("Video saved successfully!")
        
        # After update - verify changes
        video.refresh_from_db()
        print(f"AFTER UPDATE - Title: '{video.title}'")
        print(f"AFTER UPDATE - Description: '{video.description[:50]}...'")
        print(f"AFTER UPDATE - Subject: '{video.subject}'")
        print(f"AFTER UPDATE - Language: '{video.language}'")
        
        # Check if AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Video updated successfully',
                'redirect_url': reverse('user_profile', args=[request.user.username])
            })
        
        messages.success(request, 'Video updated successfully!')
        return redirect('user_profile', username=request.user.username)
        
    except Exception as e:
        print(f"ERROR in handle_video_update: {e}")
        import traceback
        traceback.print_exc()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        
        messages.error(request, f'Error updating video: {str(e)}')
        return render(request, 'edit_video.html', {
            'video': video,
            'error': str(e)
        })

def handle_video_trim(request, video):
    """Handle video trimming operation"""
    
    if not video.video_file:
        return JsonResponse({
            'status': 'error',
            'message': 'No video file to trim'
        }, status=400)
    
    try:
        start_time = float(request.POST.get('start_time', 0))
        end_time = float(request.POST.get('end_time', 0))
        video_id = request.POST.get('video_id')
        
        if end_time <= start_time:
            return JsonResponse({
                'status': 'error',
                'message': 'End time must be greater than start time'
            }, status=400)
        
        if start_time < 0 or end_time > video.duration:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid time range'
            }, status=400)
        
        # Get video file path
        video_path = video.video_file.path
        
        # Create temp directory for trimmed video
        temp_dir = Path(settings.MEDIA_ROOT) / 'temp'
        temp_dir.mkdir(exist_ok=True)
        
        # Generate output filename
        output_filename = f"trimmed_{video.video_id}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = temp_dir / output_filename
        
        # Trim video using ffmpeg
        success, message = trim_video_ffmpeg(
            video_path, 
            str(output_path), 
            start_time, 
            end_time - start_time
        )
        
        if not success:
            return JsonResponse({
                'status': 'error',
                'message': message
            }, status=500)
        
        # Read the trimmed file and save to Video model
        with open(output_path, 'rb') as f:
            # Delete old video file
            if video.video_file:
                video.video_file.delete(save=False)
            
            # Save new trimmed video
            video.video_file.save(
                f"trimmed_{video.video_id}.mp4",
                ContentFile(f.read()),
                save=False
            )
        
        # Update duration
        video.duration = end_time - start_time
        video.save()
        
        # Clean up temp file
        os.remove(output_path)
        
        # Get the URL of the new video
        new_url = video.video_file.url
        
        return JsonResponse({
            'status': 'success',
            'message': 'Video trimmed successfully',
            'new_url': new_url,
            'new_duration': video.duration
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def get_video_duration(video_path):
    """Get video duration using ffprobe"""
    try:
        if not video_path or not os.path.exists(video_path):
            return 0
            
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            return float(result.stdout.strip())
        return 0
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return 0

def trim_video_ffmpeg(input_path, output_path, start_time, duration):
    """Trim video using ffmpeg"""
    try:
        # Using copy codec for fast trimming (may not be accurate with all keyframes)
        # For more accurate trimming, remove '-c copy' but it will be slower
        result = subprocess.run([
            'ffmpeg', '-i', input_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',  # Copy codec (fast)
            '-avoid_negative_ts', 'make_zero',
            output_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            # If copy fails, try with re-encoding
            result = subprocess.run([
                'ffmpeg', '-i', input_path,
                '-ss', str(start_time),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                output_path
            ], capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True, "Success"
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)

@login_required
def delete_video(request, video_id):
    """Delete video and associated files"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    video = get_object_or_404(Video, video_id=video_id)
    
    # Check if user is owner
    if request.user != video.teacher.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    teacher = video.teacher

    try:
        # Delete video file
        if video.video_file:
            video.video_file.delete(save=False)
        
        # Delete thumbnail
        if video.thumbnail:
            video.thumbnail.delete(save=False)
        
        # Delete from database
        video.delete()
        
        if teacher.nov > 0:
                teacher.nov -= 1
                teacher.save(update_fields=["nov"])
        return JsonResponse({
            'status': 'success',
            'message': 'Video deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_video_info(request, video_id):
    """Get video information for AJAX requests"""
    video = get_object_or_404(Video, video_id=video_id)
    
    if request.user != video.teacher.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'title': video.title,
        'description': video.description,
        'subject': video.subject,
        'language': video.language,
        'duration': video.duration,
        'thumbnail_url': video.thumbnail.url if video.thumbnail else None,
        'video_url': video.video_file.url if video.video_file else None,
        'youtube_id': video.youtube_id
    })