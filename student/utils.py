from .models import Student
from datetime import date, timedelta
from django.db.models import Count

def generate_student_id(fullname):
    parts = fullname.strip().split()
    initials = "".join([p[0].upper() for p in parts[:2]])


    last_student = Student.objects.order_by("-created_at").first()

    if last_student:
        last_number = int(last_student.student_id.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"STU-{initials}-{new_number:04d}"

def get_quiz_heatmap(student):

    today = date.today()
    start = today - timedelta(days=364)

    attempts = (
        student.quiz_attempts
        .filter(created_at__date__gte=start)
        .values("created_at__date")
        .annotate(count=Count("id"))
    )

    attempt_dict = {
        a["created_at__date"]: a["count"]
        for a in attempts
    }

    heatmap = []

    for i in range(365):
        d = start + timedelta(days=i)
        count = attempt_dict.get(d, 0)

        if count == 0:
            level = 0
        elif count == 1:
            level = 1
        elif count <= 3:
            level = 2
        elif count <= 5:
            level = 3
        else:
            level = 4

        heatmap.append({
            "date": d,
            "count": count,
            "level": level
        })

    return heatmap

