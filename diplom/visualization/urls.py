from django.urls import path
from .views import room_visualization

app_name = 'visualization'
urlpatterns = [
    path('', room_visualization, name='viz'),
]
