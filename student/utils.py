from .models import Student

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
