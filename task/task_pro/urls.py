from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.create_user, name='create_user'),
    path('login/', views.login, name='login_user'),
    path('', views.list_users, name='list_users'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
]
