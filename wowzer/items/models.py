#
# Models for wowzer 'items' app
#
# $Id$
#

# Django imports
#
from django.db import models

# Wowzer imports
#
from wowzer.toons.models import Realm

#############################################################################
#
class Category(models.Model):
    """According to the Auction House (and Auctioneer) items belong to a
    certain category. They may be armor, a weapon, a reagent, a food item, a
    container, or 'miscellaneous.'  We carry the distinction in to here because
    people are going to want to sort by the same categories the auction house
    does.
    """

    name = models.CharField(maxlength = 128)
    description = models.CharField(maxlength = 1024)
    
    #########################################################################
    #
    def __str__(self):
        return self.name

#############################################################################
#
class Item(models.Model):
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
    wow_id = models.CharField(maxlength = 32, db_index = True)

    # The name of this kind of item, aka: "Rod of Arcane Wrath"
    #
    name = models.CharField(maxlength = 512, db_index = True)

    player_made = models.BooleanField()

    # An item may only be in one category (armor, weapon, reagent)
    #
    category = models.ForeignKey(Category)

    # XXX Maybe we should store foreign keys for the wow_id elements.
    #     But not sure if I want to look up how man "Foobar"'s there are.
    #     or how many have the mighty spirit enchant.
    #

    #########################################################################
    #
    def __str__(self):
        return self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/items/detail/%d/" % self.id
    
#############################################################################
#
class ItemInstance(models.Model):
    """This is a unique instance of a specific Item. If Aileen carries two
    Slicing Axes of Pain, with the +15 agility enchant we would represent this
    as two ItemInstance objects.

    The point of this class is because there are times when we care about a
    specific object. For example if an item was put up for auction twice, as
    opposed to two of the same kind of item. This way we can track items that
    have been bought and flipped again in the auction house for arbitrage like
    purposes.
    """

    item = models.ForeignKey(Item)
    realm = models.ForeignKey(Realm)
    item_instance_id = models.IntegerField(db_index = True)

    #########################################################################
    #
    def __str__(self):
        return self.get_item().name
