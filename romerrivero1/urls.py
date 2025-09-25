"""
URL configuration for romerrivero1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from b2c.payments.views import StripeWebhookView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('b2c/api/',include('accounts.urls')),
    path('b2c/api/',include('support.urls')),
    path('b2c/api/notifications/', include('notifications.urls')),
    path('b2c/api/',include('b2c.products.urls')), 
    path('b2c/api/',include('b2c.cart.urls')), 
    path('b2c/api/',include('b2c.checkout.urls')), 
    path('b2c/api/',include('b2c.orders.urls')), 
    path('b2c/api/payment/',include('b2c.payments.urls')),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'), 
    path('b2c/api/',include('b2c.reviews.urls')), 
    path('b2c/api/',include('b2c.chat.urls')), 
    path('b2c/api/',include('b2c.wishlist.urls')), 
    path('b2c/api/',include('b2c.wishlist.urls')), 
    path('b2c/api/',include('b2c.promotions.urls')),          
    # admin
    path('b2c/api/',include('b2c.admin.admin_profile.urls')),
    path('b2c/api/', include('b2c.user_profile.urls')),
    path('b2c/api/', include('dashboard.urls')),
    path('b2c/api/', include('visitors.urls')),
    path('b2c/api/', include('b2c.customers.urls')),
    path('b2c/api/', include('b2c.coupons.urls')),
    
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

