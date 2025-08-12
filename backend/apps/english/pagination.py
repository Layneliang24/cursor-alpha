from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'OK',
            'data': data,
            'pagination': {
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'total': self.page.paginator.count
            }
        })
