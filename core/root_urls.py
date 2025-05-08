from django.urls import path
from parking.views import end_parking, book_slot, start_parking

urlpatterns = [
    path('book-slot/<int:slot_id>/', book_slot, name='book_slot'),
    path('start-parking/<int:booking_id>/', start_parking, name='start_parking'),
    path('end-parking/<int:booking_id>/', end_parking, name='end_parking'),
]