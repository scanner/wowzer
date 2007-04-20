from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.users.views',
    
    (r'^$', 'index'),
    (r'^create/$', 'user_create'),
    (r'^groups/$', 'group_list'),
    (r'^groups/(?P<groupname>\w+)/$', 'group_detail'),

    (r'^(?P<username>\w+)/$', 'user_detail'),

    # This is part of our "groups belong to users" paradigm.
    #
    (r'^(?P<username>\w+)/group/$', 'group_index'),
    (r'^(?P<username>\w+)/group/create/$', 'group_create'),
    (r'^(?P<username>\w+)/group/(?P<group_id>\d+)/$', 'group_detail'),
    (r'^(?P<username>\w+)/group/(?P<group_id>\d+)/delete/$', 'group_delete'),
    
    )
    
