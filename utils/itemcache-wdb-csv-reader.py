#!/usr/bin/env python
import sys
import os

sys.path.insert(0,'/home/scanner/src/wowzer')
os.environ['DJANGO_SETTINGS_MODULE'] = 'wowzer.settings'

from wowzer.items.models import *

############################################################################   
##
##
def main():
    if len(sys.argv) != 2:
        raise "You must supply one argument. The name of the itemcache.wdb csv file to load"

    input_file = open(sys.argv[1], 'r')
    for line in input_file:
        (ItemID,EntrySize,ItemClassID,ItemSubClassID,Name1,Name2,Name3,Name4,ItemDisplayID,Quality,TypeFlags,BuyPrice,SellPrice,InventorySlot,ClassFlags,RaceFlags,ItemLevel,ReqLevel,ReqSkill,ReqSkillLevel,ReqSpell,ReqRank,ReqRank2,ReqFaction,ReqFactionLvL,isUnique,StackAmount,ContainerSlots,Stat1,Stat1Val,Stat2,Stat2Val,Stat3,Stat3Val,Stat4,Stat4Val,Stat5,Stat5Val,Stat6,Stat6Val,Stat7,Stat7Val,Stat8,Stat8Val,Stat9,Stat9Val,Stat10,Stat10Val,Damage1Min,Damage1Max,Damage1Type,Damage2Min,Damage2Max,Damage2Type,Damage3Min,Damage3Max,Damage3Type,Damage4Min,Damage4Max,Damage4Type,Damage5Min,Damage5Max,Damage5Type,PhysicalResist,HolyResist,FireResist,NatureResist,FrostResist,ShadowResist,ArcaneResist,WeaponDelay,AmmoType,RangeMod,Spell1ID,Spell1Trigger,Spell1Charges,Spell1Cooldown,Spell1Category,Spell1CategoryCooldown,Spell2ID,Spell2Trigger,Spell2Charges,Spell2Cooldown,Spell2Category,Spell2CategoryCooldown,Spell3ID,Spell3Trigger,Spell3Charges,Spell3Cooldown,Spell3Category,Spell3CategoryCooldown,Spell4ID,Spell4Trigger,Spell4Charges,Spell4Cooldown,Spell4Category,Spell4CategoryCooldown,Spell5ID,Spell5Trigger,Spell5Charges,Spell5Cooldown,Spell5Category,Spell5CategoryCooldown,BondID,Description,BookTextID,BookPages,BookStationaryID,BeginQuestID,reqLockPickSkill,Material,SheathID,RandomPropertyID,BlockValue,ItemSetID,Durability,ItemAreaID,ItemMapID,BagFamily,ignore) = line.split(',')
        if Spell1Charges > sys.maxint:
            Spell1Charges = sys.maxint
        if Spell2Charges > sys.maxint:
            Spell2Charges = sys.maxint
        if Stat2Val > sys.maxint:
            Stat2Val = sys.maxint
        if Stat1Val > sys.maxint:
            Stat1Val = sys.maxint
        if RandomPropertyID > sys.maxint:
            RandomPropertyID = sys.maxint
        if WDBItem.objects.filter(ItemID = ItemID).count() == 0:
            print 'ItemID is %s' % str(ItemID)
            print 'EntrySize is %s' % str(EntrySize)
            print 'ItemClassID is %s' % str(ItemClassID)
            print 'ItemSubClassID is %s' % str(ItemSubClassID)
            print 'Name1 is %s' % str(Name1)
            print 'Name2 is %s' % str(Name2)
            print 'Name3 is %s' % str(Name3)
            print 'Name4 is %s' % str(Name4)
            print 'ItemDisplayID is %s' % str(ItemDisplayID)
            print 'Quality is %s' % str(Quality)
            print 'TypeFlags is %s' % str(TypeFlags)
            print 'BuyPrice is %s' % str(BuyPrice)
            print 'SellPrice is %s' % str(SellPrice)
            print 'InventorySlot is %s' % str(InventorySlot)
            print 'ClassFlags is %s' % str(ClassFlags)
            print 'RaceFlags is %s' % str(RaceFlags)
            print 'ItemLevel is %s' % str(ItemLevel)
            print 'ReqLevel is %s' % str(ReqLevel)
            print 'ReqSkill is %s' % str(ReqSkill)
            print 'ReqSkillLevel is %s' % str(ReqSkillLevel)
            print 'ReqSpell is %s' % str(ReqSpell)
            print 'ReqRank is %s' % str(ReqRank)
            print 'ReqRank2 is %s' % str(ReqRank2)
            print 'ReqFaction is %s' % str(ReqFaction)
            print 'ReqFactionLvL is %s' % str(ReqFactionLvL)
            print 'isUnique is %s' % str(isUnique)
            print 'StackAmount is %s' % str(StackAmount)
            print 'ContainerSlots is %s' % str(ContainerSlots)
            print 'Stat1 is %s' % str(Stat1)
            print 'Stat1Val is %s' % str(Stat1Val)
            print 'Stat2 is %s' % str(Stat2)
            print 'Stat2Val is %s' % str(Stat2Val)
            print 'Stat3 is %s' % str(Stat3)
            print 'Stat3Val is %s' % str(Stat3Val)
            print 'Stat4 is %s' % str(Stat4)
            print 'Stat4Val is %s' % str(Stat4Val)
            print 'Stat5 is %s' % str(Stat5)
            print 'Stat5Val is %s' % str(Stat5Val)
            print 'Stat6 is %s' % str(Stat6)
            print 'Stat6Val is %s' % str(Stat6Val)
            print 'Stat7 is %s' % str(Stat7)
            print 'Stat7Val is %s' % str(Stat7Val)
            print 'Stat8 is %s' % str(Stat8)
            print 'Stat8Val is %s' % str(Stat8Val)
            print 'Stat9 is %s' % str(Stat9)
            print 'Stat9Val is %s' % str(Stat9Val)
            print 'Stat10 is %s' % str(Stat10)
            print 'Stat10Val is %s' % str(Stat10Val)
            print 'Damage1Min is %s' % str(Damage1Min)
            print 'Damage1Max is %s' % str(Damage1Max)
            print 'Damage1Type is %s' % str(Damage1Type)
            print 'Damage2Min is %s' % str(Damage2Min)
            print 'Damage2Max is %s' % str(Damage2Max)
            print 'Damage2Type is %s' % str(Damage2Type)
            print 'Damage3Min is %s' % str(Damage3Min)
            print 'Damage3Max is %s' % str(Damage3Max)
            print 'Damage3Type is %s' % str(Damage3Type)
            print 'Damage4Min is %s' % str(Damage4Min)
            print 'Damage4Max is %s' % str(Damage4Max)
            print 'Damage4Type is %s' % str(Damage4Type)
            print 'Damage5Min is %s' % str(Damage5Min)
            print 'Damage5Max is %s' % str(Damage5Max)
            print 'Damage5Type is %s' % str(Damage5Type)
            print 'PhysicalResist is %s' % str(PhysicalResist)
            print 'HolyResist is %s' % str(HolyResist)
            print 'FireResist is %s' % str(FireResist)
            print 'NatureResist is %s' % str(NatureResist)
            print 'FrostResist is %s' % str(FrostResist)
            print 'ShadowResist is %s' % str(ShadowResist)
            print 'ArcaneResist is %s' % str(ArcaneResist)
            print 'WeaponDelay is %s' % str(WeaponDelay)
            print 'AmmoType is %s' % str(AmmoType)
            print 'RangeMod is %s' % str(RangeMod)
            print 'Spell1ID is %s' % str(Spell1ID)
            print 'Spell1Trigger is %s' % str(Spell1Trigger)
            print 'Spell1Charges is %s' % str(Spell1Charges)
            print 'Spell1Cooldown is %s' % str(Spell1Cooldown)
            print 'Spell1Category is %s' % str(Spell1Category)
            print 'Spell1CategoryCooldown is %s' % str(Spell1CategoryCooldown)
            print 'Spell2ID is %s' % str(Spell2ID)
            print 'Spell2Trigger is %s' % str(Spell2Trigger)
            print 'Spell2Charges is %s' % str(Spell2Charges)
            print 'Spell2Cooldown is %s' % str(Spell2Cooldown)
            print 'Spell2Category is %s' % str(Spell2Category)
            print 'Spell2CategoryCooldown is %s' % str(Spell2CategoryCooldown)
            print 'Spell3ID is %s' % str(Spell3ID)
            print 'Spell3Trigger is %s' % str(Spell3Trigger)
            print 'Spell3Charges is %s' % str(Spell3Charges)
            print 'Spell3Cooldown is %s' % str(Spell3Cooldown)
            print 'Spell3Category is %s' % str(Spell3Category)
            print 'Spell3CategoryCooldown is %s' % str(Spell3CategoryCooldown)
            print 'Spell4ID is %s' % str(Spell4ID)
            print 'Spell4Trigger is %s' % str(Spell4Trigger)
            print 'Spell4Charges is %s' % str(Spell4Charges)
            print 'Spell4Cooldown is %s' % str(Spell4Cooldown)
            print 'Spell4Category is %s' % str(Spell4Category)
            print 'Spell4CategoryCooldown is %s' % str(Spell4CategoryCooldown)
            print 'Spell5ID is %s' % str(Spell5ID)
            print 'Spell5Trigger is %s' % str(Spell5Trigger)
            print 'Spell5Charges is %s' % str(Spell5Charges)
            print 'Spell5Cooldown is %s' % str(Spell5Cooldown)
            print 'Spell5Category is %s' % str(Spell5Category)
            print 'Spell5CategoryCooldown is %s' % str(Spell5CategoryCooldown)
            print 'BondID is %s' % str(BondID)
            print 'Description is %s' % str(Description)
            print 'BookTextID is %s' % str(BookTextID)
            print 'BookPages is %s' % str(BookPages)
            print 'BookStationaryID is %s' % str(BookStationaryID)
            print 'BeginQuestID is %s' % str(BeginQuestID)
            print 'reqLockPickSkill is %s' % str(reqLockPickSkill)
            print 'Material is %s' % str(Material)
            print 'SheathID is %s' % str(SheathID)
            print 'RandomPropertyID is %s' % str(RandomPropertyID)
            print 'BlockValue is %s' % str(BlockValue)
            print 'ItemSetID is %s' % str(ItemSetID)
            print 'Durability is %s' % str(Durability)
            print 'ItemAreaID is %s' % str(ItemAreaID)
            print 'ItemMapID is %s' % str(ItemMapID)
            print 'BagFamily is %s' % str(BagFamily)
            wdbitem = WDBItem(ItemID = ItemID,
                              EntrySize = EntrySize,
                              ItemClassID = ItemClassID,
                              ItemSubClassID = ItemSubClassID,
                              Name1 = Name1,
                              Name2 = Name2,
                              Name3 = Name3,
                              Name4 = Name4,
                              ItemDisplayID = ItemDisplayID,
                              Quality = Quality,
                              TypeFlags = TypeFlags,
                              BuyPrice = BuyPrice,
                              SellPrice = SellPrice,
                              InventorySlot = InventorySlot,
                              ClassFlags = ClassFlags,
                              RaceFlags = RaceFlags,
                              ItemLevel = ItemLevel,
                              ReqLevel = ReqLevel,
                              ReqSkill = ReqSkill,
                              ReqSkillLevel = ReqSkillLevel,
                              ReqSpell = ReqSpell,
                              ReqRank = ReqRank,
                              ReqRank2 = ReqRank2,
                              ReqFaction = ReqFaction,
                              ReqFactionLvL = ReqFactionLvL,
                              isUnique = isUnique,
                              StackAmount = StackAmount,
                              ContainerSlots = ContainerSlots,
                              Stat1 = Stat1,
                              Stat1Val = Stat1Val,
                              Stat2 = Stat2,
                              Stat2Val = Stat2Val,
                              Stat3 = Stat3,
                              Stat3Val = Stat3Val,
                              Stat4 = Stat4,
                              Stat4Val = Stat4Val,
                              Stat5 = Stat5,
                              Stat5Val = Stat5Val,
                              Stat6 = Stat6,
                              Stat6Val = Stat6Val,
                              Stat7 = Stat7,
                              Stat7Val = Stat7Val,
                              Stat8 = Stat8,
                              Stat8Val = Stat8Val,
                              Stat9 = Stat9,
                              Stat9Val = Stat9Val,
                              Stat10 = Stat10,
                              Stat10Val = Stat10Val,
                              Damage1Min = Damage1Min,
                              Damage1Max = Damage1Max,
                              Damage1Type = Damage1Type,
                              Damage2Min = Damage2Min,
                              Damage2Max = Damage2Max,
                              Damage2Type = Damage2Type,
                              Damage3Min = Damage3Min,
                              Damage3Max = Damage3Max,
                              Damage3Type = Damage3Type,
                              Damage4Min = Damage4Min,
                              Damage4Max = Damage4Max,
                              Damage4Type = Damage4Type,
                              Damage5Min = Damage5Min,
                              Damage5Max = Damage5Max,
                              Damage5Type = Damage5Type,
                              PhysicalResist = PhysicalResist,
                              HolyResist = HolyResist,
                              FireResist = FireResist,
                              NatureResist = NatureResist,
                              FrostResist = FrostResist,
                              ShadowResist = ShadowResist,
                              ArcaneResist = ArcaneResist,
                              WeaponDelay = WeaponDelay,
                              AmmoType = AmmoType,
                              RangeMod = RangeMod,
                              Spell1ID = Spell1ID,
                              Spell1Trigger = Spell1Trigger,
                              Spell1Charges = Spell1Charges,
                              Spell1Cooldown = Spell1Cooldown,
                              Spell1Category = Spell1Category,
                              Spell1CategoryCooldown = Spell1CategoryCooldown,
                              Spell2ID = Spell2ID,
                              Spell2Trigger = Spell2Trigger,
                              Spell2Charges = Spell2Charges,
                              Spell2Cooldown = Spell2Cooldown,
                              Spell2Category = Spell2Category,
                              Spell2CategoryCooldown = Spell2CategoryCooldown,
                              Spell3ID = Spell3ID,
                              Spell3Trigger = Spell3Trigger,
                              Spell3Charges = Spell3Charges,
                              Spell3Cooldown = Spell3Cooldown,
                              Spell3Category = Spell3Category,
                              Spell3CategoryCooldown = Spell3CategoryCooldown,
                              Spell4ID = Spell4ID,
                              Spell4Trigger = Spell4Trigger,
                              Spell4Charges = Spell4Charges,
                              Spell4Cooldown = Spell4Cooldown,
                              Spell4Category = Spell4Category,
                              Spell4CategoryCooldown = Spell4CategoryCooldown,
                              Spell5ID = Spell5ID,
                              Spell5Trigger = Spell5Trigger,
                              Spell5Charges = Spell5Charges,
                              Spell5Cooldown = Spell5Cooldown,
                              Spell5Category = Spell5Category,
                              Spell5CategoryCooldown = Spell5CategoryCooldown,
                              BondID = BondID,
                              Description = Description,
                              BookTextID = BookTextID,
                              BookPages = BookPages,
                              BookStationaryID = BookStationaryID,
                              BeginQuestID = BeginQuestID,
                              reqLockPickSkill = reqLockPickSkill,
                              Material = Material,
                              SheathID = SheathID,
                              RandomPropertyID = RandomPropertyID,
                              BlockValue = BlockValue,
                              ItemSetID = ItemSetID,
                              Durability = Durability,
                              ItemAreaID = ItemAreaID,
                              ItemMapID = ItemMapID,
                              BagFamily = BagFamily)
            wdbitem.save()

###########
#
# The work starts here
#
if __name__ == "__main__":
    main()
#
#
###########
