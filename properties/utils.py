from django.core.cache import cache
from .models import Property
import logging
from django_redis import get_redis_connection

from django.db.models import Count, Avg
from .models import Property

def calculate_average_price(properties=None):
    """Calculate average property price with zero division handling"""
    if properties is None:
        properties = Property.objects.all()
    
    total_price = sum(property.price for property in properties if property.price)
    total_requests = len([p for p in properties if p.price is not None])
    
    average_price = total_price / total_requests if total_requests > 0 else 0
    return round(average_price, 2)

def get_property_statistics():
    """Get comprehensive property statistics"""
    stats = Property.objects.aggregate(
        total_properties=Count('id'),
        properties_with_price=Count('id', filter=models.Q(price__isnull=False)),
        average_price=Avg('price')
    )
    
    # Handle cases where no properties have prices
    avg_price = stats['average_price'] if stats['average_price'] is not None else 0
    price_ratio = (stats['properties_with_price'] / stats['total_properties']) if stats['total_properties'] > 0 else 0
    
    return {
        'total_properties': stats['total_properties'],
        'properties_with_price': stats['properties_with_price'],
        'average_price': round(avg_price, 2),
        'price_coverage_ratio': round(price_ratio * 100, 2)
    }

def calculate_success_rate(properties):
    """Calculate success rate for properties (e.g., sold/active ratio)"""
    successful_properties = properties.filter(status='sold')
    total_requests = properties.count()
    
    success_rate = (successful_properties.count() / total_requests) * 100 if total_requests > 0 else 0
    return round(success_rate, 2)

def get_location_statistics():
    """Get statistics by location"""
    locations = Property.objects.values('location').annotate(
        property_count=Count('id'),
        avg_price=Avg('price')
    )
    
    stats = []
    for location in locations:
        avg_price = location['avg_price'] if location['avg_price'] is not None else 0
        stats.append({
            'location': location['location'],
            'property_count': location['property_count'],
            'average_price': round(avg_price, 2),
            'market_share': (location['property_count'] / Property.objects.count()) * 100 if Property.objects.count() > 0 else 0
        })
    
    return stats

def calculate_search_conversion_rate(search_requests, successful_searches):
    """Calculate conversion rate for property searches"""
    conversion_rate = (successful_searches / search_requests) * 100 if search_requests > 0 else 0
    return round(conversion_rate, 2)

def price_per_square_foot(property):
    """Calculate price per square foot with error handling"""
    if hasattr(property, 'square_footage') and property.square_footage:
        price_per_sqft = property.price / property.square_footage if property.square_footage > 0 else 0
        return round(price_per_sqft, 2)
    return 0

def get_property_engagement_metrics(property):
    """Calculate engagement metrics for a property"""
    views = getattr(property, 'views', 0)
    inquiries = getattr(property, 'inquiries', 0)
    favorites = getattr(property, 'favorites', 0)
    
    engagement_rate = (inquiries / views) * 100 if views > 0 else 0
    favorite_rate = (favorites / views) * 100 if views > 0 else 0
    
    return {
        'views': views,
        'inquiries': inquiries,
        'favorites': favorites,
        'engagement_rate': round(engagement_rate, 2),
        'favorite_rate': round(favorite_rate, 2)
    }

def calculate_batch_processing_stats(processed, total, errors=0):
    """Calculate batch processing statistics"""
    success_rate = ((processed - errors) / total) * 100 if total > 0 else 0
    error_rate = (errors / total) * 100 if total > 0 else 0
    completion_rate = (processed / total) * 100 if total > 0 else 0
    
    return {
        'processed': processed,
        'total': total,
        'errors': errors,
        'success_rate': round(success_rate, 2),
        'error_rate': round(error_rate, 2),
        'completion_rate': round(completion_rate, 2)
    }

def calculate_price_reduction_percentage(original_price, current_price):
    """Calculate price reduction percentage"""
    if original_price > 0 and current_price < original_price:
        reduction = ((original_price - current_price) / original_price) * 100
        return round(reduction, 2)
    return 0

def get_property_recommendation_score(property, user_preferences):
    """Calculate recommendation score based on user preferences"""
    score = 0
    total_criteria = 0
    
    # Price match
    if user_preferences.get('max_price') and property.price <= user_preferences['max_price']:
        score += 1
    total_criteria += 1 if user_preferences.get('max_price') else 0
    
    # Location match
    if user_preferences.get('preferred_locations') and property.location in user_preferences['preferred_locations']:
        score += 1
    total_criteria += 1 if user_preferences.get('preferred_locations') else 0
    
    # Calculate final score
    recommendation_score = (score / total_criteria) * 100 if total_criteria > 0 else 0
    return round(recommendation_score, 2)

def format_property_metrics_for_display(properties):
    """Format property metrics for API response"""
    total_properties = properties.count()
    active_properties = properties.filter(status='active').count()
    sold_properties = properties.filter(status='sold').count()
    
    active_rate = (active_properties / total_properties) * 100 if total_properties > 0 else 0
    sold_rate = (sold_properties / total_properties) * 100 if total_properties > 0 else 0
    
    return {
        'total_properties': total_properties,
        'active_properties': active_properties,
        'sold_properties': sold_properties,
        'active_rate': round(active_rate, 2),
        'sold_rate': round(sold_rate, 2),
        'available_rate': round(100 - sold_rate, 2)
    }
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
