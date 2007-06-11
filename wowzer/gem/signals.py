#
# File: $Id$
#
"""
Signal handlers for the gem application.
"""
import threading


#############################################################################
#
class GemDataJobThread(threading.Thread):
    """
    We start processing a gem data job in its own thread so that
    the response to a web request is not blocked waiting for the job
    to finish.
    """

    #########################################################################
    #
    def run(self):
        """
        This is just a wrapper around the 'process_jobs()' function in the
        gemdataloader module that does all the real work.
        """
        import wowzer.gem.gemdataloader
        
        wowzer.gem.gemdataloader.process_jobs()
        return

#############################################################################
#
def process_jobs(sender, instance, signal, *args, **kwargs):
    """
    This is the receiver for the 'post_save' on a GemDataJob object.
    If the object is in the state 'PENDING' then fire off our thread
    to process 'PENDING' jobs.
    """
    from wowzer.gem.models import GemDataJob
    
    if instance.state == GemDataJob.PENDING:
        GemDataJobThread().start()
    return
