from .models import Teacher

def generate_teacher_id(fullname):
    parts = fullname.strip().split()
    initials = "".join([p[0].upper() for p in parts[:2]])


    last_teacher = Teacher.objects.order_by("-created_at").first()

    if last_teacher:
        last_number = int(last_teacher.teacher_id.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"TCH-{initials}-{new_number:04d}"
