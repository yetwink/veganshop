from django.urls import path
from .views import *

urlpatterns = [
    path('', MainPageView.as_view(), name='index'),
    path('shop/', ShopPageView.as_view(), name='shop'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('blog/', blog_view, name='blog'),
    path('product/<slug:slug>/', ProductDetail.as_view(), name='product'),
    path('login_register/', login_register, name='login_register'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('cart/', cart, name='cart'),
    path('to_cart/<int:product_id>/<str:action>/', to_cart, name='to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', success, name='success'),
    path('payment/', create_checkout_session, name='payment')
]
