#
# Small script to initialize asforums with some data
#
from django.contrib.auth.models import User, Group, RowLevelPermission
from wowzer.asforums.models import *

users = []
groups = []

everyone, created = Group.objects.get_or_create(name = "everyone")
moderators, created = Group.objects.get_or_create(name = "moderators")

for index in range(2):
    name = 'group%d' % index
    g, created = Group.objects.get_or_create(name = name)
    groups.append(g)

for index in range(4):
    name = 'user%d' % index
    u, created = User.objects.get_or_create(username = name)
    if created:
        u.set_password(name)
        # Every user is in the 'everyone' group.
        #
        u.groups.add(everyone)

        # Stick alternating useres in different groups.
        #
        u.groups.add(groups[index % 2])
        u.save()
    users.append(u)

# Make sure scanner exists, and is in the 'everyone' group and is
# in the moderator group.
#
scanner, created = User.objects.get_or_create(username = 'scanner',
                                              defaults = { 'is_staff' : True,
                                                           'is_active' : True })
scanner.groups.add(everyone)
scanner.groups.add(moderators)
scanner.save()

# Create a bunch of forum collections that have a bunch of forums in them.
# The forums have a bunch of discussions, and the discussions have posts
# in them. Set up some permissions on who can see these forums.
#
for index in range(3):
    name = "Test Forum Collection %d" % index
    fc, ign = ForumCollection.objects.get_or_create(
        name = name,
        defaults = { 'blurb' : 'Test collection',
                     'creator' : u })
    
    RowLevelPermission.objects.create_row_level_permission(fc, scanner,
                                                           'moderate')
    if index == 0:
        # Everyone can see forum collection 0.
        #
        RowLevelPermission.objects.create_row_level_permission(fc, everyone,
                                                               'view')
    else:
        # group 0 can see fc 1, group 1 can see fc 2.
        #
        RowLevelPermission.objects.create_row_level_permission(fc,
                                                               groups[index-1],
                                                               'view')
        
    for f_index in range(5):
        name = "Test Forum %d-%d" % (index,f_index)
        f, created = Forum.objects.get_or_create(
            name = name,
            collection = fc,
            defaults = { 'collection' : fc,
                         'creator' : u,
                         'blurb' : "Much ado about nothing, nothing at all!"}
            )
        if created:
            print "Created forum '%s'" % str(f)
            # Forum 0-3 are only viewable by users 0-3, 4 has no
            # specific viewable permission, defaulting to that of the
            # forum collection.  This means we will get some odd cases
            # where a forum is viewable by a user that does not have
            # view permission on the forum collection (which means
            # that they still can not view this forum.)
            #
            if f_index < 4:
                RowLevelPermission.objects.create_row_level_permission(
                    f, users[f_index], 'view')
        for dname in ('disc1','disc2','disc3'):
            d,created = Discussion.objects.get_or_create(
                name = name,
                forum = f,
                defaults = {'creator' : u})

            if created:
                for i in range(20):
                    p = Post.objects.create(creator = u, discussion = d,
                                            post = "Test test test test")
