from django.conf.urls import url
from django.urls import include
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from cars.views import CarViewSet
from carzones.views import CarZoneViewSet
from members.views import MembersViewSet, ProfileViewSet, PhoneAuthViewSet
from prices.views import CarPriceViewSet

router = SimpleRouter(trailing_slash=False)
router.register('members', MembersViewSet)
router.register('profile', ProfileViewSet)
router.register('carzones', CarZoneViewSet)
router.register('car_prices', CarPriceViewSet)
router.register('phone_auth', PhoneAuthViewSet)

"""
carzones/123/cars
"""
carzone_router = routers.NestedSimpleRouter(router, 'carzones', lookup='carzone')
carzone_router.register('cars', CarViewSet)

urlpatterns = [
    url('', include(router.urls)),
    url('', include(carzone_router.urls)),
]
