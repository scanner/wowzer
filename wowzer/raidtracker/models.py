#
# Models for wowzer 'raidtracker' app
#
# $Id$
#

# Django imports
#
from django.db import models

# Wowzer model imports
#
from wowzer.toons.models import Toon
from wowzer.items.models import Item

#############################################################################
#
class Raid(models.Model):
    """An instance of a 'raid' - ie a group of up to 40 individuals
    """

    submitter = models.ForeignKey(Toon, related_name = 'raids_submitted')
    start_time = models.DateTimeField("Raid start time", editable = False)
    end_time = models.DateTimeField("Raid end time", editable = False,
                                    null = True)
    members = models.ManyToManyField(Toon, related_name = 'raids_attended',
                                     blank = True)
    maximal_size = models.IntegerField(editable = False, default = 0)
    notes = models.TextField(maxlength = 2048, blank = True, null = True)

    class Meta:
        ordering = ['start_time']
        
    class Admin:
        list_filter = ['start_time', 'end_time', 'maximal_size']
        search_fields = ['submitter', 'notes']

    #########################################################################
    #
    def __str__(self):
        return "Size: %d, started at %s, ended: %s, submitted by %s" % \
               (self.maximal_size, str(self.start_time), str(self.end_time),
                self.submitter.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/raidtracker/raid/%d/" % self.id

    #########################################################################
    #
    def membership_at_time(self, when):
        """This method will return a list of who was in the raid at a given
        time.

        If the time request is before or after the raid existed we raise the
        IndexError exception.
        """
        if when < self.start_time or when > self.end_time:
            raise IndexError
        
        # Basically we run through the join/leave events that are less then or
        # equal to the given datetime.
        #
        events = self.joinleave_set.filter(when__lte = when)
        membership = set([])
        for event in events:
            if event.type == 'j':
                if event.player not in membership:
                    membership.add(event.player)
            else:
                if event.player in membership:
                    membership.remove(event.player)
        return membership
                

    #########################################################################
    #
    def purge_dupe_joinleave_events(self):
        """This will go through all the join/leave events for this raid and
        remove ones that are essentially duplicates. Ie: if a player has been
        listed as joining the raid when they were already in it.

        The goal is the first join and the last leave of a set of dupes are
        considered the canonical ones.

        NOTE: This should only be called after all of the join/leave events
        for players in the raid have been entered. Otherwise we could
        accidentally remove records that are not dupes but are instead events
        for which the related 'leave' or 'join' have not been entered yet.
        """
        events = self.joinleave_set.filter(raid = self.id)
        previous_leaves = {}
        members = set([])
        for event in events:
            if event.type == 'j':
                # If the player is already in the set, then we have an event
                # we can delete.
                #
                if event.player.id in members:
                    print "Deleting duplicate join: %s" % str(event)
                    event.delete()
                else:
                    members.add(event.player.id)
            else:
                # If the player is NOT in the set we have a duplicate.
                # Delete the previous leave event for this player. If there
                # is no previous leave for this player delete _this_ event.
                #
                if event.player.id in members:
                    members.remove(event.player.id)
                    previous_leaves[event.player.id] = event
                else:
                    if previous_leaves.has_key(event.player.id):
                        # Delete the dupe.
                        #
                        print "Duplicate leave. Deleting %s" % str(previous_leaves[event.player.id])
                        previous_leaves[event.player.id].delete()
                        previous_leaves[event.player.id] = event
                    else:
                        # player had no previous leave event and is not even
                        # in the raid.. so delete this leave event.
                        #
                        print "Event had no previous join: %s" % str(event)
                        event.delete()
        return

    #########################################################################
    #
    def recount_membership(self):
        """This is very bad. If called on every join it is O(n^2)
        """
        max_members = 0
        events = self.joinleave_set.filter(raid = self.id)
        players = set([])
        for event in events:
            if event.type == 'j':
                players.add(event.player.id)
                if len(players) > max_members:
                    max_members = len(players)
            else:
                if event.player.id in players:
                    players.remove(event.player.id)
        self.maximal_size = max_members
        
    #########################################################################
    #
    def joined(self, player, when, recount = True):
        """Call this when you want to add a player to a raid. It does
        the math to make sure that the maximal raid count is correct.
        """
        self.joinleave_set.create(player = player, type = 'j', when = when)
        if recount:
            self.recount_membership()

    #########################################################################
    #
    def left(self, player, when, recount = True):
        """Call this when you want to add a player to a raid. It does
        the math to make sure that the maximal raid count is correct.
        """
        self.joinleave_set.create(player = player, type = 'l', when = when)
        if recount:
            self.recount_membership()

#############################################################################
#
JOIN_LEAVE_CHOICES = (
    ('j', 'joined'),
    ('l', 'left'),
    )

class JoinLeave(models.Model):
    """When a player joins or leaves a raid.
    """

    raid = models.ForeignKey(Raid)
    player = models.ForeignKey(Toon)
    when = models.DateTimeField()
    type = models.CharField(maxlength = 1, choices = JOIN_LEAVE_CHOICES)

    class Meta:
        ordering = ['when', 'player']
        
    class Admin:
        list_filter = ['raid', 'type', 'when']
        search_fields = ['player']

    #########################################################################
    #
    def __str__(self):
        return "%s %s at %s" % (self.player, self.get_type_display(),
                                str(self.when))
    
#############################################################################
#
class Loot(models.Model):
    """Every time something is looted by a mamber of the raid it is recorded
    here.
    """

    raid = models.ForeignKey(Raid)
    player = models.ForeignKey(Toon)
    when = models.DateTimeField(editable = False)
    item = models.ForeignKey(Item)
    count = models.IntegerField()

    class Meta:
        ordering = ['when', 'player']
        
    #########################################################################
    #
    def __str__(self):
        return "%d %s looted by %s" % (self.count, self.item.name,
                                       self.player.name)
