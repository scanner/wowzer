
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.asforums.views',

    (r'^$', 'index'),
    (r'^feed/$', 'index_feed'),

    (r'^forum_collections/$', 'fc_list'),
    (r'^forum_collections/tag/(?P<tag>[^/]+(?u))/$', 'fc_tag'),
    (r'^forum_collections/perms/$', 'fc_create_perm'),
    (r'^forum_collections/create/$', 'fc_create'),
    (r'^forum_collections/(?P<fc_id>\d+)/$', 'fc_detail'),
    (r'^forum_collections/(?P<fc_id>\d+)/perms/$', 'fc_perms'),
    (r'^forum_collections/(?P<fc_id>\d+)/update/$', 'fc_update'),
    (r'^forum_collections/(?P<fc_id>\d+)/delete/$', 'fc_delete'),
    (r'^forum_collections/(?P<fc_id>\d+)/create_forum/$', 'forum_create'),

    (r'^forums/$', 'obj_list_redir'),
    (r'^forums/tag/(?P<tag>[^/]+(?u))/$', 'forum_tag'),
    (r'^forums/(?P<forum_id>\d+)/$', 'forum_detail'),
    (r'^forums/(?P<forum_id>\d+)/perms/$', 'forum_perms'),
    (r'^forums/(?P<forum_id>\d+)/update/$', 'forum_update'),
    (r'^forums/(?P<forum_id>\d+)/delete/$', 'forum_delete'),
    (r'^forums/(?P<forum_id>\d+)/create_discussion/$', 'disc_create'),

    (r'^discs/$', 'disc_list'),
    (r'^discs/tag/(?P<tag>[^/]+(?u))/$', 'disc_tag'),
    (r'^discs/feed/new/$', 'disc_feed_new'),
    (r'^discs/feed/latest/$', 'disc_feed_latest'),
    (r'^discs/feed/subscribed/$', 'disc_feed_subscribed'),
    (r'^discs/(?P<disc_id>\d+)/$', 'disc_detail'),
    (r'^discs/(?P<disc_id>\d+)/perms/$', 'disc_perms'),
    (r'^discs/(?P<disc_id>\d+)/subunsub/$', 'disc_subunsub'),
    (r'^discs/(?P<disc_id>\d+)/update/$', 'disc_update'),
    (r'^discs/(?P<disc_id>\d+)/lock/$', 'disc_lock'),
    (r'^discs/(?P<disc_id>\d+)/unlock/$', 'disc_unlock'),
    (r'^discs/(?P<disc_id>\d+)/close/$', 'disc_close'),
    (r'^discs/(?P<disc_id>\d+)/open/$', 'disc_open'),
    (r'^discs/(?P<disc_id>\d+)/delete/$', 'disc_delete'),
    (r'^discs/(?P<disc_id>\d+)/create_post/$', 'post_create'),

    (r'^posts/$', 'obj_list_redir'),
    (r'^posts/tag/(?P<tag>[^/]+(?u))/$','post_tag'),
    (r'^posts/feed/latest/$', 'post_feed_latest'),
    (r'^posts/feed/discussion/$', 'post_feed_latest_by_discussion'),
    (r'^posts/(?P<post_id>\d+)/$','post_detail'),
    (r'^posts/(?P<post_id>\d+)/perms/$','post_detail'),
    (r'^posts/(?P<post_id>\d+)/update/$','post_update'),
    (r'^posts/(?P<post_id>\d+)/delete/$','post_delete'),
    )
