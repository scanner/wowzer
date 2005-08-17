#
# $Id$
#
# Description:
#   This defines the model's for tracking auction house pricing and such.
#
from django.core import meta
from django.models.auth import User

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
        meta.ForeignKey(Toon, name = "owner_id", rel_name = "owner"),
        meta.CharField("auction_key", maxlength = 128, db_index = True),

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
        meta.IntegerField("buyout", db_index = True),         # 0 for no buyout
        meta.IntegerField("buyout_for_one", db_index = True), # ditto

        meta.IntegerField("min_bid", db_index = True),
        meta.IntegerField("min_bid_for_one", db_index = True),

        meta.IntegerField("count"),     # How many of this item (eg: 20xSilk)
                                        # Used to calc. the "for_one" prices

        meta.DateTimeField("last_seen"),
        meta.DateTimeField("initial_seen"),
        )

    ordering = ['initial_seen']

    #########################################################################
    #
    def __repr__(self):
        return "auction of %s by %s" % (self.get_item().name,
                                        self.get_owner().name)
    
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
        meta.ForeignKey(Item, db_index = True),
        meta.ForeignKey(Auction, db_index = True),
        meta.DateTimeField("initial_seen"),
        meta.DateTimeField("last_seen"),
        meta.IntegerField("bid", db_index = True),
        meta.IntegerField("bid_for_one"),
        )

    ordering = ['initial_seen', 'last_seen']
    
    #########################################################################
    #
    def __repr__(self):
        return "%d last seen at: %s" % (self.bid, self.last_seen)

#############################################################################
#
class UploadData(meta.Model):
    """This class is used to hold a pointer to an uploaded file from one of our
    remote upload clients.

    The basic process is a remote client is expected to snip out of a
    SavedVariables.lua file the data we care about for madhouse. They then
    compress and upload this file to our server.

    This causes an UploadData object to be created. Some other process will
    then process all of the UploadData objects parsing out the lua variable
    declrations and filling in the madhouse structures based on this
    information.
    """

    fields = (
        meta.FileField('filename', maxlength = 1024,
                       upload_to = "/var/tmp/wowzer-uploads/madhouse/" \
                       "auction-data-%Y.%m.%d-%H:%M:%S"),
        meta.DateTimeField('uploaded_at'),
        meta.BooleanField('processed', default = False),
        meta.DateTimeField('when_processed', null = True, blank = True),
        meta.ForeignKey(User, null = True, blank = True),
        )

    ordering = ['uploaded_at']

    #########################################################################
    #
    def __repr__(self):
        return self.filename

