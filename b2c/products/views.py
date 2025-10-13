
import csv
import uuid
import logging
import requests
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework import permissions, status
from django.db.models import Q, Avg
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Products, ProductCategory
from .serializers import ProductSerializer, CategorySerializer
from .enums import ProductStatus
from rest_framework.permissions import AllowAny
# b2c/products/views.py
from rest_framework import generics
from django.utils import timezone
from django.db.models import Avg, DecimalField
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import Products, ProductStatus
from django.db.models import Q, Avg, Value
from rest_framework import status, permissions
from django.db.models import Avg, FloatField
from difflib import SequenceMatcher
logger = logging.getLogger(__name__)

# -------------------------
# ===== ADMIN CATEGORY VIEWS =====
# -------------------------

class AdminCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "message": " Category created successfully!",
                "category": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminCategoryRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                "message": "Category updated successfully!",
                "category": response.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        category_name = instance.name
        # if instance.products.exists():
        #     return Response(
        #         {"error": f"Cannot delete category '{category_name}' because it has products."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        self.perform_destroy(instance)
        return Response({
            "message": f"🗑️ Category '{category_name}' deleted successfully!"
        }, status=status.HTTP_200_OK)


class AdminCategoryBulkDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]
    permission_classes = None

    def delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No category IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        categories = ProductCategory.objects.filter(id__in=ids)
        deleted_count = 0
        failed = []

        for c in categories:
            if c.products.exists():
                failed.append(c.name)
                continue
            c.delete()
            deleted_count += 1

        return Response({
            "message": f"{deleted_count} categories deleted successfully",
            "failed": failed
        }, status=status.HTTP_200_OK)

# -------------------------
# ===== ADMIN PRODUCT VIEWS =====
# -------------------------

class AdminProductListCreateView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'status']

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            discount = data.get("discount", 0)
            try:
                discount = float(discount)
                if discount < 0 or discount > 100:
                    return Response({"error": "Discount must be between 0 and 100."},
                                    status=status.HTTP_400_BAD_REQUEST)
                data["discount"] = discount
            except ValueError:
                return Response({"error": "Discount must be a number."},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            # serializer = ProductSerializer(queryset, many=True, context={"request": request})
            self.perform_create(serializer)
            return Response({
                "message": "Product added successfully!",
                "product": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminProductRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                "message": "Product updated successfully!",
                "product": response.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_title = instance.title
        self.perform_destroy(instance)
        return Response({
            "message": f"🗑️ Product '{product_title}' deleted successfully!"
        }, status=status.HTTP_200_OK)


class AdminProductBulkDelete(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"error": "No product IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        products = Products.objects.filter(id__in=ids)
        deleted_count = products.count()

        # Optional: Delete images
        for product in products:
            if product.images:
                for path in product.images:
                    try:
                        default_storage.delete(path)
                    except Exception as e:
                        logger.warning(f"Failed to delete image {path}: {str(e)}")

        products.delete()
        return Response({"message": f"{deleted_count} products deleted successfully"}, status=status.HTTP_200_OK)


class AdminProductStatusListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        status_param = self.request.query_params.get("status", "").strip().lower()
        if status_param == "active":
            return Products.objects.filter(status=ProductStatus.ACTIVE)
        elif status_param == "inactive":
            return Products.objects.filter(status=ProductStatus.INACTIVE)
        return Products.objects.none()


# -------------------------
# ===== USER CATEGORY & PRODUCT VIEWS =====
# -------------------------



class UserCategoryListView(generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny] 
    pagination_class = None 



class UserCategoryProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Products.objects.filter(category_id=category_id, status=ProductStatus.ACTIVE)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProductSerializer(queryset, many=True, context={"request": request})
        print("serializers",serializer)
        return Response(serializer.data)



# ------------------------
class TopProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        limit = self.request.query_params.get("limit", 10)
        try:
            limit = int(limit)
            if limit <= 0:
                raise ValueError
        except ValueError:
            raise ValidationError({"error": "Invalid limit value. Must be a positive integer."})

        # Annotate average rating
        queryset = Products.objects.annotate(
            average_rating=Coalesce(
                Avg("reviews__rating"),
                0.0,
                output_field=DecimalField(max_digits=3, decimal_places=1)
            )
        ).order_by('-average_rating', '-id')

        return queryset[:limit]  # DRF will automatically serialize with many=True


# ------------------------
# Limited Deals Products View
# ------------------------

class LimitedDealsPagination(PageNumberPagination):
    page_size = 8 
    page_size_query_param = 'page_size' 
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })


class LimitedDealsProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitedDealsPagination

    def get_queryset(self):
        now = timezone.now()
        return Products.objects.filter(
            limited_deal_price__isnull=False,
            limited_deal_start__lte=now,
            limited_deal_end__gte=now,
            status="active"
        ).order_by("-limited_deal_end")




class UserProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_queryset(self):
        # Annotate each product with average_rating
        return (
            Products.objects.filter(status=ProductStatus.ACTIVE)
            .annotate(average_rating=Avg('reviews__rating')) 
        )



# Route 2: Load More (show all products, no pagination)
class UserProductLoadMoreView(generics.ListAPIView):
    queryset = Products.objects.filter(status=ProductStatus.ACTIVE)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']
    # disable pagination
    pagination_class = None


class UserProductDetailView(generics.RetrieveAPIView):
    queryset = Products.objects.filter(status=ProductStatus.ACTIVE)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"    
    lookup_url_kwarg = "id"


class UserProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        products = Products.objects.filter(status=ProductStatus.ACTIVE)

        if query:
            products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass
        return products


# -------------------------
# ===== CATEGORY FILTER + PAGINATION =====
# -------------------------
class CategoryProductFilterPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryProductFilterView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q")
        category_param = request.query_params.get("category")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        price_sort = request.query_params.get("price_sort")
        name_sort = request.query_params.get("name_sort")
        min_rating = request.query_params.get("min_rating")
        max_rating = request.query_params.get("max_rating")
        products = Products.objects.all().annotate(
       average_rating=Avg("reviews__rating", output_field=FloatField())
      )

        products = Products.objects.all().annotate(
    average_rating=Coalesce(Avg("reviews__rating", output_field=FloatField()), Value(0.0), output_field=FloatField())
)

        # 🔎 Search by title or description
        if query:
            products = products.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        # 📂 Category filter (id or name)
        if category_param:
            if category_param.isdigit():
                products = products.filter(category__id=int(category_param))
            else:
                products = products.filter(category__name__icontains=category_param)

        # 💰 Price filters
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                return Response({"error": "Invalid min_price"}, status=status.HTTP_400_BAD_REQUEST)

        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                return Response({"error": "Invalid max_price"}, status=status.HTTP_400_BAD_REQUEST)
    

        # ⭐ Rating filter
        rating_param = request.query_params.get("rating") 


        if rating_param:
            try:
                rating_val = float(rating_param)

                if rating_val >= 5:
                    # Only show exact 5.0 products
                    products = products.filter(average_rating__gte=5.0)
                else:
                    # Show products within the clicked rating range, e.g., 4 → 4.0 ≤ rating < 5.0
                    products = products.filter(
                        average_rating__gte=rating_val,
                        average_rating__lt=rating_val + 1
                    )
            except ValueError:
                return Response({"error": "Invalid rating filter"}, status=status.HTTP_400_BAD_REQUEST)


        # ↕ Sorting
        if price_sort:
            products = products.order_by("price" if price_sort.lower() == "asc" else "-price")
        elif name_sort:
            products = products.order_by("title" if name_sort.lower() == "asc" else "-title")
        else:
            products = products.order_by("-id")  # default newest first

        # ✅ Serialize results
        serializer = ProductSerializer(products, many=True, context={"request": request})

        return Response({
            "count": products.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)



# -------------------------
# ===== PRODUCT SEARCH/UPLOAD CSV =====
# -------------------------


def similar(a, b):
    """Helper function to check similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class ProductSearchFilterView(APIView):
    permission_classes = [permissions.AllowAny]  

    def get(self, request):
        query = request.query_params.get("q", "")
        category_param = request.query_params.get("category")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        price_sort = request.query_params.get("price_sort")
        name_sort = request.query_params.get("name_sort")
        min_rating = request.query_params.get("min_rating")
        max_rating = request.query_params.get("max_rating")
        status_param = request.query_params.get("status")

        # 🧮 Base queryset with average rating
        products = Products.objects.all().annotate(
            average_rating=Coalesce(
                Avg("reviews__rating", output_field=FloatField()), 
                Value(0.0), 
                output_field=FloatField()
            )
        )

        # 🔍 Smart Search (multi-word + typo tolerance)
        if query:
            keywords = query.split()
            matched_ids = set()

            for product in products:
                title = product.title.lower()
                desc = product.description.lower() if product.description else ""

                for word in keywords:
                    # Fuzzy match or partial inclusion
                    if (
                        word.lower() in title
                        or word.lower() in desc
                        or similar(word, title) > 0.7  # "sumsang" → "samsung"
                    ):
                        matched_ids.add(product.id)
                        break  # stop after one match per product

            products = products.filter(id__in=matched_ids)

        # 📂 Category filter (id or name)
        if category_param:
            if category_param.isdigit():
                products = products.filter(category__id=int(category_param))
            else:
                products = products.filter(category__name__icontains=category_param)

        # 💰 Price filters
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                return Response({"error": "Invalid min_price"}, status=status.HTTP_400_BAD_REQUEST)

        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                return Response({"error": "Invalid max_price"}, status=status.HTTP_400_BAD_REQUEST)

        # ⚡ Status filter
        if status_param:
            if status_param.lower() in [ProductStatus.ACTIVE, ProductStatus.INACTIVE]:
                products = products.filter(status=status_param.lower())
            else:
                return Response({"error": "Invalid status filter"}, status=status.HTTP_400_BAD_REQUEST)

        # ⭐ Rating filters
        try:
            if min_rating:
                min_rating_val = float(min_rating)
                products = products.filter(average_rating__gte=min_rating_val)
                if min_rating_val > 0:
                    products = products.exclude(average_rating=0.0)
            if max_rating:
                max_rating_val = float(max_rating)
                products = products.filter(average_rating__lte=max_rating_val)
        except ValueError:
            return Response({"error": "Invalid rating filter"}, status=status.HTTP_400_BAD_REQUEST)

        # ↕ Sorting
        if price_sort:
            products = products.order_by("price" if price_sort.lower() == "asc" else "-price")
        elif name_sort:
            products = products.order_by("title" if name_sort.lower() == "asc" else "-title")
        else:
            products = products.order_by("-id") 

        # ✅ Serialize results
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(
            {"count": products.count(), "results": serializer.data},
            status=status.HTTP_200_OK,
        )


# related product view
class RelatedProductsView(generics.ListAPIView):
    """
    Returns related products based on the same category
    but excludes the current product itself.
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")

        # Get the product or raise 404
        product = get_object_or_404(Products, id=product_id, status=ProductStatus.ACTIVE)

        # Return other products in the same category, excluding the current one
        return Products.objects.filter(
            category=product.category,
            status=ProductStatus.ACTIVE
        ).exclude(id=product.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)




# import csv
# import uuid
# import requests
# import logging
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# from django.utils.text import slugify
# from rest_framework import status, permissions, generics
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from b2c.products.models import Products, ProductCategory
# from b2c.products.serializers import ProductSerializer

# logger = logging.getLogger(__name__)

# class BulkUploadProductView(APIView):
#     permission_classes = [permissions.IsAdminUser]
#     parser_classes = [MultiPartParser, FormParser]

#     def post(self, request):
#         file = request.FILES.get('file', None)
#         print("file", file)
#         if not file:
#             return Response(
#                 {"detail": "No file provided. Make sure the key is 'file' and type is File in Postman."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         print("Received FILES:", request.FILES)  

#         try:
#             file_data = file.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(file_data)
#         except Exception as e:
#             logger.error(f"CSV read error: {str(e)}")
#             return Response({"detail": f"Error reading CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

#         created_products = []
#         failed_rows = []

#         for row in reader:
#             try:
#                 category_name = row.get('category')
#                 if not category_name:
#                     raise ValueError("Category is missing.")
#                 category, _ = ProductCategory.objects.get_or_create(name=category_name)

#                 colors = [c.strip() for c in row.get('colors', '').split(',') if c.strip()]
#                 image_paths = []

#                 for url in row.get('images', '').split('|'):
#                     url = url.strip()
#                     if not url:
#                         continue
#                     try:
#                         response = requests.get(url, timeout=5)
#                         response.raise_for_status()
#                         ext = url.split('.')[-1].split('?')[0]  # remove query params if any
#                         seo_name = f"{slugify(row['title'])}-{uuid.uuid4().hex}.{ext}"
#                         full_path = f'product_images/{seo_name}'
#                         default_storage.save(full_path, ContentFile(response.content))
#                         image_paths.append(full_path)
#                     except Exception as e:
#                         logger.warning(f"Failed to download image {url}: {str(e)}")

#                 product_data = {
#                     'title': row.get('title'),
#                     'product_code': row.get('product_code', ''),
#                     'category': category.id,
#                     'colors': colors,
#                     'available_stock': int(row.get('available_stock', 0)),
#                     'price': float(row.get('price', 0)),
#                     'description': row.get('description', ''),
#                     'images': image_paths
#                 }

#                 serializer = ProductSerializer(data=product_data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     created_products.append(serializer.data)
#                 else:
#                     failed_rows.append({"row": row, "errors": serializer.errors})

#             except Exception as e:
#                 failed_rows.append({"row": row, "errors": str(e)})
#                 logger.error(f"Error processing row {row}: {str(e)}")

#         return Response({
#             "created_products": created_products,
#             "failed_rows": failed_rows
#         }, status=status.HTTP_201_CREATED)

#     def delete(self, request):
#         ids = request.data.get("ids", [])
#         if not ids:
#             return Response({"error": "No product IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

#         products = Products.objects.filter(id__in=ids)
#         deleted_count = products.count()

#         for product in products:
#             if product.images:
#                 for path in product.images:
#                     try:
#                         default_storage.delete(path)
#                     except Exception as e:
#                         logger.warning(f"Failed to delete image {path}: {str(e)}")

#         products.delete()
#         return Response({"message": f"{deleted_count} products deleted successfully"}, status=status.HTTP_200_OK)
