#
# $Id$
#
# Description:
#   This module defines 'helper' routines for the items app.
#   The most basic thing is a set of functions that do "find_or_create()"
#   semantics for an object.
# 

import string
from django.models.items import *


#############################################################################
#
def find_or_create_category(name):
    try:
        category = categorys.get_object(name__exact = name)
    except categorys.CategoryDoesNotExist:
        category = categorys.Category(name = name)
        category.save()
    return category

#############################################################################
#
def find_or_create_item(item_class_id, rand_prop_id, enchant_id,
                        name, category, player_made):
    item_key = "%d:%d:%d" % (item_class_id, rand_prop_id, enchant_id)
    try:
        item = items.get_object(wow_id__exact = item_key)
    except items.ItemDoesNotExist:
        item = items.Item(wow_id = item_key, name = name,
                          player_made = player_made, category = category)
        item.save()
    return item

#############################################################################
#
def find_or_create_item_instance(item_instance_id, item, realm):

    try:
        item_instance = iteminstances.get_object(item_instance_id__exact = \
                                                 item_instance_id,
                                                 realm__id__exact = realm.id)
    except iteminstances.ItemInstanceDoesNotExist:
        item_instance = iteminstances.ItemInstance(item_instance_id = \
                                                   item_instance_id,
                                                   item = item,
                                                   realm = realm)
        item_instance.save()
    return item_instance

    
