#
# File: $Id$
#
"""
GEM (Guild Event Manager) data views.
"""

# System imports
#
import sys
import pytz
from urlparse import urlparse
from datetime import datetime, timedelta

# Django imports
#
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
from wowzer.utils import msg_user, TZ_CHOICES
from wowzer.decorators import logged_in_or_basicauth
from wowzer.main.views import rlp_edit
from wowzer.main.decorators import breadcrumb
from wowzer.main.fields import UserOrGroupField

# RSS Feeds
#


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
from wowzer.gem.models import Event, GemDataJob
from wowzer.main.models import Breadcrumb, UserProfile

paginate_by = 20

############################################################################
#
@login_required
def index(request):
    """
    For now the index just redirects to the events index.
    """
    return HttpResponseRedirect("events/")

############################################################################
#
@login_required
@breadcrumb(name="GEM Event List Index")
def event_list(request):
    """
    Get the list of events, from newest to oldest

    XXX we should support sorting and filtering
    """
    if "showhidden" in request.GET:
        query_set = Event.objects.all().order_by('-created')
    else:
        query_set = Event.objects.filter(hidden = False).order_by('-created')
        
    return object_list(request, query_set, paginate_by = paginate_by,
                       template_name = "gem/event_list.html")

############################################################################
#
@login_required
def event_feed(request):
    return "Not implemented"

############################################################################
#
@login_required
@breadcrumb(name = "Event Tag Cloud")
def event_tag(request):
    return "Not implemented"

############################################################################
#
@login_required
@breadcrumb
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk = event_id)
#     if not request.user.has_perm("gem.view_event", object = event):
#         raise PermissionDenied
    Breadcrumb.rename_last(request,"GEM Event %s" % event.name)
    t = get_template("gem/event_detail.html")
    c = Context(request, {
        'event': event,
        })
    return HttpResponse(t.render(c))
    
############################################################################
#
@login_required
@permission_required('gem.change_event')
@breadcrumb
def event_update(request, event_id):
    event = get_object_or_404(Event, pk = event_id)
    if not request.user.has_perm("gem.change_event", object = event):
        raise PermissionDenied
    Breadcrumb.rename_last(request,"Update GEM Event %s" % event.name)
    EventForm = forms.models.form_for_instance(event)
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            entry = form.save()
            msg_user(request.user,
                     "Event '%s' updated." % entry.name)
            return HttpResponseRedirect(entry.get_absolute_url())
    else:
        form = EventForm()

    t = get_template("asforums/event_update.html")
    c = Context(request, { 'event' : event,
                           'form'  : form })
    return HttpResponse(t.render(c))

############################################################################
#
@login_required
@breadcrumb(name="GEM Data Job List")
def datajob_list(request):
    """
    Get the list of datajobs, from newest to oldest

    XXX we should support sorting and filtering
    """
    query_set = GemDataJob.objects.all().order_by('-created')
    return object_list(request, query_set, paginate_by = paginate_by,
                       template_name = "gem/datajob_list.html")

############################################################################
#
class UploadForm(forms.Form):
    data_file = forms.Field(widget = forms.FileInput,
                            label = "Data file",
                            help_text = "The GuildEventManager2.lua file "
                            "from your SavedVariables directory.")
    timezone = forms.CharField(max_length = 128, label = "Timezone",
                               help_text = "The timezone of the machine this "
                               "data file was generated on.",
                               widget = widgets.Select(choices=TZ_CHOICES))
                               
    
############################################################################
#
@login_required
@permission_required('gem.add_gemdatajob')
@breadcrumb(name="Submit a GEM Data File")
def datajob_submit(request):
    """
    Present and process a form for a user submitting a job to process.
    """
    if request.method == "POST":

        new_data = request.POST.copy()
        new_data.update(request.FILES)
        form = UploadForm(new_data)

        if form.is_valid():
            job = GemDataJob(submitter = request.user,
                             state = GemDataJob.PENDING)
            data_file = form.cleaned_data['data_file']
            job.save_data_file_file(data_file['filename'],
                                    data_file['content'])
            job.save()
            msg_user(request.user, "GEM data file submitted.")
            return HttpResponseRedirect(job.get_absolute_url())
    else:

        # Pre-fill in the tz field with something based on the user's
        # profile, if they have one.. otherwise use the settings
        # timezone.
        #
        try:
            profile = request.user.get_profile()
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user = request.user)
        tz = pytz.timezone(profile.timezone)
        form = UploadForm(data = {'timezone'  : profile.timezone,
                                  'data_file' : ''})

    t = get_template("gem/datajob_submit.html",)
    c = Context(request, {
        'form'       : form,
        })
    return HttpResponse(t.render(c))
        
############################################################################
#
@login_required
@breadcrumb
def datajob_detail(request, job_id):
    job = get_object_or_404(GemDataJob, pk = job_id)
    Breadcrumb.rename_last(request, str(job))
    t = get_template("gem/datajob_detail.html")
    c = Context(request, {
        'job'       : job,
        })
    return HttpResponse(t.render(c))
