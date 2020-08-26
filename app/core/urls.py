from django.conf.urls import url
from django.urls import include
from rest_framework.routers import SimpleRouter

from carzones.views import CarZoneViewSet
from members.views import MembersViewSet

router = SimpleRouter()
router.register('members', MembersViewSet)
router.register('carzones', CarZoneViewSet)

urlpatterns = [
    url('', include(router.urls)),
]
