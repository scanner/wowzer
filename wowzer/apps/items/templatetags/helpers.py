#
# File: $Id$
#
"""This module contains helper routines that are useful to all of the
apps. This includes things like formating monetary values as strings with 'g',
's', and 'c' designations. Thus: 50000 is 5g0c0s
"""

import django.core.template

#############################################################################
#
def num_to_gold(value, arg):
    """This function will convert a raw value in to g/c/s standard used in
    World of Warcraft.

    The basic rule is: 100c to 1s, 100s to 1g.

    If 'compact' is true we will not display g/c/s if they are 0.
    """

    # First we need to round up this number to a solid integer.
    #
    value = int(round(float(value)))

    (gold, rem) = divmod(value, 10000)
    (silver, copper) = divmod(rem, 100)

    compact = compact.lower()
    if compact[0] == "f":
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

# Now we have this function to make it truly useful we register it as a filter
# thus it can be used in our html template files directly as <9000>|num_to_gold
#
django.core.template.register_filter('num_to_gold', num_to_gold, True)
