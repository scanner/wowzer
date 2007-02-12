#
# File: $Id$
#
from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',  # The module name prefix.

    #
    # The top level index url.
    #
    (r'^$', 'wowzer.main.views.index'),
    )
