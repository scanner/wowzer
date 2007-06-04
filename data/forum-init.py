#
# Small script to initialize asforums with some data
#
#from django.utils.lorem_ipsum import words, paragraphs
import random
from django.contrib.auth.models import User, Group, RowLevelPermission
from django.contrib.webdesign.lorem_ipsum import paragraphs, sentence
from wowzer.asforums.models import *
from wowzer.text.bbcode import to_html

num_discussions = 22
posts_per_discussion = 25
users = []
groups = []

def create_fcs(users):
    for index in range(4):
        name = "%s's Forum Collection" % users[index].username
        fc, created = ForumCollection.objects.get_or_create(
            name = name,
            defaults = { 'blurb' : 'Where %s rules the roost' % \
                         users[index].username,
                         'author' : users[index] })

        if created:
            print "Created fc: %s" % fc
            # Moderators can moderate every forum collection.
            RowLevelPermission.objects.create_row_level_permission(fc,
                                                    moderators,
                                                    'moderate_forumcollection')
            # And give everyone else the standard set of permissions.
            #
            for perm in ('view_forumcollection', 'read_forumcollection',
                         'discuss_forumcollection', 'post_forumcollection'):
                RowLevelPermission.objects.create_row_level_permission(fc,
                                                                      everyone,
                                                                      perm)
        # Make sure each FC has 4 forums.
        #
        create_forums(users, fc, index)

def create_forums(users, fc, fc_i):
    for index in range(3):
        name = "Forum %d-%d" % (index, fc_i)
        f, created = Forum.objects.get_or_create(
            name = name, collection = fc,
            defaults = { 'blurb'  : sentence()[:120] + "...",
                         'author' : random.choice(users) })
        if created:
            print "Created forum %s" % f
        create_discussions(users, f, index)

def create_discussions(users,f,f_i):
    for index in range(num_discussions):
        name = "Discussion %d" % index
        d, created = Discussion.objects.get_or_create(
            name = name, forum = f,
            defaults = { 'blurb'  : sentence()[:120] + "...",
                         'author' : random.choice(users) })
        if created:
            print "Created discussion %s" % d
        create_posts(users, d)

def create_posts(users, d):
    needed = posts_per_discussion - d.post_set.count()
    print "need to create %d posts for discussion %s" % (needed, d)
    for index in range(needed):
        text = '\n\n'.join(paragraphs(3, common = True))
        html_text = to_html(text)
        p = Post.objects.create(author = random.choice(users), discussion = d,
                                content = text,
                                content_html = html_text,
                                markup = "text.bbcode" )

everyone, created = Group.objects.get_or_create(name = "system:everyone")
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
if created:
    scanner.set_password('testtest')
scanner.groups.add(everyone)
scanner.groups.add(moderators)
scanner.save()

# Create a bunch of forum collections that have a bunch of forums in them.
# The forums have a bunch of discussions, and the discussions have posts
# in them. Set up some permissions on who can see these forums.
#
create_fcs(users)
