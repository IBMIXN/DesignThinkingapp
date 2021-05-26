from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile', views.profile, name='profile'),
    path('newdesign', views.newdesign, name='newdesign'),
    path('review/<str:id>', views.review, name='review'),
    path('help', views.helpPage, name='help'),
    path('dashboard', views.dashboard, name='dashboard')
]
