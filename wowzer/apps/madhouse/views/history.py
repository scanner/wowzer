#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for looking at historical auction data.
"""

# Utility routines..
#
from wowzer.apps.madhouse.helpers import average, mode
from wowzer.apps.items.templatetags.helpers import doit_ntg

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
def for_realm_for_faction(request, item_id, realm_id, faction_id):
    """This is the canonical application of madhouse. The ability to inspect
    the buyout & min bid history for a specific item (within a specific
    faction's auction house on a specific realm.)

    This view generates a list of lists, one entry for each unique time stamp
    that contains the timestamp, the average buyout (for one), the average
    min_bid (for one), the buyout mode, the buyout range, the min bid mode, and
    the minbid range, and the # of times that item.

    Finally we will also produce: for all the auctions listed the average
    buyout, average minbid, mode of the buyout and mode of the minbid.

    We limit the number of auctions we look up to be 100.
    """

    # Modify this to change how many auctions we look up
    #
    limit = 100
    # Get a number of auctions for the specific item within a realm & faction
    #
    auct_list = auctions.get_list(item_id__exact = item_id, buyout__gt = 0,
                                  realm_id__exact = realm_id,
                                  faction_id__exact = faction_id,
                                  limit = limit,
                                  order_by = ('-last_seen',))

    item = items.get_object(pk = item_id)
    realm = realms.get_object(pk = realm_id)
    faction = factions.get_object(pk = faction_id)
    
    # okay, now we create a dictionary. The key is the date. The value is
    # another dictionary with keys "buyout" and "minbid" - the values of those
    # keys is a list of the values at that date.
    #
    auct_data = {}
    all_buyouts = []
    all_minbids = []
    for auct in auct_list:
        last_seen = str(auct.last_seen)
        if not auct_data.has_key(last_seen):
            auct_data[last_seen] = {}
            auct_data[last_seen]['buyout'] = []
            auct_data[last_seen]['minbid'] = []
        auct_data[last_seen]['buyout'].append(auct.buyout_for_one)
        auct_data[last_seen]['minbid'].append(auct.min_bid_for_one)
        all_buyouts.append(auct.buyout_for_one)
        all_minbids.append(auct.min_bid_for_one)

    # Now we go through our dictionary and compute the average, mode, range,
    # and number of items for each element in the dictionary.
    #
    for date in auct_data.keys():
        auct_data[date]['buyout_avg'] = average(auct_data[date]['buyout'])
        auct_data[date]['minbid_avg'] = average(auct_data[date]['minbid'])
        auct_data[date]['buyout_mode'] = mode(auct_data[date]['buyout'])
        auct_data[date]['minbid_mode'] = mode(auct_data[date]['minbid'])

    total_buyout_average = average(all_buyouts)
    total_minbid_average = average(all_minbids)
    total_buyout_mode = mode(all_buyouts)
    total_minbid_mode = mode(all_minbids)

    # Now build up our list to pass the template. It is going to be a list of
    # dictionaries. The dictionary will have the values from our auct_data
    # dictionary. The list is built in date order.
    #
    auct_result = []
    for date in sorted(auct_data.keys()):
        datum = { 'date'         : date,
                  'num_auctions' : len(auct_data[date]['buyout']),
                  'buyout_avg'   : auct_data[date]['buyout_avg'],
                  'buyout_mode'  : auct_data[date]['buyout_mode'],
                  'buyout_range' : '%s-%s' % (doit_ntg(min(auct_data[date]['buyout']),"t"),
                                              doit_ntg(max(auct_data[date]['buyout']),"t")),
                  'minbid_avg'   : auct_data[date]['minbid_avg'],
                  'minbid_mode'  : auct_data[date]['minbid_mode'],
                  'minbid_range' : '%s-%s' % (doit_ntg(min(auct_data[date]['minbid']),"t"),
                                              doit_ntg(max(auct_data[date]['minbid']),"t")),
                  }
        auct_result.append(datum)

    t = template_loader.get_template('madhouse/history_realm_faction')
    c = Context(request, {
        'limit'          : limit,
        'item'           : item,
        'faction'        : faction,
        'realm'          : realm,
        'auction_result' : auct_result,
        'buyout_avg'     : total_buyout_average,
        'minbid_avg'     : total_minbid_average,
        'buyout_mode'    : total_buyout_mode,
        'minbid_mode'    : total_minbid_mode,
        'num_auctions'   : len(auct_list)
        })
    return HttpResponse(t.render(c))
        
