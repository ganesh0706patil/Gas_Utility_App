from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('booking/', views.booking, name='booking'),
    path('logout/', views.logout_view, name='logout'),
    path('status/', views.status, name='status'),
    path('support/', views.support, name='support'),
    path("profile/", views.profile, name="profile"),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'), 
]
