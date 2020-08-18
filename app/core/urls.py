from django.conf.urls import url
from django.urls import include
from rest_framework.routers import SimpleRouter

from members.views import MembersViewSet

router = SimpleRouter()
router.register('members', MembersViewSet)

urlpatterns = [
    url('', include(router.urls)),
]
