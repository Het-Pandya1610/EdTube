
import calendar
from .models import Student
from datetime import timedelta
from django.db.models import Count
import math
from datetime import timedelta
from django.utils import timezone
from datetime import date
from .models import QuizAttempt

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
    start_date = date(2026, 2, 1)
    end_date = date.today()

    attempts = (
        QuizAttempt.objects
        .filter(student=student, created_at__date__range=[start_date, end_date])
        .values("created_at__date")
        .annotate(count=Count("id"))
    )

    attempt_dict = {
        a["created_at__date"]: a["count"]
        for a in attempts
    }

    heatmap = []
    months = []
    last_month = None

    for i in range(365):
        d = start_date + timedelta(days=i)
        count = attempt_dict.get(d, 0)

        # activity level
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

        # month tracking
        if d.month != last_month:
            months.append(calendar.month_abbr[d.month])
            last_month = d.month
        else:
            months.append("")

    weekdays = ["Sun", "", "Tue", "", "Thu", "", "Sat"]

    return {
        "days": heatmap,
        "months": months,
        "weekdays": weekdays,
    }


def calculate_coins(score, total_questions):
    if total_questions == 0:
        return 0

    accuracy = score / total_questions
    base = score * 2

    bonus = math.exp(accuracy * 2)

    return int(base * bonus) 