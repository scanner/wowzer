#
# $Id$
#
# Description:
#   This defines the model's for tracking Gatherer information.
#
from django.core import meta
from django.models.auth import User

# Wowzer model imports - continents & zones
from django.models.world import Zone, Continent

#############################################################################
#
class GatherType(meta.Model):
    """
    """
    gtype = meta.IntegerField(primary_key = True, db_index = True)
    name  = meta.CharField(maxlength = 128, db_index = True)

#############################################################################
#
class GatherIcon(meta.Model):
    """
    """
    icon = meta.IntegerField(primary_key = True, db_index = True)
    image = meta.CharField(maxlength = 1024)
    
#############################################################################
#
class GatherItem(meta.Model):
    """
    """

    gather_type       = meta.ForeignKey(GatherType, db_index = True)
    continent         = meta.ForeignKey(Continent, db_index = True)
    zone              = meta.ForeignKey(Zone, db_index = True)
    name              = meta.CharField(maxlength = 128, db_index = True)
    x                 = meta.FloatField()
    y                 = meta.FloatField()
    icon              = meta.ForeignKey(GatherIcon)
    count             = meta.IntegerField()
    submitted_by      = meta.ForeignKey(User, null = True, blank = True)
    also_submitted_by = meta.ManyToManyField(User, null = True, blank = True)
    trusted           = meta.BooleanField(default = False)
