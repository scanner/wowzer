#
# File: $Id$
#
"""AS forums views. Viewing, editing, creating forums, discussions, posts, etc.
"""

# System imports
#
import sys
from urlparse import urlparse
from datetime import datetime, timedelta

# Django imports
#
from django import oldforms

from django import newforms as forms
from django.newforms import widgets

from django.shortcuts import get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.views.generic.create_update import create_object
from django.views.generic.create_update import update_object
from django.views.generic.create_update import delete_object
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

# Django contrib.auth imports
#
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test

# Wowzer utility functions
#
from wowzer.utils import msg_user
from wowzer.decorators import logged_in_or_basicauth
from wowzer.main.views import rlp_edit
from wowzer.main.decorators import breadcrumb
from wowzer.main.fields import UserOrGroupField

# RSS Feeds
#
from wowzer.asforums.feeds import LatestPosts, LatestPostsByForumDiscussion

# Django contrib models
#
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

# 3rd party models & utils
#
from tagging.models import TaggedItem
from tagging.utils import get_tag

# The data models from our apps:
#
from wowzer.asforums.models import ForumCollection, Forum, Discussion, Post
from wowzer.main.models import Breadcrumb

paginate_by = 10

############################################################################
#
class DeleteForm(forms.Form):
    reason = forms.CharField(max_length = 128)

############################################################################
#
@login_required
@breadcrumb(name="Forum Index")
def index(request):
    """Simplistic top level index. Shows all forum collections and their
    forums
    """
    query_set = Forum.objects.viewable(request.user).order_by('collection',
                                                              'created')
    ec = {}

    return object_list(request, query_set,
                       paginate_by = 10,
                       template_name = 'asforums/index.html',
                       extra_context = ec)

############################################################################
#
@login_required
@breadcrumb(name = "Forum collection list")
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
@login_required
@breadcrumb
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
    if not request.user.has_perm("asforums.read_forumcollection", object = fc):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Forum Collection %s" % fc.name)
    ec = { 'forum_collection' : fc }
    query_set = fc.forum_set.viewable(request.user).order_by('created')
    return object_list(request, query_set,
                       paginate_by = 10,
                       template_name = "asforums/fc_detail.html",
                       extra_context = ec)

############################################################################
#
class AddForumCollectionCreatePermForm(forms.Form):
    user_or_group = UserOrGroupField(label = "User or Group",
                                     help_text = "The user or group to grant "
                                     "forum collection create priveleges to.")

############################################################################
#
class DelForumCollectionCreatePermForm(forms.Form):
    groups = forms.MultipleChoiceField(label = "Groups",
                                       required = False,
                                       help_text = "Groups " \
                                       "that have 'create' forum " \
                                       "collection permission. Check the " \
                                       "ones that you wish to remove the " \
                                       "permission from.")
    users = forms.MultipleChoiceField(label = "Users",
                                      required = False,
                                      help_text = "Users " \
                                      "that have 'create' forum " \
                                      "collection permission. Check the ones "\
                                      "that you wish to remove the permission"\
                                      " from.")

############################################################################
#
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@breadcrumb(name="Forum Collection Create Permission")
def fc_create_perm(request):
    """
    The permission to create a forum collection is a class or model
    permission. It uses the simple style django permission to set that
    you can create a forum collection object.

    This is the only permission that can be set this way via the webui
    for the entire forum system. As forms go it is also pretty
    simple. Whether the entity is a user or a group, the name of the
    user or group.
    """

    # We need to construct the values for the current set of users and groups
    # that have this permission.
    #
    create_perm = Permission.objects.select_related().get(\
             codename="add_forumcollection",
             content_type = ContentType.objects.get_for_model(ForumCollection))

    user_choices = []
    group_choices = []
    for user in create_perm.user_set.all():
        user_choices.append((str(user.id), user.username))
    for group in create_perm.group_set.all():
        group_choices.append((str(group.id), group.name))

    DelForumCollectionCreatePermForm.base_fields['groups'].choices = \
                                                                  group_choices
    DelForumCollectionCreatePermForm.base_fields['groups'].widget = \
                    widgets.CheckboxSelectMultiple(choices = group_choices)
    DelForumCollectionCreatePermForm.base_fields['users'].choices = \
                                                                  user_choices
    DelForumCollectionCreatePermForm.base_fields['users'].widget = \
                    widgets.CheckboxSelectMultiple(choices = user_choices)

    # This is a post they have submitted one of the two forms. Based on the
    # 'submit' button they pushed we determine which form was submitted.
    #
    if request.method == "POST":
        # The 'add create permission' form
        #
        if request.POST["submit"] == "Add create permission":
            add_form = AddForumCollectionCreatePermForm(request.POST)
            if add_form.is_valid():
                u_or_g, name = add_form.cleaned_data['user_or_group'].split(',')
                if u_or_g == "user":
                    u = User.objects.get(username=name)
                    u.user_permissions.add(create_perm)
                else:
                    g = Group.objects.get(name=name)
                    g.permissions.add(create_perm)
                msg_user(request.user, "Added '%s' permission to %s " \
                         "%s." % (create_perm, u_or_g, name))
                return HttpResponseRedirect(".")
        else:
            add_form = AddForumCollectionCreatePermForm()

        # The 'delete create permission' form. This is a teeny bit
        # trickier as the 'selected' items in our form are the entities
        # to remove the 'create forum collection' permission from.
        #
        if request.POST["submit"] == "Remove create permission":
            rem_form = DelForumCollectionCreatePermForm(request.POST)
            if rem_form.is_valid():
                for g_id in rem_form.cleaned_data['groups']:
                    try:
                        g = Group.objects.get(pk = g_id)
                        g.permissions.remove(create_perm)
                        msg_user(request.user, "Removed '%s' permission " \
                                 "from group %s." % (create_perm, g.name))
                    except Group.DoesNotExist:
                        pass
                for u_id in rem_form.cleaned_data['users']:
                    try:
                        u = User.objects.get(pk = u_id)
                        u.user_permissions.remove(create_perm)
                        msg_user(request.user, "Removed '%s' permission " \
                                 "from user %s." % (create_perm, u.username))
                    except Group.DoesNotExist:
                        pass
                return HttpResponseRedirect(".")
        else:
            rem_form = DelForumCollectionCreatePermForm()
    else:
        add_form = AddForumCollectionCreatePermForm()
        rem_form = DelForumCollectionCreatePermForm()

    t = get_template("asforums/fc_create_perm.html")
    c = Context(request, {'add_form' : add_form, 'rem_form' : rem_form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def fc_perms(request, fc_id):
    """
    Display / edit the row level permissions for a specific forum collection.
    """
    fc = get_object_or_404(ForumCollection, pk = fc_id)

    # You must have edit permission on a fc to modify the permissions.
    # You must have view permission on a fc to see its permissions.
    #
    if (not request.user.has_perm("asforums.view_forumcollection",
                                  object = fc)) or \
       (request.method == "POST" and \
        not request.user.has_perm("asforums.change_forumcollection",
                                  object = fc)):
        raise PermissionDenied
    Breadcrumb.rename_last(request, "Forum Collection %s permissions" % fc.name)
    return rlp_edit(request, fc, template = "asforums/fc_perms.html")

############################################################################
#
@login_required
@breadcrumb
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
    if not request.user.has_perm("asforums.change_forumcollection",
                                 object = fc):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Update Forum Collection %s" % fc.name)
    FCForm = forms.models.form_forinstance(fc)
    if request.method == "POST":
        form = FCForm(request.POST)
        if form.is_valid():
            entry = form.save()
            msg_user(request.user,
                     "Forum collection '%s' updated." % entry.name)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = FCForm()

    t = get_template("asforums/fc_update.html")
    c = Context(request, { 'forumcollection' : fc,
                           'form' : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
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
    if not request.user.has_perm("asforums.delete_forumcollection",
                                 object = fc):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Delete Forum Collection %s" % fc.name)
    return delete_object(request, ForumCollection,
                         "/asforums/forum_collections/",
                         object_id = fc_id,
                         template_name = "asforums/fc_confirm_delete.html")

############################################################################
#
@permission_required('asforums.create_forumcollection')
@breadcrumb(name="Create a Forum Collection")
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
            msg_user(request.user, "Forum collection '%s' created." % \
                     entry.name)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = FCForm()

    t = get_template("asforums/fc_create.html")
    c = Context(request, { 'form' : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def obj_list_redir(request):
    """For index url's for which we have no specific view we send the user
    back to the top level view of this app."""

    return HttpResponseRedirect("/asforums/")

############################################################################
#
@login_required
@breadcrumb("Create a Forum")
def forum_create(request,fc_id):
    """Creation of a new forum.
    XXX For now until we get the form filled and our such we are going to
    XXX hand stuff off to the generic crud views. I am doing it this way
    XXX instead of entirely in the urls.py file because I am going to put
    XXX stuff here and I feel better with this stub defined.
    """
    fc = get_object_or_404(ForumCollection, pk = fc_id)

    if not request.user.has_perm('createforum_forumcollection', object = fc):
        raise PermissionDenied

    ForumForm = forms.models.form_for_model(Forum)

    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            entry = form.save(commit = False)
            entry.author = request.user
            entry.collection = fc
            entry.save()
            msg_user(request.user, "You have created the forum '%s' in "
                     "forum collection '%s'." % entry.name, fc.name)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = ForumForm()

    t = get_template("asforums/forum_create.html")
    c = Context(request, { "forumcollection" : fc, "form" : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def forum_detail(request, forum_id):
    """A forum detail shows just the forum and its details. Not much here.
    """
    try:
        forum = Forum.objects.select_related().get(pk = forum_id)
        fc = forum.collection
    except Forum.DoesNotExist:
        raise Http404

    # To make thing shorter
    #
    r = request

    # Must have moderate or read permissions on the forum collection
    # and forum.
    #
    if not (r.user.has_perm("asforums.moderate_forum", object = forum) or \
            (r.user.has_perm("asforums.read_forumcollection", object = fc) and \
             r.user.has_perm("asforums.read_forum", object = forum))):
        raise PermissionDenied
    Breadcrumb.rename_last(request, "Forum %s" % forum.name)

    ec = { 'forum' : forum }

    # All discussions in a forum that you can read are viewable.
    #
    qs = forum.discussion_set.all().order_by('sticky','created')
    return object_list(request, forum.discussion_set.all(),
                       paginate_by = 10,
                       template_name = "asforums/forum_detail.html",
                       extra_context = ec)

############################################################################
#
@login_required
@breadcrumb
def forum_update(request, forum_id):
    """Modify an existing forum object.
    """
    try:
        f = Forum.objects.select_related().get(pk = forum_id)
        fc = f.collection
    except Forum.DoesNotExist:
        raise Http404

    # You need moderate permission on the forum collection it
    # is in or update permission on the forum.
    #
    if not (request.user.has_perm("asforums.moderate_forumcollection",
                                  object = fc) or \
            request.user.has_perm("asforums.update_forum", object = f)):
        raise PerissionDenied

    Breadcrumb.rename_last(request, "Update Forum %s" % forum.name)
    ForumForm = forms.models.form_for_instance(f)

    if request.method == "POST":
        form = ForumForm(request.POST)
        if form.is_valid():
            entry = form.save()
            msg_user(request.user, "Forum was updated.")
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = ForumForm()
    t = get_template("asforums/forum_update.html")
    c = Context(request, {'forumcollection' : fc, 'form' : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def forum_perms(request, forum_id):
    """
    Display / edit the row level permissions for a specific forum collection.
    """
    f = get_object_or_404(Forum, pk = forum_id)

    # You must have edit permission to modify the permissions.
    # You must have read permission to see its permissions.
    #
    if (not request.user.has_perm("asforums.read_forum", object = f)) or \
        (request.method == "POST" and \
         not request.user.has_perm("asforums.change_forum", object = f)):
        raise PermissionDenied
    Breadcrumb.rename_last(request, "Forum %s permissions" % f.name)
    return rlp_edit(request, f, template = "asforums/forum_perms.html")

############################################################################
#
@login_required
@breadcrumb
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
        forum = Forum.objects.select_related().get(pk = forum_id)
        fc = forum.collection
    except Forum.DoesNotExist:
        raise Http404

    # You must have moderate on the forumcollection or delete permission
    # on this forum.
    #
    if not (request.user.has_perm("asforums.moderate_forumcollection",
                                  object = fc) or \
            request.user.has_perm("asforums.delete_forum", object = forum)):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Delete Forum %s" % forum.name)
    # After delete redirect to the forum collection this forum was in
    #
    return delete_object(request, Forum,
                         post_delete_redirect = fc.get_absolute_url(),
                         object_id = forum_id)

############################################################################
#
@login_required
@breadcrumb(name = "Discussion list")
def disc_list(request):
    """This will produce a list of discussions that match some arbitrary
    criteria specified as parameters.

    XXX This always needs to be limited by the 'view' permissions on
    XXX discussions.
    """

    query_set = Discussion.objects.viewable(request.user).order_by('sticky',
                                                                   'forum',
                                                                   'created')
    return object_list(request, query_set,
                       paginate_by = 10,
                       template_name = "asforums/disc_list.html")

############################################################################
#
@login_required
@breadcrumb
def disc_create(request, forum_id):
    """Creation of a new discussion.
    XXX When you create a discussion instead of dynamically referring to the
    XXX permissions of the forum & forum collection we will have the
    XXX permissions copied in to the discussion object. This if a person
    XXX has 'post' permissions on a forum, then all discussions that are
    XXX created will be created with 'post' permissions.
    """
    f = get_object_or_404(Forum, pk = forum_id)

    # They need 'moderate' or 'discuss' permissions on this forum.
    #
    if not (request.user.has_perm("asforums.moderate_forum", object = f) or \
            request.user.has_perm("asforums.discuss_forum", object = f)):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Create Discussion in %s" % f.name)

    DiscForm = forms.models.form_for_model(Discussion)
    if request.method == "POST":
        form = DiscForm(request.POST)
        if form.is_valid():
            entry = form.save(commit = False)
            entry.author = request.user
            entry.forum = f
            entry.save()
            msg_user(request.user, "Your have created the discussion "
                     "'%s'." % entry.name)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = DiscForm()

    t = get_template("asforums/disc_create.html")
    c = Context(request, { 'forum' : f, 'form' : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
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
    try:
        disc = Discussion.objects.select_related().get(pk=disc_id)
        f = disc.forum
    except Discussion.DoesNotExist:
        raise Http404

    # To read a discussion they must have 'read' on the forum it is contained
    # in. The discussion must not be locked, unless they are a moderator.
    #
    if not (request.user.has_perm("asforums.moderate_forum", object = f) or \
            (not disc.locked and
             request.user.has_perm("asforums.read_forum", object = f))):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Discussion %s" % disc.name)
    # Getting a discussion detail bumps its view count.
    #
    #    disc.increment_viewed() # We tried custom sql. It did not work.
    #
    # If the referrer url was this same url then we should NOT bump up
    # the viewed count.. (otherwise the viewed count gets bumped every
    # time you go to the next page of posts in a multi-page listing)
    if request.META.has_key("HTTP_REFERER") and \
       urlparse(request.META['HTTP_REFERER'])[2] == disc.get_absolute_url():
        pass
    else:
        disc.views += 1
        disc.save()

    ec = { 'discussion' : disc }

    qs = Post.objects.readable(request.user).filter(discussion = disc).order_by('created')
    # If the 'post' parameter was passed use this to determine what
    # page to display since we know how many posts per page to display
    # (and that the post number is a linearly increasing value with
    # the number of posts in this discussion.)
    #
    page = None
    if request.GET.has_key('post'):
        try:
            page = ((int(request.GET.get('post')) - 1) / paginate_by) + 1
        except ValueError:
            page = None

    return object_list(request, qs,
                       page = page,
                       paginate_by = paginate_by,
                       template_name = "asforums/disc_detail.html",
                       extra_context = ec)

############################################################################
#
@login_required
@breadcrumb
def disc_perms(request, disc_id):
    """
    Display / edit the row level permissions for a specific discussion.
    """
    d = get_object_or_404(Discussion, pk = disc_id)

    # You must have edit permission on the discussion to modify the
    # permissions.  You must have read permission on the forum to see
    # its permissions.
    #
    if (not request.user.has_perm("asforums.read_forum",
                                  object = d.forum)) or \
       (request.method == "POST" and \
        not request.user.has_perm("asforums.change_discussion", object = d)):
        raise PermissionDenied
    Breadcrumb.rename_last(request, "Discussion %s permissions" % d.name)
    return rlp_edit(request, d, template = "asforums/disc_perms.html")

############################################################################
#
@login_required
@breadcrumb
def disc_update(request, disc_id):
    """Modify an existing discussion object.
    """
    try:
        d = Discussion.objects.select_related().get(pk = disc_id)
        f = d.forum
    except Discussion.DoesNotExist:
        raise Http404

    if not (request.user.has_perm("asforums.moderate_forum", object = f) or \
            (not d.locked and
             request.user.has_perm("asforums.update_discussion", object = d))):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Update Discussion %s" % d.name)
    DiscForm = forms.models.form_for_instance(d)
    if request.method == "POST":
        form = DiscForm(request.POST)
        if form.is_valid():
            entry = form.save()
            msg_user(request.user, "Discussion %s updated." % entry.name)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = DiscForm()

    t = get_template("asforums/disc_update.html")
    c = Context(request, { 'forum'      : f,
                           'discussion' : d,
                           'form'       : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def disc_tag(request, tag):
    """
    Display a list of all the discussions that have the given tag, ordered
    by forum, from most recent to oldest.
    """
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise Http404, 'No tag found matching "%s"' % tag

    Breadcrumb.rename_last(request, 'Discussions w/tag "%s"' % tag)
    tqs = TaggedItem.objects.get_by_model(Discussion, tag)
    qs = Discussion.objects.viewable(request.user,
                                     query_set = tqs).order_by('sticky',
                                                               '-forum',
                                                               '-created')
    return object_list(request, qs, paginate_by = 10,
                       template_name = "asforums/disc_list.html")

############################################################################
#
@login_required
@breadcrumb
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
        disc = Discussion.objects.select_related().get(pk = disc_id)
        forum = disc.forum
    except Forum.DoesNotExist:
        raise Http404

    # Need to have delete permission on the discussion,
    # or moderate permission on the forum. Can not delete locked
    # discussions unless you are a moderator.
    #
    if not ((request.user.has_perm("asforums.moderate_forum", object = forum)) or \
            (not disc.locked and
             request.user.has_perm("asforums.delete_discussion", object = disc))):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Delete Discussion %s" % disc.name)
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            disc.delete()
            msg_user(request.user, "Discussion deleted")
            return HttpResponseRedirect(forum.get_absolute_url())
    else:
        form = DeleteForm()

    t = get_template("asforums/disc_delete.html")
    c = Context(request, {
        'discussion' : disc,
        'form' : form,
        })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb
def post_create(request, disc_id):
    try:
        disc = Discussion.objects.select_related().get(pk = disc_id)
        forum = disc.forum
        fc = forum.collection
    except Discussion.DoesNotExist:
        raise Http404

    # Only people with 'post' permission can post to this discussion.
    #
    # If a discussion is locked or closed, no one except for moderators
    # of this forum can post to it.
    #
    if not ((not disc.locked and \
             not disc.closed and \
             request.user.has_perm("asforums.post_discussion", object = disc)) or \
            request.user.has_perm("asforums.moderate_forum", object = forum)):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Post in discussion %s" % disc.name)

    # If this post is in reply to another post, the other post's id
    # will passed in via a parameter under "in_reply_to". We make sure
    # that no monkey business is going on.
    #
    irt = None
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

    PostForm = forms.models.form_for_model(Post)
    PostForm.base_fields['content'].widget = \
                widgets.Textarea(attrs = {'cols' : '80', 'rows' : '12'})
    PostForm.base_fields['content_html'].widget = widgets.HiddenInput()

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
            return HttpResponseRedirect(entry.get_discussion_url())
    else:
        if irt:
            # This is in reply to another post. Stick in the reference to
            # that other post and fill in the message being posted with a
            # quote of the post being replied to.
            #
            form = PostForm({ 'in_reply_to' : irt.id,
                              'content'     : '[quote="%s"]%s[/quote]' % \
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
@login_required
@breadcrumb
def post_tag(request, tag):
    """
    Display a list of all of the posts that have the given tag, organized
    by discussion from most recent to oldest.
    """
    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise Http404, 'No tag found matching "%s"' % tag

    Breadcrumb.rename_last(request, 'Posts w/tag "%s"' % tag)
    tqs = TaggedItem.objects.get_by_model(Post, tag)
    qs = Post.objects.readable(request.user,
                               query_set = tqs).order_by('-discussion_id',
                                                         '-post_number')
    return object_list(request, qs, paginate_by = 10,
                       template_name = "asforums/post_list.html")

############################################################################
#
@logged_in_or_basicauth(realm = "wowzer")
def post_feed_latest(request):
    """
    A RSS feed of the 30 latests posts.
    """
    feedgen = LatestPosts("latest_posts", request.path,
                          request.user).get_feed()
    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

############################################################################
#
@logged_in_or_basicauth(realm = "wowzer")
def post_feed_latest_by_discussion(request):
    """
    A RSS feed of the 30 latests posts.
    """
    feedgen = LatestPostsByForumDiscussion("latest_posts", request.path,
                                           request.user).get_feed()
    response = HttpResponse(mimetype=feedgen.mime_type)
    feedgen.write(response, 'utf-8')
    return response

############################################################################
#
@login_required
@breadcrumb
def post_detail(request, post_id):
    try:
        post = Post.objects.select_related().get(pk = post_id)
    except Post.DoesNotExist:
        raise Http404

    if not ((request.user.has_perm("asforums.moderate_forum",
                                   object = post.discussion.forum)) or \
            (not post.discussion.locked and \
             not post.deleted and \
             request.user.has_perm("asforums.read_discussion",
                                   object = post.discussion))):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Post #%d in %s" % (post.post_number,
                                                        post.discussion.name))

    return object_detail(request, Post.objects.readable(request.user),
                         object_id = post_id)

############################################################################
#
@login_required
@breadcrumb
def post_perms(request, post_id):
    """
    Display / edit the row level permissions for a post.
    """
    p = get_object_or_404(Post, pk = post_id)

    # You must have edit permission on the post to modify the permissions.
    # You must have read permission on the discussion to see its permissions.
    #
    if (not request.user.has_perm("asforums.read_discussion", object = p.discussion)) or \
        (request.method == "POST" and \
         not request.user.has_perm("asforums.change_post", object = p)):
        raise PermissionDenied
    Breadcrumb.rename_last(request, "Post #%d in %s permissions" % \
                           (post.post_number, post.discussion.name))
    return rlp_edit(request, p, template = "asforums/post_perms.html")

############################################################################
#
@login_required
@breadcrumb
def post_update(request, post_id):
    try:
        post = Post.objects.select_related().get(pk = post_id)
    except Post.DoesNotExist:
        raise Http404

    # You need to have update permission on a post or be moderator of
    # the forum that the discussion is in that contains this post.
    #
    if not ((request.user.has_perm("asforums.moderate_forum",
                                   object = post.discussion.forum)) or \
            (not post.discussion.locked and not post.discussion.closed and \
             (post.author == request.user or \
              request.user.has_perm("asforums.update_post", object = post)))):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Update post #%d in %s" % \
                           (post.post_number, post.discussion.name))
    PostForm = forms.models.form_for_instance(post)
    PostForm.base_fields['content'].widget = \
                widgets.Textarea(attrs = {'cols' : '80', 'rows' : '12'})
    PostForm.base_fields['content_html'].widget = widgets.HiddenInput()

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            entry = form.save(commit = False)
            entry.edited = True
            entry.changed = datetime.utcnow()
            entry.save()

            msg_user(request.user, "Post was updated.")
            return HttpResponseRedirect(entry.get_discussion_url())
    else:
        form = PostForm()

    t = get_template("asforums/post_create.html")
    c = Context(request, {
        'discussion' : post.discussion,
        'form'       : form,
        })
    return HttpResponse(t.render(c))

############################################################################
#
class PostDeleteForm(forms.Form):
    reason = forms.CharField(max_length = 128)

@login_required
@breadcrumb
def post_delete(request, post_id):
    try:
        post = Post.objects.select_related().get(pk = post_id)
    except Post.DoesNotExist:
        raise Http404

    # In order to delete a post you must be a moderator of the forum
    # or the discussion must not be locked and you must be the author of the
    # post or author of the discussion.
    #
    if not ((request.user.has_perm("asforums.moderate_forum",
                                   object = post.discussion.forum)) or \
            (not post.discussion.locked and \
             (post.author == request.user or \
              post.discussion.author == request.user or \
              request.user.has_perm("asforums.delete_post", object = post)))):
        raise PermissionDenied

    Breadcrumb.rename_last(request, "Delete post #%d in %s" % \
                           (post.post_number, post.discussion.name))

    if request.method == "POST":
        form = PostDeleteForm(request.POST)
        if form.is_valid():
            post.deleted = True
            post.deleted_by = request.user
            post.deletion_reason =  form.cleaned_data['reason']
            post.save()

            request.user.message_set.create(message = "Post deleted")
            return HttpResponseRedirect(post.get_discussion_url())
    else:
        form = PostDeleteForm()

    t = get_template("asforums/post_delete.html")
    c = Context(request, {
        'post' : post,
        'form' : form,
        })
    return HttpResponse(t.render(c))
