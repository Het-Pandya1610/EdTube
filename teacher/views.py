from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Teacher, Follower

@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
 
    teacher_profile = target_user.teacher

    follow_record, created = Follower.objects.get_or_create(
        teacher=teacher_profile,
        follower=request.user
    )

    if created:
        teacher_profile.nos += 1
        action = "followed"
    else:
        follow_record.delete()
        teacher_profile.nos -= 1
        action = "unfollowed"
    
    teacher_profile.save()
    
    return JsonResponse({
        'status': 'success',
        'action': action,
        'new_count': teacher_profile.nos
    })