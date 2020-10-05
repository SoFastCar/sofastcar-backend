from django.urls import path, include
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg import openapi

"""
for docs
"""
schema_view = get_schema_view(
    openapi.Info(
        title='SoFastCar Backend API',
        default_version='v1',
        description='SoCar Clone App Backend (DRF)',
        contact=openapi.Contact(email='hsw0905@gmail.com'),
        license=openapi.License(name="MIT Licence"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)
