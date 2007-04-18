#
# File: $Id$
#
"""This module is all of the views for the 'users' and 'groups'.
"""

# Django imports
#
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
from django.http import HttpResponseForbidden
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

# Django contrib.auth imports
#
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

# Wowzer utility functions
#
from wowzer.utils import msg_user

# Data models.
#
from django.contrib.auth.models import User, Group

############################################################################
#
@login_required
def index(request):
    """The top level view of 'users'. This is a list view of all of the user
    objects.
    """

    # Staff users can see deactivated users. Everyone else can only
    # see active user accounts.
    #
    if request.user.is_staff:
        qs = User.objects.order_by('username')
    else:
        qs = User.objects.filter(active = True).order_by('username')
        
    return object_list(request, qs, paginate_by = 20,
                       template_name = "users/index.html")

############################################################################
#
@login_required
def user_detail(request, username):
    """Simple display of a user object.
    """
    u = get_object_or_404(User, username = username)

    return object_detail(request, User.objects.all(), object_id = u.id)

############################################################################
#
@login_required
def user_update(request, username):
    """Allows editing of a user object. You must be staff or have
    'change_user' permission or be the user being updated (because of
    that last requirement we can not use the 'user_passes_test'
    decorator to control access to this view.
    """

    u = get_object_or_404(User, username = username)
    if not (request.user.is_staff or \
            request.user.has_perm("auth.change_user") or \
            username == request.user.username):
        return HttpResponseForbidden("You do not have the requisite "
                                     "permissions to edit this user.")

    UserForm = forms.models.form_for_instance(u)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            entry = form.save()
            msg_user(request.user, "User '%s' was updated." % entry.username)
            return HttpResponseRedirect(entry.get_absolute_url())

############################################################################
#
class DeleteForm(forms.Form):
    reason = forms.CharField(max_length = 128, blank = False)

############################################################################
#
@user_passes_test(lambda u: u.is_staff or u.has_perm("auth.delete_user"))
def user_deactivate(request, username):
    """Deactivates a user account (we do not allow deletions. You can
    just deactivate a user so that they can not log in anymore.
    """
    u = get_object_or_404(User, username = username)
