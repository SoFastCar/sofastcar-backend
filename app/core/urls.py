from rest_framework.routers import SimpleRouter

from carzones.views import CarZoneViewSet
from members.views import MembersViewSet

router = SimpleRouter()
router.register('members', MembersViewSet)
router.register('carzones', CarZoneViewSet)

urlpatterns = router.urls
