from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property

@receiver([post_save, post_delete], sender=Property)
def invalidate_property_cache(sender, **kwargs):
    """Invalidate the all_properties cache on Property changes"""
    cache.delete('all_properties')
