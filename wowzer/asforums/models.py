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
from django.db.models import signals, Q
from django.dispatch import dispatcher
from django.template.defaultfilters import slugify as django_slugify


# django model imports
#
from django.contrib.auth.models import User
from django.contrib.auth.models import RowLevelPermission

# Wowzer model imports
#
from wowzer.main.models import TaggedItem

# Signal imports
#
#from wowzer.asforums.signals import update_last_post_at

# This is a dictionary that maps permissions in a container object to
# the permissions in a sub-object that will inherit the effective
# permission. ie: the permission 'view_forumcollection' on a forum collection
# grants the save 'view_forum' permission on forum in that forum collection.
#
permission_inheritance = {
    "view_forumcollection"     : ("view_forum", "read_forum"),
    "moderate_forumcollection" : ("moderate_forum",),
    "discuss_forumcollection"  : ("discuss_forum",),
    "post_forumcollection"     : ("post_forum",),
    "change_forumcollection"   : ("change_forum",),
    "delete_forumcollection"   : ("delete_forum",),

    "post_forum"   : ("post_discussion",),
    "delete_forum" : ("delete_discussion",),
    "change_forum" : ("change_discussion",),

    "delete_discussion" : ("delete_post",),
    }

#############################################################################
#
def inherit_permissions(object, container):
    """A utility function that will go through all of the row level
    permissions on the container object and set the appropriate
    inherited permission on our destination object."""

    rlp_list = container.row_level_permissions.select_related()
    for rlp in rlp_list:
        if rlp.permission.codename in permission_inheritance:
            for perm in permission_inheritance[rlp.permission.codename]:
                RowLevelPermission.objects.create_row_level_permission(\
                    object, rlp.owner, perm, negative = rlp.negative)

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
class ForumCollectionManager(models.Manager):
    """A custom ForumCollection Manager that has a method that can filter
    a forum collection list for forums collections that are viewable
    by a specific user.
    """
    def viewable(self, user):
        """Returns a query set of forum collections filtered by the given user
        having 'view' or 'moderate' permission on any given forum
        collection instance.
        """

        # Super user can see everything.
        #
        if user.is_authenticated() and user.is_superuser:
            return self.all()

        # We need to see if they have any 'moderate' or 'view' permissions
        # and build our query up conditionally based on which they have.
        #
        # This is because if we do it all inline in one query and they
        # lack one of the permissions the 'select' will fail due to
        # something like "in ()" where the '()' is empty.

        fc_view = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_moderate = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'moderate_forumcollection')

        print "Forum collections with view: %s" % str(fc_view)
        print "Forum collections with moderate: %s" % str(fc_moderate)

        if len(fc_view) == 0 and len(fc_moderate) == 0:
            return self.none()

        if len(fc_view) != 0 and len(fc_moderate) != 0:
            q = Q(id__in = fc_view) | Q(id__in = fc_moderate)
        elif len(f_view) != 0:
            q = Q(id__in = fc_view)
        else:
            q = Q(id__in = fc_moderate)

        return self.filter(q)
    
#############################################################################
#
class ForumCollection(models.Model):
    """A collection of forums.
    """
    name = models.CharField(maxlength = 128, db_index = True, unique = True,
                            blank = False)
    blurb = models.CharField(maxlength = 128)
    author = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False)
    tags = models.GenericRelation(TaggedItem)
    objects = ForumCollectionManager()

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
                       ("read_forumcollection",
                        "Can ready discussions in forum"),
                       ("post_forumcollection",
                        "Can post in a discussion in forum"))

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
class ForumManager(models.Manager):
    """A custom Forum Manager that has a method that can filter a forum list
    for forums that are viewable by a specific user.
    """
    def viewable(self, user):
        """Returns a list of forums filtered by the given user having 'view'
        or 'moderate' permission on any given forum instance and they
        must also have 'view' or 'moderate' permission on the forum
        collections that forum is contained in.
        """

        # Super user can see everything.
        #
        if user.is_authenticated() and user.is_superuser:
            return self.all()

        # We need to see if they have any 'moderate' or 'view' permissions
        # and build our query up conditionally based on which they have.
        #
        # This is because if we do it all inline in one query and they
        # lack one of the permissions the 'select' will fail due to
        # something like "in ()" where the '()' is empty.
        #
        f_view = RowLevelPermission.objects.get_model_list(\
            user, self.model, 'view_forum')
        f_moderate = RowLevelPermission.objects.get_model_list(\
            user, self.model, 'moderate_forum')
        fc_view = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_moderate = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'moderate_forumcollection')

        print "Forums with view: %s" % str(f_view)
        print "Forums with moderate: %s" % str(f_moderate)
        print "Forum collections with view: %s" % str(fc_view)
        print "Forum collections with moderate: %s" % str(fc_moderate)

        if (len(f_view) == 0 and len(f_moderate) == 0) or \
            (len(fc_view) == 0 and len(fc_moderate) == 0):
            return self.none()

        if len(f_view) != 0 and len(f_moderate) != 0:
            q1 = Q(id__in = f_view) | Q(id__in = f_moderate)
        elif len(f_view) != 0:
            q1 = Q(id__in = f_view)
        else:
            q1 = Q(id__in = f_moderate)

        if len(fc_view) != 0 and len(fc_moderate) != 0:
            q2 = Q(collection__in = fc_view) | Q(collection__in = fc_moderate)
        elif len(f_view) != 0:
            q2 = Q(collection__in = fc_view)
        else:
            q2 = Q(collection__in = fc_moderate)

        return self.filter(q1).filter(q2)

#############################################################################
#
class Forum(models.Model):
    """A forum is a collection of discussions
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    blurb = models.CharField(maxlength = 128)
    author = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                      db_index = True)
    collection = models.ForeignKey(ForumCollection, db_index = True)
    tags = models.GenericRelation(TaggedItem)

#    last_post = models.ForeignKey("Post")
#    last_post_at = models.DateTimeField(null = True, db_index = True)

    objects = ForumManager()

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
                       ("read_forum",
                        "Can ready discussions in forum"),
                       ("post_forum",
                        "Can post in discussions in the forum"))

    #########################################################################
    #
    def __str__(self):
        return "Forum %s" % self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forums/%d/" % self.id

    #########################################################################
    #
    def save(self):
        """We have our own save() method deal with permissions.  When you
        create this object it inherits the appropriate permissions
        from the container it is in. """

        # We need to know if we created this object or not on this save()
        # call, because we need to do something -after- it has been saved
        # if this call creates it.
        #
        created = False
        if not self.id:
            created = True

        res = super(Forum,self).save()
    
        # Okay, if this save() created this forum, then create new row level
        # permissions on the forum based on the permissions on the forum
        # collection that are said to inherit (see the 'permission_inheritance'
        # dictionary.
        #
        if created:
            inherit_permissions(self, self.collection)

        return res

#############################################################################
#
class DiscussionManager(models.Manager):
    """A enchanced manager for discussions. Basically this implements the
    viewable concept. You can only view discussions that are in forums
    that you have view permissions on (and those forums must be in
    forum collections that you must have view permissions on.)
    """
    def viewable(self, user):
        """Returns a list of discussions filtered by the given user having
        'view' or 'moderate' permission on the forum instance that the
        discussion is in. They must also have 'view' or 'moderate'
        permission on the forum collections that forum is contained
        in.  """

        # Super user can see everything.
        #
        if user.is_authenticated() and user.is_superuser:
            return self.all()

        # We need to see if they have any 'moderate' or 'view' permissions
        # and build our query up conditionally based on which they have.
        #
        # This is because if we do it all inline in one query and they
        # lack one of the permissions the 'select' will fail due to
        # something like "in ()" where the '()' is empty.
        #
        f_view = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'view_forum')
        f_moderate = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'moderate_forum')
        fc_view = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_moderate = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'moderate_forumcollection')

        print "Forums with view: %s" % str(f_view)
        print "Forums with moderate: %s" % str(f_moderate)
        print "Forum collections with view: %s" % str(fc_view)
        print "Forum collections with moderate: %s" % str(fc_moderate)

        # If they do not have moderate or view on any forums or forum
        # collections then they can see no discussions.
        #
        if (len(f_view) == 0 and len(f_moderate) == 0) or \
            (len(fc_view) == 0 and len(fc_moderate) == 0):
            return self.none()

        if len(f_view) != 0 and len(f_moderate) != 0:
            q1 = Q(forum__in = f_view) | Q(forum__in = f_moderate)
        elif len(f_view) != 0:
            q1 = Q(forum__in = f_view)
        else:
            q1 = Q(forum__in = f_moderate)

        if len(fc_view) != 0 and len(fc_moderate) != 0:
            q2 = Q(forum__collection__in = fc_view) | \
                Q(forum__collection__in = fc_moderate)
        elif len(f_view) != 0:
            q2 = Q(forum__collection__in = fc_view)
        else:
            q2 = Q(forum__collection__in = fc_moderate)

        posts = self.filter(q2).filter(q2)

#############################################################################
#
class Discussion(models.Model):
    """Discussions, in a forum.
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    forum = models.ForeignKey(Forum)
    author = models.ForeignKey(User, db_index = True)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                      db_index = True)
    blurb = models.CharField(maxlength = 128)
    views = models.IntegerField(default = 0, editable = False)
    last_modified = models.DateTimeField(auto_now = True)
    edited = models.BooleanField(default = False)

    # Why do we have 'locked' and 'closed' for discussions when they already
    # have a 'read' and 'post' permission? Quite simply a lock or a close may
    # be a temporary item and we do not want to destructively modify the
    # permission structure for a discussion. Also we do not want permission
    # foolery to let some people around a locked or closed discussion.
    #
    # The exception is that if someone is a moderator on a forum they can
    # see and post to locked and closed discussions.
    #
    # A 'closed' discussion can be read but not modified by anyone but
    # a moderator of the forum the discussion is in.
    #
    # A 'locked' discussion can not be read or modified by anyone but
    # a moderator of the forum the discussion is in.
    #
    locked = models.BooleanField(default = False)
    closed = models.BooleanField(default = False)
    sticky = models.BooleanField(default = False)

    tags = models.GenericRelation(TaggedItem)

    objects = DiscussionManager()

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        unique_together = (("name", "forum"),)
        permissions = (("post_discussion",
                        "Can post to the discussion"),)
        
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
    def save(self):
        """We have our own save() method deal with permissions.  When you
        create this object it inherits the appropriate permissions
        from the container it is in. """

        # We need to know if we created this object or not on this save()
        # call, because we need to do something -after- it has been saved
        # if this call creates it.
        #
        created = False
        if not self.id:
            created = True

        res = super(Discussion,self).save()
    
        # Okay, if this save() created this forum, then create new row level
        # permissions on the discussion based on the permissions on the forum
        # that are said to inherit (see the 'permission_inheritance'
        # dictionary.
        #
        if created:
            inherit_permissions(self, self.forum)

        return res

#############################################################################
#
class PostManager(models.Manager):
    """Like the discussion (and forum and forum collection) managers, we
    need a method that produces a queryset that is filtered for what
    is 'viewable' by a user.

    Posts have an additional constraint, you must have 'read'
    permission on the discussion that they are in order to be able to
    read them.
    """

    def readable(self, user):
        """Returns a query set of posts that are readable by the given user. A
        post is readable if the user has view permissions on the forum
        and forum collection and read permission on the discussion
        containing a post. A post is also readable if the user has
        moderate permissions on the forum containing the discussion
        containing the post."""

        # Super user can see everything.
        #
        if user.is_authenticated() and user.is_superuser:
            return self.all()

        # So, the user must have moderate|view permissions on the
        # containing forum and forum collection, and read permission
        # on the discussion the post is contained in.
        #
        f_view = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'view_forum')
        f_moderate = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'moderate_forum')
        fc_view = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_moderate = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'moderate_forumcollection')

        # If they do not have moderate or view on any forums or forum
        # collections then having read on a specific discussion does
        # no good.
        #
        if (len(f_view) == 0 and len(f_moderate) == 0) or \
            (len(fc_view) == 0 and len(fc_moderate) == 0):
            return self.none()

        # if they have moderate or view on a fc and moderate on a f
        # they can read all posts in all discussions in the f they
        # have moderate on
        #
        # If they have moderate or view on a fc and view on a f and
        # read on a discussion then they can read all posts in that
        # discussion.
        #
        if len(f_view) != 0 and len(f_moderate) != 0:
            q1 = Q(discussion__forum__in = f_view) | \
                Q(discussion__forum__in = f_moderate)
        elif len(f_view) != 0:
            q1 = Q(discussion__forum__in = f_view)
        else:
            q1 = Q(discussion__forum__in = f_moderate)

        if len(fc_view) != 0 and len(fc_moderate) != 0:
            q2 = Q(discussion__forum__collection__in = fc_view) | \
                Q(discussion__forum__collection__in = fc_moderate)
        elif len(f_view) != 0:
            q2 = Q(discussion__forum__collection__in = fc_view)
        else:
            q2 = Q(discussion__forum__collection__in = fc_moderate)


        # Now we need to know what forums the user has read on.
        f_read = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'read_forum')
        if len(f_read) == 0 and len(f_moderate) == 0:
            return self.none()

        if len(f_read) !=0 and len(f_moderate) != 0:
            q3 = Q(discussion__in = f_read, discussion__locked = False) | \
                Q(discussion__forum__in = f_moderate)
        elif len(f_read) != 0:
            q3 = Q(discussion__in = f_read, discussion__locked = False)
        else:
            q3 = Q(discussion__forum__in = f_moderate)

        return self.filter(q3).filter(q2).filter(q1)

#############################################################################
#
class Post(models.Model):
    """Posts, in a discussion, in a forum.
    """

    author = models.ForeignKey(User, db_index = True, editable = False)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    changed = models.DateTimeField(null = True, editable = False)
    edited = models.BooleanField(default = False, editable = False)
    discussion = models.ForeignKey(Discussion, editable = False)
    post_number = models.IntegerField(db_index = True, default = 0,
                                      editable = False)
    deleted = models.BooleanField(default = False, editable = False)
    deleted_by = models.ForeignKey(User, null = True, editable = False,
                                   related_name = "deleted_posts")
    deletion_reason = models.CharField(maxlength = 128, blank = True,
                                       editable = False)
    content = models.TextField(maxlength = 4000, blank = True)
    content_html = models.TextField(maxlength = 4000, blank = True)
    markup = models.CharField(maxlength=80, blank=True, editable = False)
    in_reply_to = models.ForeignKey('self', related_name = 'replies',
                                    null = True, editable = False)
    tags = models.GenericRelation(TaggedItem, editable = False)
    views = models.IntegerField(default = 0, editable = False)
    smilies = models.BooleanField(default = True)
    signature = models.BooleanField(default = True)
    #notify = models.BooleanField(default = True)

    objects = PostManager()

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True

        # because of how we assign post numbers we can not insure that they
        # are unique per discussion.
        #
        # unique_together = (("discussion", "post_number"),)

    #########################################################################
    #
    def save(self):
        if not self.id:
            created = True
            self.created = datetime.utcnow()
            self.post_number = self.discussion.post_set.count() + 1
        else:
            created = False
            self.changed = datetime.utcnow()

        res = super(Post,self).save()

        if created:
            inherit_permissions(self, self.discussion)

        return res
    
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
