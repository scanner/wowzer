from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.asforums.views',
    
    (r'^$', 'index'),

    (r'^forum_collections/$', 'fc_list'),
    (r'^forum_collections/create/$', 'fc_create'),
    (r'^forum_collections/(?P<fc_id>\d+)/$', 'fc_detail'),
    (r'^forum_collections/(?P<fc_id>\d+)/update/$', 'fc_update'),
    (r'^forum_collections/(?P<fc_id>\d+)/tag/$', 'fc_tag'),
    (r'^forum_collections/(?P<fc_id>\d+)/user_tag/$', 'fc_usertag'),
    (r'^forum_collections/(?P<fc_id>\d+)/delete/$', 'fc_delete'),
    (r'^forum_collections/(?P<fc_id>\d+)/create_forum/$', 'forum_create'),

    (r'^forums/$', 'obj_list_redir'),
    (r'^forums/(?P<forum_id>\d+)/$', 'forum_detail'),
    (r'^forums/(?P<forum_id>\d+)/update/$', 'forum_update'),
    (r'^forums/(?P<forum_id>\d+)/delete/$', 'forum_delete'),
    (r'^forums/(?P<forum_id>\d+)/create_discussion/$', 'disc_create'),

    (r'^discs/$', 'disc_list'),
    (r'^discs/(?P<disc_id>\d+)/$', 'disc_detail'),
    (r'^discs/(?P<disc_id>\d+)/update/$', 'disc_update'),
    (r'^discs/(?P<disc_id>\d+)/delete/$', 'disc_delete'),
    (r'^discs/(?P<disc_id>\d+)/create_post/$', 'post_create'),

    (r'^posts/$', 'obj_list_redir'),
    (r'^posts/(?P<post_id>\d+)/$','post_detail'),
    (r'^posts/(?P<post_id>\d+)/update/$','post_update'),
    (r'^posts/(?P<post_id>\d+)/delete/$','post_delete'),
    )
