from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^$', include('wowzer.main.urls')),
    (r'^main/$', include('wowzer.main.urls')),
    (r'^toons/', include('wowzer.toons.urls')),
    (r'^items/', include('wowzer.items.urls')),
    (r'^raidtracker/', include('wowzer.raidtracker.urls')),
    (r'^asforums/', include('wowzer.asforums.urls')),

    # Basic account stuff.
    #
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/change_pw/$', 'django.contrib.auth.views.password_change'),
    (r'^accounts/reset_pw/$', 'django.contrib.auth.views.password_reset'),
    
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
