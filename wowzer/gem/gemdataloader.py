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
from datetime import datetime

# Django imports
#
from django.db import transaction

# Wowzer utilities
#
from wowzer.savedvarparser import SavedVarParser

# Wowzer models
#
from wowzer.gem.models import Event, ClassLimit, EventMember, GemDataJob
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

# Ditto for guilds. They will very likely not change in any
# significant fashion while this script is running.
#
GUILDS = {}

#############################################################################
#
@transaction.commit_on_success
def loaddata(filename, job):
    """
    Given a file name, read it in and parse it. Then go through the parsed GEM
    data creating new events, updating old ones, creating new toons, and
    guilds and updating old ones.

    If this function raises an exception the database will be rolled back.
    """

    svp = SavedVarParser(open(filename).read())
    svp.parse()

    process_events(svp, job)
    process_templates(svp, job)
    process_players(svp, job)
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
    if jobs.count() > 0:
        print "%d jobs to process this run." % jobs.count()
    for job in jobs:
        job.state = GemDataJob.PROCESSING
        job.save()
        print "Processing %s" % job
        try:
            loaddata(job.get_data_file_filename(), job)
        except:
            job.state = GemDataJob.ERROR
            job.save()
            raise
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
def process_events(svp, job):
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


        # Right now that is all we have because we do not have a gem
        # data file with any events in it.
        #
    return


#############################################################################
#
def process_templates(svp, job):
    
    # Right now we have no code to process templates. We need to define
    # some so that we can see what we need to do here.
    #
    pass

#############################################################################
#
def process_players(svp, job):
    """
    One side advantage of GEM is that it gets all sorts of interesting
    information about players in the gem channels, including the channel
    all the other players are using if you are in it. This gives me
    things like their lastlog and lastleave times, their guild,
    where they were seen last, their guild rank, etc.
    """

    for realm_name in svp['GEM_Players'].keys():
        realm, ign = Realm.objects.get_or_create(name = realm_name)

        # We are assuming that the 'lastlogin' is in the timezone
        # of the submitter. If we do not have a timezone for the submitter
        # then assume the timezone of the server.
        #
        submitter_tz = job.submitter.get_profile().timezone
        if submitter_tz is None or submitter_tz == "":
            tz = pytz.timezone(realm.timezone)
        else:
            tz = pytz.timezone(submitter_tz)
    
        for channel_name in svp['GEM_Players'][realm_name].keys():
            players = svp['GEM_Players'][realm_name][channel_name]

            for player_name in players.keys():
                player, ign = Toon.objects.get_or_create(name = player_name,
                                                         realm = realm)
                if ign:
                    print "Created new toon %s" % player
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
    if gem_player_data['guild'] != "":
        guild_name = gem_player_data['guild']
        if player.guild is None or player.guild.name != guild_name:
            changed = True
            if guild_name in GUILDS:
                player.guild = GUILDS[guild_name]
            else:
                guild, created = Guild.objects.get_or_create(name = guild_name,
                                                             realm = realm)
                GUILDS[guild_name] = guild
                if created:
                    print "Created guild %s" % guild
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
    if gem_player_data['grank_name'] != "":
        grank_name = gem_player_data['grank_name']
        if player.guild_rank is None or player.guild_rank.name != grank_name:
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
            if created:
                print "Created guild rank %s" % grank
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
