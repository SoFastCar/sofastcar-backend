from rest_framework.routers import SimpleRouter

from members.views import MembersViewSet

router = SimpleRouter()
router.register('members', MembersViewSet)

urlpatterns = router.urls
