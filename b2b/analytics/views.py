from django.shortcuts import render
# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Sum, F
from b2b.order.models import Order, OrderItem
from b2b.product.models import Product
from b2b.inquiries.models import Inquiry
from b2b.customer.models import Customer
from django.db.models.functions import TruncMonth
from django.utils import timezone
from accounts.models import User
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
# Customer Segmentation View
from rest_framework import viewsets
from accounts .models import User
# from customer.serializers import 
from b2b.customer.serializers import CustomerSerializer
from rest_framework.response import Response
from b2b.order.models import Order 
from b2b.order.serializers import OrderSerializer
# from b2b.customer.models import CustomerProfile
from b2b.customer.models import Customer

# User Growth View
User = get_user_model()  

class UserGrowthView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Make sure 'date_joined' exists in your User model
            user_growth = User.objects.annotate(month=TruncMonth('date_joined')).values('month').annotate(count=Count('id')).order_by('month')

            # Return the response
            return Response(user_growth, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any errors that occur during querying

            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Order Status Distribution View
class OrderStatusDistributionView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Get order status distribution
        order_status_distribution = (
            Order.objects.values('order_status')
            .annotate(count=Count('id'))
        )
        return Response(order_status_distribution)

# Top Selling Products View
class TopSellingProductsView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Get the top-selling products based on order items
        top_selling_products = (
            OrderItem.objects
            .values('product')
            .annotate(total_sales=Sum(F('quantity') * F('price_at_time')))
            .order_by('-total_sales')[:10]
        )
        return Response(top_selling_products)


class CustomerSegmentationView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Segment 1: High Spenders
        high_spenders = User.objects.filter(total_spent__gt=1000) 

        # Segment 2: Low Spenders
        low_spenders = User.objects.filter(total_spent__lt=100)

        # Segment 3: Location-based segmentation (example: customers from 'New York')
        new_york_customers = User(location='New York')

        # You can dynamically calculate any segmentation data like this
        user_segment_data = {
            "high_spenders_count": high_spenders.count(),
            "low_spenders_count": low_spenders.count(),
            "new_york_customers_count": new_york_customers.count(),
        }

        return Response(user_segment_data)



# Customer by Location View
class CustomerByLocationView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Get customer count by location (location could be a field in the Customer model)
        customer_by_location = (
            Customer.objects
            .values('location')  # Assuming you have a 'location' field in your Customer model
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        return Response(customer_by_location)

# Order Statistics View
class OrderStatisticsView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # Get statistics for orders (total number, total amount, etc.)
        total_orders = Order.objects.count()
        total_amount = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum']
        pending_orders = Order.objects.filter(order_status='PENDING').count()
        completed_orders = Order.objects.filter(order_status='COMPLETED').count()

        order_stats = {
            "total_orders": total_orders,
            "total_amount": total_amount,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders
        }

        return Response(order_stats)

