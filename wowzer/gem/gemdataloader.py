#
# File: $Id$
#
"""
A utility module used by a task that will read in datafiles as specified
by GemDataJob objects.
"""

# System imports
#
import sys
import pytz
import traceback
from datetime import datetime

# Django imports
#
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

# Wowzer utilities
#
from wowzer.savedvarparser import SavedVarParser

# Wowzer models
#
from wowzer.main.models import UserProfile
from wowzer.gem.models import Event, ClassRule, Member, GemDataJob
from wowzer.toons.models import Toon, PlayerClass, Realm, Guild, GuildRank

# We keep some variables that are global to this module for caching
# purposes.
#
# We have player classes in the database, but instead of doing sql
# lookups on them all the time once we look up a player class object
# we put it in this cache the class name. It is not going to
# change so this is a safe operation.
#
PLAYER_CLASSES = {}

#############################################################################
#
@transaction.commit_on_success
def loaddata(job):
    """
    Given a file name, read it in and parse it. Then go through the parsed GEM
    data creating new events, updating old ones, creating new toons, and
    guilds and updating old ones.

    If this function raises an exception the database will be rolled back.
    """

    svp = SavedVarParser(open(job.get_data_file_filename()).read())
    svp.parse()

    tz = pytz.timezone(job.timezone)

    process_events(svp, tz, job)
    process_players(svp, tz)
    return

#############################################################################
#
def process_jobs():
    """
    This is the driver function. It will go through the GemDataJob objects in
    the database that have not been completed yet.
    """

    # Get all the jobs that have not been completed yet, in order that
    # they were created.
    #
    jobs = GemDataJob.objects.filter(state = \
                                     GemDataJob.PENDING).order_by('created')
    for job in jobs:
        job.state = GemDataJob.PROCESSING
        job.save()
        print "Processing %s" % job
        try:
            loaddata(job)
        except:

            # If something goes south this job enters the 'error'
            # state.  What is more we pull out the string of the
            # actual exception that busted us, chop off the \n, and
            # save that as well. NOTE: That is not meant as a real
            # debugging method. The user is expected to read the error
            # log of the server.
            #
            except_strings = traceback.format_exception_only(sys.last_type,
                                                             sys.last_value)
            job.state = GemDataJob.ERROR
            job.error = except_strings[-1][:1][:1023]
            job.save()

            # Print the full exception information to standard error.
            #
            traceback.print_exc()
        else:
            # Our job finished successfully. Mark it as completed.
            #
            job.state = GemDataJob.COMPLETED
            job.completed_at = datetime.utcnow()
            job.save()
            print "Successuflly processed %s" % job
    return

#############################################################################
#
def process_events(svp, tz, job):
    """
    Go through all the events for all the realms we have info for
    and add them to our database.
    """
    if 'realms' not in svp['GEM_Events']:
        # Huh, no realms to process. Whatever.
        #
        return
    for realm_name in svp['GEM_Events']['realms'].keys():
        realm, ign = Realm.objects.get_or_create(name = realm_name)

        for event_name in svp['GEM_Events']['realms'][realm_name]['events'].keys():
            evt_data = svp['GEM_Events']['realms'][realm_name]['events'][event_name]

            # Make the event time be in UTC and naieve. Grr. postgres orm
            # for django only deals with naieve datetimes.
            #
            when = datetime.fromtimestamp(evt_data["ev_date"], tz).\
                astimezone(pytz.UTC).replace(tzinfo = None)
            update_time = datetime.fromtimestamp(evt_data["update_time"], tz).\
                astimezone(pytz.UTC).replace(tzinfo = None)
            place = evt_data["ev_place"]
            leader, ign = Toon.objects.get_or_create(name = evt_data['leader'],
                                                     realm = realm)

            defaults = {'leader'      : leader,
                        'channel'     : evt_data['channel'],
                        'update_time' : update_time,
                        'min_level'   : evt_data['min_lvl'],
                        'max_level'   : evt_data['max_lvl'],
                        'max_count'   : evt_data['max_count'],
                        }

            event, created = Event.objects.get_or_create(name = event_name,
                                                         place = place,
                                                         when = when,
                                                         realm = realm,
                                                         defaults = defaults)

            event.sources.add(job)
            if not created:
                # This is an update of the event info. Add this job to the
                # sources of data for this event.
                #
                # NOTE: Some of these fields will never change during an event's
                # lifetime, but I am being safe and lazy by just updating them
                # all, just in case.
                #
                event.leader = leader
                event.channel = evt_data['channel']
                event.update_time = update_time
                event.min_level = evt_data['min_lvl']
                event.max_level = evt_data['max_lvl']
                event.max_count = evt_data['max_count']
                event.save()

            # Go through all the types of lists of members, making sure
            # That they relate to the event in the right fashion.
            #
            for state, key in Member.PLAYER_STATE_KEYS:
                update_event_members(event, realm, state, evt_data[key], tz)

            # Go through the class rules for this event and update,
            # add or subtract the appropriate class rule.
            #
            for key, class_name in ClassRule.CLASSES:
                if class_name in PLAYER_CLASSES:
                    player_class = PLAYER_CLASSES[class_name]
                else:
                    player_class = PlayerClass.objects.get(name = class_name)

                if key in evt_data["classes"]:
                    defaults = { 'min_count' : evt_data["classes"][key]["min"],
                                 'max_count' : evt_data["classes"][key]["max"]}
                    cr, created = ClassRule.objects.get_or_create(event = event,
                                                                  player_class = player_class,
                                                                  defaults = defaults)
                    if created:
                        cr.min_count = evt_data["classes"][key]["min"]
                        cr.max_count = evt_data["classes"][key]["max"]
                        cr.save()
                else:
                    # This player class was not in the class rules for
                    # this event. Make sure that there are no ClassRule
                    # objects defined for this class for this event.
                    #
                    try:
                        cr = event.classrule_set.get(player_class=player_class)
                        cr.delete()
                    except ClassRule.DoesNotExist:
                        pass
    return

#############################################################################
#
def update_event_members(event, realm, state, member_data, tz):
    """
    """
    # Delete any member objects for players that are not in our list
    # of players for this state.
    #
    member_names = [member_data[k]["name"] for k in member_data.keys()]
    to_delete = Member.objects.filter(event = event,
                                      state = state).\
                                      exclude(toon__name__in = member_names)
    for td in to_delete:
        td.delete()
    
    for i in member_data.keys():
        player, ign = Toon.objects.get_or_create(name = member_data[i]["name"],
                                                 realm = realm)
        member, ign = Member.objects.get_or_create(event = event,
                                                   toon = player,
                                                   state = state)
        if 'comment' in member_data[i]:
            member.comment = member_data[i]["comment"]
        if 'update_time' in member_data[i]:
            member.update_time = datetime.fromtimestamp(member_data[i]["update_time"], tz).astimezone(pytz.UTC)
        else:
            member.update_time = datetime.utcnow()
        if 'place' in member_data[i]:
            member.place = member_data[i]['place']
        member.save()
    return
    
#############################################################################
#
def process_players(svp, tz):
    """
    One side advantage of GEM is that it gets all sorts of interesting
    information about players in the gem channels, including the channel
    all the other players are using if you are in it. This gives me
    things like their lastlog and lastleave times, their guild,
    where they were seen last, their guild rank, etc.
    """

    for realm_name in svp['GEM_Players'].keys():
        realm, ign = Realm.objects.get_or_create(name = realm_name)

        for channel_name in svp['GEM_Players'][realm_name].keys():
            players = svp['GEM_Players'][realm_name][channel_name]

            for player_name in players.keys():
                player, ign = Toon.objects.get_or_create(name = player_name,
                                                         realm = realm)
                update_player(player, players[player_name], realm, tz)
                
#############################################################################
#
def update_player(player, gem_player_data, realm, tz):
    """
    Given a Toon object and the gem player data we have for this toon
    see if any fields need to be updated. Update them if they do, and
    if we update any fields, then save the object when we are done.
    """
    
    changed = False

    # Check to see if we have the right guild for the player.
    #
    if 'guild' in gem_player_data and gem_player_data['guild'] != "":
        guild_name = gem_player_data['guild']
        if player.guild is None or player.guild.name != guild_name:
            changed = True
            guild, created = Guild.objects.get_or_create(name = guild_name,
                                                         realm = realm)
            if created and player.faction:
                guild.faction = player.faction
                guild.save()
            player.guild = guild
    elif player.guild is not None:
        player.guild = None
        changed = True

    # See if our last login time for the player matches what we already
    # have. Be sure to convert it to UTC.
    #
    lastlog = datetime.fromtimestamp(gem_player_data['lastlog'], tz).astimezone(pytz.UTC)
    if player.last_login_time is None or player.last_login_time.replace(tzinfo = pytz.UTC) != lastlog:
        changed = True
        player.last_login_time = lastlog

    # This should never change.. (unless someone takes over the name of a
    # character we used to know.
    #
    if player.player_class is None or \
       player.player_class.name != gem_player_data['class']:
        changed = True
        if gem_player_data['class'] in PLAYER_CLASSES:
            player.player_class = PLAYER_CLASSES[gem_player_data['class']]
        else:
            player.player_class = PlayerClass.objects.get(name = gem_player_data['class'])

    # Next we do the guild rank for this player.
    #
    if 'grank_name' in gem_player_data and gem_player_data['grank_name'] != "":
        grank_name = gem_player_data['grank_name']
        if player.guild_rank is None or player.guild_rank.name != grank_name:
#            print "new guild rank - for %s Guild: %s, rank: %s" % (player, player.guild, grank_name)
            changed = True
            grank, created = GuildRank.objects.get_or_create(guild = player.guild,
                                                             name = grank_name)
            grank_changed = False
            if grank.level != gem_player_data['grank_idx']:
                grank_changed = True
                grank.level = gem_player_data['grank_idx']
            if gem_player_data['officer'] == 1 and not grank.officer:
                grank_changed = True
                grank.officer = True
            if grank_changed:
                grank.save()
            player.guild_rank = grank
    elif player.guild_rank is not None:
        changed = True
        player.guild_rank = None

    if player.last_seen_location is None or \
       player.last_seen_location != gem_player_data['location']:
        player.last_seen_location = gem_player_data['location']
        changed = True

    if player.level != gem_player_data['level']:
        player.level = gem_player_data['level']
        changed = True

    # See if our last logout time for the player matches what we already
    # have
    if 'lastleave' in gem_player_data:
        lastleave = datetime.fromtimestamp(gem_player_data['lastleave'], tz).astimezone(pytz.UTC)
        if player.last_logout_time is None or \
               player.last_logout_time.replace(tzinfo = pytz.UTC) != lastleave:
            changed = True
        player.last_logout_time = lastleave

    # After all that, if changed is True, save the updated
    # player record.
    #
    if changed:
        player.save()

    return
