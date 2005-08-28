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
    """Do a simplistic search.. this just puts data up on the page letting
    people start their own searched.
    """
    limit = 100

    # Find all the items that a simple search. Eventually we should put in
    # pagination so that you can more easily browse the list of what is in the
    # db. Probably doing something like 'name__gt <last name on page>'
    #
    item_list = items.get_list(limit = 100, order_by = ('name',))

    t = template_loader.get_template('items/index')
    c = Context(request, {
        'limit'        : limit,
        'item_list'    : item_list,
        })
    return HttpResponse(t.render(c))

#############################################################################
#
def detail(request, item_id):
    """This displays the detail information for an item. Right now we have very
    little detail information. We provide links to the most recent auctions for
    this item on all realms & factions.
    """

    item = items.get_object(pk = item_id)
    auction_list = auctions.get_list(item__id__exact = item_id, limit = 20,
                                     order_by = ('-last_seen',))

    t = template_loader.get_template('items/detail')
    c = Context(request, {
        'item'         : item,
        'auction_list' : auction_list,
        })
    return HttpResponse(t.render(c))

#############################################################################
#
def search(request):
    """Handles a submission of a form letting people search for auctions by
    item name. We use the same template that was used by the index, too."""

    limit = 100

    # We should do some quoting to make sure this is a safe request
    #
    item_search = request.GET['item_search']

    # Find all the items that match our search. Eventually we should put in
    # pagination so that you can more easily browse the list of what is in the
    # db. Probably doing something like 'name__gt <last name on page>'
    #
    item_list = items.get_list(name__icontains = item_search, limit = 100,
                               order_by = ('name',))

    t = template_loader.get_template('items/index')
    c = Context(request, {
        'limit'        : limit,
        'item_list'    : item_list,
        'item_search'  : item_search,
        })
    return HttpResponse(t.render(c))

