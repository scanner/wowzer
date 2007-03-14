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
from django.views.generic.create_update import create_object
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object
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
@login_required
def fc_update(request, fc_id):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return update_object(request, ForumCollection, fc_id)

############################################################################
#
@login_required
def fc_delete(request):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return delete_object(request, ForumCollection,
                         "/asforums/forum_collections/",
                         object_id = fc_id)

############################################################################
#
@login_required
def fc_create(request):
    """Creation of a new forum collection.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return create_object(request, ForumCollection)

############################################################################
#
def obj_list_redir(request):
    """Because of how objects in the asforum app are organized there is
    no way to blindly list any one set of objects except the top level
    hiearchy - the forum collection. So attempts to list any object
    type except a forum collection results in a redirect to the
    closest thing doing what the user may be after - the top level
    index that lists collections, forums, etc."""

    return HttpResponseRedirect("/asforums/")

############################################################################
#
@login_required
def forum_create(request,fc_id):
    """Creation of a new forum.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    fc = get_object_or_404(ForumCollection, pk = fc_id)

    manipulator = Forum.AddManipulator()
    if request.POST:
        # XXX Does user have 'post' permission in this discussion,
        # XXX forum, forum collection (they need to explicitly have
        # XXX the permission at some level.)
        # if not request.user.has_perm():
        #     raise HttpResponseForbidden("discussion")
        #     raise HttpResponseForbidden("forum")
        #     raise HttpResponseForbidden("forum collection")
        new_data = request.POST.copy()
        new_data['collection'] = fc.id
            
        # Check for errors
        errors = manipulator.get_validation_errors(new_data)
        manipulator.do_html2python(new_data)

        if not errors:
            # No errors -- this means we can save the data!
            new_object = manipulator.save(new_data)

            if request.user.is_authenticated():
                request.user.message_set.create(\
                    message="The Forum %s was created "
                    "successfully." % new_object.name)

            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        # No POST, so we want a brand new form without any data or errors
        errors = {}
        new_data = manipulator.flatten_data()

    # Create the FormWrapper, template, context, response
    form = oldforms.FormWrapper(manipulator, new_data, errors)
    t = get_template("asforums/forum_form.html")
    c = Context(request, {
            'forum_collecton' : fc,
            'form'       : form,
            })
    return HttpResponse(t.render(c))

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

    ec = { 'forum' : forum }

    return object_list(request, Discussion.objects.filter(forum = forum)
                       template_name = "asforums/forum_detail.html",
                       extra_context = ec)

############################################################################
#
@login_required
def forum_update(request, forum_id):
    """Modify an existing forum object.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return update_object(request, Forum, object_id = forum_id)

############################################################################
#
@login_required
def forum_delete(request, forum_id):
    """Ask for confirmation if this is a GET, and if it is a POST we the
    proper bits set, delete the forum.

    This will permanently delete all discussions and posts in this forum.
    
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    try:
        forum = Forum.objects.get(pk = forum_id)
        fc = forum.collection
    except Forum.DoesNotExist:
        raise Http404

    # After delete redirect to the forum collection this forum was in
    #
    return delete_object(request, Forum,
                         post_delete_redirect = fc.get_absolute_url(),
                         object_id = forum_id)

############################################################################
#
@login_required
def disc_create(request, forum_id):
    """Creation of a new discussion.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    forum = get_object_or_404(Forum, pk = forum_id)

    manipulator = Discussion.AddManipulator()
    if request.POST:
        # XXX Does user have 'post' permission in this discussion,
        # XXX forum, forum collection (they need to explicitly have
        # XXX the permission at some level.)
        # if not request.user.has_perm():
        #     raise HttpResponseForbidden("discussion")
        #     raise HttpResponseForbidden("forum")
        #     raise HttpResponseForbidden("forum collection")
        new_data = request.POST.copy()
        new_data['forum'] = forum.id
            
        # Check for errors
        errors = manipulator.get_validation_errors(new_data)
        manipulator.do_html2python(new_data)

        if not errors:
            # No errors -- this means we can save the data!
            new_object = manipulator.save(new_data)

            if request.user.is_authenticated():
                request.user.message_set.create(\
                    message="The discussion %s was created "
                    "successfully." % new_object.name)

            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        # No POST, so we want a brand new form without any data or errors
        errors = {}
        new_data = manipulator.flatten_data()

    # Create the FormWrapper, template, context, response
    form = oldforms.FormWrapper(manipulator, new_data, errors)
    t = get_template("asforums/disc_form.html")
    c = Context(request, {
            'forum_collecton' : fc,
            'form'       : form,
            })
    return HttpResponse(t.render(c))

############################################################################
#
def disc_detail(request, disc_id):
    """A discussion detail shows the discussion details and a list of
    all posts that match the filter/sort criteria.
    """
    try:
        disc = Discussion.objects.get(pk=disc_id)
    except Discussion.DoesNotExist:
        raise Http404

    ec = { 'discussion' : disc }

    return object_list(request, Post.objects.filter(discussion = disc)
                       template_name = "asforums/disc_detail.html",
                       extra_context = ec)

############################################################################
#
@login_required
def disc_update(request, disc_id):
    """Modify an existing discussion object.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    return update_object(request, Discussion, object_id = disc_id)

############################################################################
#
@login_required
def disc_delete(request, disc_id):
    """Ask for confirmation if this is a GET, and if it is a POST we the
    proper bits set, delete the discussion.

    This will permanently delete all posts this discussion.

    XXX Only a moderator and the super user can delete this.
    XXX The owner can only 'shutdown' it, which is makes it unviewable
    XXX and unpostable by everyone but moderators and the super user.
    
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    try:
        disc = Discussion.objects.get(pk = disc_id)
        forum = disc.forum
    except Forum.DoesNotExist:
        raise Http404

    # After delete redirect to the forum detail this discussion was in.
    #
    return delete_object(request, Discussion,
                         post_delete_redirect = forum.get_absolute_url(),
                         object_id = disc_id)


############################################################################
#
@login_required
def post_create(request, disc_id):
    disc = get_object_or_404(Discussion, pk = disc_id)
    forum = disc.forum
    fc = forum.collection

    manipulator = Post.AddManipulator()
    if request.POST:
        # XXX Does user have 'post' permission in this discussion,
        # XXX forum, forum collection (they need to explicitly have
        # XXX the permission at some level.)
        # if not request.user.has_perm():
        #     raise HttpResponseForbidden("discussion")
        #     raise HttpResponseForbidden("forum")
        #     raise HttpResponseForbidden("forum collection")
        new_data = request.POST.copy()
        new_data['discussion'] = disc.id
            
        # Check for errors
        errors = manipulator.get_validation_errors(new_data)
        manipulator.do_html2python(new_data)

        if not errors:
            # No errors -- this means we can save the data!
            new_object = manipulator.save(new_data)

            if request.user.is_authenticated():
                request.user.message_set.create(\
                    message="Your post was made to discussion %s" % \
                    discussion.name)
            return HttpResponseRedirect(new_object.get_absolute_url())
    else:
        # No POST, so we want a brand new form without any data or errors
        errors = {}
        new_data = manipulator.flatten_data()

    # Create the FormWrapper, template, context, response
    form = oldforms.FormWrapper(manipulator, new_data, errors)
    t = get_template("asforums/post_form.html")
    c = Context(request, {
            'discussion' : disc,
            'form'       : form,
            })
    return HttpResponse(t.render(c))

############################################################################
#
def post_detail(request, post_id):
    return object_detail(request, Post.objects.all(), object_id = post_id)

############################################################################
#
@login_required
def post_update(request, post_id):
    return update_object(request, Post, post_id)

############################################################################
#
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return delete_object(request, Post, post.discussion.get_absolute_url())

