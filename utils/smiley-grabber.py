#!/usr/bin/env python
#
# Simple script to help me grab smilies from web pages which keep them
# as simple IMG tags (because no one seems to offer a simple download
# of smilies as an archive file.
#
import sys
import os
import os.path
import urllib2
import zipfile
import shutil
from BeautifulSoup import BeautifulSoup


##############################################################################
#
def get_file(url, filename):
    """The URL for a file is specified as an argument. The url is opened and
    the entire contents are downloaded.

    If no file name is specified then the basename of the URL (treated as a
    directory) is used as the file to download to.

    If no directory is specified the default TMP_DOWNLOAD_DIR will be used.
    """
    f = open(filename, 'w')
    f.write(urllib2.urlopen(url).read())
    f.close()

def main():
    url = "http://home.tiscali.nl/wildwizard/smileys3.html"
    url_base = "http://home.tiscali.nl/wildwizard/"
    imgs = BeautifulSoup(urllib2.urlopen(url).read()).html.body.findAll('img')

    for img in imgs:
        img_url = url_base + img['src']
        filename = os.path.basename(img['src'])
        print "Getting '%s' from '%s'" % (filename, img_url)
        get_file(img_url, filename)

###########
#
# The work starts here
#
if __name__ == "__main__":
    main()
#
#
###########
        
        
