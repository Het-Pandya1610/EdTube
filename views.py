# from django.http import HttpResponse

from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login

def index(request):
    return render(request, "EduNex.html")

def reg(request):
    if request.method == "POST":
        username = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        confirmed_pass = request.POST['confirm_password']

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {"error": "email already exists"})
        elif confirmed_pass != password:
            return render(request, "register.html", {"error": "Confirmed password didn't matched with entered password"})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect("login")

    return render(request, "register.html")

def faqs(request):
    return render(request, "faqs.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Email not found"})

        user = authenticate(
            request,
            username=user_obj.username,
            password=password
        )

        if user is not None:
            auth_login(request, user)   # ✅ CORRECT
            return redirect("index")

        return render(request, "login.html", {"error": "Invalid password"})

    return render(request, "login.html")

def terms(request):
    return render(request, "terms.html")

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

def courses(request):
    return render(request, "courses.html")

def blog(request):
    return render(request, "blog.html")

def blog1(request):
    return render(request, "blog-details.html")

def blog2(request):
    return render(request, "blog2-details.html")

def blog3(request):
    return render(request, "blog3-details.html")

def blog4(request):
    return render(request, "blog4-details.html")

def aboutUs(request):
    return render(request, "about-us.html")