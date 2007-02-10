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
from wowzer.asforums.models import *

############################################################################
#
def index(request):

############################################################################
#
def forum_list(request):
    """A view that shows the forums that a person can see."""

    page_number = int(request.GET.get('page', 0))
    
