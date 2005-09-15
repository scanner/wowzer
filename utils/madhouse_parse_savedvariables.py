#!/usr/bin/env python

import os
import sys
import string
import lex
import yacc
import time

from datetime import datetime

# We need to import our models from django
#
from django.models.toons import realms, toons, factions
from django.models.items import items, iteminstances
from django.models.madhouse import auctions, bids, uploaddatas

from wowzer.apps.toons.helpers import *
from wowzer.apps.items.helpers import *

from wowzer.apps.savedvarparser import ParseSavedVariables
    
        
#############################################################################
#
class AuctioneerImporter(object):
    """This class is a thread that will go through the madhouse UploadData
    objects looking for objects that have been uploaded but not processed.

    When run we will check periodically to see if any data has been
    uploaded. We do this by looking for UploadData objects that have their
    'processed' flag set to False.
    """

    #########################################################################
    #
    def __init__(self):
        """This does not do very much except set up initial structures.
        The thread does not start running until the 'run()' method is invoked.
        """
        # We keep a boolean called 'running' to use on checks to see if we
        # should exit this thread or not. (if we were threaded, which we are no
        # longer. If we add that back this will be good to have around.
        #
        self.running = True

        sys.stderr.write("Woot! New AuctioneerImporter Initialized!\n")
        sys.stderr.flush()
        return

    #########################################################################
    #
##    def shutdown(self):
##        """This will set the 'running' variable to False and signal this 
##        thread to wake up at which point it should notice that it is not 
##        running and exit.
##        """
##        self.running = False
##        self.wakeup()
        
    #########################################################################
    #
##    def wakeup(self):
##        """This method is for other modules to call to wake up this
##        thread and tell it to see if any new data needs to be imported.
##        """

##        self.new_data_event.set()

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
            sys.stderr.write("Problem spitting auction key: '%s'\n" % \
                             auction_key)
            sys.stderr.flush()
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
                bid_list = auction.get_bid_list(bid__exact = bid_amount)
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
        self.create_or_update_auction(auction_key = my_auction_key,
                                      item = item, owner = owner,
                                      realm = realm, faction = faction,
                                      buyout = buyout, minbid = minbid,
                                      count = count, last_seen = last_seen,
                                      initial_seen = initial_seen,
                                      bid_amount = auction_data['bidamount'])
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

        sys.stderr.write("Reading in Auctioneer variable declaration " \
                         "file %s\n" %  os.path.basename(uploaddatum.filename))
        sys.stderr.flush()
        f = open(uploaddatum.filename, 'r')
        data = f.read()
        f.close()
        sys.stderr.write("Done reading in file. Searching for expressions " \
                         "we care about.\n")
        sys.stderr.flush()
        
        # This class is what holds on to the single reference to our parser
        # object that can parse the declarations in a SavedVariables.lua
        # file in to python dictionaries.
        #
        self.parser = ParseSavedVariables(output_dir = "/var/tmp/")

        self.parser.process(data)
        del data
        sys.stderr.write("Done parsing in file. Next we update the db\n")
        sys.stderr.flush()

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
            sys.stderr.write("Error! File %s was missing one of our " \
                             "Auctioneer  variables\n" % uploaddatum.filename)
            sys.stderr.flush()
            return
        
        for realm_faction in self.parser.variables['AHSnapshot'].keys():

            # One of the keys in the AHSnapshot dictionary is going to be the
            # 'version' of this db. Depending on the version we should do
            # different things. However, right now we only support version 1.0
            #
            if realm_faction == 'version':
                if self.parser.variables['AHSnapshot']['version'] != '1.0':
                    sys.stderr.write("Yow! AHSnapshot has version %s, " \
                                     "expected version 1.0" % \
                                     self.parser.variables['AHSnapshot']['version'])
                continue

            # Separate out the realm & faction names and look up (create if not
            # found) the realm & faction objects.
            #
            # NOTE: the find_or_create() functions are imported from the toons
            # & items apps.
            #
            (realm_name, faction_name) = realm_faction.split('-')
            realm = find_or_create_realm(realm_name)
            faction = find_or_create_faction(faction_name)

            print "Processing auction entries for %s on %s" % \
                  (realm.name, faction.name)
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
        self.parser = None
        del self.parser
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

        sys.stderr.write("AuctioneerImporter is now running!\n")
        sys.stderr.flush()

        while True and self.running:

            # Get the list of unprocessed UploadData objects
            uploaddata = uploaddatas.get_list(processed__exact = False)

            sys.stderr.write("We have %d UploadData to process\n" % \
                             len(uploaddata))
            sys.stderr.flush()
            for uploaddatum in uploaddata:
                sys.stderr.write("Starting processing file: %s\n" % \
                                 os.path.basename(uploaddatum.filename))
                sys.stderr.flush()
                self.process_uploaded_data(uploaddatum)

                sys.stderr.write("Finished processing file: %s\n" % \
                                 os.path.basename(uploaddatum.filename))
                sys.stderr.flush()

                # After we have processed a file we delete the datum
                # and then delete the file.
                #
                # NOTE: Currently we do not delete them..
                #
                #filename = uploaddatum.filename
                #uploaddatum.delete()
                #os.unlink(filename)

                # We also sleep for a short bit between files because we want
                # to be a little nicer to the system.
                #
                time.sleep(20)

            sys.stderr.write("Done processing uploaded data. Waiting for " \
                             "more.\n")
            sys.stderr.flush()

            # Now we sleep for a little while before checking our queue again.
            #
            time.sleep(5 * 60)
            #
            # And that is it.. we loop back to the top and we wait for more
            # events.
            
        return

############################################################################   
##
## And so begins the program that uses our lua variable declartion lexer and
## parser to parse out Auctioneer data and fill in the data models in wowzer
## that it relates to.
##
def main():
    auctioneer_import_thread = AuctioneerImporter()
    auctioneer_import_thread.run()

###########
#
# The work starts here
#
if __name__ == "__main__":
    main()
#
#
###########
