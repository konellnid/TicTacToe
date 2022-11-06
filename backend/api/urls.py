# api/urls.py

from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('', views.getRoutes),
    path('test/', views.testEndPoint, name='test'),
    path('find_game/', views.find_game_end_point, name='find_game'),
    path('current_game/', views.current_game, name='current_game'),
    path('make_move/', views.make_move, name='make_move'),
    path('statistics/', views.statistics, name='statistics'),
]
