from django.conf import settings 
from django.utils.html import strip_tags, escape, linebreaks
from django.http import HttpResponse, Http404
from zilbo.common.prefs.utils import get_user_prefs
from zilbo.common.utils.misc import get_object
from django.utils import simplejson

#import simplejson
import sha

def preview( request ):
    """
    Generate the markup
    """
    if not request.POST:
        raise Http404, "Only POSTs are allowed"

    # note.. the middleware does the magic for us
    if request.POST.has_key("description_html"):
        description_html = request.POST["description_html"]
    else:
        description_html ='type something'
    
    return HttpResponse(simplejson.dumps(description_html), 'text/javascript')

def quote( request, content_type_id, object_id, hash ):
    """
    Generate the markup for a 'quote' of a comment
    """
    if not hash == sha.new("%s/%s" % (content_type_id, object_id) + settings.SECRET_KEY).hexdigest():
        return HttpResponse(simplejson.dumps(""), 'text/javascript')

    prefs = get_user_prefs(request)
    callback = prefs['editing_markup']

    obj = get_object(content_type_id, object_id )
    func, ignore = getattr(__import__("zilbo.common."+callback, '', '', ['']), "quote"), {}

    if obj.markup == callback:
        desc = func( obj.description, obj.get_absolute_url() )
    else:
        desc = func( linebreaks(escape(strip_tags(obj.description_html ))), obj.get_absolute_url() )

    return HttpResponse(simplejson.dumps(desc), 'text/javascript')

def get( request, content_type_id, object_id, hash ):
    """
    Generate the markup for a 'quote' of a comment
    """
    if not hash == sha.new("%s/%s" % (content_type_id, object_id) + settings.SECRET_KEY).hexdigest():
        return HttpResponse(simplejson.dumps(""), 'text/javascript')

    prefs = get_user_prefs(request)
    callback = prefs['editing_markup']

    obj = get_object(content_type_id, object_id )
    if obj.markup == callback:
        desc = obj.description
    else:
        desc = linebreaks(escape(strip_tags(obj.description_html )))

    return HttpResponse(simplejson.dumps(desc), 'text/javascript')

