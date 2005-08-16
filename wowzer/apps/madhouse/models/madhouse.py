#
# $Id$
#
# Description:
#   This defines the model's for the "objects" app in wowzer.
#   This app and its models represent objects in wow, like the "Rod of Arcane
#   Wrath"
#
#   This model is not used for auction house tracking stuff. That is in the
#   madhouse app. That app uses these models.
#
#   Yes, this basically duplicates thottbot data. We needed the basic
#   information anyways to map to the things in the auction house.
#   There is a LOT more data on thott (and where we can we link to thott's
#   info)
#
from django.core import meta

from wowzer.apps.toons.models.toons import Realm, Toon, Faction
from wowzer.apps.items.models.items import Item, ItemInstance

#############################################################################
#
class Auction(meta.Model):
    """This object represents a unique auction for a specific item. If the same
    exact item is auctioned more than once there will be more than one
    auction. There will be one auction object every time a unique item is seen
    up for auction if any of the owner, buyout, or min bid are different.

    This is closely related to Auctioneer's sense of what an auction is too -
    entries in Auctioneer's AHSnapshot dictionary.

    The 'min_bid' is simply the lowest bid we have seen for an auction.
    """

    fields = (
        meta.ForeignKey(Toon, rel_name = "owner"),

        meta.ForeignKey(Item),         # We have both Item and ItemInstance
        meta.ForeignKey(ItemInstance,  # relations because even though Item is
                        blank = True,  # contained via ItemInstance we want to
                        null = True),  # be able to make it easy to say "Give
                                       # me all the auctions of LBS's that we
                                       # know about so I can plot their buyout
                                       # price over time.
                                       #
                                       # ItemInstance is here so we can say
                                       # 'how many times has this specific item
                                       # instance been auctioned? Of dubious
                                       # use. The idea is to track items that
                                       # get flipped a lot.
                                       #
                                       # NOTE: Some things like linen and such
                                       # have no instance id ever.

        meta.ForeignKey(Realm),
        meta.ForeignKey(Faction),
        meta.ForeignKey(Toon, rel_name = "high_bidder"),
        meta.ManyToManyField(Toon, rel_name = "bidders"), # Unordered relation
                                                          # of toons that have
                                                          # bidded on this
                                                          # auction
        meta.IntegerField("buyout"),         # 0 for no buyout
        meta.IntegerField("buyout_for_one"), # ditto

        meta.IntegerField("min_bid"),
        meta.IntegerField("min_bid_for_one"),

        meta.IntegerField("cur_bid"),        # 0 if not cur bid
        meta.IntegerField("cur_bid_for_one"),# ditto

        meta.IntegerField("count"),     # How many of this item (eg: 20xSilk)
                                        # Used to calc. the "for_one" prices

        meta.DateTimeField("last_seen"),
        meta.DateTimeField("initial_seen"),
        )

    #########################################################################
    #
    def __repr__(self):
        return "auction of %s by %s" % (self.get_item().name,
                                        self.get_toon().name)
    
#############################################################################
#
class Bid(meta.Model):
    """The Auction object captures the basic info about an auction - min bid,
    buyout, start time, last time we saw it, current bid.

    However one of the things we really want to know is: what is the bidding
    history of an item. Thus the bid object. It is really small.

    It has a bid price. The time the bid price was seen. Who saw the bid price,
    what auction this bid price is related to and what item this bid price is
    related to.

    Yes, the item relation is redundant, but it lets us say 'what is the
    bidding history of Silk' without having to get all the auctions first. Also
    Item's are across all realms - which is not good for bidding history.

    That leads us to an important note: we store the bid price and the 'bid
    price for one' so that you have a way of seeing bids on individual silk
    sheets.

    We may want to make bid's unique to a realm because they obviously are.
    We could do that by simply getting rid of the 'Item' relation and doing
    everything via Auction's. Somehow you need to say 'get me the bids of the
    auctions for this item on where the auctions are only on this realm.'

    Furthermore - since that is likely to be a common operation it should be a
    cheap operation.

    NOTE: We could do this by creating an ItemRealm object in addition to Item
    and add an additional relation for that.
    """

    fields = (
        meta.ForeignKey(Item),
        meta.ForeignKey(Auction),
        meta.DateTimeField("time"),
        meta.IntegerField("bid"),
        meta.IntegerField("bid_for_one"),
#        meta.ForeignKey(Toon), # Debatable - who made this bid. Moot since
#        auction does not give us this data.
        )

    ordering = ['time']
    
    #########################################################################
    #
    def __repr__(self):
        toon = self.get_toon()
        return "%d by %s of %s at %s" % (self.bid, toon.name, toon.realm,
                                         self.time)

