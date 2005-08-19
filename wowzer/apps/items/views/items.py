#
# File: $Id$
#
"""This is file contains the code to support django views which are the pages
actually used by remote users.

This is the main set of views for items in WoW that we have gleaned from
auctioneer data (and eventually lootlink data I imagine)
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
    """Placeholder for something that lets you search our item db.
    """
    return HttpResponse("Nothing to see here yet. Move along.")

#############################################################################
#
def detail(request, item_id):
    """This displays the detail information for an item. Right now we have very
    little detail information. We provide links to the most recent auctions for
    this item on all realms & factions.
    """

    item = items.get_object(pk = item_id)
    auction_list = auctions.get_list(item_id__exact = item_id, limit = 20,
                                     order_by = ('-last_seen'))

    t = template_loader.get_template('items/detail')
    c = Context(request, {
        'item'         : item,
        'auction_list' : auction_list,
        })
    return HttpResponse(t.render(c))
