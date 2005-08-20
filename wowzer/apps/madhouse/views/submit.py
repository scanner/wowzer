#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for submitting auctioneer data to madhouse.
"""

import zlib
import os.path
from datetime import datetime

# We do not support the in-django threading stuff at this time. Breaks under
# mod_python
##import wowzer.apps.madhouse.maintenance

from django.models.madhouse import uploaddatas
from django.utils.httpwrappers import HttpResponse

#############################################################################
#
def submit(request):
    """Processes a blind request from a client hopefully sent as a POST with
    two keys (user and password), and one file ('auction_data').
    """
    files = request._get_files()

    # This is going to be huge.. 
    #
    time = datetime.now()
    data = zlib.decompress(files['auction_data']['content'])
    filename = "%s-%04d.%02d.%02d-%02d:%02d:%02d.%06d" % \
               (files['auction_data']['filename'], time.year, time.month,
                time.day, time.hour, time.minute, time.second,
                time.microsecond)
    full_path = os.path.join("/var/tmp/wowzer-uploads/madhouse", filename)
    df = open(full_path, 'w')
    df.write(data)
    df.close()
    del data

    ud = uploaddatas.UploadData(filename = full_path, uploaded_at = time,
                                processed = False)
    ud.save()

    # Now poke the auctioneer importer object in to wakefullness so it will
    # process any new datums we have. We will bring this back when we support
    # something like this.. perhaps a forked subprocess? Hmmm.. that might
    # do it.
    #
##    try:
##        wowzer.apps.madhouse.maintenance.auctioneer_import_thread.wakeup()
##    except:
##        print "Ooops. Unable to wake up the madhouse maintenance thread."
    
    return HttpResponse("Thank you for your submission.")

#############################################################################
#
def poke_ud_queue(request):
    """The 'submit' view is there for uploading data to the server and then
    poking the worker thread that processes the queue. The queue will run
    checks at four hour intervals but sometimes we may want to force the queue
    to check immediately. Poking this URL will cause that to happen.
    """

    # Now poke the auctioneer importer object in to wakefullness so it will
    # process any new datums we have. We will bring this back when we support
    # something like this.. perhaps a forked subprocess? Hmmm.. that might
    # do it.
    #
##    try:
##        wowzer.apps.madhouse.maintenance.auctioneer_import_thread.wakeup()
##    except:
##        print "Ooops. Unable to wake up the madhouse maintenance thread."
    return HttpResponse("The queue has been poked..")

