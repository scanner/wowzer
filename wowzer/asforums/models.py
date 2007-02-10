#
# Models for wowzer 'raidtracker' app
#
# $Id$
#

# Django imports
#
from django.db import models
from django.db.models import signals
from django.dispatch import dispatcher

# django model imports
#
from django.contrib.auth.models import User

# Signal imports
#
#from wowzer.asforums.signals import update_last_post_at

#############################################################################
#
class Forum(models.Model):
    """A forum is a collection of discussions
    """

    name = models.CharField(maxlength = 128, db_index = True)
    slug = models.SlugField(maxlength = 20, prepopulate_from = ("name",))
    creator = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    last_post_at = models.DateTimeField(null = True)

    class Admin:
        # prepopulated_fields = {'slug' : ('name',)} # Newformsadmin branch
        pass

    class Meta:
        row_level_permissions = True

    #########################################################################
    #
    def __str__(self):
        return "Forum %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/%s/" % self.slug
        
#############################################################################
#
class Discussion(models.Model):
    """Discussions, in a forum.
    """

    name = models.CharField(maxlength = 128, db_index = True)
    slug = models.SlugField(prepopulate_from = ("name",))
    forum = models.ForeignKey(Forum)
    creator = models.ForeignKey(User, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    number_views = models.IntegerField(default = 0, editable = False)
    last_post_at = models.DateTimeField(null = True)
    
    class Admin:
        # prepopulated_fields = {'slug' : ('name',)} # Newformsadmin branch
        pass

    class Meta:
        row_level_permissions = True

    #########################################################################
    #
    def __str__(self):
        return "Discussion %s in forum %s" % (self.name, self.forum.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/%s/%s/" % (self.forum.slug, self.slug)

#############################################################################
#
class Post(models.Model):
    """Posts, in a discussion, in a forum.
    """

    creator = models.ForeignKey(User, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    discussion = models.ForeignKey(Discussion)
    post = models.TextField()

    class Admin:
        # prepopulated_fields = {'slug' : ('name',)} # Newformsadmin branch
        pass

    class Meta:
        row_level_permissions = True

    #########################################################################
    #
    def __str__(self):
        return "Post %d in discussion %s in forum %s" % \
            (self.id,
             self.discussion.name,
             self.discussion.forum.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/%s/%s/%d/" % (self.discussion.forum.slug,
                                        self.discussion.slug,
                                        self.id)

    #########################################################################
    #
    def save(self):
        """When a post is saved, for the first time (ie: on creation)
        we want to update various things (like last_post_at in its dicussion
        and forum)
        """

        # If the "id" is none then this object has not been saved yet.
        # That means that this is a new object.
        #
        if self.id is None:
            created = True
        else:
            created = False

        super(Post, self).save() # Call the real save method.

        # If this is a creation, and the save succeeded then we want to
        # update the discussion and forum this post is in.
        #
        if created:
            now = datetime.utcnow()
            self.discussion.last_post_at = now
            self.discussion.forum.last_post_at = now

        return

# Connect the signal for a new post being created to our signal function
# that kicks off and updates various things when a post is made.
#
#dispatcher.connect(update_last_post_at, signal = signals.post_save,
#                   sender = Post)
