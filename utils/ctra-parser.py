#!/usr/bin/env python
#
#
import sys
import re
from datetime import datetime
sys.path.append('.')
import wowzer.settings

from wowzer.savedvarparser import ParseSavedVariables
from wowzer.toons.models import Toon, Realm
from wowzer.raidtracker.models import Raid, JoinLeave

date_re = re.compile('^(?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d\d) '
                     '(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)$')

############################################################################   
##
def dt_from_str(string):
    """Parse a string in a specific format in to a datetime object."""

    st = date_re.search(string)
    dt = datetime(int(st.group('year')) + 2000,
                  int(st.group('month')), int(st.group('day')),
                  int(st.group('hour')), int(st.group('minute')),
                  int(st.group('second')))
    return dt

    
############################################################################   
##
## And so begins the program that uses our lua variable declartion lexer and
## parser to parse out Auctioneer data and fill in the data models in wowzer
## that it relates to.
##
def main():
    print "Reading file"
    f = open('/home/scanner/tmp/CT_RaidTracker.lua', 'r')
#    f = open('/home/scanner/tmp/ctrt-test.lua', 'r')
    data = f.read()
    f.close()
    parser = ParseSavedVariables(output_dir = "/tmp/")
    print "Parsing data"
    parser.process(data)
    print "Done parsing data"

    players = {}
    submitter = Toon.objects.get(name='Tamrielo')
    realm = Realm.objects.get(name='Argent Dawn')
    num_raids_entered = 0
    for raid in parser.variables['CT_RaidTracker_RaidLog'].keys():
        raid_info = parser.variables['CT_RaidTracker_RaidLog'][raid]

        if num_raids_entered > 100:
            break
        # See if a raid object exists taht was submitted by this player
        # with this same start time.
        #
        st = dt_from_str(raid_info['key'])
        if Raid.objects.filter(start_time = st,
                               submitter = submitter).count() > 0:
            print "Skipping raid started by %s at %s" % (submitter, str(st))
            continue
        # Create our raid object
        #
        raid_obj = Raid(submitter = submitter)
        raid_obj.start_time = dt_from_str(raid_info['key'])
        if raid_info.has_key("raidEnd"):
            raid_obj.end_time = dt_from_str(raid_info['raidEnd'])
        raid_obj.save()

        print "\n\nCreated raid object %s" % raid_obj
        
        # Now add the join/leave events.
        #
        
        raid_size = len(raid_info['Join'].keys())
        print "   Number of people in raid: %d" % raid_size
        joinleave_info = []

        for plid in raid_info['Join'].keys():
            join_info = raid_info['Join'][plid]
            joinleave_info.append({ 'player': join_info['player'],
                                    'time'  : dt_from_str(join_info['time']),
                                    'type'  : 'j' })
            
        for plid in raid_info['Leave'].keys():
            join_info = raid_info['Leave'][plid]
            joinleave_info.append({ 'player': join_info['player'],
                                    'time'  : dt_from_str(join_info['time']),
                                    'type'  : 'l' })

        joinleave_info.sort(cmp = lambda x,y: cmp(x['time'], y['time']))

        for event in joinleave_info:
            player_name = event['player']
            print "Player: %s" % player_name
            try:
                player = Toon.objects.get(name=player_name, realm = realm)
            except Toon.DoesNotExist:
                # This toon does not exist. Create it.
                #
                player = Toon(name = player_name, realm = realm)
                player.save()

            if event['type'] == 'j':
                raid_obj.joined(player, event['time'], recount = False)
                raid_obj.members.add(player)
            else:
                raid_obj.left(player, event['time'], recount = False)
        raid_obj.purge_dupe_joinleave_events()

        # If we had no end-time then get the last join/leave event and
        # make that the end time.
        #
        if raid_obj.end_time is None:
            event = raid_obj.joinleave_set.order_by('-when')[0]
            raid_obj.end_time = event.when
            print "Raid %s had no end time. (forcing to last event)" % \
                  str(raid_obj)
        raid_obj.recount_membership()
        raid_obj.save()
        rtmp = Raid.objects.get(pk=raid_obj.id)
##         if rtmp.maximal_size > 40:
##             raise AssertionError("Raid size: %d can not be more then 40" % \
##                                  rtmp.maximal_size)
        print "  Done adding joins/leaves, raid maximal size: %d" % \
              rtmp.maximal_size
        num_raids_entered += 1
    print "Done."
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

