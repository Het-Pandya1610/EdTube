from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Sum
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
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
import imghdr
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from accounts.models import SearchHistory
from PIL import Image
from student.models import DailyQuizCoinsRedemption, CoinTransaction, QuizAttempt
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


def coinsInventory(request):
    student = request.user.student
    
    # Calculate total coins balance
    credits = CoinTransaction.objects.filter(
        student=student, 
        transaction_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    debits = CoinTransaction.objects.filter(
        student=student, 
        transaction_type='debit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    coins_balance = credits - debits
    
    # Get recent transactions (last 5-10)
    recent_transactions = CoinTransaction.objects.filter(
        student=student
    ).order_by('-created_at')[:10]
    
    # Calculate progress to next reward
    next_reward_threshold = 100
    coins_to_next_reward = next_reward_threshold - (coins_balance % next_reward_threshold)
    progress_percentage = (coins_balance % next_reward_threshold) / next_reward_threshold * 100
    
    # Determine next reward title
    if coins_balance < 100:
        next_reward_title = "Basic Quiz Pack"
    elif coins_balance < 250:
        next_reward_title = "Premium Quiz"
    elif coins_balance < 500:
        next_reward_title = "Video Lesson"
    else:
        next_reward_title = "Certificate"
    
    # Check daily quiz coins redemption status
    today = timezone.now().date()
    last_24h = timezone.now() - timedelta(hours=24)
    
    # Check if user has taken a quiz today
    has_quiz_today = QuizAttempt.objects.filter(
        student=student,
        created_at__date=today
    ).exists()
    
    # Check last redemption
    last_redeem = DailyQuizCoinsRedemption.objects.filter(
        student=student,
        redeemed_at__gte=last_24h
    ).first()
    
    can_redeem = has_quiz_today and not last_redeem
    
    # Calculate timer if redemption exists
    timer_display = "24h"
    if last_redeem:
        time_left = last_redeem.redeemed_at + timedelta(hours=24) - timezone.now()
        if time_left.total_seconds() > 0:
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            timer_display = f"{hours}h {minutes}m"
    
    context = {
        'coins_balance': coins_balance,
        'recent_transactions': recent_transactions,
        'progress_percentage': round(progress_percentage),
        'coins_to_next_reward': coins_to_next_reward,
        'next_reward_title': next_reward_title,
        'can_redeem': can_redeem,
        'has_quiz_today': has_quiz_today,
        'timer_display': timer_display,
        'last_redeem': last_redeem,
    }
    
    return render(request, 'coins.html', context)


def daily_quiz_coins_redeem(request):
    if request.method == 'POST':
        student = request.user.student
        today = timezone.now().date()
        
        # Check if user has taken at least one quiz today
        quiz_today = QuizAttempt.objects.filter(
            student=student,
            created_at__date=today
        ).count()
        
        if quiz_today == 0:
            messages.error(request, "You need to complete at least one quiz today first!")
            return redirect('coins')
        
        # Check if already redeemed in last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        recent_redeem = DailyQuizCoinsRedemption.objects.filter(
            student=student,
            redeemed_at__gte=last_24h
        ).exists()
        
        if recent_redeem:
            # Get the last redemption to calculate remaining time
            last_redeem = DailyQuizCoinsRedemption.objects.filter(
                student=student
            ).latest('redeemed_at')
            
            time_left = last_redeem.redeemed_at + timedelta(hours=24) - timezone.now()
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            
            messages.error(
                request, 
                f"Already claimed! Try again in {hours}h {minutes}m"
            )
            return redirect('coins')
        
        # Give coins
        CoinTransaction.objects.create(
            student=student,
            amount=10,
            transaction_type='credit',
            title='Daily Quiz Coins Reward'
        )
        
        student.coins += 10
        student.save()


        # Record redemption
        DailyQuizCoinsRedemption.objects.create(student=student)
        
        messages.success(request, "10 coins added to your balance!")
        return redirect('coins')
    
    return redirect('coins')

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
        # ===== UPDATED: Save search to DATABASE instead of JSON =====
        if request.user.is_authenticated:
            # Save to database
            SearchHistory.objects.create(
                user=request.user,
                query=raw_query[:255]  # Limit length
            )
            
            # Optional: Clean up old searches (keep last 100)
            # This prevents the table from growing indefinitely
            from django.db.models import Count
            search_count = SearchHistory.objects.filter(user=request.user).count()
            if search_count > 100:
                # Keep only the 100 most recent
                oldest_to_keep = SearchHistory.objects.filter(
                    user=request.user
                ).order_by('-searched_at')[100:].values_list('id', flat=True)
                SearchHistory.objects.filter(
                    user=request.user,
                    id__in=oldest_to_keep
                ).delete()
        
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

            # ===== UPDATED: Better hashtag search =====
            videos = Video.objects.filter(
                Q(description__icontains=f"#{tag_query}") |
                Q(description__icontains=f"#{tag_query} ") |
                Q(description__icontains=f"#{tag_query},") |
                Q(description__icontains=f"#{tag_query}.") |
                Q(title__icontains=tag_query) |
                Q(subject__icontains=tag_query)
            ).select_related("teacher")
            
            teachers = Teacher.objects.filter(
                Q(name__icontains=tag_query) |
                Q(username__icontains=tag_query)
            )
        else:
            # Normal search
            videos = Video.objects.filter(
                Q(title__icontains=raw_query) |
                Q(subject__icontains=raw_query) |
                Q(description__icontains=raw_query)
            ).select_related("teacher")

            teachers = Teacher.objects.filter(
                Q(name__icontains=raw_query) |
                Q(username__icontains=raw_query)
            )
    
    # ===== NEW: Get popular searches for the template =====
    popular_searches = []
    if request.user.is_authenticated:
        from django.db.models import Count
        popular_searches = SearchHistory.objects.filter(
            user=request.user
        ).values('query').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
    
    return render(request, "search_results.html", {
        "query": query,
        "videos": videos,
        "teachers": teachers,
        "popular_searches": popular_searches,
        "result_count": len(videos) + len(teachers)
    })
    
@login_required
def search_suggestions(request):
    """API endpoint for search suggestions"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # 1. Get user's search history that matches
    history_suggestions = SearchHistory.objects.filter(
        user=request.user,
        query__icontains=query
    ).values_list('query', flat=True).order_by('-searched_at')[:3]
    
    # 2. Get video title suggestions
    video_suggestions = Video.objects.filter(
        Q(title__icontains=query) |
        Q(subject__icontains=query)
    ).values_list('title', flat=True).distinct()[:5]
    
    # 3. Get teacher name suggestions
    teacher_suggestions = Teacher.objects.filter(
        Q(name__icontains=query) |
        Q(username__icontains=query)
    ).values_list('name', flat=True)[:3]
    
    # Combine and remove duplicates
    suggestions = []
    suggestions.extend(list(history_suggestions))
    suggestions.extend(list(video_suggestions))
    suggestions.extend(list(teacher_suggestions))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen and s.lower() != query.lower():
            seen.add(s)
            unique_suggestions.append(s)
            if len(unique_suggestions) >= 8:
                break
    
    return JsonResponse(unique_suggestions, safe=False)

@login_required
def popular_searches_api(request):
    """Get user's most frequent searches"""
    from django.db.models import Count
    
    popular = SearchHistory.objects.filter(
        user=request.user
    ).values('query').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return JsonResponse(list(popular), safe=False)
       
@login_required
def get_search_suggestions(request):
    """Get user's search history from DATABASE for suggestions"""
    try:
        # Get last 20 searches from database
        searches = SearchHistory.objects.filter(
            user=request.user
        ).order_by('-searched_at').values_list('query', flat=True)[:20]
        
        # Remove duplicates while preserving order
        unique_searches = []
        seen = set()
        for query in searches:
            if query not in seen:
                seen.add(query)
                unique_searches.append(query)
                if len(unique_searches) >= 8:
                    break
        
        return JsonResponse(unique_searches, safe=False)
        
    except Exception as e:
        return JsonResponse([], safe=False)

@login_required
def delete_search_suggestion(request):
    """Delete a specific search query from DATABASE"""
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query_to_delete = data.get("query")
            
            # Delete from database
            deleted = SearchHistory.objects.filter(
                user=request.user,
                query=query_to_delete
            ).delete()
            
            return JsonResponse({"status": "success", "deleted": deleted[0]})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "unauthorized"}, status=401)
    
@login_required
def clear_search_history(request):
    """Clear all search history from DATABASE"""
    
    if request.method == "POST":
        try:
            deleted = SearchHistory.objects.filter(
                user=request.user
            ).delete()
            
            
            return JsonResponse({"status": "success", "deleted": deleted[0]})
            
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