#
# File: $Id$
#
"""
RSS Feeds for the asforums app.

These are based on the django.contrib.syndication module. We use its
feed builder. But we use our own views to actually render the feeds.

"""

from django.contrib.syndication.feeds import Feed
from wowzer.asforums.models import Post, Discussion

############################################################################
#
class LatestPosts(Feed):
    """
    This is a feed that renders up the 30 latest posts that a specific user
    can see.
    """

    title = "Latest Posts"
    description = "The latests posts that have been made in the forums"
    link = "/asforums/posts/"

    ########################################################################
    #
    def __init__(self, slug, feed_url, user):
        """
        We need to redefine the __init__ method so that we can stow
        away the user that is attempting to view this feed.
        """
        self.user = user
        super(LatestPosts, self).__init__(slug, feed_url)
        return

    ########################################################################
    #
    def items(self):
        """
        Return the query set of the 30 latest posts readable by this
        user, sorted by so that the most recent posts appear first.
        """
        return Post.objects.readable(self.user).order_by('-created')[:30]

############################################################################
#
class LatestPostsByForumDiscussion(Feed):
    """
    Like 'LatestPosts' except this groups all the posts by forum and
    discussion within forum.
    """

    title = "Latest Posts, by Forum and Discussion"
    description = "The latests posts that have been made in the forums " \
                  "grouped by forum and discussion within forum."
    link = "/asforums/posts/"

    ########################################################################
    #
    def __init__(self, slug, feed_url, user):
        """
        We need to redefine the __init__ method so that we can stow
        away the user that is attempting to view this feed.
        """
        self.user = user
        super(LatestPostsByForumDiscussion, self).__init__(slug, feed_url)
        return

    ########################################################################
    #
    def items(self):
        """
        Return the query set of the 30 latest posts readable by this
        user, sorted by so that the most recent posts appear first.
        """
        return Post.objects.readable(self.user).order_by('-discussion',
                                                         '-created')[:30]
