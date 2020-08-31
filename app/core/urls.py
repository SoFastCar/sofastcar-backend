from django.conf.urls import url
from django.urls import include
from rest_framework.routers import SimpleRouter

from cars.views import CarViewSet
from carzones.views import CarZoneViewSet
from members.views import MembersViewSet
from prices.views import CarPriceViewSet

router = SimpleRouter()
router.register('members', MembersViewSet)
router.register('carzones', CarZoneViewSet)
router.register('cars', CarViewSet)
router.register('car_prices', CarPriceViewSet)

urlpatterns = [
    url('', include(router.urls)),
]
