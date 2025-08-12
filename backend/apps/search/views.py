from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def search_view(request):
    q = request.query_params.get('q', '')
    return Response({
        "success": True,
        "message": "search placeholder",
        "data": {
            "query": q,
            "results": []
        }
    })


