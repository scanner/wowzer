#
# Small script to initialize asforums with some data
#
from django.contrib.auth.models import User
from wowzer.asforums.models import *

u, created = User.objects.get_or_create(username = 'scanner',
                                        defaults = { 'is_staff' : True,
                                                     'is_active' : True })

for name in ('Test','Test2'):
    fc, ign = ForumCollection.objects.get_or_create(name = name, \
                                     defaults = { 'slug' : name,
                                                  'blurb' : 'Test collection',
                                                  'creator' : u })
    for name in ('test1', 'test2', 'test3', 'test4'):
        f, ign = Forum.objects.get_or_create(name = name,
                                        defaults = { 'slug' : name,
                                                     'collection' : fc,
                                                     'creator' : u })
        print "Created forum '%s'" % str(f)
        for dname in ('disc1','disc2','disc3'):
            d,created = Discussion.objects.get_or_create(name = name,
                                                         forum = f,
                                                 defaults = { 'slug' : name,
                                                              'creator' : u})
            if created:
                for i in range(20):
                    p = Post.objects.create(creator = u, discussion = d,
                                            post = "Test test test test")
