from django.conf.urls.defaults import *
from wowzer.raidtracker.models import *

date_info_dict = {
    'queryset'   : Raid.objects.all(),
    'date_field' : 'start_time',
}

info_dict = {
    'queryset'    : Raid.objects.all(),
}

urlpatterns = patterns(
    'django.views.generic',  # The module name prefix.
    #
    # Generic list & detail
    #
    (r'^raid/$',
     'list_detail.object_list', dict(info_dict, paginate_by=30)),
    (r'^raid/(?P<object_id>\d+)/$',
     'list_detail.object_detail', info_dict),
    #
    # Date based
    #
    (r'^raid/date/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
     'date_based.archive_day',   date_info_dict),
    (r'^raid/date/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
     'date_based.archive_month', date_info_dict),
    (r'^raid/date/(?P<year>\d{4})/$',
     'date_based.archive_year',  date_info_dict),
    (r'^raid/date/?$',
     'date_based.archive_index', date_info_dict),
)
