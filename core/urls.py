from django.contrib import admin
from django.urls import path, include
from parking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.register, name='register'),  # Default route to register
    path('home/', views.home, name='home'),  # Home page
    path('login/', views.login_view, name='login'),  # Login view
    path('logout/', views.logout_view, name='logout'),  # Logout view
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard view
    path('parking/', include('parking.urls')),  # Include parking app URLs
    path('contact/', views.contact, name='contact'),  # Contact view
]
