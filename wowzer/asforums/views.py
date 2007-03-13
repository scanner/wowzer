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
def fc_list(request):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    query_set = ForumCollection.objects.all()
    return object_list(request, query_set, "asforums/fc_list.html")

############################################################################
#
def fc_detail(request, fc_id):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    try:
        fc = ForumCollection.objects.get(pk=fc_id)
    except ForumCollection.DoesNotExist:
        raise Http404

    query_set = Forum.objects.filter(collection = fc)
    return object_list(request, query_set, "asforums/fc_detail.html")

############################################################################
#
def fc_update(request):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    pass

############################################################################
#
def fc_delete(request):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    pass

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
def forum_create(request):
    """Creation of a new forum.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return create_object(request, Forum)

############################################################################
#
def forum_update(request, forum_id):
    """Modify an existing forum object.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return update_object(request, Forum, slug = forum_id, slug_field="slug")

############################################################################
#
def forum_delete(request, forum_id):
    """Ask for confirmation if this is a GET, and if it is a POST we the
    proper bits set, delete the forum.

    This will permanently delete all discussions and posts in this forum.
    
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    forum = Forum.objects.get(slug = forum_id)

    # After delete redirect to the forum collection this forum was in
    #
    return delete_object(request, Forum, post_delete_redirect = \
                         forum.collection.get_absolute_url()
                         slug = forum_id, slug_field="slug")

############################################################################
#
def forum_disc_list(request, forum_id):
    """A forum/discussion list. Basically lists some of the forum detail and
    a list of discussions in that forum (filtered and sorted according to the
    queryset.)
    """
    try:
        forum = Forum.objects.get(pk=forum_id)
    except Forum.DoesNotExist:
        raise Http404

    # Orders the list of discussions in this forum.
    #
    order_by = request.GET.get('order_by', 'created_at')
    if order_by not in ('name', 'slug', 'creator', 'created_at',
                        'last_post_at'):
        order_by = 'created_at'

    # Get the list of discussions in this forum that match our filter and
    # ordering criteria.
    #
    query_set = Forum.objects.all().order_by(order_by)
    ec = { 'order_by' : order_by, 'forum' : forum }

    return object_list(request, query_set,
                       template_name = 'asforums/forum_disc_list.html',
                       extra_context = ec)

