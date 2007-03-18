"""
'helper' middleware.. auto-convert any 'description' with special markup code to real html
"""
from django.utils.html import strip_tags
from zilbo.common.prefs.utils import get_user_prefs, get_default_prefs

class Markup:
    def process_request(self, request ):
        if request.POST:
            newpost=request.POST.copy()
            if newpost.has_key('description'):
                prefs={}
                try:
                    prefs = request.session['PREFS']
                except KeyError:
                    if request.user.is_anonymous():
                        prefs = get_default_prefs(request) 
                    else:
                        prefs = get_user_prefs(request)
                        if not prefs:
                            prefs = get_default_prefs(request)
                    request.session['PREFS'] = prefs
                try:
                    callback = prefs['editing_markup']
                except KeyError:
                    # this happens while we are setting up the editing_markup option itself
                    callback = 'text.bbcode'

                newpost['markup'] = callback
                func, ignore = getattr(__import__("zilbo.common."+callback, '', '', ['']), 
                                                   "to_html"), {}
                newpost['description_html'] = func(  newpost['description'] )
            if newpost.has_key('name'):
                newpost['name'] = strip_tags(newpost['name'])
            request._post = newpost

        return None
