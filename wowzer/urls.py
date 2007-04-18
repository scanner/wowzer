from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^$', include('wowzer.main.urls')),
    (r'^main/', include('wowzer.main.urls')),
    (r'^toons/', include('wowzer.toons.urls')),
    (r'^items/', include('wowzer.items.urls')),
    (r'^raidtracker/', include('wowzer.raidtracker.urls')),
    (r'^asforums/', include('wowzer.asforums.urls')),
    (r'^users/', include ('wowzer.users.urls')),

    # The 'registration' app takes over the accounts/ urls.
    #
    (r'^accounts/', include ('wowzer.registration.urls')),
    
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
