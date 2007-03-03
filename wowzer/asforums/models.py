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
    slug = models.SlugField(maxlength = 20, prepopulate_from = ("name",),
                            db_index = True, unique = True, blank = False)
    blurb = models.CharField(maxlength = 128)
    creator = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False)

    class Admin:
        # prepopulated_fields = {'slug' : ('name',)} # Newformsadmin branch
        pass

    class Meta:
        row_level_permissions = True
        permissions = (("view", "Can see the forum collection"),
                       ("moderate", "Can moderate all the forums in "
                        "collection"),
                       ("createforum", "Can create a forum in collection"),
                       ("discuss", "Can create a discussion in forum"),
                       ("post", "Can post in a discussion in forum"))

    #########################################################################
    #
    def __str__(self):
        return "Forum %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forum_collections/%s" % self.slug

    #########################################################################
    #
    def save(self):
        # If the slug is not defined when we attempt to save this
        # instance create one for us.
        #
        if not self.slug:
            self.slug = slugify(self.name, 20)
        super(ForumCollection, self).save()

#############################################################################
#
class Forum(models.Model):
    """A forum is a collection of discussions
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    slug = models.SlugField(maxlength = 20, prepopulate_from = ("name",),
                            db_index = True, blank = False)
    blurb = models.CharField(maxlength = 128)
    creator = models.ForeignKey(User, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    collection = models.ForeignKey(ForumCollection, db_index = True)
#    last_post = models.ForeignKey("Post")
#    last_post_at = models.DateTimeField(null = True, db_index = True)

    class Admin:
        # prepopulated_fields = {'slug' : ('name',)} # Newformsadmin branch
        pass

    class Meta:
        row_level_permissions = True
        unique_together = (("name", "collection"), ("slug", "collection"))
        permissions = (("view", "Can see forum"),
                       ("moderate", "Can moderate forum"),
                       ("discuss", "Can create a discussion in forum"),
                       ("post", "Can post in a discussion in forum"))

    #########################################################################
    #
    def __str__(self):
        return "Forum %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forums/%s/" % self.slug

    #########################################################################
    #
    def save(self):
        # If the slug is not defined when we attempt to save this
        # instance create one for us.
        #
        if not self.slug:
            self.slug = slugify(self.name, 20)
        super(Forum, self).save()
        
#############################################################################
#
class Discussion(models.Model):
    """Discussions, in a forum.
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    slug = models.SlugField(prepopulate_from = ("name",))
    forum = models.ForeignKey(Forum)
    creator = models.ForeignKey(User, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    blurb = models.CharField(maxlength = 128)
    number_views = models.IntegerField(default = 0, editable = False)
#    last_post_at = models.DateTimeField(null = True)
    last_modified = models.DateTimeField(auto_now = True)
    edited = models.BooleanField(default = False)
    
    class Admin:
        # prepopulated_fields = {'slug' : ('name',)} # Newformsadmin branch
        pass

    class Meta:
        row_level_permissions = True
        unique_together = (("name", "forum"), ("slug", "forum"))
        permissions = (("post", "Can post to discussion"),)
        
    #########################################################################
    #
    def __str__(self):
        return "Discussion %s in forum %s" % (self.name, self.forum.name)

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forums/%s/%s/" % (self.forum.slug, self.slug)

    #########################################################################
    #
    def save(self):
        # If the slug is not defined when we attempt to save this
        # instance create one for us.
        #
        if not self.slug:
            self.slug = slugify(self.name, 20)
        super(Discussion, self).save()

#############################################################################
#
class Post(models.Model):
    """Posts, in a discussion, in a forum.
    """

    creator = models.ForeignKey(User, db_index = True)
    created_at = models.DateTimeField(auto_now_add = True, editable = False)
    last_modified = models.DateTimeField(null = True)
    edited = models.BooleanField(default = False)
    discussion = models.ForeignKey(Discussion)
    deleted = models.BooleanField(default = False)
    post = models.TextField(blank = True)
    in_reply_to = models.ForeignKey('self', related_name = 'replies',
                                    null = True)
    #bbcode = models.BooleanField(default = True)
    #smilies = models.BooleanField(default = True)
    #signature = models.BooleanField(default = True)
    #notify = models.BooleanField(default = True)

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
        return "/asforums/forums/%s/%s/%d/" % (self.discussion.forum.slug,
                                              self.discussion.slug,
                                              self.id)


# Connect the signal for a new post being created to our signal function
# that kicks off and updates various things when a post is made.
#
#dispatcher.connect(update_last_post_at, signal = signals.post_save,
#                   sender = Post)
