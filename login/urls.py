from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path


urlpatterns = [
    path('', TokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='login_token_refresh')
]