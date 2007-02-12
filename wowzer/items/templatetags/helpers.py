#
# File: $Id$
#
"""This module contains helper routines that are useful to all of the
apps. This includes things like formating monetary values as strings with 'g',
's', and 'c' designations. Thus: 50000 is 5g0c0s
"""
from django import template

register = template.Library()

#############################################################################
#
def doit_ntg(value, arg):
    """num_to_gold the filter can handle ints, strings, floats and lists of
    those things. This is the sub-function that does the actual work in case
    of a list.
    """
    value = int(round(float(value)))

    (gold, rem) = divmod(value, 10000)
    (silver, copper) = divmod(rem, 100)

    arg = arg.lower()
    if arg[0] == "f":
        return "%dg%ds%dc" % (gold, silver, copper)

    # Otherwise we have to be a little trickier.
    #
    res = ""
    if gold > 0:
        res += "%dg" % gold
    if silver > 0:
        res += "%ds" % silver
    if copper > 0:
        res += "%dc" % copper

    return res

#############################################################################
#
@register.filter
def num_to_gold(value, arg = "t"):
    """This function will convert a raw value in to g/c/s standard used in
    World of Warcraft.

    The basic rule is: 100c to 1s, 100s to 1g.

    If 'arg' is true we will not display g/c/s if they are 0.
    """

    # If this is a list then we create a new list that is each individual
    # value converted. Otherwise we just conver the single value and pass it
    # back.
    if isinstance(value, list):
        result = []
        for val in value:
            result.append(doit_ntg(val, arg))
        return result
    else:
        return doit_ntg(value, arg)

#############################################################################
#
@register.filter
def name_to_thotturl(value):
    """Given an item name translate it in to a URL that should locate the item
    on thottbot.

    This means convert spaces to +, at least.. and I am sure some other things,
    and prefix it with 'http://www.thottbot.com/?s='
    """
    return 'http://www.thottbot.com/?s=' + urllib.quote_plus(value)
    
    
