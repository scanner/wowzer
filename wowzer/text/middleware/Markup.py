"""
'helper' middleware.. auto-convert any 'description' with special markup code
to real html
"""
from django.utils.html import strip_tags
#from zilbo.common.prefs.utils import get_user_prefs, get_default_prefs

class Markup:
    def process_request(self, request ):
        if request.POST:
            newpost=request.POST.copy()
            if newpost.has_key('content'):
                markup = 'text.bbcode'
                newpost['markup'] = markup
                func, ignore = getattr(__import__("wowzer."+markup,
                                                  '', '', ['']), 
                                       "to_html"), {}
                newpost['content_html'] = func(  newpost['description'] )
            if newpost.has_key('name'):
                newpost['name'] = strip_tags(newpost['name'])
            request._post = newpost
        return None
