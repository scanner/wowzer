#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for browsing and inspecting auctions by various means.

We offer a list of auctions by item, by user, or by specific auction key.
"""

# django specific imports
#
from django.core import template_loader
from django.core.extensions import DjangoContext as Context
from django.utils.httpwrappers import HttpResponse
from django.core.exceptions import Http404

# The data models from our apps:
#
from django.models.madhouse import *
from django.models.items import *
from django.models.toons import *

#############################################################################
#
def auction(request):
    return HttpResponse("Hello, world. You're at the madhouse auction index.")

#############################################################################
#
def auction_by_owner_name(request, owner_name):

    # Look up the owner id and just call auction_by_owner_id
    #
    return HttpResponse("Hello, world. You're at the madhouse auction by " \
                        "owner name page.")

#############################################################################
#
def auction_by_owner_id(request, owner_id):
    return HttpResponse("Hello, world. You're at the madhouse auction by " \
                        "owner id page.")

#############################################################################
#
def auction_by_item(request):
    """Displays a certain number of auctions that we have for a specific
    item. Nothing here about what auctions for an item we display. This is
    where you are going to want to do things like 'cheapest buyouts' or buyouts
    by time or something.
    """
    return HttpResponse("Hello, world. You're at the madhouse auction by " \
                        "item page.")

#############################################################################
#
def by_iteminstance(request):
    return HttpResponse("Hello, world. You're at the madhouse auction by " \
                        "item instance page.")

#############################################################################
#
def detail(request, auction_id):
    """Displays the details of a single auction."""

    try:
        auction = auctions.get_object(pk = auction_id)
    except auctions.AuctionDoesNotExist:
        raise Http404

    owner = auction.get_owner()
    item = auction.get_item()
    bids = auction.get_bid_list()
    realm = auction.get_realm()
    other_aucts = auctions.get_list(owner_id__exact = owner.id)
    t = template_loader.get_template('madhouse/detail')
    c = Context(request, {
        'auction': auction,
        'owner'  : owner,
        'realm'  : realm,
        'item'   : item,
        'bids'   : bids,
        'other_aucts' : other_aucts,
    })
    return HttpResponse(t.render(c))

