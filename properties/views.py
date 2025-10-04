from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Property

# Example 1: Get all properties as JSON
def property_list(request):
    properties = Property.objects.all()
    data = [
        {
            'id': property.id,
            'title': property.title,
            'description': property.description,
            'price': str(property.price),
            'location': property.location,
            'created_at': property.created_at.isoformat(),
        }
        for property in properties
    ]
    return JsonResponse({'properties': data})

# Example 2: Get single property by ID
def property_detail(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    data = {
        'id': property.id,
        'title': property.title,
        'description': property.description,
        'price': str(property.price),
        'location': property.location,
        'created_at': property.created_at.isoformat(),
    }
    return JsonResponse(data)

# Example 3: Create new property (API endpoint)
@csrf_exempt
@require_http_methods(["POST"])
def create_property(request):
    try:
        data = json.loads(request.body)
        property = Property.objects.create(
            title=data.get('title'),
            description=data.get('description'),
            price=data.get('price'),
            location=data.get('location'),
        )
        return JsonResponse({
            'id': property.id,
            'message': 'Property created successfully',
            'data': {
                'title': property.title,
                'description': property.description,
                'price': str(property.price),
                'location': property.location,
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Example 4: Search properties
def search_properties(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    
    properties = Property.objects.all()
    
    if query:
        properties = properties.filter(title__icontains=query)
    if location:
        properties = properties.filter(location__icontains=location)
    
    data = [
        {
            'id': property.id,
            'title': property.title,
            'price': str(property.price),
            'location': property.location,
        }
        for property in properties
    ]
    return JsonResponse({'results': data, 'count': len(data)})

# Example 5: Health check endpoint
def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'properties API'})
