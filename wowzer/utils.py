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

