#
# File: $Id$
#
"""AS forums views. Viewing, editing, creating forums, discussions, posts, etc.
"""

# System imports
#
import sys
from datetime import datetime, timedelta

# Django imports
#
from django import oldforms

from django import newforms as forms
from django.newforms import widgets

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

# Django contrib.auth imports
#
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

# Wowzer utility functions
#
from wowzer.utils import msg_user

# The data models from our apps:
#
from wowzer.asforums.models import *

paginate_by = 10

############################################################################
#
def index(request):
    """Simplistic top level index. Shows all forum collections and their
    forums
    """
    query_set = Forum.objects.viewable(request.user).order_by('collection','created')
    ec = {}
    
    return object_list(request, query_set,
                       paginate_by = 10,
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
    query_set = ForumCollection.objects.viewable(request.user).order_by('created')
    return object_list(request, query_set,
                       paginate_by = 10,
                       template_name = "asforums/fc_list.html")

############################################################################
#
def fc_detail(request, fc_id):
    """A list of forum collections that the user can view.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    fc = get_object_or_404(ForumCollection, pk = fc_id)

    # You must have read permission on a fc to read it.
    #
    if not request.userhas_perm("read_forumcollection", object = fc):
        return HttpResponseForbidden("You do not have the requisite "
                                     "permissions to see this forum "
                                     "collection")
    
    ec = { 'forum_collection' : fc }
    query_set = fc.forum_set.viewable(request.user).order_by('created')
    return object_list(request, query_set,
                       paginate_by = 10,
                       template_name = "asforums/fc_detail.html",
                       extra_context = ec)

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
    
    fc = get_object_or_404(ForumCollection, pk = fc_id)

    # You must have change permission on a fc.
    #
    if not request.user.has_perm("change_forumcollection", object = fc):
        return HttpResponseForbidden("You do not have the requisite "
                                     "permissions to change this forum "
                                     "collection")

    FCForm = forms.models.form_for_model(ForumCollection)
    if request.method == "POST":
        form = FCForm(request.POST)
        if form.is_valid():
            entry = form.save()
            msg_user(request.user, "Your modification of forum collection "
                     "'%s' was successfull." % entry.name)
            return HttpResponseRedirect(entry.get_absolute_url)
    else:
        form = FCForm()

    t = get_template("asforums/fc_update.html")
    c = Context(request, { 'forumcollection' : fc,
                           'form' : form })
    return HttpResponse(t.render(c))

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
    fc = get_object_or_404(ForumCollection, pk = fc_id)

    # You must have delete permission on a fc to delete it.
    #
    if not request.user.has_perm("delete_forumcollection", object = fc):
        return HttpResponseForbidden("You do not have the requisite "
                                     "permissions to delete this forum "
                                     "collection")
    return delete_object(request, ForumCollection,
                         "/asforums/forum_collections/",
                         object_id = fc_id,
                         template_name = "asforums/fc_confirm_delete.html")

############################################################################
#
@permission_required('asforums.create_forumcollection')
def fc_create(request):
    """Creation of a new forum collection.
    """
    FCForm = forms.models.form_for_model(ForumCollection)
    if request.method == "POST":
        form = FCForm(request.POST)
        if form.is_valid():
            entry = form.save(commit = False)
            entry.author = request.user
            entry.save()
            msg_user(request.user, "Your have created forum collection "
                     "'%s'." % entry.name)
            return HttpResponseRedirect(entry.get_absolute_url)
    else:
        form = FCForm()

    t = get_template("asforums/fc_create.html")
    c = Context(request, { 'form' : form })
    return HttpResponse(t.render(c))

############################################################################
#
def obj_list_redir(request):
    """For index url's for which we have no specific view we send the user
    back to the top level view of this app."""

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

    if not request.user.has_perm('createforum_forumcollection', object = fc):
        return HttpResponseForbidden("You do not have the requisite "
                                     "permissions to create this forum.")

    ForumForm = forms.models.form_for_model(Forum)

    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            entry = form.save(commit = False)
            entry.author = request.user
            entry.collection = fc
            entry.save()
            msg_user(request.user, "You have created the forum '%s' in "
                     "forum collection '%s'." % forum.name, fc.name)
            return HttpResponseRedirect(entry.get_absolute_url)
    else:
        form = ForumForm()

    t = get_template("asforums/forum_create.html")
    c = Context(request, { "forumcollection" : fc, "form" : form })
    return HttpResponse(t.render(c))

############################################################################
#
def forum_detail(request, forum_id):
    """A forum detail shows just the forum and its details. Not much here.
    """
    try:
        form = Forum.objects.select_related().get(pk = forum_id)
        fc = Forum.collection
    except Forum.DoesNotExist:
        raise Http404

    # Must have moderate or read permissions on the forum collection
    # and forum.
    #
    if (not request.user.has_perm("read_forumcollection", object = fc) or \
        not request.user.has_perm("moderate_forumcollection", object = fc)) and \
       (not request.user.has_perm("read_forum", object = forum) or \
        not request.user.has_perm("moderate_forum", object = forum)):
        return HttpResponseForbidden("You do not have the requisite "
                                     "permissions to read this forum.")

    ec = { 'forum' : forum }

    # All discussions in a forum that you can view are viewable.
    #
    qs = forum.discussion_set.all().order_by('created')
    return object_list(request, forum.discussion_set.all(),
                       paginate_by = 10,
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
def disc_list(request):
    """This will produce a list of discussions that match some arbitrary
    criteria specified as parameters.

    XXX This always needs to be limited by the 'view' permissions on
    XXX discussions.
    """

    query_set = Discussion.objects.viewable(request.user).order_by('created')
    return object_list(request, query_set,
                       paginate_by = 10,
                       template_name = "asforums/disc_list.html")
    
############################################################################
#
@login_required
def disc_create(request, forum_id):
    """Creation of a new discussion.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.

    XXX When you create a discussion instead of dynamically referring to the
    XXX permissions of the forum & forum collection we will have the
    XXX permissions copied in to the discussion object. This if a person
    XXX has 'post' permissions on a forum, then all discussions that are
    XXX created will be created with 'post' permissions.
    """
    forum = get_object_or_404(Forum, pk = forum_id)

    manipulator = Discussion.AddManipulator()
    if request.method == "POST":
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

    Since a 'discussion detail' lists posts in a discussion (as well as the
    discussion details) we take a bunch of parameters that adjust the posts we
    list.

    The parameters are:
    o page (goes to that page in the listing of posts)
    o order_by (sorts the listing of posts by this field)
    o post (goes to that page in the listing of posts that this post is on)
    o author (finds posts by that author)
    o search (find posts that contain the given expression in their content)
             (this one is a tbd. We need to use something like merquery)
    """

    if request.META.has_key("HTTP_REFERER"):
        print "Referrer url was: %s" % request.META["HTTP_REFERER"]
    
    try:
        disc = Discussion.objects.get(pk=disc_id)
    except Discussion.DoesNotExist:
        raise Http404

    # Getting a discussion detail bumps its view count.
    #
    #    disc.increment_viewed() # We tried custom sql. It did not work.
    #
    # If the referrer url was this same url then we should NOT bump up
    # the viewed count.. (otherwise the viewed count gets bumped every
    # time you go to the next page of posts in a multi-page listing)
    disc.views += 1
    disc.save()
    
    ec = { 'discussion' : disc }

    qs = Post.objects.readable(request.user).filter(discussion = disc).order_by('created')
    return object_list(request, qs,
                       paginate_by = 10,
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
    try:
        disc = Discussion.objects.select_related().get(pk = disc_id)
        forum = disc.forum
        fc = forum.collection
    except Discussion.DoesNotExist:
        raise Http404

    # If a discussion is locked or closed, no one except for moderators
    # of this forum can post to it.
    #
    if (disc.locked or disc.closed) and \
        not request.user.has_perm("moderate_forum", object = forum):
        return HttpResponseForbidden("You do not have "
                                     "the requisite permissions to post to "
                                     "this discussion.")
    
    # They must have post permission on the discussion, forum, forum collection
    # or a moderator of the forum.
    #
    if (not request.user.has_perm("moderate_forum")) or \
       (not (request.user.has_perm("post_discussion", object = disc) and \
             request.user.has_perm("post_forum", object = forum) and \
             request.user.has_perm("post_forumcollection", object = fc))):
        return HttpResponseForbidden("You do not have "
                                     "the requisite permissions to post to "
                                     "this discussion.")

    # If this post is in reply to another post, the other post's id
    # will passed in via a parameter under "in_reply_to". We make sure
    # that no monkey business is going on.
    #
    if request.REQUEST.has_key('in_reply_to'):
        try:
            irt = Post.objects.select_related().get(\
                pk = int(request.REQUEST['in_reply_to']))
        except Post.DoesNotExist:
            raise Http404
        if irt.discussion.id != disc.id:
            return HttpResponseServerError("Post you are replying to is in dis"
                                           "cussion %s, you are replying in di"
                                           "scussion %s. You can only reply to"
                                           " posts in the same discussion." % \
                                           (disc.name, irt.discussion.name))
    else:
        irt = None

    PostForm = forms.models.form_for_model(Post)
    PostForm.base_fields['content'].widget = \
                widgets.Textarea(attrs = {'cols' : '80', 'rows' : '12'})

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            entry = form.save(commit = False)
            entry.author = request.user
            entry.discussion = disc
            if irt:
                entry.in_reply_to = irt

            entry.save()

            msg_user(request.user,
                     "Your post was made to discussion %s" % disc.name)
            return HttpResponseRedirect(disc.get_absolute_url() +
                                        "?post=%d#%d" % (entry.id, entry.id))
    else:
        if irt:
            # This is in reply to another post. Stick in the reference to
            # that other post and fill in the message being posted with a
            # quote of the post being replied to.
            #
            form = PostForm({ 'in_reply_to' : irt.id,
                              'content'     : "[quote=%s]%s[/quote]" % \
                              (irt.author.username, irt.content)})
        else:
            form = PostForm()

    t = get_template("asforums/post_create.html")
    c = Context(request, {
        'in_reply_to': irt,
        'discussion' : disc,
        'form'       : form,
        })
    return HttpResponse(t.render(c))

############################################################################
#
def post_detail(request, post_id):
    return object_detail(request, Post.objects.readable(request.user), object_id = post_id)

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

