#
# Models for 'asforums' app. These  are meant to be part of a
# project-independent "forum" application.
#
# $Id$
#

# System imports
#
from datetime import datetime, timedelta

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
        permissions = (("view_forumcollection",
                        "Can see the forum collection"),
                       ("moderate_forumcollection",
                        "Can moderate all the forums in collection"),
                       ("createforum_forumcollection",
                        "Can create a forum in collection"),
                       ("discuss_forumcollection",
                        "Can create a discussion in forum"),
                       ("post_forumcollection",
                        "Can post in a discussion in forum"),
                       ("tag_forumcollection",
                        "Can tag a forum collection and its descendents"))

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
#class ForumManager(models.Manager):
#    """A custom Forum Manager that has a method that can filter a forum list
#    for forums that are viewable by a specific user.
#    """
#    def viewable(self, user):
#        """Returns a list of forums filtered by the given user having
#        'view_forum' permission on any given forum instance (using
#        row level permissions.
#        """
#        forum_ctype, ign = ContentType.get_or_create(app_label="asforums",
#                                                     model="forum",
#                                                defaults = { 'name': 'forum'})
#        user_ctype = ContentType.objects.get_for_model(user)
#        if user_ctypes.groups.count > 0:
#            group_ctype = ContentType.objects.get_for_model(user.groups[0])
#        else:
#            group_ctype = None
#
#        view_forum_perm = Permission.objects.get(name="view_forum")
#        view_fc_perm = Permission.
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
        permissions = (("view_forum",
                        "Can see the forum"),
                       ("moderate_forum",
                        "Can moderate the forum"),
                       ("discuss_forum",
                        "Can create discussions in the forum"),
                       ("post_forum",
                        "Can post in discussions in the forum"),
                       ("tag_forum",
                        "Can tag the forum and its descendents"))

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
    views = models.IntegerField(default = 0, editable = False)
    last_modified = models.DateTimeField(auto_now = True)
    edited = models.BooleanField(default = False)
    tags = models.GenericRelation(TaggedItem)
    
    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        unique_together = (("name", "forum"),)
        permissions = (("post_discussion",
                        "Can post to the discussion"),
                       ("tag_discussion",
                        "Can tag the discussion and its posts"))
        
    #########################################################################
    #
    def __str__(self):
        return "Discussion %s in forum %s" % (self.name, self.forum.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/discs/%d/" % self.id

#############################################################################
#
class Post(models.Model):
    """Posts, in a discussion, in a forum.
    """

    creator = models.ForeignKey(User, db_index = True, editable = False)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    changed = models.DateTimeField(null = True, editable = False)
    edited = models.BooleanField(default = False, editable = False)
    discussion = models.ForeignKey(Discussion, editable = False)
    post_number = models.IntegerField(default = 0, editable = False)
    deleted = models.BooleanField(default = False, editable = False)
    content = models.TextField(maxlength = 4000, blank = True)
    content_html = models.TextField(maxlength = 4000, blank = True,
                                    editable = False)
    markup = models.CharField(maxlength=80, blank=True, editable = False)
    in_reply_to = models.ForeignKey('self', related_name = 'replies',
                                    null = True, editable = False)
    tags = models.GenericRelation(TaggedItem, editable = False)
    views = models.IntegerField(default = 0, editable = False)
    smilies = models.BooleanField(default = True)
    signature = models.BooleanField(default = True)
    #notify = models.BooleanField(default = True)

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        permissions = (("tag_post", "Can tag the post"),)

        # because of how we assign post numbers we can not insure that they
        # are unique per discussion.
        #
        # unique_together = (("discussion", "post_number"),)

    #########################################################################
    #
    def save(self):
        if not self.id:
            self.created = datetime.utcnow()
            self.post_number = self.discussion.post_set.count() + 1
        else:
            self.changed = datetime.utcnow()
        return super(Post,self).save()
    
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
        text or when a specific post is referenced.

        XXX This does not work. The sql statement is correct, but nothing
        happens in the database."""

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
