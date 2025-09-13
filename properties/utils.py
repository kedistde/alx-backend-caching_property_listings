from django.core.cache import cache
from .models import Property
import logging
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

def get_all_properties():
    """Get all properties from cache or database"""
    cached_properties = cache.get('all_properties')
    
    if cached_properties is not None:
        return cached_properties
    
    properties = list(Property.objects.all())
    cache.set('all_properties', properties, 3600)  # Cache for 1 hour
    return properties

def get_redis_cache_metrics():
    """Get Redis cache hit/miss metrics"""
    try:
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        
        total = hits + misses
        hit_ratio = hits / total if total > 0 else 0
        
        metrics = {
            'hits': hits,
            'misses': misses,
            'total_operations': total,
            'hit_ratio': hit_ratio
        }
        
        logger.info(f"Redis Cache Metrics: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting Redis metrics: {e}")
        return None
