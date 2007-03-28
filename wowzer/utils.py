#
# File: $Id$
#
"""some top level utilities used by wowzer. Like, sticking the media url
variable in to the template context so that we can have our templates not hard
# code their references to where the media is and instead use the value set in
# the settings.py file.
"""

from django.conf import settings

#############################################################################
#
def media_context(request):
    """Insert in to the template context the values of settings.media_url
    """
    return { 'MEDIA_URL' : settings.MEDIA_URL }

#############################################################################
#
def msg_user(user, message):
    """A helper function to send a 'message' to a user (using the message
    object framework for users from the django.contrib.auth
    module. This is NOT email. This is for basic messages like "you
    have successfully posted your message" etc.
    """
    if user.is_authenticated():
        user.message_set.create(message = message)
    return
