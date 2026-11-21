from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.utils.cache import add_never_cache_headers, patch_vary_headers
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response


delete_conflict = inline_serializer('DeleteConflict', fields={
    'code': serializers.CharField(),
    'detail': serializers.CharField(),
    'related_count': serializers.IntegerField(),
})


class DashboardViewSet(viewsets.ModelViewSet):
    """CRUD com proteção de vínculos e representações específicas por usuário."""

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        add_never_cache_headers(response)
        patch_vary_headers(response, ('Authorization', 'Cookie'))
        return response

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'destroy':
            return queryset.select_for_update()
        return queryset

    @extend_schema(responses={204: None, 409: delete_conflict})
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as error:
            return Response({
                'code': 'protected_relation',
                'detail': self.protected_message,
                'related_count': len(error.protected_objects),
            }, status=status.HTTP_409_CONFLICT)
