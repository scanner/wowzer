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

results_per_page = 20

############################################################################
#
def index(request):
    """Simplistic top level index. Shows all forum collections and their
    forums
    """

    page_number = int(request.GET.get('page', 0))
    query_set = Forum.objects.all().order_by('collection','created_at')

    paginator = ObjectPaginator(query_set, results_per_page)

    try:
        object_list = paginator.get_page(page_number)
    except InvalidPage:
        if page_number == 0:
            object_list = []
        else:
            raise Http404

    if paginator.pages > 1:
        is_paginated = True
    else:
        is_paginated = False
        
    t = get_template('asforums/index.html')
    c = Context(request, {
#        'order_by'         : order_by,
        'is_paginated'     : is_paginated,
        'results_per_page' : results_per_page,
        'page'             : page_number + 1,
        'pages'            : paginator.pages,
        'hits'             : paginator.hits,
        'has_next'         : paginator.has_next_page(page_number),
        'has_previous'     : paginator.has_previous_page(page_number),
        'next'             : page_number + 2,
        'previous'         : page_number,
        'object_list'      : object_list,
        })
    return HttpResponse(t.render(c))


############################################################################
#
def forum_list(request):
    """A view that shows the forums that a person can see."""

    page_number = int(request.GET.get('page', 0))
    order_by = request.GET.get('order_by', 'created_at')
    if order_by not in ('name', 'slug', 'creator', 'created_at',
                        'last_post_at'):
        order_by = 'created_at'

    query_set = Forum.objects.all().order_by(order_by)
    paginator = ObjectPaginator(query_set, results_per_page)

    try:
        object_list = paginator.get_page(page_number)
    except InvalidPage:
        if page_number == 0:
            object_list = []
        else:
            raise Http404

    if paginator.pages > 1:
        is_paginated = True
    else:
        is_paginated = False
        
    t = get_template('asforums/forum_list.html')
    c = Context(request, {
        'order_by'         : order_by,
        'is_paginated'     : is_paginated,
        'results_per_page' : results_per_page,
        'page'             : page_number + 1,
        'pages'            : paginator.pages,
        'hits'             : paginator.hits,
        'has_next'         : paginator.has_next_page(page_number),
        'has_previous'     : paginator.has_previous_page(page_number),
        'next'             : page_number + 2,
        'previous'         : page_number,
        'object_list'      : object_list,
        })
    return HttpResponse(t.render(c))
