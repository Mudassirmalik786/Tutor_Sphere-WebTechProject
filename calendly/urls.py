from django.urls import path
from calendly import views

urlpatterns = [
    path('connect/', views.connect_calendly, name='connect_calendly'),
    path('auth/', views.calendly_auth, name='calendly_auth'),
    path('disconnect/<int:pk>/', views.disconnect_calendly,
         name='disconnect_calendly'),
]
