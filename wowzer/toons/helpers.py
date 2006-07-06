#
# $Id$
#
# Description:
#   This module defines 'helper' routines for the toons app.
#   The most basic thing is a set of functions that do "find_or_create()"
#   semantics for an object.
# 

import string
from django.models.toons import *

#############################################################################
#
def find_or_create_realm(realm_name):
    """If we can not find the given realm by name then create a new realm with
    the given name. It will be assigned a realm type of 'unknown.' Presumably
    an admin can go in and fill it out later.
    """

    try:
        realm = realms.get_object(name__exact = realm_name)
    except realms.RealmDoesNotExist:
        realm = realms.Realm(name = realm_name)
        realm.save()
    return realm

#############################################################################
#
def find_or_create_faction(faction_name):
    """If we can not find the given faction, create it."""
    try:
        faction = factions.get_object(name__exact = faction_name)
    except factions.FactionDoesNotExist:
        faction = factions.Faction(name = faction_name)
        faction.save()
    return faction

#############################################################################
#
def find_or_create_toon(name, realm, faction):
    try:
        toon = toons.get_object(name__exact = name)
    except toons.ToonDoesNotExist:
        toon = toons.Toon(name = name, realm = realm,
                          faction = faction)
        toon.save()

    return toon

