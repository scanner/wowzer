#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for browsing and inspecting auctions by various means.

We offer a list of auctions by item, by user, or by specific auction key.
"""

# System imports
#
from datetime import datetime, timedelta

# Django imports
#
from django import forms
from django.shortcuts import get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

# The data models from our apps:
#
from wowzer.toons.models import *
from wowzer.items.models import *

#############################################################################
#
def index(request):
    t = get_template('toons/index.html')
    c = Context(request, {})
    return HttpResponse(t.render(c))

############################################################################
#
def client_list(request):
    """A generic view to browse objects on a specific engine instance.
    """
    page_number = int(request.GET.get('page', 0))
    
    # Right now we build a query set of all the objects of this class. Later
    # on this is where a submitted form of values is used to determine the
    # query set for browsing.
    #
    query_set = Toon.objects.all()

    # XXX the value '30' is how many object to page by. This should be settable
    # XXX in a user's profile with some either 'system' or 'skin' default.
    #
    paginator = ObjectPaginator(query_set, 30)

    try:
        object_list = paginator.get_page(page_number)
    except InvalidPage:
        if page_number == 0:
            object_list = []
        else:
            raise Http404
    
    t = get_template('toons/toon_list.html')
    c = Context(request, {
        'order_by'    : order_by,
        'engine'      : engine,
        'page_number' : page_number,
        'pages'       : paginator.pages-1,
        'hits'        : paginator.hits,
        'has_next'    : paginator.has_next_page(page_number),
        'has_previous': paginator.has_previous_page(page_number),
        'next'        : page_number + 1,
        'previous'    : page_number - 1,
        'objects'     : object_list,
        })
    return HttpResponse(t.render(c))

#############################################################################
#
def detail(request, toon_id):
    """Displays the details of a single toon."""

    toon = get_object_or_404(Toon, pk = toon_id)

    # Pull out the number of raids above certain sizes that they have been in
    #
    # we go for: 1-15, 15-25, 25-30, 30->
    #
    attended = []
    sizes = ((1,15),(16-25),(26-30),(31-100))
    for bot, top in sizes:
        size = toon.raids_attended.filter(maximal_size__lte = top,
                                          maximal_size__gte = bot).count()
        attended.append({'size' : top, 'num_attended' : size })

    # and now find out how long they have been raiding with raids submitted by
    # tamrielo
    #
    first_raid = toon.raids_attended.order_by('start_time')[0]
    last_raid = toon.raids_attended.order_by('-start_time')[0]
    time_delta = last_raid.start_time - first_raid.start_time
    
##     aucts = toon.get_madhouse_auction_list(order_by = ('-last_seen',),
##                                            limit = 50)

    t = get_template('toons/toon_detail.html')
    c = Context(request, {
        'object'        : toon,
        'attended'      : attended,
        'first_raid'    : first_raid,
        'last_raid'     : last_raid,
        'raiding_duration' : time_delta,
    })
    return HttpResponse(t.render(c))
    
