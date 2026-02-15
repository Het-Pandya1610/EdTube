import random
from django.contrib.auth.models import User 

def generate_suggestions_by_name(full_name):
    """Generate username suggestions from full name"""
    suggestions = []
    
    # Clean the name
    name = full_name.lower().strip()
    name = ''.join(c for c in name if c.isalnum() or c.isspace())
    parts = name.split()
    
    if not parts:
        return suggestions
    
    # Basic combinations
    first_name = parts[0]
    last_name = parts[-1] if len(parts) > 1 else ""
    
    # 1. firstname
    suggestions.append(first_name[:15])
    
    # 2. firstname.lastname
    if last_name:
        suggestions.append(f"{first_name}.{last_name}"[:20])
    
    # 3. firstinitial_lastname
    if last_name:
        suggestions.append(f"{first_name[0]}_{last_name}"[:20])
    
    # 4. firstnamelastname
    if last_name:
        suggestions.append(f"{first_name}{last_name}"[:20])
    
    # 5. firstname_lastname
    if last_name:
        suggestions.append(f"{first_name}_{last_name}"[:20])
    
    # Add numbers to make unique
    base_suggestions = suggestions.copy()
    for i in range(1, 4):
        for base in base_suggestions[:3]:
            numbered = f"{base}{random.randint(1, 999)}"
            if len(numbered) <= 30:
                suggestions.append(numbered)
            numbered = f"{base}_{random.randint(1, 99)}"
            if len(numbered) <= 30:
                suggestions.append(numbered)
    
    # Remove duplicates
    suggestions = list(dict.fromkeys(suggestions))
    suggestions = [s[:30] for s in suggestions]
    
    return suggestions

def generate_suggestions_by_username(username):
    """Generate username suggestions from current username"""
    suggestions = []
    
    # Remove numbers at the end
    import re
    base = re.sub(r'\d+$', '', username)
    
    suggestions.append(base)
    
    if '_' in base:
        parts = base.split('_')
        if len(parts) > 1:
            suggestions.append(''.join(parts))
            suggestions.append('.'.join(parts))
    elif '.' in base:
        parts = base.split('.')
        if len(parts) > 1:
            suggestions.append(''.join(parts))
            suggestions.append('_'.join(parts))
    
    # Add random numbers
    for i in range(1, 4):
        suggestions.append(f"{base}{random.randint(1, 999)}")
        suggestions.append(f"{base}_{random.randint(1, 99)}")
    
    # Remove duplicates
    suggestions = list(dict.fromkeys(suggestions))
    suggestions = [s[:30] for s in suggestions]
    
    return suggestions