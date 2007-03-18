#
# File: $Id$
#
from django.conf.urls.defaults import *

urlpatterns = patterns(
    'wowzer.main.views',  # The module name prefix.

    #
    # The top level index url.
    #
    (r'^$', 'index'),
    )
