from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', include('wowzer.main.urls')),
    (r'^main/$', include('wowzer.main.urls')),
    (r'^toons/', include('wowzer.toons.urls')),
    (r'^items/', include('wowzer.items.urls')),
    (r'^raidtracker/', include('wowzer.raidtracker.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
