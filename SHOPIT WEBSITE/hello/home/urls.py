from django.urls import path
from . import views

urlpatterns = [
    # Home & Static Pages
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('seller/', views.seller, name='seller'),
    
    # Products
    path('products/', views.products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart & Checkout
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    
    # Addresses
    path('save-address/', views.save_address, name='save_address'),
    
    # Support
    path('support/', views.create_support_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # Returns
    path('return/<str:order_id>/', views.request_return, name='request_return'),
    
    # API
    path('api/validate-coupon/', views.validate_coupon, name='validate_coupon'),
]
