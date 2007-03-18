from django.utils.html import strip_tags,escape, linebreaks
def to_html(text):
    return linebreaks(escape(strip_tags(text)))

def name():
    return "plain"

def quote(text,url):
    return text
