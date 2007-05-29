#
# Models for 'asforums' app. These  are meant to be part of a
# project-independent "forum" application.
#
# $Id$
#

# System imports
#
from datetime import datetime, timedelta
import pytz

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
from django.contrib.contenttypes import generic

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
def add_all_permissions(obj, owner):
    """
    Adds all permissions that an object has, including its default
    'change' and 'delete' (but not 'add') as row level permissios for the
    given user.
    """
    RowLevelPermission.objects.create_default_row_permissions(obj,owner)
    for perm,ign in obj._meta.permissions:
        RowLevelPermission.objects.create_row_level_permission(obj, owner, perm)
    return

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

        fc_list = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_list.extend(RowLevelPermission.objects.get_model_list(\
                user, ForumCollection, 'moderate_forumcollection'))

        if len(fc_list) == 0:
            return self.none()
        return self.filter(id__in = fc_list)

#############################################################################
#
class ForumCollection(models.Model):
    """
    A collection of forums.

    # Create some forum collections.
    #
    # To create forum collections, we need users.
    #
    >>> from django.contrib.auth.models import User
    >>> u,ign = User.objects.get_or_create(username='fctest')

    >>> fc1,ign = ForumCollection.objects.get_or_create(name='foo1',
    ...                                                 author = u,
    ...                                                 blurb = 'no blurb')
    >>> fc2,ign = ForumCollection.objects.get_or_create(name='foo2',
    ...                                                 author = u,
    ...                                                 blurb = 'no blurb')

    # See that they exist.
    #
    >>> fc1
    <ForumCollection: foo1>
    >>> fc2
    <ForumCollection: foo2>

    # Get the listing of forums collections viewable by the author.
    #
    >>> ForumCollection.objects.viewable(u).count()
    2
    >>> ForumCollection.objects.viewable(u)
    [<ForumCollection: foo1>, <ForumCollection: foo2>]

    # Create a second user that does not have view permissions, make sure
    # that we get no forum collections back when attempting to view them.
    #
    >>> u2,ign = User.objects.get_or_create(username='noview')
    >>> ForumCollection.objects.viewable(u2).count()
    0
    >>> ForumCollection.objects.viewable(u2)
    []

    # Add view permission to fc2 and make sure that u2 can see it.
    #
    >>> RowLevelPermission.objects.create_row_level_permission(fc2, u2,
    ...                                                'view_forumcollection')
    forum collection | Can see the forum collection | user:noview | forum collection:foo2
    >>> ForumCollection.objects.viewable(u2).count()
    1
    >>> ForumCollection.objects.viewable(u2)
    [<ForumCollection: foo2>]

    # Create a third user, and give him moderate priveleges. This should let him
    # see the forum collection
    #
    >>> u3,ign = User.objects.get_or_create(username='moderator')
    >>> ForumCollection.objects.viewable(u3).count()
    0
    >>> RowLevelPermission.objects.create_row_level_permission(fc1, u3,
    ...                                             'moderate_forumcollection')
    forum collection | Can moderate all the forums in the collection | user:moderator | forum collection:foo1
    >>> ForumCollection.objects.viewable(u3)
    [<ForumCollection: foo1>]

    # When all is said and done delete the objects we created.
    #
    >>> fc1.delete()
    >>> fc2.delete()
    >>> u.delete()
    >>> u2.delete()
    >>> u3.delete()

    """
    name = models.CharField(maxlength = 128, db_index = True, unique = True,
                            blank = False)
    blurb = models.CharField(maxlength = 128)
    author = models.ForeignKey(User, db_index = True, editable = False)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    tags = generic.GenericRelation(TaggedItem)

    objects = ForumCollectionManager()

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        ordering = ['name']
        row_level_permissions = True
        permissions = (("view_forumcollection",
                        "Can see the forum collection"),
                       ("createforum_forumcollection",
                        "Can create a forum in the collection"),
                       # The following permissions - discuss,read,post,moderate
                       # are not permissions on forumcollection actions.
                       # they are permissions that are set on forums
                       # created in this forum collection.
                       ("moderate_forumcollection",
                        "Can moderate all the forums in the collection"),
                       ("discuss_forumcollection",
                        "Can create a discussion in the forum"),
                       ("read_forumcollection",
                        "Can read discussions in the forum"),
                       ("post_forumcollection",
                        "Can post to a discussion in the forum"))

    #########################################################################
    #
    def __str__(self):
        return self.name

    #########################################################################
    #
    def get_absolute_url(self):
        return "/asforums/forum_collections/%d/" % self.id

    #########################################################################
    #
    def save(self):
        """
        When creating a forum collection we make sure that the creator has
        all of the basic row level permissions for this forum collection.
        """

        # If this fc is being created we need to save that so that we can
        # add the row level permissions after it has been saved.
        #
        created = False
        if not self.id:
            created = True

        res = super(ForumCollection, self).save()

        if created:
            # If this was freshly created. Give the author all
            # permissions (except 'add' because that does not relate
            # to any instance of a fc)
            #
            add_all_permissions(self, self.author)

        return

    #########################################################################
    #
    def latest_post(self, user):
        """
        A helper function that returns the latest post in all forums in
        the forum collection.
        """
        try:
            return Post.objects.readable(user).filter(discussion__forum__collection = self).latest()
        except Post.DoesNotExist:
            return None

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
        import sys # for print stderr

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
        f_list = RowLevelPermission.objects.get_model_list(\
            user, self.model, 'view_forum')
        f_list.extend(RowLevelPermission.objects.get_model_list(\
                user, self.model, 'moderate_forum'))
        fc_list = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_list.extend(RowLevelPermission.objects.get_model_list(\
                user, ForumCollection, 'moderate_forumcollection'))

        if len(f_list) == 0 or len(fc_list) == 0:
            return self.none()
        return self.filter(id__in = f_list).filter(collection__in = fc_list)

#############################################################################
#
class Forum(models.Model):
    """A forum is a collection of discussions. It resides in a ForumCollection.

    # We need to create a forum collection, and we need an author.
    #
    >>> from django.contrib.auth.models import User, RowLevelPermission
    >>> u, ign = User.objects.get_or_create(username='fctest')

    >>> fc,ign = ForumCollection.objects.get_or_create(name='foo1',
    ...                                                author = u,
    ...                                                blurb = 'no blurb')

    >>> f,ign = Forum.objects.get_or_create(name='forum1', blurb = 'no blurb',
    ...                                     author = u, collection = fc)

    >>> f
    <Forum: forum1>

    >>> f.collection
    <ForumCollection: foo1>

    >>> fc.forum_set.all()
    [<Forum: forum1>]

    # Create another user, that does not have view permission on the forum and
    # make sure that they are not able to see this forum.
    #
    >>> u2,ign = User.objects.get_or_create(username='noview')
    >>> Forum.objects.viewable(u2)
    []

    # Now give them view permission and make sure that they can see the forum.
    #
    >>> RowLevelPermission.objects.create_row_level_permission(fc, u2,
    ...                                                'view_forumcollection')
    forum collection | Can see the forum collection | user:noview | forum collection:foo1
    >>> RowLevelPermission.objects.create_row_level_permission(f, u2,
    ...                                                        'view_forum')
    forum | Can see the forum | user:noview | forum:forum1
    >>> Forum.objects.viewable(u2)
    [<Forum: forum1>]

    # Make a 3rd user, give them moderate permission and make sure that they
    # can see the forum.
    #
    >>> u3,ign = User.objects.get_or_create(username='moderator')
    >>> RowLevelPermission.objects.create_row_level_permission(fc, u3,
    ...                                                'view_forumcollection')
    forum collection | Can see the forum collection | user:moderator | forum collection:foo1
    >>> RowLevelPermission.objects.create_row_level_permission(f, u3,
    ...                                                        'moderate_forum')
    forum | Can moderate the forum | user:moderator | forum:forum1
    >>> Forum.objects.viewable(u3)
    [<Forum: forum1>]

    # When all is said and done delete the objects we created.
    #
    >>> f.delete()
    >>> fc.delete()
    >>> u.delete()
    >>> u2.delete()
    >>> u3.delete()
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    blurb = models.CharField(maxlength = 128)
    author = models.ForeignKey(User, db_index = True, editable = False)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    collection = models.ForeignKey(ForumCollection, db_index = True,
                                   editable = False)
    tags = generic.GenericRelation(TaggedItem)

#    last_post = models.ForeignKey("Post")
#    last_post_at = models.DateTimeField(null = True, db_index = True)

    objects = ForumManager()

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        order_with_respect_to = 'collection'
        ordering = ['created']
        row_level_permissions = True
        unique_together = (("name", "collection"),)
        permissions = (("view_forum",
                        "Can see the forum"),
                       ("moderate_forum",
                        "Can moderate the forum"),
                       ("discuss_forum",
                        "Can create discussions in the forum"),
                       ("read_forum",
                        "Can read discussions in the forum"),
                       ("post_forum",
                        "Can post to discussions in the forum"))

    #########################################################################
    #
    def __str__(self):
        return self.name

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
        # The creator of the forum also gets all of the forum permissions
        # as well.
        #
        if created:
            add_all_permissions(self, self.author)
            inherit_permissions(self, self.collection)

        return res

    #########################################################################
    #
    def latest_post(self, user):
        """
        A helper function that returns the latest post in all forums in
        the forum collection.
        """
        try:
            return Post.objects.readable(user).filter(discussion__forum = self).latest()
        except Post.DoesNotExist:
            return None

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
        'read' or 'moderate' permission on the forum instance that the
        discussion is in. They must also have 'view' or 'moderate'
        permission on the forum collections that forum is contained
        in.  """

        # Super user can see everything.
        #
        if user.is_authenticated() and user.is_superuser:
            return self.all()

        # To see a discussion they must have: read and view or
        # moderate on the forum the discussion is in. They must have
        # view or moderate on the forum collection that the forum is
        # in.
        #
        # NOTE: Yes, it is possible for someone to have set it up so
        # that someone has read permission on a forum but not view on
        # the forum collection thus preventing them from seeing
        # discussions.
        #
        f_view = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'view_forum')
        f_read = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'read_forum')
        f_moderate = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'moderate_forum')
        f_view.extend(f_moderate)
        f_read.extend(f_moderate)
        fc_list = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_list.extend(RowLevelPermission.objects.get_model_list(\
                user, ForumCollection, 'moderate_forumcollection'))

        # If any of our lists is empty then they do not have the
        # requisite permissions.
        #
        if len(f_view) == 0 or len(f_read) == 0 or len(fc_list) == 0:
            return self.none()

        q1 = Q(forum__collection__in = fc_list)
        q2 = Q(forum__in = f_view) & Q(forum__in = f_read)

        return self.filter(q1).filter(q2)

#############################################################################
#
class Discussion(models.Model):
    """Discussions, in a forum. There is where all the action takes place.

    # Discussions are posted by an author and exist in a forum
    #
    >>> from django.contrib.auth.models import User, RowLevelPermission
    >>> u = User.objects.create(username='fctest')
    >>> fc = ForumCollection.objects.create(name='foo1', author = u,
    ...                                     blurb = 'no blurb')
    >>> f = Forum.objects.create(name='forum1', blurb = 'no blurb',
    ...                          author = u, collection = fc)
    >>> d1 = Discussion.objects.create(name = 'disucssion boo',
    ...                                forum = f, author = u,
    ...                                blurb = 'blurbless')
    >>> d2 = Discussion.objects.create(name = 'disucssion boo 2',
    ...                                forum = f, author = u,
    ...                                blurb = 'blurbless')
    >>> d3 = Discussion.objects.create(name = 'disucssion boo 3',
    ...                                forum = f, author = u,
    ...                                blurb = 'blurbless')

    >>> d1
    <Discussion: Discussion disucssion boo in forum forum1>
    >>> d1.forum
    <Forum: forum1>

    # The author should be able to see the created discussions.
    #
    >>> Discussion.objects.viewable(u)
    [<Discussion: Discussion disucssion boo in forum forum1>, <Discussion: Discussion disucssion boo 2 in forum forum1>, <Discussion: Discussion disucssion boo 3 in forum forum1>]

    # Create a new user that does not have view permissions (yet) and make sure
    # that they can not see any discussions.
    #
    >>> u2 = User.objects.create(username="noview")
    >>> Discussion.objects.viewable(u2)
    []

    # Now create a new forum and grant this user view permission on
    # the forum collection, then create some discussions. They should
    # be able to see these discussions but still not see the original
    # three. This should happen because the forum when created will
    # inherit read & view because the user had view on the forum
    # collection.
    #
    >>> RowLevelPermission.objects.create_row_level_permission(fc, u2,
    ...                                                  'view_forumcollection')
    forum collection | Can see the forum collection | user:noview | forum collection:foo1
    >>> f2 = Forum.objects.create(name='forum viewable', blurb = 'no blurb',
    ...                           author = u, collection = fc)
    >>> d4 = Discussion.objects.create(name = 'disucssion boo 4',
    ...                                forum = f2, author = u,
    ...                                blurb = 'blurbless')
    >>> d5 = Discussion.objects.create(name = 'disucssion boo 5',
    ...                                forum = f2, author = u,
    ...                                blurb = 'blurbless')
    >>> d6 = Discussion.objects.create(name = 'disucssion boo 6',
    ...                                forum = f2, author = u,
    ...                                blurb = 'blurbless')
    >>> Discussion.objects.viewable(u2)
    [<Discussion: Discussion disucssion boo 4 in forum forum viewable>, <Discussion: Discussion disucssion boo 5 in forum forum viewable>, <Discussion: Discussion disucssion boo 6 in forum forum viewable>]

    # And delete our forum collection when we are done.. that should get rid
    # of all forums and discussions.
    #
    >>> fc.delete()
    >>> u.delete()
    >>> u2.delete()
    """

    name = models.CharField(maxlength = 128, db_index = True, blank = False)
    forum = models.ForeignKey(Forum, editable = False)
    author = models.ForeignKey(User, db_index = True, editable = False)
    created = models.DateTimeField(auto_now_add = True, editable = False,
                                   db_index = True)
    blurb = models.CharField(maxlength = 128)
    views = models.IntegerField(default = 0, editable = False)
    last_modified = models.DateTimeField(auto_now = True)
    edited = models.BooleanField(default = False, editable = False)

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
    locked = models.BooleanField(default = False, editable = False)
    closed = models.BooleanField(default = False)
    sticky = models.BooleanField(default = False, editable = False)

    tags = generic.GenericRelation(TaggedItem)

    objects = DiscussionManager()

    class Admin:
        pass

    class Meta:
        get_latest_by = 'created'
        row_level_permissions = True
        unique_together = (("name", "forum"),)
        order_with_respect_to = 'forum'
        ordering = ['sticky', 'created']
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
        # dictionary. The creator of the discussion also gets all the
        # permissions for the discussion.
        #
        if created:
            inherit_permissions(self, self.forum)
            add_all_permissions(self, self.author)

        return res

    #########################################################################
    #
    def latest_post(self, user):
        """
        A helper function that returns the latest post in all forums in
        the forum collection.
        """
        try:
            return Post.objects.readable(user).filter(discussion__forum = self).latest()
        except Post.DoesNotExist:
            return None

    #########################################################################
    #
    def last_post_seen(self, user):
        """A helper function that will return the last post that was seen by
        this user in this discussion.

        If the user has not seen any posts in the discussion, then the first
        post is returned. If the discussion has no posts then None is returned.
        """
        pass

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
        """
        Returns a query set of posts that are readable by the given
        user. A post is readable if read and view or moderate on the
        forum the discussion is in. They must have view or moderate on
        the forum collection that the forum is in.

        If a discussion is 'locked' then the posts in that discussion
        are not readable, unless the user has moderate permission on the
        forum that the discussion is in.

        NOTE: Yes, it is possible for someone to have set it up so
        that someone has read permission on a forum but not view on
        the forum collection thus preventing them from seeing
        discussions.
        """
        # Superuser can see everything.
        #
        if user.is_authenticated() and user.is_superuser:
            return self.all()

        f_view = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'view_forum')
        f_read = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'read_forum')
        f_moderate = RowLevelPermission.objects.get_model_list(\
            user, Forum, 'moderate_forum')
        f_view.extend(f_moderate)
        f_read.extend(f_moderate)
        fc_list = RowLevelPermission.objects.get_model_list(\
            user, ForumCollection, 'view_forumcollection')
        fc_list.extend(RowLevelPermission.objects.get_model_list(\
                user, ForumCollection, 'moderate_forumcollection'))

        # If any of our lists is empty then they do not have the
        # requisite permissions.
        #
        if len(f_view) == 0 or len(f_read) == 0 or len(fc_list) == 0:
            return self.none()

        q1 = Q(discussion__forum__collection__in = fc_list)
        q2 = Q(discussion__forum__in = f_view) & Q(discussion__forum__in = f_read) & Q(discussion__locked = False)
        q3 = Q(discussion__forum__in = f_moderate)
        q4 = q2 | q3
        return self.filter(q1).filter(q4)

#############################################################################
#
class Post(models.Model):
    """
    Posts, in a discussion, in a forum.

    >>> u = User.objects.create(username='fctest')
    >>> fc = ForumCollection.objects.create(name='foo1', author = u,
    ...                                     blurb = 'no blurb')
    >>> f = Forum.objects.create(name='forum1', blurb = 'no blurb',
    ...                          author = u, collection = fc)
    >>> d1 = Discussion.objects.create(name = 'disucssion boo',
    ...                                forum = f, author = u,
    ...                                blurb = 'blurbless')
    >>> d2 = Discussion.objects.create(name = 'disucssion boo 2',
    ...                                forum = f, author = u,
    ...                                blurb = 'blurbless')
    >>> p1 = d1.post_set.create(author = u, content = "test content")
    >>> d1.post_set.create(author = u, content = "test content2",
    ...                    in_reply_to = p1)
    <Post: Post 2 in discussion disucssion boo in forum forum1>
    >>> p1.replies.all()
    [<Post: Post 2 in discussion disucssion boo in forum forum1>]

    >>> p2 = d2.post_set.create(author = u, content = "U!")
    >>> d2.post_set.create(author = u, content = "NO U!", in_reply_to = p2)
    <Post: Post 2 in discussion disucssion boo 2 in forum forum1>

    >>> p2.replies.all()
    [<Post: Post 2 in discussion disucssion boo 2 in forum forum1>]

    >>> d1.post_set.all()
    [<Post: Post 1 in discussion disucssion boo in forum forum1>, <Post: Post 2 in discussion disucssion boo in forum forum1>]

    >>> d2.post_set.all()
    [<Post: Post 1 in discussion disucssion boo 2 in forum forum1>, <Post: Post 2 in discussion disucssion boo 2 in forum forum1>]

    >>> Post.objects.readable(u).order_by('discussion', 'post_number')
    [<Post: Post 1 in discussion disucssion boo in forum forum1>, <Post: Post 2 in discussion disucssion boo in forum forum1>, <Post: Post 1 in discussion disucssion boo 2 in forum forum1>, <Post: Post 2 in discussion disucssion boo 2 in forum forum1>]

    # Now we make a new user. At first he will not have sufficient permissions
    # so no posts should be readable.
    #
    >>> u2 = User.objects.create(username="noview")
    >>> Post.objects.readable(u2).order_by('discussion', 'post_number')
    []

    # Now we give u2 the necessary permissions to read posts in our forum.
    # (NOTE: but not moderate!)
    #
    >>> RowLevelPermission.objects.create_row_level_permission(fc, u2,
    ...                                                  'view_forumcollection')
    forum collection | Can see the forum collection | user:noview | forum collection:foo1
    >>> RowLevelPermission.objects.create_row_level_permission(f, u2,
    ...                                                  'view_forum')
    forum | Can see the forum | user:noview | forum:forum1
    >>> RowLevelPermission.objects.create_row_level_permission(f, u2,
    ...                                                  'read_forum')
    forum | Can read discussions in the forum | user:noview | forum:forum1
    >>> Post.objects.readable(u2).order_by('discussion', 'post_number')
    [<Post: Post 1 in discussion disucssion boo in forum forum1>, <Post: Post 2 in discussion disucssion boo in forum forum1>, <Post: Post 1 in discussion disucssion boo 2 in forum forum1>, <Post: Post 2 in discussion disucssion boo 2 in forum forum1>]

    # Now we 'lock' discussion 'boo 2' because it has inappropriate
    # content.  u should still be able to read it, since they are a
    # moderator of f.  However u2 should not be able to see the posts
    # in 'boo 2' (but still see the ones in 'boo') because they are
    # NOT a moderator.
    >>> d2.locked = True
    >>> d2.save()

    >>> Post.objects.readable(u).order_by('discussion', 'post_number')
    [<Post: Post 1 in discussion disucssion boo in forum forum1>, <Post: Post 2 in discussion disucssion boo in forum forum1>, <Post: Post 1 in discussion disucssion boo 2 in forum forum1>, <Post: Post 2 in discussion disucssion boo 2 in forum forum1>]

    >>> Post.objects.readable(u2).order_by('discussion', 'post_number')
    [<Post: Post 1 in discussion disucssion boo in forum forum1>, <Post: Post 2 in discussion disucssion boo in forum forum1>]

    # And clean up.
    #
    >>> fc.delete()
    >>> u.delete()
    >>> u2.delete()
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
    content = models.TextField(maxlength = 16000, blank = True)
    content_html = models.TextField(maxlength = 16000, blank = True)
    markup = models.CharField(maxlength=80, blank=True, editable = False)
    in_reply_to = models.ForeignKey('self', related_name = 'replies',
                                    null = True, editable = False)
    tags = generic.GenericRelation(TaggedItem, editable = False)
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
        order_with_respect_to = 'discussion'
        ordering = ['post_number']

        # because of how we assign post numbers we can not insure that they
        # are unique per discussion.
        #
        # unique_together = (("discussion", "post_number"),)

    #########################################################################
    #
    def save(self):
        if not self.id:
            created = True
            self.created = datetime.now(pytz.utc)
            self.post_number = self.discussion.post_set.count() + 1
        else:
            created = False
            self.changed = datetime.now(pytz.utc)

        res = super(Post,self).save()

        if created:
            inherit_permissions(self, self.discussion)
            add_all_permissions(self, self.author)

        return res

    #########################################################################
    #
    def seen_by(self, user):
        """ A helper function to record the last post in a discussion that the
        user has seen (so that they can easily tell which posts they
        have not seen yet.
        """
        pass

    #########################################################################
    #
    def __str__(self):
        return "Post %d in discussion %s in forum %s" % \
            (self.post_number,
             self.discussion.name,
             self.discussion.forum.name)

    #########################################################################
    #
    def get_discussion_url(self):
        return "%s?post=%d#%d" % (self.discussion.get_absolute_url(),
                                   self.post_number, self.post_number)

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

#############################################################################
#
class LastPostSeen(models.Model):
    """
    This is a model that captures the information about the last post
    a specific user has seen in a specific discussion. We could have
    just had the fields be 'user' and 'post' as post implies
    discussion, but we wanted to better capture the spirit of this and
    also constrain it so that any given user can only have one
    'LastPostSeen' per discussion/user pair.

    Since this is a user batch many-to-many relationship we could have
    added this to the user profile, but that means we are now
    dictating even moreabout what needs to be in the user profile.

    NOTE: We need to make sure that the post is in the discussion
    indicated. I thought about using the post number.. but might as
    well just refer to the post itself directly.

    """
    user = models.ForeignKey(User, db_index = True)
    post = models.ForeignKey(Post)
    discussion = models.ForeignKey(Discussion, db_index = True)

    class Meta:
        order_with_respect_to = 'discussion'
        unique_together = (("user", "discussion"),)

# Connect the signal for a new post being created to our signal function
# that kicks off and updates various things when a post is made.
#
#dispatcher.connect(update_last_post_at, signal = signals.post_save,
#                   sender = Post)
