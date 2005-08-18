#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for browsing and inspecting auctions by various means.

We offer a list of auctions by item, by user, or by specific auction key.
"""

# django specific imports
#
from django.core import template_loader
from django.core.extensions import DjangoContext as Context
from django.utils.httpwrappers import HttpResponse
from django.core.exceptions import Http404

# The data models from our apps:
#
from django.models.madhouse import *
from django.models.items import *
from django.models.toons import *

#############################################################################
#
def index(request):
    return HttpResponse("Hello, world. You're at the toons index.")


#############################################################################
#
def detail(request, toon_id):
    """Displays the details of a single toon."""

    try:
        toon = toons.get_object(pk = toon_id)
    except toons.ToonDoesNotExist:
        raise Http404

    aucts = auctions.get_list(owner_id__exact = toon_id,
                              order_by = ('-last_seen',),
                              limit = 20)

    t = template_loader.get_template('toons/detail')
    c = Context(request, {
        'toon'    : toon,
        'aucts'   : aucts,
    })
    return HttpResponse(t.render(c))
    
