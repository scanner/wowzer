#
# File: $Id$
#
"""
Custom fields.
"""

# Wowzer imports
#
from wowzer.main.widgets import UserOrGroupWidget

# Django imports
#
from django import newforms as forms
from django.newforms import fields
from django.newforms.util import ValidationError

# Django contrib model imports
#
from django.contrib.auth.models import User,Group


############################################################################
#
class UserOrGroupField(fields.MultiValueField):
    """
    A field that contains a choice of 'user' or 'group' and a field that
    is the name of a user or group (depending on the multiple choice field.)
    """
    #######################################################################
    #
    def __init__(self, required=True, widget=UserOrGroupWidget(),
                 label=None, initial=None, help_text=None):
        myfields = (
            fields.ChoiceField(choices=(('user', 'User'), ('group', 'Group'))),
            fields.CharField(max_length=30)
            )
        super(UserOrGroupField, self).__init__(myfields, required, widget,
                                               label, initial, help_text)

    #######################################################################
    #
    def compress(self, data_list):
        if data_list:
            return '%s,%s' % (data_list[0],data_list[1])
        return None

    #######################################################################
    #
    def clean(self, value):
        """
        I know that in general a multivaluefield will not need a clean
        method. However the UserOrGroupField needs to make sure that
        the name supplied matches an existing user or group (depending
        on the value of the choice field, ie: 'user' or 'group.'
        """

        # We call the MultiValueField's clean first. We will get back
        # the compressed data so we need to uncompress it first (which
        # we can do inline since we know its form) and then lookup the
        # User or Group in the database to make sure that they exist.
        #
        clean_data = super(UserOrGroupField, self).clean(value)
        user_or_group, name = clean_data.split(',')
        if user_or_group == 'user':
            if User.objects.filter(username = name).count() != 1:
                raise ValidationError('"%s" does not match any username' % \
                                      name)
        else:
            if Group.objects.filter(name = name).count() != 1:
                raise ValidationError('"%s" does not match any group' % name)
        return clean_data
