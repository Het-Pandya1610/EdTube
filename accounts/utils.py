import random
import re
from django.contrib.auth.models import User

def generate_suggestions_by_name(full_name):
    base = re.sub(r'\s+', '', full_name).lower()
    if not base:
        base = "user"
        
    suggestions = set()
    suffixes = ['Edu', 'Pro', 'Tutor', 'Academy', 'Class', 'Hub', 'Official']
    
    while len(suggestions) < 4:
        style_a = f"{base}{random.randint(10, 99)}"
        style_b = f"{base}_{random.choice(suffixes)}"
        name_parts = full_name.lower().split()
        if len(name_parts) > 1:
            style_c = f"{name_parts[0][0]}{name_parts[-1]}{random.randint(1, 9)}"
            if not User.objects.filter(username=style_c).exists():
                suggestions.add(style_c)
        for cand in [style_a, style_b]:
            if not User.objects.filter(username=cand).exists():
                suggestions.add(cand)
                    
    return list(suggestions)[:4]