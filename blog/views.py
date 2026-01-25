from django.shortcuts import render

# Create your views here.
def blog(request):
    return render(request, "blog.html")


def blog1(request):
    return render(request, "blog1-details.html")


def blog2(request):
    return render(request, "blog2-details.html")


def blog3(request):
    return render(request, "blog3-details.html")


def blog4(request):
    return render(request, "blog4-details.html")