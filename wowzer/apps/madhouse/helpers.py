#
# File: $Id$
#
"""This module contains various helper functions used by the madhouse
app. Things like computing the average, mode, range of lists of numbers.
"""

#############################################################################
#
def average(values):
    """Given a list of numbers return the arithmetic mean."""
    try:
        return sum(values) / len(values)
    except: ZeroDivisionError:
        return 0

#############################################################################
#
def mode(values, size = 2):
    """Given a list of values determine the mode. The mode is simply
    the number that appears the most often in the set. A set can have
    more than one mode. This function returns a list. The size is the
    maximum # of elements in the mode list we allow."""

    mode_dict = {}
    for val in values:
        if mode_dict.has_key(val):
            mode_dict[val] += 1
        else:
            mode_dict[val] = 1

    mode = []
    max = 0.0
    for val in mode_dict.keys():
        if mode_dict[val] > max:
            max = mode_dict[val]
    for val in mode_dict.keys():
        if mode_dict[val] == max:
            mode.append(val)

    mode.sort(reverse = True)
    if len(mode) > size:
        mode = mode[:size]
    return mode

    
