
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.aswiki.views',

    (r'^$', 'index'),
    (r'^feed/$', 'index_feed'),
    (r'^recent/', 'recent'),

    (r'^topic/', 'topic_list'),
    (r'^topic/(?P<topic_id>\d+)/$', 'topic_byid'),
    (r'^topic/(?P<slug>[a-zA-Z0-9_-]+)/$', 'topic_byslug'),
    
    (r'^topic/(?P<topic_id>\d+)/edit/$', 'topic_edit_byid'),
    (r'^topic/(?P<slug>[a-zA-Z0-9_-]+)/edit/$', 'topic_edit_byslug'),

    (r'^topic/(?P<topic_id>\d+)/rename/$', 'topic_rename_byid'),
    (r'^topic/(?P<slug>[a-zA-Z0-9_-]+)/rename/$', 'topic_rename_byslug'),

    (r'^topic/(?P<topic_id>\d+)/delete/$', 'topic_delete_byid'),
    (r'^topic/(?P<slug>[a-zA-Z0-9_-]+)/delete/$', 'topic_delete_byslug'),

    (r'^topic/(?P<topic_id>\d+)/history/$', 'topic_history_byid'),
    (r'^topic/(?P<slug>[a-zA-Z0-9_-]+)/history/$', 'topic_history_byslug'),

    (r'^topic/(?P<topic_id>\d+)/feed/$', 'topic_feed_byid'),
    (r'^topic/(?P<slug>[a-zA-Z0-9_-]+)/feed/$', 'topic_feed_byslug'),

    )
