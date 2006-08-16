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
class WDBItem(models.Model):
    ItemID = models.IntegerField(db_index = True)
    EntrySize = models.IntegerField()
    ItemClassID = models.IntegerField()
    ItemSubClassID = models.IntegerField()
    Name1 = models.CharField(maxlength = 256, db_index = True)
    Name2 = models.CharField(maxlength = 256)
    Name3 = models.CharField(maxlength = 256)
    Name4 = models.CharField(maxlength = 256)
    ItemDisplayID = models.IntegerField()
    Quality = models.IntegerField()
    TypeFlags = models.CharField(maxlength = 32)
    BuyPrice = models.IntegerField()
    SellPrice = models.IntegerField()
    InventorySlot = models.IntegerField()
    ClassFlags = models.CharField(maxlength = 32)
    RaceFlags = models.CharField(maxlength = 32)
    ItemLevel = models.IntegerField()
    ReqLevel = models.IntegerField()
    ReqSkill = models.IntegerField()
    ReqSkillLevel = models.IntegerField()
    ReqSpell = models.IntegerField()
    ReqRank = models.IntegerField()
    ReqRank2 = models.IntegerField()
    ReqFaction = models.CharField(maxlength = 32)
    ReqFactionLvL = models.IntegerField()
    isUnique = models.IntegerField()
    StackAmount = models.IntegerField()
    ContainerSlots = models.IntegerField()
    Stat1 = models.IntegerField()
    Stat1Val = models.IntegerField()
    Stat2 = models.IntegerField()
    Stat2Val = models.IntegerField()
    Stat3 = models.IntegerField()
    Stat3Val = models.IntegerField()
    Stat4 = models.IntegerField()
    Stat4Val = models.IntegerField()
    Stat5 = models.IntegerField()
    Stat5Val = models.IntegerField()
    Stat6 = models.IntegerField()
    Stat6Val = models.IntegerField()
    Stat7 = models.IntegerField()
    Stat7Val = models.IntegerField()
    Stat8 = models.IntegerField()
    Stat8Val = models.IntegerField()
    Stat9 = models.IntegerField()
    Stat9Val = models.IntegerField()
    Stat10 = models.IntegerField()
    Stat10Val = models.IntegerField()
    Damage1Min = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage1Max = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage1Type = models.IntegerField()
    Damage2Min = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage2Max = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage2Type = models.IntegerField()
    Damage3Min = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage3Max = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage3Type = models.IntegerField()
    Damage4Min = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage4Max = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage4Type = models.IntegerField()
    Damage5Min = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage5Max = models.FloatField(max_digits = 12, decimal_places = 2)
    Damage5Type = models.IntegerField()
    PhysicalResist = models.IntegerField()
    HolyResist = models.IntegerField()
    FireResist = models.IntegerField()
    NatureResist = models.IntegerField()
    FrostResist = models.IntegerField()
    ShadowResist = models.IntegerField()
    ArcaneResist = models.IntegerField()
    WeaponDelay = models.IntegerField()
    AmmoType = models.IntegerField()
    RangeMod = models.FloatField(max_digits = 12, decimal_places = 2)
    Spell1ID = models.IntegerField()
    Spell1Trigger = models.IntegerField()
    Spell1Charges = models.IntegerField()
    Spell1Cooldown = models.IntegerField()
    Spell1Category = models.IntegerField()
    Spell1CategoryCooldown = models.IntegerField()
    Spell2ID = models.IntegerField()
    Spell2Trigger = models.IntegerField()
    Spell2Charges = models.IntegerField()
    Spell2Cooldown = models.IntegerField()
    Spell2Category = models.IntegerField()
    Spell2CategoryCooldown = models.IntegerField()
    Spell3ID = models.IntegerField()
    Spell3Trigger = models.IntegerField()
    Spell3Charges = models.IntegerField()
    Spell3Cooldown = models.IntegerField()
    Spell3Category = models.IntegerField()
    Spell3CategoryCooldown = models.IntegerField()
    Spell4ID = models.IntegerField()
    Spell4Trigger = models.IntegerField()
    Spell4Charges = models.IntegerField()
    Spell4Cooldown = models.IntegerField()
    Spell4Category = models.IntegerField()
    Spell4CategoryCooldown = models.IntegerField()
    Spell5ID = models.IntegerField()
    Spell5Trigger = models.IntegerField()
    Spell5Charges = models.IntegerField()
    Spell5Cooldown = models.IntegerField()
    Spell5Category = models.IntegerField()
    Spell5CategoryCooldown = models.IntegerField()
    BondID = models.IntegerField()
    Description = models.CharField(maxlength = 512)
    BookTextID = models.IntegerField()
    BookPages = models.IntegerField()
    BookStationaryID = models.IntegerField()
    BeginQuestID = models.IntegerField()
    reqLockPickSkill = models.IntegerField()
    Material = models.IntegerField()
    SheathID = models.IntegerField()
    RandomPropertyID = models.IntegerField()
    BlockValue = models.IntegerField()
    ItemSetID = models.IntegerField()
    Durability = models.IntegerField()
    ItemAreaID = models.IntegerField()
    ItemMapID = models.IntegerField()
    BagFamily = models.IntegerField()
    date_entered = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['Name1']

    #########################################################################
    #
    def __str__(self):
        return self.Name1

    #########################################################################
    #
    def get_absolute_url(self):
        return "/items/wdbitem/%d/" % self.id

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
