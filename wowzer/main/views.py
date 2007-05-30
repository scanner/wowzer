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

# Wowzer imports
#
from wowzer.utils import msg_user
from wowzer.main.fields import UserOrGroupField
from wowzer.main.decorators import breadcrumb

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
@breadcrumb(name = "Top")
def index(request):
    t = get_template('index.html')
    c = Context(request, {})
    return HttpResponse(t.render(c))

#############################################################################
#
class AddPermissionForm(forms.Form):
    user_or_group = UserOrGroupField(label = "User or Group",
                                     help_text = "The user or group to grant "
                                     "the permission priveleges to.")
    permission = forms.IntegerField(help_text = "Select the permission you "
                                    "wish to add.")
    negative = forms.BooleanField(initial = False, required = False)

#############################################################################
#
class RemPermissionForm(forms.Form):
    # We have separate user's and group's listing just
    # to keep them separate in the UI. We think it makes the UI a bit
    # more clear.
    #
    groups = forms.MultipleChoiceField(label = "Groups", required = False)
    users = forms.MultipleChoiceField(label = "Users", required = False)

#############################################################################
#
@login_required
@breadcrumb
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
    rlp_choices_group = []
    rlp_choices_users = []
    for rlp in rlps:
        if rlp.negative:
            perm_name = "NOT %s" % rlp.permission.name
        else:
            perm_name = rlp.permission.name
        if isinstance(rlp.owner, Group):
            string = "%s - %s" % (rlp.owner.name, perm_name)
            rlp_choices_group.append((rlp.id, string))
        else:
            string = "%s - %s" % (rlp.owner.username, perm_name)
            rlp_choices_users.append((rlp.id, string))

    # The row level permissions that can be added to this object. This is all
    # of the permissions that the object has, minus the 'add_' permission.
    #
    add_codename = 'add_%s' % ct.model
    AddPermissionForm.base_fields['permission'].widget = \
                      widgets.Select(choices = [(x.id, x.name) \
                                                for x in obj_perms \
                                                if x.codename != add_codename])
    RemPermissionForm.base_fields['groups'].choices = rlp_choices_group
    RemPermissionForm.base_fields['groups'].widget = \
               widgets.CheckboxSelectMultiple(choices = rlp_choices_group)
    RemPermissionForm.base_fields['users'].choices = rlp_choices_users
    RemPermissionForm.base_fields['users'].widget = \
               widgets.CheckboxSelectMultiple(choices = rlp_choices_users)

    # If this is a post they are either removing a permission, or
    # adding a permission. We determine which by the  field
    # in the form submitted.
    #
    if request.method == "POST":
        if request.POST["submit"] == "Add Permission":
            add_form = AddPermissionForm(request.POST)
            if add_form.is_valid():
                u_or_g, name = add_form.clean_data['user_or_group'].split(',')
                if u_or_g == "user":
                    e = User.objects.get(username=name)
                else:
                    e = Group.objects.get(name=name)
                p_id = add_form.clean_data['permission']
                p = Permission.objects.get(pk = p_id)
                RowLevelPermission.objects.create_row_level_permission(\
                                  obj, e, p, \
                                  negative = add_form.clean_data['negative'])
                msg_user(request.user, "Added '%s' permission to '%s' for %s" \
                                       " %s" % (p.name, obj, u_or_g, name))
                return HttpResponseRedirect(".")
        else:
            add_form = AddPermissionForm()

        # Loop through the list of rlp's in the 'users' and 'groups'
        # multi-selects.
        #
        if request.POST["submit"] == "Remove Permissions":
            rem_form = RemPermissionForm(request.POST)
            if rem_form.is_valid():
                for rlp_id in rem_form.clean_data['groups']:
                    try:
                        rlp = RowLevelPermission.objects.get(pk = rlp_id)
                        rlp.delete()
                        msg_user(request.user, "Removed '%s' permission " \
                                 "from group %s" % (rlp.permission.name,
                                                    rlp.owner.name))
                    except RowLevelPermission.DoesNotExist:
                        pass
                for rlp_id in rem_form.clean_data['users']:
                    try:
                        rlp = RowLevelPermission.objects.get(pk = rlp_id)
                        rlp.delete()
                        msg_user(request.user, "Removed '%s' permission " \
                                 "for '%s'" % (rlp.permission.name,
                                               rlp.owner))
                    except RowLevelPermission.DoesNotExist:
                        pass
                return HttpResponseRedirect(".")
        else:
            rem_form = RemPermissionForm()
    else:
        add_form = AddPermissionForm()
        rem_form = RemPermissionForm()

    t = get_template(template)
    c = Context(request, { 'object'   : obj,
                           'add_form' : add_form,
                           'rem_form' : rem_form })
    return HttpResponse(t.render(c))
