from django.urls import path
from booking import views
from .webhooks import webhook

urlpatterns = [
    path('fetch-calendly-data/<int:pk>/',
         views.fetch_calendly_data_view, name='fetch_calendly_data'),
    path('schedule-success/<int:pk>/',
         views.ScheduleSuccessView.as_view(), name='schedule_success'),
    path('payments/<int:pk>/', views.payment_view, name='payments'),
    path('payments/create/', views.PaymentCreateView.as_view(),
         name='payment_create'),
    path('payments/success/<int:pk>',
         views.PaymentDetailView.as_view(), name='payment_success'),
    path('wh/', webhook, name='webhook'),
    path('cache-payment-data/', views.cache_payment_data,
         name='cache_payment_data'),
    path('cancel-session/<int:pk>/',
         views.cancel_session_view, name='cancel_session'),
]
