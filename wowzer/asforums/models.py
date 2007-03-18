#
# Models for 'asforums' app. These  are meant to be part of a
# project-independent "forum" application.
#
# $Id$
#

# Django imports
#
from django.db import models
from django.db.models import signals
from django.dispatch import dispatcher
from django.template.defaultfilters import slugify as django_slugify

# django model imports
#
from django.contrib.auth.models import User

# Wowzer model imports
#
from wowzer.main.models import TaggedItem

# Signal imports
#
#from wowzer.asforums.signals import update_last_post_at

#############################################################################
#
def slugify(value, length):
    """Take the given string and slugify it, making sure it does not exceed
    the specified length.
    """
    if len(value) > length:
        return django_slugify(value[:length/2] + value[-length/2:])
    else:
        return django_slugify(value)

#############################################################################
#
class ForumCollection(models.Model):
    """A collection of forums.
    """
    name = models.CharField(maxlength = 128, db_index = True, unique = True,
                            blank = False)
    blurb = models.CharField(maxlength = 128)
    creator = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False)
    tags = models.GenericRelation(TaggedItem)
    
    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        permissions = (("view", "Can see the forum collection"),
                       ("moderate", "Can moderate all the forums in "
                        "collection"),
                       ("createforum", "Can create a forum in collection"),
                       ("discuss", "Can create a discussion in forum"),
                       ("post", "Can post in a discussion in forum"),
                       ("tag", "Can tag a forum collection and its descendents"))

    #########################################################################
    #
    def __str__(self):
        return "Forum %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forum_collections/%d/" % self.id

#############################################################################
#
class Forum(models.Model):
    """A forum is a collection of discussions
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    blurb = models.CharField(maxlength = 128)
    creator = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                      db_index = True)
    collection = models.ForeignKey(ForumCollection, db_index = True)
    tags = models.GenericRelation(TaggedItem)
#    last_post = models.ForeignKey("Post")
#    last_post_at = models.DateTimeField(null = True, db_index = True)

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        unique_together = (("name", "collection"),)
        permissions = (("view", "Can see forum"),
                       ("moderate", "Can moderate forum"),
                       ("discuss", "Can create a discussion in forum"),
                       ("post", "Can post in a discussion in forum"),
                       ("tag", "Can tag a forum and its descendents"))

    #########################################################################
    #
    def __str__(self):
        return "Forum %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forums/%d/" % self.id

#############################################################################
#
class Discussion(models.Model):
    """Discussions, in a forum.
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    forum = models.ForeignKey(Forum)
    creator = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                      db_index = True)
    blurb = models.CharField(maxlength = 128)
    number_views = models.IntegerField(default = 0, editable = False)
    last_modified = models.DateTimeField(auto_now = True)
    edited = models.BooleanField(default = False)
    tags = models.GenericRelation(TaggedItem)
    views = models.IntegerField(default = 0, editable = False)
    
    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        unique_together = (("name", "forum"),)
        permissions = (("post", "Can post to discussion"),
                       ("tag", "Can tag a discussion and its posts"))
        
    #########################################################################
    #
    def __str__(self):
        return "Discussion %s in forum %s" % (self.name, self.forum.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/discs/%d/" % self.id

    #########################################################################
    #
    def increment_viewed(self):
        """Increments the counter that tells us how many times this discussion
        has been viewed. This is intended to be called whenever the
        discussion detail is viewed, or when any post in the
        discussion is viewed."""

        # Since django does not provide any atomic increment function we fall
        # back on django's nice ability to let us do raw sql if we want to.
        #
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("update asforums_discussion set views = views + 1 where id=%d", [self.id])
        
#############################################################################
#
class Post(models.Model):
    """Posts, in a discussion, in a forum.
    """

    creator = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    last_modified = models.DateTimeField(null = True)
    edited = models.BooleanField(default = False)
    discussion = models.ForeignKey(Discussion)
    deleted = models.BooleanField(default = False)
    content = models.TextField(maxlength = 4000, blank = True)
    content_html = models.TextField(maxlength = 4000, blank = True)
    markup = models.CharField(maxlength=80, blank=True)
    in_reply_to = models.ForeignKey('self', related_name = 'replies',
                                    null = True)
    tags = models.GenericRelation(TaggedItem)
    views = models.IntegerField(default = 0, editable = False)
    smilies = models.BooleanField(default = True)
    signature = models.BooleanField(default = True)
    #notify = models.BooleanField(default = True)

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        permissions = (("tag", "Can tag a post"),)

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
        return "/asforums/posts/%d/" % self.id

    #########################################################################
    #
    def increment_viewed(self):
        """Increments the counter that tells us how many times this post
        has been viewed. This is intended to be called whenever the
        post content is viewed either as part of a listing of posts with their
        text or when a specific post is referenced."""

        # Since django does not provide any atomic increment function we fall
        # back on django's nice ability to let us do raw sql if we want to.
        #
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("update asforums_post set views = views + 1 where id=%d", [self.id])


# Connect the signal for a new post being created to our signal function
# that kicks off and updates various things when a post is made.
#
#dispatcher.connect(update_last_post_at, signal = signals.post_save,
#                   sender = Post)
