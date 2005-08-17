#!/usr/bin/env python
#
"""'ecs' stands for 'Extract Compress and Send.' These are a series of scripts
to extract relevant variable declarations from the named file (usually
SavedVariables.lua), compress it, and then send it to the specified wowzer app
on the specified http server.

This script is specifically for data for the madhouse module to process.  What
we are extracting are a couple of variables that the Auctioneer AddOn saves in
your SavedVariables.lua file.

We compress it because it is freaking huge, but plain text, so it
compresses well.
"""

import zlib
import os
import os.path
import string
import exceptions
import optparse
import re

# We map the verbosity level strings in to an integer. Makes for easier
# comparisons "if verbosity > verbose_levels['terse']:"
#
verbose_levels = {
    "quiet"   : 0,
    "terse"   : 5,
    "verbose" : 10,
    "debug"   : 15,
    }

############################################################################
#
def post_multipart(host, selector, fields, files):
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)  
    headers = {
        'User-Agent': 'INSERT USERAGENTNAME',
        'Content-Type': content_type
        }
    h.request('POST', selector, body, headers)
    res = h.getresponse()
    return res.read()


############################################################################
#
def run(filename, submit_url, user, password, verbosity = 5):
    """The workhouse of this script. We break the work up in to three parts:
    1) Read in the lua file and extract out the text for the variable
       declarations we care about using some huge assumptions about the
       formatting of the file.
    2) Compress the data using zlib.
    3) Send the compressed data to the server via the submit_url.
    """

    # Read the file in. This will cause a huge sucking sound as this file can
    # be rather large (19mb in many cases!)
    #
    if verbosity >= 10:
        print "Opening file '%s'" % filename
    f = open(filename, 'r')
    data = f.read()
    f.close()
    if verbosity >= 10:
        print "Done reading data in from file. Closing file."

    # Our resulting data goes in this variable.
    #
    extracted = ""

    # The regular expressions we use are simplistic and ASSUME A LOT. We assume
    # that 1) The variable declaration is going to be at the beginning of a
    # line and always "^varname =", 2) we assume that we are ONLY loading lua
    # hash tables and that the hash table is ended by _the first_ "}" at the
    # beginning of a line after the varname declaration.
    #
    re_endbrace = re.compile(r'^}', re.MULTILINE)
    
    # For madhouse we care about just two Auctioneer variables: AHSnapshot and
    # AuctionPrices. 
    for varname in ['AHSnapshot', 'AuctionPrices']:
        re_start = re.compile("^%s =" % varname, re.MULTILINE)
        if verbosity >= 10:
            print "Extracting variable declaration '%s'" % varname

        try:
            start = re_start.search(data).start()
            end = self.re_endbrace.search(data, start).end()
            extracted += data[start:end] + "\n"
        except:
            # Should really be prepared for an re to fail here and do something
            # somewhat gracefully with it.
            #
            raise

    # We no longer need to keep 'data' in memory. Let gc'ing happen.
    #
    del data
    
    # Now in 'extracted' we have all of our variable declarations that we care
    # about. We need to compress this (many megs to few megs! Really important
    # for those network transfers!)
    #
    if verbosity >= 5:
        print "Compressing data."
    compressed = zlib.compress(extracted)

    if verbosity >= 10:
        print "Done comrpessing data."

    # We can flush the extracted data too now. All that matters is the
    # compressed data.
    #
    del extracted

    # And finally we submit our data to the web app.
        
    
    
############################################################################
#
def setup_option_parser():
    """This function uses the python OptionParser module to define an option
    parser for parsing the command line options for this script. This does not
    actually parse the command line options. It returns the parser object that
    can be used for parsing them.
    """
    parser = optparse.OptionParser(usage = "%prog [options]",
                                   version = "%prog 1.0")
    parser.add_option("-v", "--verbosity", type="choice", dest="verbosity",
                      default="terse", choices = verbose_levels.keys(),
                      help = """Controls how talkative the script is about what
                      it is doing. In 'verbose' mode it will tell you
                      every track it finds. In 'terse' mode it will only tell
                      you about tracks that are changed, added or removed.
                      In 'quiet' mode it will say nothing. DEFAULT:
                      '%default'""")
    parser.add_option("-f", "--file", type="string", dest="filename",
                      default="SavedVariables.lua", help = """Designates the
                      file to load and extract variables to send to the wowzer
                      server. This file MUST be in the format saved by World of
                      Warcraft as the 'SavedVariables.lua' file. DEFAULT:
                      '%default'""")
    parser.add_option("-s", "--submit", type="string", dest="submit_url",
                      default="http://wowzer.apricot.com/madhouse/submit",
                      help = """The url to which the extracted and compressed
                      variables are sent. DEFAULT: '%default'""")
    parser.add_otpion("-u", "--user", type="string", dest="wowzer_user",
                      default = "noone",
                      help = """The user to send this batch of data to the
                      server as. Right now this is not used but in the future
                      we will only allow specific trusted users to submit
                      data.""")
    parser.add_option("-p", "--password", type="string", dest="wowzer_pw",
                      default = "nopassword",
                      help = """Along with a user name the submitter must have
                      a password to authenticate to the server with. Right now
                      this is not used but in the future we will only allow
                      specific trusted users to submit data.""")

    return parser

############################################################################   
##
##
def main():
    """The main entry point is only used if running this script as a standalone
    program. This will parse our the command line options and then call the
    'run()' routine with all the required parameters.

    The 'run()' routine does all the actual work. This way someone can import
    this script as a module and just call run() with the requisite parameters
    if they want to have an uber script that launches several of these ecs
    scripts.
    """

    parser = setup_option_parser()
    (opts, args) = parser.parse_args()

    verbosity = verbose_levels[opts.verbosity]
    if verbosity >= 3:
        print "Processing file: '%s'" % opts.filename
        print "Submitting as %s to: %s" % (opts.user, opts.submit_url)
    
    run(filename = opts.filename, submit_url = opts.submit_url, user =
        opts.user, password = opts.password, verbosity = verbosity)

    print "All done."

###########
#
# The work starts here
#
if __name__ == "__main__":
    main()
#
#
###########
