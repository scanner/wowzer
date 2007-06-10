
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.asforums.gem',

    (r'^$', 'index'),
    (r'^submit/$', 'submit_gemdata'),
    (r'^events/$', 'event_list'),
    (r'^events/feed/$', 'event_feed'),
    (r'^events/tag/(?P<tag>[^/]+(?u))/$', 'event_tag'),
    (r'^events/(?P<event_id>\d+)/$', 'event_detail'),
    (r'^events/(?P<event_id>\d+)/update/$', 'event_update'),

    (r'^datajobs/$', 'datajob_list'),
    (r'^datajobs/(?P<job_id>\d+)/$', 'datajob_detail'),

    )
