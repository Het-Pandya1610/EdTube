import re
from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse


register = template.Library()

@register.filter(name='hashtag_links')
def hashtag_links(value):
    if not value:
        return ''
    
    text = str(value)
    
    try:
        search_url = reverse('search')
    except:
        search_url = '/search-results/'
    
    # URL encode the hashtag query
    result = re.sub(
        r'#(\w+)', 
        lambda match: f'<a href="{search_url}?q=%23{match.group(1)}" class="hashtag-link">#{match.group(1)}</a>', 
        text
    )
    
    return mark_safe(result)