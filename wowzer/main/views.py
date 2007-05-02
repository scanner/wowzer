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
from django.contrib.auth.models import RowLevelPermission, Permission
from django.contrib.auth.models import User, Group

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
    user_or_group = forms.ChoiceField(choices = (("user","User"),
                                                 ("group","Group")),
                                      label = "User or group", help_text = \
                                      "To set whether you are adding a "
                                      "permission for a user or a group.")
    name = forms.CharField(max_length = 30, initial = "Username to permit",
                           help_text = "Enter the name of the user or "
                           "group you wish to add a permission for.")
    permission = forms.IntegerField(help_text = "Select the permission you "
                                    "wish to add.")
    current_perms = forms.MultipleChoiceField(label = "Current Permissions",
                                              help_text = "Select the permissi"
                                              "ons you wish to remove from "
                                              "this object")

    # XXX Hm.. I think we need to write a custom constructor that is
    # XXX like "form_for_instance" except it uses a permission and the
    # XXX permission form above to construct the custom form we need for
    # XXX each permission.

#############################################################################
#
@login_required
def rlp_edit(request, obj, template = "main/rlp_generic_template.html",
             extra_context = {} ):
    """
    This is a generic helper view. It is passed an object that has row
    level permissions. We build a form based on the permissions
    present on GET and render it. If we are a post then we modify the
    permissions associated with the object according to what was in
    the form.
    """

    # XXX There should be an easy way to find the "change" permission
    # XXX for the object we were passed and do the check here to see
    # XXX if they have "change" permission on this object.
    # XXX basically we need to construct the "appname" . "change_<modelname lc>

    ct = ContentType.objects.get_for_model(obj)
    obj_perms = Permission.objects.select_related().filter(content_type = ct)
    rlps = RowLevelPermission.objects.filter(model_id = obj.id, model_ct = ct)
    rlp_choices = []
    for rlp in rlps:
        if rlp.negative:
            perm_name = "NOT %s" % rlp.permission.name
        else:
            perm_name = rlp.permission.name
        if isinstance(rlp.owner, Group):
            string = "Group: %s - %s" % (rlp.owner.name, perm_name)
        else:
            string = "User: %s - %s" % (rlp.owner.username, perm_name)
        rlp_choices.append((rlp.id, string))

    PermissionForm.base_fields['permission'].widget = \
               widgets.Select(choices = [(x.id, x.name) for x in obj_perms])
    PermissionForm.base_fields['current_perms'].widget = \
               widgets.CheckboxSelectMultiple(choices = rlp_choices)

    # If this is a post they are either removing a permission, or
    # adding a permission. We determine which by the  field
    # in the form submitted.
    #
    if request.method == "POST":
        form = PermissionForm(request.POST)
        if form.is_valid():
            if request.POST["submit"] == "Add Permission":
                print "Adding permission."
            elif request.POST["submit"] == "Remove Permissions":
                print "Remove permission."
            return HttpResponseRedirect(".")
    else:
        form = PermissionForm()

    t = get_template(template)
    c = Context(request, { 'object' : obj,
                           'form'   : form, })
    return HttpResponse(t.render(c))
