# File: $Id$
#
"""This module handles maintenance tasks for the madhouse app.
Other modules call in to this module to inform recurring tasks of new data.

We have a central module for this so we can have some persistent state for
things like threads that need to be around always doing things - cases like
processing uploaded Auctioneer data. We need to make sure that _only one_
thread is processing this information so we do not get duplicates.

This is done in this module by having it hold on to the thread and have the
messaging API other modules use to tell this thread to do things.
"""

import sys
import threading
from datetime import datetime

from django.models.toons import realms, toons, factions
from django.models.items import items, iteminstances
from django.models.madhouse import auctions, bids, uploaddatas

from wowzer.apps.toons.helpers import *
from wowzer.apps.items.helpers import *

import wowzer.apps.savedvarparser

#############################################################################
#
class AuctioneerImporter(threading.Thread):
    """This class is a thread that will go through the madhouse UploadData
    objects looking for objects that have been uploaded but not processed.

    It is important that this be the ONLY thread doing this so we do not get
    duplicate information inserted in to our database.

    When run we will check periodically to see if any data has been
    uploaded. When waiting we will sit on a semaphore that may be trigged by
    other processes in the server to start looking immediately for new data to
    import.
    """

    #########################################################################
    #
    def __init__(self):
        """This does not do very much except set up initial structures.
        The thread does not start running until the 'run()' method is invoked.
        """
        # Since we are a subclass of thread we are required by the thread class
        # to inoke its __init__ method before we do anything else.
        #
        threading.Thread.__init__(self)

        # Other modules need a way to notify this thread that new data needs to
        # be imported. We use a simple Event() for this.
        #
        self.new_data_event = threading.Event()

        # We keep a boolean called 'running' to use on checks to see if we
        # should exit this thread or not.
        #
        self.running = True

        # This class is what holds on to the single reference to our parser
        # object that can parse the declarations in a SavedVariables.lua
        # file in to python dictionaries.
        #
        self.parser = wowzer.apps.savedvarparser.ParseSavedVariables()

        print "Woot! New AuctioneerImporter Initialized!"
        return

    #########################################################################
    #
    def shutdown(self):
        """This will set the 'running' variable to False and signal this thread
        to wake up at which point it should notice that it is not running and
        exit.
        """
        self.running = False
        self.wakeup()
        
    #########################################################################
    #
    def wakeup(self):
        """This method is for other modules to call to wake up this thread and
        tell it to see if any new data needs to be imported.
        """

        self.new_data_event.set()

    #########################################################################
    #
    def split_auction_key(self, auction_key):
        """The auction key is a big colon separated string. We use 'split'
           for easy separation of the elements. There is one trick, however
           in that the 'name' can have a colon in it (eg: 'Recipe: Tasty
           Murlock Legs') However I think that is the only case.. so what we
           do is split the string apart. If the number of elements  we get
           is 8 then we can just assign them. If we get 9 then we need to
           recombine elements 3 and 4 back in to the name.
           
           item_class_id - the generic item class without properties. Aka:
           'Tundra Necklace'

           rand_prop_id - bonuses from the item: "of the Monkey"
           enchant_id - if it has an enchant.
           name - the derived name: "Tundra Necklace of the Monkey"
           count - ie: 20 sheets of silk
           minbid - minimum bid auction was set up for
           buyout - buyout price (0 if none set)
           unique id - instance of this item. If item does not have specific
                       instances (aka: sheets of silk, large brilliant shards)
                       this will be 0.
        """

        try:
            parts = auction_key.split(':')
            (item_class_id, rand_prop_id, enchant_id) = parts[:3]
            
            if len(parts) == 9:
                name = "%s:%s" % (parts[3], parts[4])
                (count, minbid, buyout, item_instance_id) = parts[5:]
            else:
                (name, count, minbid, buyout, item_instance_id) = parts[3:]
        except:
            print "Problem spitting auction key: '%s'" % auction_key
            raise
        
        item_class_id = int(item_class_id)
        rand_prop_id = int(rand_prop_id)
        enchant_id = int(enchant_id)
        count = int(count)
        minbid = int(minbid)
        buyout = int(buyout)
        item_instance_id = int(item_instance_id)

        return (item_class_id, rand_prop_id, enchant_id, name, count, minbid,
                buyout, item_instance_id)

    #########################################################################
    #
    def create_or_update_auction(self, auction_key, item, owner, realm,
                                 faction, buyout, minbid, count,
                                 last_seen, initial_seen, bid_amount):
        """This method does the actual work of creating an auction if it does
        not exist (as defined by the auction key). If it does exit then it
        updates the auction with when it was last seen.

        If we have a non-zero bid amount and no bid for this auction is the
        same as this amount then we also create a new bid for this auction.
        """
        # See if this auction already exists. NOTE: The owner.id makes
        # this auction unique among the realms & factions so we do not need
        # to include those in our auction search. This key is unique to
        # this auction.
        #
        try:
            auction = auctions.get_object(auction_key__exact = auction_key)

            # If we actually find this auction we need to update the
            # last_seen_time
            #
            auction.last_seen = last_seen
            auction.save()

            # If this auction has a non-zero bidamount then see if it has
            # any bids for the exact same amount. If it does then update
            # that bids last_seen_time. If it does not create a new bid.
            #
            if bid_amount > 0:
                bid_list = bids.get_list(auction_id__exact = auction.id,
                                         bid__exact = bid_amount)
                if len(bid_list) == 0:
                    # No bids at this price, make a new one.
                    #
                    bid = bids.Bid(item_id = item.id,
                                   auction_id = auction.id,
                                   initial_seen = initial_seen,
                                   last_seen = last_seen,
                                   bid = bid_amount,
                                   bid_for_one = int(bid_amount / count))
                else:
                    # At a given price there will be only one bid recorded
                    # so we can just get the first element of this list.
                    # Update its last seen to be the current time.
                    bid = bid_list[0]
                    bid.last_seen = last_seen

                bid.save()

        except auctions.AuctionDoesNotExist:
            # The auction we tried to find does not exist so we get to make
            # a new one.
            #
            auction = auctions.Auction(owner_id = owner.id,
                                       auction_key = auction_key,
                                       item_id = item.id,
                                       realm_id = realm.id,
                                       faction_id = faction.id,
                                       buyout = buyout,
                                       buyout_for_one = int(buyout / count),
                                       min_bid = minbid,
                                       min_bid_for_one = int(minbid / count),
                                       count = count,
                                       last_seen = last_seen,
                                       initial_seen = initial_seen)
            auction.save()

            # This auction did not exist. It will have no bids. Create a
            # new bid if the bid amount is not zero.
            #
            if bid_amount > 0:
                bid = bids.Bid(item_id = item.id, auction_id = auction.id,
                               initial_seen = initial_seen,
                               last_seen = last_seen,
                               bid = bid_amount,
                               bid_for_one = int(bid_amount / count))
                bid.save()
        return

    #########################################################################
    #
    def process_auction(self, auction_key, auction_data, realm, faction):
        """This processes the information from a single auction creating and
        updating objects in our db as necessary.
        """

        realm_faction = "%s-%s" % (realm.name, faction.name)
        last_seen = datetime.fromtimestamp(auction_data['lastSeenTime'])
        initial_seen = datetime.fromtimestamp(auction_data['initialSeenTime'])

        # Split out the individual datum from the auction_key created by
        # auctioneer.
        #
        (item_class_id, rand_prop_id, enchant_id, name, count, minbid,
         buyout, item_instance_id) = self.split_auction_key(auction_key)

        # Now although we have what Auctioneer uses as the unique identifier
        # for an auction I want something a little different. For example
        # having the item name be part of the key is a bit of useless
        # redundancy. The combination of item_class_id and rand_prop_id is just
        # basically the same information
        #
        # So perhaps (item_class_id, rand_prop_id, enchant_id, count, minbid,
        # buyout, item_instance_id, owner_id) would make a good key. Basically
        # subsituting out the name of the item with the id of the auction owner
        # (which may be 'unknown')
        #
        owner = find_or_create_toon(auction_data['owner'], realm, faction)

        my_auction_key = "%d:%d:%d:%d:%d:%d:%d:%d" % \
                         (item_class_id, rand_prop_id, enchant_id, count,
                          minbid, buyout, item_instance_id, owner.id)

        wow_id = "%d:%d:%d" % (item_class_id, rand_prop_id, enchant_id)

        # Now we have to pull out some item related info from the AuctionPrices
        # variable.
        auction_price_data = self.parser.variables['AuctionPrices']\
                             [realm_faction][wow_id]

        # If we have to create the item we are going to need to know its
        # category.
        #
        category_name = auction_price_data["category"]

        category = find_or_create_category(category_name)

        # See if we have this item in our item db or not.
        #
        item = find_or_create_item(item_class_id, rand_prop_id, enchant_id,
                                   name, category,
                                   auction_price_data["playerMade"])

        # If the item_instance_id is not zero then see if we have
        # an item instance created yet.
        #
        if item_instance_id != 0:
            item_instance = \
                          find_or_create_item_instance(item_instance_id,
                                                       item, realm)

        # And finally we create our update our auction object.
        #
        self.create_or_update_auction(my_auction_key, item, owner, realm,
                                      faction, buyout, minbid, count,
                                      last_seen, initial_seen,
                                      auction_data['bidamount'])
        # and that is it.
        #
        return
        
        
    #########################################################################
    #
    def process_uploaded_data(self, uploaddatum):
        """This method will read in the contents of the file that was uploaded
        to us from some user out in the world.

        We will then hand this data to our SavedVariables.lua parser.

        We then go through the parsed out data and fill in our wowzer data
        models for users, items, and auctions from this information.
        """

        print "Reading in Auctioneer variable declaration file %s" % \
              uploaddatum.filename
        f = open(uploaddatum.filename, 'r')
        data = f.read()
        f.close()
        print "Done reading in file. Searching for expressions we care about."
        
        self.parser.process(data)

        print "Done parsing in file. Next we update the db"

        # There are two variables we care about in this data: AHSnapshot is
        # what drives our data mining. It has the keys that we can then use to
        # look up additional info in AuctionPrices. AHSnapshot defines a
        # snapshot of the auction house at a given time.
        #
        # In AHSnapshot there is data for each faction's AH on each realm that
        # the player has scanned data on.
        #

        # If either of these varialbes is missing just return.. but we mark
        # this uploaddatum as processed? Should have added an error state to
        # these.
        if not self.parser.variables.has_key('AHSnapshot') or \
               not self.parser.variables.has_key('AuctionPrices'):
            print "Error! File %s was missing one of our Auctioneer " \
                  "variables" % uploaddatum.filename
            return
        
        for realm_faction in self.parser.variables['AHSnapshot'].keys():

            # Separate out the realm & faction names and look up (create if not
            # found) the realm & faction objects.
            #
            # NOTE: the find_or_create() functions are imported from the toons
            # & items apps.
            #
            (realm_name, faction_name) = realm_faction.split('-')
            realm = find_or_create_realm(realm_name)
            faction = find_or_create_faction(faction_name)

            # Loop through all the auction in this (realm, faction)'s auction
            # house.
            #
            for auction_key in \
                    self.parser.variables['AHSnapshot'][realm_faction].keys():

                # Now call a new method to actually process the data in this
                # specifc auction.
                #
                self.process_auction(auction_key,
                                     self.parser.variables['AHSnapshot']\
                                     [realm_faction][auction_key],
                                     realm, faction)
            

        # Now that we have processed all the auctions we need to make this
        # uploaddatum as processed and when we finished processing it.
        #
        uploaddatum.processed = True
        uploaddatum.when_processed = datetime.now()
        uploaddatum.save()
        return
    
    #########################################################################
    #
    def run(self):
        """This method is what starts our own thread of execution. What we do
        is wait for some other thread to signal us on the event
        self.new_data_event. If we get signaled, or we have waited for a
        certain amount of time we get all of the UploadData objects that have
        been defined. For any object that is not flagged as processed we load
        up the local file that is indicated, process it, mark it as processed,
        remove the UploadData object and then remove the file associated with
        it.

        After we have done that we go back to waiting for an event.
        """

        print "AuctioneerImporter is now running!"

        while True and self.running:
            # Wait for the event to be raised, or until it times out (in 14400
            # seconds, ie: 4 hours.)
            #
            self.new_data_event.wait(14400.0)
            self.new_data_event.clear()
            
            # If we are not running exit.
            if not self.running:
                return

            # Otherwise get the list of UploadData objects
            uploaddata = uploaddatas.get_list(processed__exact = False)

            print "We have %d UploadData to process" % len(uploaddata)
            for uploaddatum in uploaddata:
                print "Processing file: %s" % uploaddatum.filename
                self.process_uploaded_data(uploaddatum)

                # After we have processed a file we delete the datum
                # and then delete the file.
                #
                # NOTE: Currently we do not delete them..
                #
                #filename = uploaddatum.filename
                #uploaddatum.delete()
                #os.unlink(filename)

            print "Done processing uploaded data. Waiting for more."

            # And that is it.. we loop back to the top and we wait for more
            # events.
        return

#############################################################################
#
# When this module is read in this code down here will execute! This will
# create an auctioneer importer and start it up.
#
auctioneer_import_thread = AuctioneerImporter()
auctioneer_import_thread.start()



