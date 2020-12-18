from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register('accounts', views.AccountViewSet, basename='AccountAPI')
router.register('transfers', views.TransfersViewSet, basename='TransferAPI')

urlpatterns = router.urls