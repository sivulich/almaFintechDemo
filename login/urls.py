from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from login import views

router = routers.SimpleRouter()
router.register('users', views.UserViewSet, basename='AccountAPI')
router.register('profiles', views.ProfileViewSet, basename='TransferAPI')


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_token_refresh')
]

urlpatterns += router.urls
