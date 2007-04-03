#
# Small script to initialize asforums with some data
#
#from django.utils.lorem_ipsum import words, paragraphs
from django.contrib.auth.models import User, Group, RowLevelPermission
from wowzer.asforums.models import *
from wowzer.text.bbcode import to_html

DUMMY_TEXT = """Sed ut perspiciatis unde omnis iste natus error sit voluptatem
accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae
ab illo inventore veritatis et quasi architecto beatae vitae dicta
sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit
aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos
qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui
dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed
quia non numquam eius modi tempora incidunt ut labore et dolore magnam
aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum
exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex
ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in
ea voluptate velit esse quam nihil molestiae consequatur, vel illum
qui dolorem eum fugiat quo voluptas nulla pariatur?"""

DUMMY_TEXT_HTML = to_html(DUMMY_TEXT)

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
fc_list = []
for index in range(3):
    name = "Test Forum Collection %d" % index
    fc, created = ForumCollection.objects.get_or_create(
        name = name,
        defaults = { 'blurb' : 'Test collection',
                     'author' : u })
    fc_list.append(fc)
    if not created:
        continue

    # Moderators can moderate every forum collection.
    RowLevelPermission.objects.create_row_level_permission(fc, moderators,
                                                  'moderate_forumcollection')
    # Moderators can view every forum collection.
    RowLevelPermission.objects.create_row_level_permission(fc, moderators,
                                                        'view_forumcollection')
    for perm in ('view_forumcollection', 'read_forumcollection',
                 'discuss_forumcollection', 'post_forumcollection'):
        print  "Setting permission %s" % perm
        if index == 0:
            # Everyone can view, read, post, and create discussions in forum
            # collection 0.
            #
            RowLevelPermission.objects.create_row_level_permission(fc,
                                                                   everyone,
                                                                   perm)
        else:
            # group 0 can see fc 1, group 1 can see fc 2.
            #
            RowLevelPermission.objects.create_row_level_permission(\
                fc, groups[index-1], perm)

forum_list = []
for index in range(3):
    fc = fc_list[index]
    for f_index in range(5):
        name = "Test Forum %d-%d" % (index,f_index)
        f, created = Forum.objects.get_or_create(
            name = name,
            collection = fc,
            defaults = { 'collection' : fc,
                         'author' : u,
                         'blurb' : "Much ado about nothing, nothing at all!"}
            )
        forum_list.append(f)
        if not created:
            continue

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
                f, users[f_index], 'view_forum')

disc_list = []
for index in range(3):
    fc = fc_list[index]
    for f_index in range(5):
        f = forum_list[f_index]
        for d_index in range(20):
            dname = "Discussion %d" % d_index
            d,created = Discussion.objects.get_or_create(
                name = dname,
                forum = f,
                defaults = {'author' : u,
                            'blurb'   : "blurbity blurb lorem ipsum",
                            })
            disc_list.append(d)
            if not created:
                continue
            
            print "Created discussion %s" % d.name

for index in range(3):
    fc = fc_list[index]
    for f_index in range(5):
        f = forum_list[f_index]
        for d_index in range(20):
            d = disc_list[d_index]
            for i in range(20):
                p = Post.objects.create(author = u, discussion = d,
                                        content = DUMMY_TEXT,
                                        content_html = DUMMY_TEXT_HTML,
                                        markup = "text.bbcode" )
                print "Created post: %s" % str(p)
