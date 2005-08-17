#!/usr/bin/env python

import os
import sys
import string
import lex
import yacc
import re

from datetime import datetime

# We need to import our models from django
#
from django.models.toons import realms, toons, factions
from django.models.items import items, iteminstances
from django.models.madhouse import auctions, bids
from wowzer.apps.toons.helpers import *
from wowzer.apps.items.helpers import *
#from wowzer.apps.madhouse.helpers import *

#############################################################################
#
# Our class for parsing lua files that only have variable declarations from
# constants.
#
# Way slow.
class ParseSavedVariables:
    """This class uses the PLY lexx/yacc tools to define a gramar that will
    read in a SavedVariables.lua file and return a dictionary that has defined
    as keys the variable declarations from the SavedVariables.lua. Lua hashes
    are turned in to python dictionaries. We have support for strings, ints,
    floats, and booleans.
    """
    tokens = (
        'STRING', 'INTEGER', 'FLOAT', 'LBRACE', 'RBRACE', 'LBRACK', 'RBRACK',
        'ASSIGN', 'COMMA', 'BOOLEAN', 'NAME', 'BIGNUM'
        )

    # Actual token definitions as regular expressions
    #
    t_STRING = r'\"([^\\\n]|(\\\n)|(\\.))*?\"'
    t_NAME   = r'[a-zA-Z][a-zA-Z0-9_]*'
    t_ASSIGN = r'='
    t_INTEGER = r'[0-9]+'
    t_FLOAT  = r'[0-9]+\.[0-9]+'
    t_BIGNUM = r'[0-9]+(\.[0-9]+)?e\+[0-9]+'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACK = r'\['
    t_RBRACK = r'\]'
    t_COMMA  = r','
    t_BOOLEAN = r'([Tt][Rr][Uu][Ee]|[Ff][Aa][Ll][Ss][Ee])'


    # We ignore white space
    #
    t_ignore = ' \t'

    # We count newlines so we can report parsing errors
    #
    def t_newline(self, t):
        r'\n+'
        t.lineno += t.value.count("\n")

    def t_error(self, t):
        print "Illegal character '%s' at line: %d" % (t.value[0], t.lineno)
        t.skip(1)

    ##
    ## And so ends the lexer
    ##
    #########################################################################
    #########################################################################
    ##
    ## And so begins the parser
    ##
    def p_declarations(self, p):
        '''declarations : declaration
                        | declaration declarations'''
        return

    # Here is where variables are declared. We only want to really store
    # declarations of variables that we actually care about so if the NAME is
    # not one that we care about we just skip it. Otherwise, we assign a key in
    # our variables dictionary to be the value we have parsed out for this
    # declaration.
    #
    def p_declaration(self, p):
        '''declaration : NAME ASSIGN value'''
        self.variables[p[1]] = p[3]
        return

    def p_value(self, p):
        '''value : dictionary
                 | scalar'''
        p[0] = p[1]
        return

    def p_scalar(self, p):
        '''scalar : string
                  | integer
                  | float
                  | bignum
                  | boolean'''
        p[0] = p[1]
        return

    def p_string(self, p):
        '''string : STRING'''
        p[0] = p[1][1:-1]
        return

    def p_integer(self, p):
        '''integer : INTEGER'''
        p[0] = int(p[1])
        return

    def p_float(self, p):
        '''float : FLOAT'''
        p[0] = float(p[1])
        return

    # Going to force the scientific notation bigums in to ints because that is
    # the only way they are used in the SavedVariables.lua file
    #
    def p_bignum(self, p):
        '''bignum : BIGNUM'''
        p[0] = int(float(p[1]))
        return

    def p_boolean(self, p):
        '''boolean : BOOLEAN'''
        if string.lower(p[1]) == "true":
            p[0] = True
        else:
            p[0] = False
        return
    
    def p_dictionary(self, p):
        '''dictionary : LBRACE keyvalues RBRACE
                      | LBRACE RBRACE
        '''
        if len(p) == 4:
            p[0] = dict(p[2])
        elif len(p) == 3:
            p[0] = {}
        return

    def p_keyvalues(self, p):
        '''keyvalues : keyvalue
                     | keyvalue COMMA
                     | keyvalue COMMA keyvalues'''
        if len(p) == 2 or len(p) == 3:
            p[0] = [ p[1] ]
        elif len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        return

    def p_keyvalue(self, p):
        '''keyvalue : LBRACK scalar RBRACK ASSIGN value'''
        p[0] = ( p[2], p[5] )
        return

    def p_error(self, p):
        while True:
            tok = yacc.token()
            if not tok or tok.type == 'RBRACE':
                break
        yacc.restart()

    ##
    ## And so ends the parser declaration
    ##
    ########################################################################

    ########################################################################
    #
    def __init__(self):
        """This will initialize our lexer and parser and define the dictionary
        used to hold the results of our parsing.
        """
        self.variables = {}
        self.lexer = lex.lex(module = self)
        self.parser = yacc.yacc(module = self)
        # self.parser = yacc.yacc(module = self, write_tables = 0)

        self.re_endbrace = re.compile(r'^}', re.MULTILINE)

        return

    ######################################################################
    #
    def process(self, data, varnames):
        """We are handed a string which contains the entire lua script we wish
        to parse. We are also given a list of names of variables whose
        declaration we wish to extract from the script and define as elements
        in the python dictionary self.variables.
        """
        for varname in varnames:
            re_start = re.compile("^%s" % varname, re.MULTILINE)
            try:
                start = re_start.search(data).start()
                end = self.re_endbrace.search(data, start).end()
                area = data[start:end]
                self.lexer.input(area)
                self.parser.parse()
            except:
                raise
    
        
############################################################################   
##
## And so begins the program that uses our lua variable declartion lexer and
## parser to parse out Auctioneer data and fill in the data models in wowzer
## that it relates to.
##
def main():
    f = open(sys.argv[1], "r")
    data = f.read()
    f.close()
    print "Done reading in file. Searching for expressions we care about."
    
    lua_proc = ParseSavedVariables()
    lua_proc.process(data, ['AHSnapshot', 'AuctionPrices'])

    # AHSnapshot is what drives our data mining. It has the keys that we can
    # then use to look up additional info in AuctionPrices. AHSnapshot defines
    # a snapshot of the auction house at a given time.
    #
    # In AHSnapshot there is data for each faction's AH on each realm that the
    # player has scanned data on.
    #

    for realm_faction in lua_proc.variables['AHSnapshot'].keys():

        # Separate out the realm & faction names and look up (create if not
        # found) the realm & faction objects.
        #
        (realm_name, faction_name) = realm_faction.split('-')
        realm = find_or_create_realm(realm_name)
        faction = find_or_create_faction(faction_name)

        # Loop through all the auction in this (realm, faction)'s auction
        # house.
        #
        for auction_key in \
                lua_proc.variables['AHSnapshot'][realm_faction].keys():

            auction_data = lua_proc.variables['AHSnapshot']\
                           [realm_faction][auction_key]

            last_seen = datetime.fromtimestamp(auction_data['lastSeenTime'])
            initial_seen = datetime.fromtimestamp(auction_data['initialSeenTime'])

            # The auction key is a big colon separated string. We use 'split'
            # for easy separation of the elements. There is one trick, however
            # in that the 'name' can have a colon in it (eg: "Recipe: Tasty
            # Murlock Legs") However I think that is the only case.. so what we
            # do is split the string apart. If the number of elements  we get
            # is 8 then we can just assign them. If we get 9 then we need to
            # recombine elements 3 and 4 back in to the name.
            #
            # item_class_id - the generic item class without properties. Aka:
            # "Tundra Necklace"
            #
            # rand_prop_id - bonuses from the item: "of the Monkey"
            #
            # enchant_id - if it has an enchant.
            #
            # name - the derived name: "Tundra Necklace of the Monkey"
            #
            # count - ie: 20 sheets of silk
            #
            # minbid - minimum bid auction was set up for
            #
            # buyout - buyout price (0 if none set)
            #
            # unique id - instance of this item. If item does not have specific
            # instances (aka: sheets of silk, large brilliant shards) this will
            # be 0.
            #
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
                continue

            item_class_id = int(item_class_id)
            rand_prop_id = int(rand_prop_id)
            enchant_id = int(enchant_id)
            count = int(count)
            minbid = int(minbid)
            buyout = int(buyout)
            item_instance_id = int(item_instance_id)
            
            # Now although we have what Auctioneer uses as the unique
            # identifier for an auction I want something a little
            # different. For example having the item name be part of the key is
            # a bit of useless redundancy. The combination of item_class_id and
            # rand_prop_id is just basically the same information
            #
            # So perhaps (item_class_id, rand_prop_id, enchant_id, count,
            # minbid, buyout, item_instance_id, owner_id) would make a good
            # key. Basically subsituting out the name of the item with the id
            # of the auction owner (which may be 'unknown')
            #
            owner = find_or_create_toon(auction_data['owner'], realm, faction)

            auction_key = "%d:%d:%d:%d:%d:%d:%d:%d" % \
                          (item_class_id, rand_prop_id, enchant_id, count,
                           minbid, buyout, item_instance_id, owner.id)

            wow_id = "%d:%d:%d" % (item_class_id, rand_prop_id, enchant_id)
            auction_price_data = lua_proc.variables['AuctionPrices'][realm_faction][wow_id]

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
                if auction_data['bidamount'] > 0:
                    bid_list = bids.get_list(auction_id__exact = auction.id,
                                             bid__exact = auction_data['bidamount'])
                    if len(bid_list) == 0:
                        # No bids at this price, make a new one.
                        #
                        bid = bids.Bid(item_id = item.id,
                                       auction_id = auction.id,
                                       initial_seen = initial_seen,
                                       last_seen = last_seen,
                                       bid = auction_data['bidamount'],
                                       bid_for_one = \
                                       int(auction_data['bidamount'] / count))
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
                                           buyout_for_one = int(buyout / \
                                                                count),
                                           min_bid = minbid,
                                           min_bid_for_one = int(minbid / \
                                                                 count),
                                           count = count,
                                           last_seen = last_seen,
                                           initial_seen = initial_seen)
                auction.save()

                # This auction did not exist. It will have no bids. Create a
                # new bid if the bid amount is not zero.
                #
                if auction_data['bidamount'] > 0:
                    bid = bids.Bid(item_id = item.id, auction_id = auction.id,
                                   initial_seen = initial_seen,
                                   last_seen = last_seen,
                                   bid = auction_data['bidamount'],
                                   bid_for_one = \
                                   int(auction_data['bidamount'] / count))
                    bid.save()

            # Done auction loop
            
        # Done realm loop

    # Done function
    return

###########
#
# The work starts here
#
if __name__ == "__main__":
    main()
#
#
###########
