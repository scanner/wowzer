#
# File: $Id$
#
"""
This module defines some custom widgets.
"""

from django import newforms as forms
from django.newforms import widgets

############################################################################
#
class UserOrGroupWidget(widgets.MultiWidget):
    """
    A multiwidget composed of a user/group selector, and a text field
    for entering the name of a user or group.
    """

    #######################################################################
    #
    def __init__(self, attrs=None):
        mywidgets = (
            widgets.Select(choices=(('user', 'User'),('group', 'Group'))),
            widgets.TextInput()
            )
        super(UserOrGroupWidget, self).__init__(mywidgets, attrs)

    #######################################################################
    #
    def decompress(self, value):
        if value:
            return value.split(",")
        return ['', '']
    
