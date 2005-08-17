#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for submitting auctioneer data to madhouse.
"""

from django.utils.httpwrappers import HttpResponse

#############################################################################
#
def submit(request):
    return HttpResponse("Hello, world. You're at the madhouse submission " \
                        "page.")

