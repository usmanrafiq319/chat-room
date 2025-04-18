from django.urls import path
from . import views


urlpatterns = [
    path('', views.getRouts),
    path('rooms', views.getRooms),
    path('room/<int:pk>', views.getRoom),

]