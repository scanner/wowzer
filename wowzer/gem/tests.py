#
# File: $Id$
#
# The unit tests for the 'gem' application.
#
import unittest

# Import wowzer utilities.
#
from wowzer.savedvarparser import SavedVarParser

# Import django contrib models.
#
from django.contrib.auth.models import User

# Import the models we use in these unit tests.
#
from wowzer.gem.models import Event, ClassLimit, EventMember
from wowzer.toons.models import Toon, Guild, Realm

#############################################################################
#
class LoadAndParse(unittest.TestCase):

    #########################################################################
    #
    def setUp(self):
        f = open("data/GuildEventManager2.lua")
        self.s = SavedVarParser(open("data/GuildEventManager2.lua").read())
        self.s.parse()
        return
    
