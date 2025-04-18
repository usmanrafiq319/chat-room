from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('room/<int:pk>/', views.room, name='room'),
    path('create-room/', views.createRoom, name='create-room'),
    path('profile/<int:pk>/', views.userProfile, name='user-profile'),
    path('update-room/<int:pk>', views.updateRoom, name='update-room'),
    path('update-user/', views.updateUser, name='update-user'),
    path('delete-room/<int:pk>', views.DeleteRoom, name='delete-room'),
    path('delete-message/<int:pk>', views.DeleteMessage, name='delete-message'),
    path('login/', views.LoginPage, name='login'),
    path('register/', views.registerPage, name='register'), 
    path('logout/', views.logoutUser, name='logout'),
    path('topic/', views.allTopics, name='topics'),
    path('activity/', views.usersActivity, name='messages'),

]