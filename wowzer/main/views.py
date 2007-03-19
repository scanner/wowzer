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
from django import forms
from django.shortcuts import get_object_or_404
from django.core.paginator import ObjectPaginator, InvalidPage
from django.template.loader import get_template
from django.template import RequestContext as Context
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

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
