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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('b2c/api/',include('accounts.urls')),
    path('b2c/api/',include('support.urls')),
    path('b2c/api/notifications/', include('notifications.urls')),
    path('b2c/api/',include('b2c.products.urls')), 
    path('api/cart/',include('b2c.cart.urls')), 
    path('api/shipping/',include('b2c.checkout.urls')), 
    # path('api/shipping/', include('b2c.shipping.urls')),
    path('b2c/api/orders/',include('b2c.orders.urls')), 
    path('b2c/api/payment/',include('b2c.payments.urls')), 
    path('b2c/api/',include('b2c.reviews.urls')), 
    path('b2c/api/messages/',include('b2c.chat.urls')),
    # path('b2c/api/accounts/', include('accounts.urls')),    
    path('b2c/api/',include('b2c.user_profile.urls')),          
    # admin
    path('b2c/api/',include('b2c.admin.admin_profile.urls')),
    path('b2c/api/admin/', include('b2c.admin.add_product.urls')),
    path('b2c/api/', include('b2c.admin.coupons.urls')),

    # b2b
    # path('b2b/api/',include('accounts_b.urls')),
    path('b2b/api/', include('b2b.analytics.urls')),
    path('b2b/api/', include('b2b.product.urls')),
    path('b2b/api/', include('b2b.inquiries.urls')),
    path('b2b/api/', include('b2b.order.urls')),
    path('b2b/api/', include('b2b.connections.urls')),
    path('b2b/api/', include('b2b.customer.urls')),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

