#
# File: $Id$
#
# The unit tests for the 'gem' application.
#
import unittest

# Django utilities
#
from django.test import TestCase

# Import wowzer utilities.
#
from wowzer.gem.gemdataloader import loaddata

# Import django contrib models.
#
from django.contrib.auth.models import User

# Import the models we use in these unit tests.
#
from wowzer.gem.models import Event, ClassRule, Member, GemDataJob
from wowzer.toons.models import Toon, Guild, Realm

#############################################################################
#
class LoadAndParse(unittest.TestCase):

    fixtures = ['playerclass']

    #########################################################################
    #
    def setUp(self):
        u1, ign = User.objects.get_or_create(username="test01")
        u1.set_password("test01")
        u1.save()

        u2, ign = User.objects.get_or_create(username="test02")
        u2.set_password("test02")
        u2.save()

        return

    #########################################################################
    #
    # Test loading our gem data files individually.
    #
    def testLoad01(self):
        u = User.objects.get(username='test01')
        g = GemDataJob(data_file = 'testdata/gem2-test-data-01.lua',
                       submitter = u, state = GemDataJob.PROCESSING,
                       timezone = "US/Pacific")
        g.save()
        loaddata(g)
        return

    def testLoad02(self):
        u = User.objects.get(username='test02')
        g = GemDataJob(data_file = 'testdata/gem2-test-data-02.lua',
                       submitter = u, state = GemDataJob.PROCESSING,
                       timezone = "US/Central")
        g.save()
        loaddata(g)
        return

    def testLoad03(self):
        u = User.objects.get(username='test01')
        g = GemDataJob(data_file = 'testdata/gem2-test-data-03.lua',
                       submitter = u, state = GemDataJob.PROCESSING,
                       timezone = "US/Pacific")
        g.save()
        loaddata(g)
        return

    #########################################################################
    #
    # Test loading all three gem data files to make sure data merges properly
    #
    def testLoadAll(self):
        self.testLoad01()
        self.testLoad02()
        self.testLoad03()
        return

    #########################################################################
    #
    # Start actually testing some views.
    #
#     def testView01(self):
#         # Load some test data.
#         #
#         self.testLoad01()

#         # Log in our test client.
#         self.client.login("test01", "test01")
#         response = self.client.get("/gem/events/")
#         assertTemplateUsed(response, "/gem/event_list.html")
#         response = self.client.get("/gem/events/1/")
#         assertTemplateUsed(response, "/gem/event_detail.html")
