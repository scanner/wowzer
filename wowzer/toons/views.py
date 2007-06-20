#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for browsing and inspecting auctions by various means.

We offer a list of auctions by item, by user, or by specific auction key.
"""

# System imports
#
import sys
from datetime import datetime, timedelta

# Django imports
#
from django import newforms as forms
from django.newforms import widgets
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

# Wowzer utility functions
#
from wowzer.utils import msg_user
from wowzer.decorators import logged_in_or_basicauth
from wowzer.main.views import rlp_edit
from wowzer.main.decorators import breadcrumb

# 3rd party models & utils
#
from tagging.models import TaggedItem
from tagging.utils import get_tag

# The data models from our apps:
#
from wowzer.toons.models import Toon
from wowzer.main.models import Breadcrumb

paginate_by = 20

############################################################################
#
@login_required
def index(request):
    """
    For now the index just redirects to the toons index.
    """
    return HttpResponseRedirect("toons/")

############################################################################
#
@login_required
@breadcrumb(name="Character List")
def toon_list(request):
    if 'order_by' in request.GET and \
       request.GET['order_by'] in Toon.valid_order_by:
        order_by = request.GET['order_by']
    else:
        query_set = Toon.objects.extra(tables = ['toons_realm']).order_by('toons_realm.name', 'name')
    return object_list(request, query_set, paginate_by = paginate_by,
                       template_name = "toons/toon_list.html")
    
#############################################################################
#
@login_required
@breadcrumb
def toon_detail(request, toon_id):
    """Displays the details of a single toon."""

    toon = get_object_or_404(Toon, pk = toon_id)

    Breadcrumb.rename_last(request, name = str(toon))

    # Pull out the number of raids above certain sizes that they have been in
    #
    # we go for: 1-15, 15-25, 25-30, 30->
    #
    attended = []
    sizes = ((1,15),(16,25),(26,30),(31,100))
    for bot, top in sizes:
        size = toon.raids_attended.filter(maximal_size__lte = top,
                                          maximal_size__gte = bot).count()
        attended.append({'size': "%d-%d" % (bot, top), 'num_attended' : size })

    # and now find out how long they have been raiding with raids submitted by
    # tamrielo
    #
    if toon.raids_attended.count() != 0:
        first_raid = toon.raids_attended.order_by('start_time')[0]
        last_raid = toon.raids_attended.order_by('-start_time')[0]
        time_delta = last_raid.start_time - first_raid.start_time
    else:
        first_raid = None
        last_raid = None
        time_delta = None
    
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
    
