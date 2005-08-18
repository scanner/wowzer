#
# File: $Id$
#
"""This is file contains the code to support a django view used by remote users
for submitting auctioneer data to madhouse.
"""

import zlib
import os.path
from datetime import datetime

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
    return HttpResponse("Thank you for your submission.")
