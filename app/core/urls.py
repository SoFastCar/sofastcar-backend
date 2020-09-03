from rest_framework.routers import SimpleRouter

from cars.views import CarViewSet
from carzones.views import CarZoneViewSet
from members.views import MembersViewSet, ProfileViewSet, PhoneAuthViewSet
from prices.views import CarPriceViewSet

router = SimpleRouter()
router.register('members', MembersViewSet)
router.register('profile', ProfileViewSet)
router.register('carzones', CarZoneViewSet)
router.register('cars', CarViewSet)
router.register('car_prices', CarPriceViewSet)
router.register('phone_auth', PhoneAuthViewSet)

urlpatterns = router.urls
