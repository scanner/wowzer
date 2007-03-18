from django.contrib.auth.models import User
def obfuscate_email( text ):
    return "email@example.com"

def get_member_link( text ):
    try:
        user = User.objects.get( username = text )
        return "<a title='Information about user %s' href='%s'>%s</a>" % (user.username, user.get_absolute_url(), user.username )
    except User.DoesNotExist:
        return text
