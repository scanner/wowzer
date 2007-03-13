#
# File: $Id$
#
"""AS forums views. Viewing, editing, creating forums, discussions, posts, etc.
"""

# System imports
#
import sys
from datetime import datetime, timedelta

from django import forms
from django.shortcuts import get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

# The data models from our apps:
#
from wowzer.asforums.models import *

results_per_page = 20

############################################################################
#
def index(request):
    """Simplistic top level index. Shows all forum collections and their
    forums
    """
    query_set = Forum.objects.all().order_by('collection','created_at')
    ec = {}
    
    return object_list(request, query_set,
                       template_name = 'asforums/index.html',
                       extra_context = ec)

############################################################################
#
def forum_list(request):
    """A view that shows the forums that a person can see."""

    order_by = request.GET.get('order_by', 'created_at')
    if order_by not in ('name', 'slug', 'creator', 'created_at',
                        'last_post_at'):
        order_by = 'created_at'

    query_set = Forum.objects.all().order_by(order_by)
    ec = { 'order_by' : order_by }

    return object_list(request, query_set,
                       template_name = 'asforums/forum_list.html',
                       extra_context = ec)

############################################################################
#
def forum_detail(request, forum_id):
    """A forum detail shows just the forum and its details. Not much here.
    but this is the view that lets people update/delete their forums.
    """
    try:
        forum = Forum.objects.get(pk=forum_id)
    except Forum.DoesNotExist:
        raise Http404

    return object_detail(request, Forum.objects.all(), object_id = forum_id)


############################################################################
#
def forum_disc_list(request, forum_id):
    """A forum/discussion list. Basically lists some of the forum detail and
    a list of discussions in that forum (filtered and sorted according to the
    queryset.)
    """
    order_by = request.GET.get('order_by', 'created_at')
    if order_by not in ('name', 'slug', 'creator', 'created_at',
                        'last_post_at'):
        order_by = 'created_at'

    query_set = Forum.objects.all().order_by(order_by)
    ec = { 'order_by' : order_by }

    return object_list(request, query_set,
                       template_name = 'asforums/discussion_list.html',
                       extra_context = ec)

