from datetime import datetime, timedelta, date
from decimal import Decimal
from collections import Counter
from django.utils.timezone import now
from django.db.models import Sum, Count, F, Min, Q
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from accounts.models import User
from b2c.orders.models import Order, OrderItem, OrderStatus
from b2c.reviews.models import Review
from b2c.products.models import Products
from visitors.models import Visitor
from b2c.user_profile.models import UserProfile
import phonenumbers
from phonenumbers import geocoder

def get_country_from_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, None)
        return geocoder.description_for_number(parsed, "en") or "Unknown"
    except Exception:
        return "Unknown"

class DashboardOverview(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            period = request.query_params.get("period", "weekly").lower()
            current_time = now()

            # Base Querysets
            orders = Order.objects.all()
            order_items = OrderItem.objects.select_related("product").all()
            users = User.objects.filter(is_staff=False)

            # Total metrics
            total_income = orders.aggregate(total=Sum("final_amount"))["total"] or Decimal("0.00")
            total_sales = order_items.count()
            total_new_customers = users.count()
            total_orders_completed = orders.filter(order_status=OrderStatus.DELIVERED).count()

            # Choose truncate function
            if period == "weekly":
                truncate_func = TruncWeek
                periods = 10
            elif period == "monthly":
                truncate_func = TruncMonth
                periods = 12
            elif period == "yearly":
                truncate_func = TruncYear
                periods = 5
            else:
                return Response({"error": "Invalid period. Use weekly, monthly, or yearly."}, status=status.HTTP_400_BAD_REQUEST)

            # Revenue grouped by period
            revenue_data = (
                orders.annotate(period=truncate_func("created_at"))
                      .values("period")
                      .annotate(total_revenue=Sum("final_amount"))
                      .order_by("period")
            )
            revenue_map = {d["period"].date(): d["total_revenue"] for d in revenue_data}

            # Completed orders grouped by period
            completed_data = (
                orders.filter(order_status=OrderStatus.DELIVERED)
                    .annotate(period=truncate_func("created_at"))
                    .values("period")
                    .annotate(completed_orders=Count("id"))
                    .order_by("period")
                )
            completed_map = {d["period"].date(): d["completed_orders"] for d in completed_data}

            # Visitors grouped by period
            visitor_data = (
                Visitor.objects.annotate(period=truncate_func("last_visit"))
                               .values("period")
                               .annotate(visitors_count=Count("id"))
                               .order_by("period")
            )
            visitor_map = {d["period"].date(): d["visitors_count"] for d in visitor_data}

            # Build trend lists
            # revenue_trend = []
            # visitors_trend = []

            # for i in range(periods):
            #     if period == "weekly":
            #         bucket_start = current_time - (i * 7 * timedelta(days=1))
            #         bucket_start = bucket_start - timedelta(days=bucket_start.weekday())
            #     elif period == "monthly":
            #         bucket_start = current_time.replace(day=1) - i * timedelta(days=30)
            #         bucket_start = bucket_start.replace(day=1)
            #     elif period == "yearly":
            #         bucket_start = current_time.replace(month=1, day=1) - i * timedelta(days=365)
            #         bucket_start = bucket_start.replace(month=1, day=1)

            #     key = bucket_start.date()
            #     revenue_trend.append({
            #         "period": bucket_start.strftime("%Y-%m-%d"),
            #         "total_revenue": float(revenue_map.get(key, 0)),
            #         "orders_completed": int(completed_map.get(key, 0)),
            #     })
            #     visitors_trend.append({
            #         "period": bucket_start.strftime("%Y-%m-%d"),
            #         "visitors": int(visitor_map.get(key, 0)),
            #     })

            # Build trend lists
            revenue_trend = []
            visitors_trend = []

            for i in range(periods):
                if period == "weekly":
                    bucket_start = current_time - timedelta(days=i*7)
                    bucket_start = bucket_start - timedelta(days=bucket_start.weekday())  # start of week
                elif period == "monthly":
                    month = (current_time.month - i - 1) % 12 + 1
                    year = current_time.year - ((current_time.month - i - 1) // 12)
                    bucket_start = current_time.replace(year=year, month=month, day=1)
                elif period == "yearly":
                    year = current_time.year - i
                    bucket_start = current_time.replace(year=year, month=1, day=1)

                key = bucket_start.date()
                revenue_trend.append({
                    "period": bucket_start.strftime("%Y-%m-%d"),
                    "total_revenue": float(revenue_map.get(key, 0)),
                    "orders_completed": int(completed_map.get(key, 0)),
                })
                visitors_trend.append({
                    "period": bucket_start.strftime("%Y-%m-%d"),
                    "visitors": int(visitor_map.get(key, 0)),
                })


            # Recent activity
            recent_reviews = Review.objects.order_by("-created_at")[:5].values(
                "id", "product__title", "user__name", "user__email", "rating", "comment", "created_at"
            )
            recent_orders = orders.order_by("-created_at")[:5].values(
                "id", "order_number", "user__name", "user__email", "final_amount", "order_status", "created_at"
            )

            # Best-selling products
            best_selling_products = (
                OrderItem.objects.values("product__id", "product__title")
                                 .annotate(total_sold=Sum("quantity"))
                                 .order_by("-total_sold")[:5]
            )

            response_data = {
                "total_income": float(total_income),
                "total_sales": total_sales,
                "total_new_customers": total_new_customers,
                "total_orders_completed": total_orders_completed,
                "revenue_trend": revenue_trend[::-1],  
                "visitors_trend": visitors_trend[::-1],
                "recent_activity": {
                    "recent_orders": list(recent_orders),
                    "recent_reviews": list(recent_reviews),
                },
                "best_selling_products": list(best_selling_products),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]
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
            
            # ✅ FIXED: Define start_date for ALL filters
            if filter_type == "weekly":
                start_date = today - timedelta(weeks=12)
            elif filter_type == "monthly":
                start_date = today.replace(day=1) - timedelta(days=365)
            else:  # yearly
                start_date = date(today.year - 5, 1, 1)

            # -------- User Growth --------
            total_users = User.objects.count()

            if filter_type == "weekly":
                growth_data = []
                for i in range(12):
                    week_start = start_date + timedelta(weeks=i)
                    week_end = week_start + timedelta(days=6)
                    count = User.objects.filter(date_joined__date__range=(week_start, week_end)).count()
                    growth_data.append({"period": f"Week {i+1}", "count": count})

            elif filter_type == "monthly":
                growth_data = []
                for i in range(12):
                    month = (today.month - i - 1) % 12 + 1
                    year = today.year - ((i + 1) // 12)
                    count = User.objects.filter(
                        date_joined__year=year, date_joined__month=month
                    ).count()
                    growth_data.insert(0, {"period": f"{year}-{month:02}", "count": count})

            else:  # yearly
                start_year = today.year - 5
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
                orders_in_range = orders_in_range.filter(created_at__gte=start_date)
            elif filter_type == "monthly":
                orders_in_range = orders_in_range.filter(created_at__gte=start_date)
            else:  # yearly
                orders_in_range = orders_in_range.filter(created_at__year__gte=today.year - 5)

            order_stats = {
                "pending": orders_in_range.filter(order_status=OrderStatus.PENDING).count(),
                "processing": orders_in_range.filter(order_status=OrderStatus.PROCESSING).count(),
                "cancelled": orders_in_range.filter(order_status=OrderStatus.CANCELLED).count(),
                "completed": orders_in_range.filter(order_status=OrderStatus.DELIVERED).count(),
            }

            total_orders = sum(order_stats.values())

            # Avoid division by zero
            if total_orders == 0:
                order_percentages = {k: 0 for k in order_stats}
            else:
                # Calculate raw percentages
                raw_percentages = {k: v / total_orders * 100 for k, v in order_stats.items()}

                # Round each except the last
                rounded_percentages = {}
                keys = list(raw_percentages.keys())
                for k in keys[:-1]:
                    rounded_percentages[k] = round(raw_percentages[k], 2)

                # Make last one = 100 - sum of others
                rounded_percentages[keys[-1]] = round(100 - sum(rounded_percentages.values()), 2)

                order_percentages = rounded_percentages

            print(order_percentages)


            # -------- Customer Segmentation --------
       

        # -------- Customer Counts --------
            new_count = User.objects.filter(date_joined__gte=start_date).count()

            returning_count = Order.objects.filter(
                order_status__in=[
                    OrderStatus.PENDING,
                    OrderStatus.PROCESSING,
                    OrderStatus.SHIPPED,
                    OrderStatus.OUT_FOR_DELIVERY,
                    OrderStatus.DELIVERED,
        
                ]
            ).values('user_id') \
            .annotate(total_orders=Count('id')) \
            .filter(total_orders__gt=1) \
            .count()

            # -------- Total Customers --------
            total_customers = new_count + returning_count

            # -------- Percentages --------
            if total_customers == 0:
                customer_segmentation = {"new": 0, "returning": 0}
            else:
                new_percent = round(new_count / total_customers * 100, 2)
                returning_percent = round(100 - new_percent, 2)
                customer_segmentation = {"new": new_percent, "returning": returning_percent}

            # -------- Use customer_segmentation --------
            print(customer_segmentation)


            

            # -------- Overall Selling (Top Products) --------
            order_items_qs = OrderItem.objects.filter(order__in=orders_in_range).values(
                "product_id", "product__title"
            ).annotate(quantity_sold=Sum("quantity")).order_by("-quantity_sold")[:5]

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

            # # -------- Customer by Country (Phone-Based) --------
            # customer_profiles = UserProfile.objects.exclude(phone_number__isnull=True).exclude(phone_number__exact="")
            # countries = []

            # for profile in customer_profiles:
            #     phone = profile.phone_number
            #     print( "Processing phone number:", phone)  
            #     try:
            #         parsed = phonenumbers.parse(phone, None)  # ✅ FIXED: Use None, not "BD"
            #         country_name = geocoder.description_for_number(parsed, "en")
            #         print("Detected country:", country_name)
            #         if country_name:
            #             countries.append(country_name)
            #     except Exception:
            #         continue

            # top_countries = Counter(countries).most_common(10)
            # print("Top countries:", top_countries)
            # customer_by_country = [{"country": c[0], "count": c[1]} for c in top_countries]



            customer_profiles = UserProfile.objects.exclude(phone_number__isnull=True).exclude(phone_number__exact="")
            countries = []

            for profile in customer_profiles:
                phone = profile.phone_number
                try:
                    # Try parsing assuming BD as fallback
                    parsed = phonenumbers.parse(phone, None)
                    if not phonenumbers.is_valid_number(parsed):
                        parsed = phonenumbers.parse(phone, "BD")  # fallback

                    region_code = phonenumbers.region_code_for_number(parsed)
                    if region_code:
                        country_name = phonenumbers.geocoder.country_name_for_number(parsed, "en")
                        if country_name:
                            countries.append(country_name)
                except Exception as e:
                    print(f"Error parsing {phone}: {e}")
                    continue

            top_countries = Counter(countries).most_common(10)
            print("Top countries:", top_countries)
            customer_by_country = [{"country": c[0], "count": c[1]} for c in top_countries]
            print("Top countries:", customer_by_country)


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