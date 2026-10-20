from django.contrib import admin
from django.urls import path, include  # <-- make sure 'include' is here
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:pk>/', views.category, name='category'),
    path('shop/', views.shop, name='shop'),
    path('about/', views.about, name='about'), 

    path('contact/', views.contact, name='contact'),
    path('product/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('search/', views.search, name='search'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('success/', views.thankyou, name='payment_success'),
    path('checkout/', views.checkout, name='checkout'), # ADD THIS
    path('payment/', views.payment, name='payment'),
    path('thankyou/', views.thankyou, name='thankyou'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.track_order, name='track_order'),
]