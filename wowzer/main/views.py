#
# File: $Id$
#
#
# The main views for the wowzer site. It is the place for glue that
# reaches over several apps and/or does not properly belong in any one app.
#

# System imports
#
import sys
from datetime import datetime, timedelta

# Django imports
#
from django import newforms as forms
from django.newforms import widgets
from django.shortcuts import get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

# Django provided contrib models.
#
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.modles import RowLevelPermission, Permission
from django.contrib.auth.modles import User, Group

# The data models from our apps:
#
from wowzer.toons.models import *
from wowzer.items.models import *

#############################################################################
#
def index(request):
    t = get_template('index.html')
    c = Context(request, {})
    return HttpResponse(t.render(c))

#############################################################################
#
class PermissionForm(forms.Form):
    permission = forms.CharField(max_length = 128,
                                 widget = widgets.HiddenInput())
    user_or_group = forms.ChoiceField(choices = ("user", "group"),
                                      label = "User or group", help_text = \
                                      "To set whether you are adding a "
                                      "permission for a user or a group.")
    name = forms.CharField(max_length = 30, initial = "Username to permit",
                           help_text = "Enter the name of the user or "
                           "group you wish to add a permission for.")
    permission = forms.IntegerField(help_text = "Select the permission you "
                                    "wish to add.")
    current_perms = forms.MulitpleChoiceField(label = "Current Permissions",
                                              help_text = "Select the permissi"
                                              "ons you wish to remove from "
                                              "this object")

    # XXX Hm.. I think we need to write a custom constructor that is
    # XXX like "form_for_instance" except it uses a permission and the
    # XXX permission form above to construct the custom form we need for
    # XXX each permission.

#############################################################################
#
def rlp_edit(request, obj, ct):
    """This is a generic view that is given an object and the content
    type of that object. It is meant to be wrapped by an actual view
    that looks up the object and its content type and validates that
    the user has permission to change the permissions on the object,

    
    In the 'GET' form will look up the permissions that object can have, and
    then any row level permissions related to that object. These will be
    turned in to forms that are sent back to the browser for display.

    In the 'POST' form we will find out which action was taken - posting the
    set of entities that have a specific permission or adding some entity to
    a permission.
    """

    obj_perms = Permission.objects.select_related().filter(content_type = ct)
    
    # If this is a post they are either removing a permission, or
    # adding a permission. We determine which by the permission field
    # in the form submitted.
    #
    if request.method == "POST":
        for perm in obj_perms:

            if request.POST["permission"] == perm.codename:
                form = PermissionForm
