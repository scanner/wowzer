from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.users.views',
    
    (r'^$', 'index'),

    (r'^groups/$', 'group_list'),
    (r'^groups/(?P<groupname>\w+)/$', 'group_detail'),

    (r'^(?P<username>\w+)/$', 'user_detail'),
    (r'^(?P<username>\w+)/update/$', 'user_update'),
    (r'^(?P<username>\w+)/delete/$', 'user_deactivate'),
    (r'^(?P<username>\w+)/activate/$', 'user_activate'),
    (r'^(?P<username>\w+)/create/$', 'user_create'),

    # This is part of our "groups belong to users" paradigm.
    #
    (r'^(?P<username>\w+)/group/$', 'group_index'),
    (r'^(?P<username>\w+)/group/create/$', 'group_create'),
    (r'^(?P<username>\w+)/group/(?P<group_id>\d+)/$', 'group_detail'),
    (r'^(?P<username>\w+)/group/(?P<group_id>\d+)/delete/$', 'group_delete'),
    
    )
    
