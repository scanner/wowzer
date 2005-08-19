#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
of the madhouse app. This module contains all the code for the views that goes
nowhere else really. Things like the index of the madhouse app.

This was initially setup just for testing.
"""

# django specific imports
#
from django.core import template_loader
from django.core.extensions import DjangoContext as Context
from django.utils.httpwrappers import HttpResponse

# The data models from our apps:
#
from django.models.madhouse import *
from django.models.items import *
from django.models.toons import *

#############################################################################
#
def index(request):
    """This will display the twenty last seen auctions.

    What I really want to do here is display the top twenty auctions that for
    that item have the lowest mid_bid_for_one price.
    """

    auction_list = auctions.get_list(limit = 30,
                                     order_by = ('-last_seen',))
    t = template_loader.get_template('madhouse/index')
    c = Context(request, {
        'auction_list' : auction_list,
        })
    return HttpResponse(t.render(c))
