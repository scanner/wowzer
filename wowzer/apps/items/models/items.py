#
# $Id$
#
# Description:
#   This defines the model's for the "items" app in wowzer.
#   This app and its models represent items in wow, like the "Rod of Arcane
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

from wowzer.apps.toons.models.toons import Realm

#############################################################################
#
class Category(meta.Model):
    """According to the Auction House (and Auctioneer) items belong to a
    certain category. They may be armor, a weapon, a reagent, a food item, a
    container, or 'miscellaneous.'  We carry the distinction in to here because
    people are going to want to sort by the same categories the auction house
    does.
    """

    fields = (
        meta.CharField('name', maxlength = 128),
        meta.CharField('description', maxlength = 1024),
        )

    verbose_name_plural = 'categories'
    
    #########################################################################
    #
    def __repr__(self):
        return self.name

#############################################################################
#
class Item(meta.Model):
    """
    An item is defined by the combination of the 'item id', a 'random property'
    and an 'enchant.' These three things were chosen because they effect an
    items worth. A 'Gleaming Rod of the Eagle' is potentially worth a different
    amount from a 'Gleaming Rod of the Owl.' Both are worth more if they (could
    have) an enchant of any sort of them. The differences in price may be
    totally minimal but we think it is an important difference.

    NOTE: This is how Auctioneer defines an item.

    NOTE: If there are two 'Rod of Arcane Wrath' out there they point to
    the same object here. However, they may be represented by two
    distinct ItemInstance objects. For the most part people only care
    about the Item.

    NOTE: The biggest weakness here, that we get directly from Auctioneer, is
    that an enchant makes two items that would ordinarily be the same appear as
    different items. If we change something it is likely to be that.
    """

    fields = (
        # The 'wow-id' is a string that is three integers separated by colons.
        # Both auctioneer & lootlink represent an object in WoW using this
        # although they differ on the order of int's 2 & 3.
        #
        # Since we mostly care about auctioneer we are using its definitions.
        #
        # The ints are (in order): item id, random property, enchant
        #
        # XXX The name is derived from these fields to some extent. We could
        # argue for a data model that uses some of these numbers as a foreign
        # key and even have our name somewhat generated from that.
        #
        meta.CharField('wow_id', maxlength = 32, db_index = True),

        # The name of this kind of item, aka: "Rod of Arcane Wrath"
        #
        meta.CharField('name', maxlength = 512, db_index = True),

        meta.BooleanField('player_made'),

        # An item may only be in one category (armor, weapon, reagent)
        #
        meta.ForeignKey(Category),

        # XXX Maybe we should store foreign keys for the wow_id elements.
        #     But not sure if I want to look up how man "Foobar"'s there are.
        #     or how many have the mighty spirit enchant.
        #
        )

    #########################################################################
    #
    def __repr__(self):
        return self.name
    
#############################################################################
#
class ItemInstance(meta.Model):
    """This is a unique instance of a specific Item. If Aileen carries two
    Slicing Axes of Pain, with the +15 agility enchant we would represent this
    as two ItemInstance objects.

    The point of this class is because there are times when we care about a
    specific object. For example if an item was put up for auction twice, as
    opposed to two of the same kind of item. This way we can track items that
    have been bought and flipped again in the auction house for arbitrage like
    purposes.
    """

    fields = (
        meta.ForeignKey(Item),
        meta.ForeignKey(Realm),
        meta.IntegerField("item_instance_id", db_index = True),
        )
        
