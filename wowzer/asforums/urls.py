from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.asforums.views',
    (r'^$', 'index'),
    (r'^forum_collections/$', 'forum_coll_list'),
    (r'^forum_collections/(?P<forum_id>\d+)/$', 'forum_coll_detail'),
    (r'^forums/$', 'forum_list'),
    (r'^forums/(?P<forum_id>\d+)/$', 'forum_detail'),
    (r'^forums/(?P<forum_id>\d+)/(?P<disc_id>\d+)/$', 'disc_detail'),
    (r'^forums/(?P<forum_id>\d+)/(?P<disc_id>\d+)/(?P<post_id>\d+)/$',
     'post_detail'),
    )
