from django.db.models import Sum, Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from datetime import datetime, timedelta
from b2c.orders.models import Order, OrderItem
from b2c.reviews.models import Review
from b2c.products.models import Products
from visitors.models import Visitor
from datetime import timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from accounts. models import User
from rest_framework import status
from django.db.models import Count, Sum, F
from collections import Counter
import phonenumbers
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum
from django.utils.timezone import now
from datetime import timedelta, date
from collections import Counter
import phonenumbers
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth import get_user_model
from b2c.orders.models import Order
from b2c.user_profile.models import UserProfile

# from b2c.sales.models import Sale  

class DashboardOverview(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admin can access

    def get(self, request):
        try:
            period = request.query_params.get("period", "weekly").lower()
            now = datetime.now()

            # Base querysets
            orders = Order.objects.all()
            order_items = OrderItem.objects.select_related("product").all()

            # Total calculations
            total_income = orders.aggregate(total=Sum("total_amount"))["total"] or 0
            total_orders = orders.count()
            total_sales = order_items.count()
            orders_completed = orders.filter(order_status="DELIVERED").count()

            # Determine time filter and annotation function
            if period == "weekly":
                start_date = now - timedelta(days=7)
                truncate_func = TruncWeek
            elif period == "monthly":
                start_date = now - timedelta(days=30)
                truncate_func = TruncMonth
            elif period == "yearly":
                start_date = now - timedelta(days=365)
                truncate_func = TruncYear
            else:
                return Response({"error": "Invalid period. Use weekly, monthly, or yearly."}, status=status.HTTP_400_BAD_REQUEST)

            # Filtered revenue
            revenue_queryset = orders.filter(created_at__gte=start_date).annotate(period=truncate_func("created_at"))
            revenue_data = (
                revenue_queryset
                .values("period")
                .annotate(total_revenue=Sum("total_amount"))
                .order_by("period")
            )

            # Filtered recent reviews
            recent_reviews = Review.objects.filter(created_at__gte=start_date).order_by("-created_at")[:5].values(
                "id", "product__title", "user__email", "rating", "comment", "created_at"
            )

            # Recent orders (always latest 5)
            recent_orders = orders.order_by("-created_at")[:5].values(
                "id", "order_number", "user__email", "total_amount", "order_status", "created_at"
            )

            # Best-selling products
            best_selling_products = (
                OrderItem.objects.values("product__id", "product__title")
                .annotate(total_sold=Sum("quantity"))
                .order_by("-total_sold")[:5]
            )

            # Visitors today
            today = now.date()
            current_visitors = Visitor.objects.filter(last_visit__date=today).count()

            response_data = {
                "total_income": total_income,
                "total_sales": total_sales,
                "total_orders": total_orders,
                "orders_completed": orders_completed,
                "revenue": list(revenue_data),
                "recent_activity": {
                    "recent_orders": list(recent_orders),
                    "recent_reviews": list(recent_reviews),
                },
                "best_selling_products": list(best_selling_products),
                "visitors": current_visitors,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class AnalyticsView(APIView):
    """
    Analytics Dashboard:
    - User Growth
    - Order Statistics
    - Customer Segmentation
    - Overall Selling (Top Products)
    - Customer by Country
    """

    def get(self, request):
        try:
            filter_type = request.query_params.get("filter", "monthly").lower()
            if filter_type not in ["weekly", "monthly", "yearly"]:
                return Response(
                    {"error": "Invalid filter. Use weekly, monthly, or yearly."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            today = now().date()

            # -------- User Growth --------
            total_users = User.objects.count()

            if filter_type == "weekly":
                start_date = today - timedelta(weeks=12)  # last 12 weeks
                period_format = "week"  # for response
                users_qs = User.objects.filter(date_joined__gte=start_date)
                growth_data = []
                for i in range(12):
                    week_start = start_date + timedelta(weeks=i)
                    week_end = week_start + timedelta(days=6)
                    count = users_qs.filter(date_joined__date__range=(week_start, week_end)).count()
                    growth_data.append({"period": f"Week {i+1}", "count": count})

            elif filter_type == "monthly":
                start_date = today.replace(day=1) - timedelta(days=365)  # last 12 months
                growth_data = []
                for i in range(12):
                    month = (today.month - i - 1) % 12 + 1
                    year = today.year - ((i + 1) // 12)
                    count = User.objects.filter(
                        date_joined__year=year, date_joined__month=month
                    ).count()
                    growth_data.insert(0, {"period": f"{year}-{month:02}", "count": count})

            else:  # yearly
                start_year = today.year - 5  # last 6 years
                growth_data = []
                for i in range(6):
                    year = start_year + i
                    count = User.objects.filter(date_joined__year=year).count()
                    growth_data.append({"period": str(year), "count": count})

            user_growth = {
                "total": total_users,
                "new_users": sum([d["count"] for d in growth_data]),
                "growth_data": growth_data,
            }

            # -------- Order Statistics --------
            orders_in_range = Order.objects.all()
            if filter_type == "weekly":
                orders_in_range = orders_in_range.filter(created_at__gte=today - timedelta(weeks=12))
            elif filter_type == "monthly":
                orders_in_range = orders_in_range.filter(created_at__gte=today - timedelta(days=365))
            else:  # yearly
                orders_in_range = orders_in_range.filter(created_at__year__gte=today.year - 5)

            order_stats = {
                "completed": orders_in_range.filter(order_status="completed").count(),
                "pending": orders_in_range.filter(order_status="pending").count(),
                "processing": orders_in_range.filter(order_status="processing").count(),
                "cancelled": orders_in_range.filter(order_status="cancelled").count(),
            }

            # -------- Customer Segmentation --------
            new_customers = User.objects.filter(date_joined__gte=start_date).count()
            returning_customers = max(
                orders_in_range.values("user").distinct().count() - new_customers, 0
            )
            customer_segmentation = {"new": new_customers, "returning": returning_customers}

            # -------- Overall Selling (Top Products) --------
            order_items_qs = OrderItem.objects.filter(order__in=orders_in_range).values(
                "product_id", "product__title"
            ).annotate(quantity_sold=Sum("quantity")).order_by("-quantity_sold")[:10]

            def rating_label(qty):
                if qty >= 30:
                    return "Excellent"
                elif qty >= 20:
                    return "Good"
                elif qty >= 10:
                    return "Average"
                else:
                    return "Bad"

            top_products = [
                {
                    "product_id": item["product_id"],
                    "title": item["product__title"],
                    "quantity_sold": item["quantity_sold"],
                    "rating": rating_label(item["quantity_sold"]),
                }
                for item in order_items_qs
            ]

            # -------- Customer by Country (Phone-Based) --------
            customer_profiles = UserProfile.objects.exclude(phone_number="").values("phone_number")
            countries = []
            for entry in customer_profiles:
                phone = entry["phone_number"]
                try:
                    parsed = phonenumbers.parse(phone, None)
                    country = phonenumbers.region_code_for_number(parsed)
                    if country:
                        countries.append(country)
                except Exception:
                    continue

            top_countries = Counter(countries).most_common(10)
            customer_by_country = [{"country": c[0], "count": c[1]} for c in top_countries]

            # -------- Final Response --------
            data = {
                "filter": filter_type,
                "user_growth": user_growth,
                "order_statistics": order_stats,
                "customer_segmentation": customer_segmentation,
                "top_products": top_products,
                "customer_by_country": customer_by_country,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
