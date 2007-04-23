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
def rlp_edit(request, obj_id, ct_id):
    """This is a generic view that is given an object id and the content type
    of that object.

    
    In the 'GET' form will look up the permissions that object can have, and
    then any row level permissions related to that object. These will be
    turned in to forms that are sent back to the browser for display.

    In the 'POST' form we will find out which action was taken - posting the
    set of entities that have a specific permission or adding some entity to
    a permission.
    """
    pass
