# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from django.shortcuts import get_object_or_404
# from .models import HeroPromotion, HeroPromotions
# from .serializers import HeroPromotionSerializer, HeroPromotionsSerializer


# # ---------------- HeroPromotion ----------------
# class HeroPromotionView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
#     """
#     GET    /api/hero-promotion/   -> Anyone
#     POST   /api/hero-promotion/   -> Admin only
#     PATCH  /api/hero-promotion/   -> Admin only
#     PUT    /api/hero-promotion/   -> Admin only
#     DELETE /api/hero-promotion/   -> Admin only
#     """

#     serializer_class = HeroPromotionSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]

#     def get_permissions(self):
#         if self.request.method == "GET":
#             return [permissions.AllowAny()]
#         return [permissions.IsAdminUser()]

#     def get_object(self):
#         obj = HeroPromotion.objects.first()
#         if not obj:
#             raise Response({"error": "No Hero Promotion found"}, status=status.HTTP_404_NOT_FOUND)
#         return obj

#     def create(self, request, *args, **kwargs):
#         if not request.user.is_staff:
#             return Response({"error": "Only admins can create promotions"}, status=status.HTTP_403_FORBIDDEN)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=request.user if request.user.is_authenticated else None)
#         return Response({"message": "Promotion created successfully", "data": serializer.data},
#                         status=status.HTTP_201_CREATED)

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"message": "Promotion updated successfully", "data": serializer.data},
#                         status=status.HTTP_200_OK)

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.delete()
#         return Response({"message": "Promotion deleted successfully"}, status=status.HTTP_200_OK)


# # ---------------- HeroPromotions ----------------
# class HeroPromotionsView(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
#     """
#     GET    /api/hero-promotions/   -> Anyone
#     POST   /api/hero-promotions/   -> Admin only
#     PATCH  /api/hero-promotions/   -> Admin only
#     PUT    /api/hero-promotions/   -> Admin only
#     DELETE /api/hero-promotions/   -> Admin only
#     """

#     serializer_class = HeroPromotionsSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]

#     def get_permissions(self):
#         if self.request.method == "GET":
#             return [permissions.AllowAny()]
#         return [permissions.IsAdminUser()]

#     def get_object(self):
#         obj = HeroPromotions.objects.first()
#         if not obj:
#             raise Response({"error": "No Hero Promotions found"}, status=status.HTTP_404_NOT_FOUND)
#         return obj

#     def create(self, request, *args, **kwargs):
#         if not request.user.is_staff:
#             return Response({"error": "Only admins can create promotions"}, status=status.HTTP_403_FORBIDDEN)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=request.user if request.user.is_authenticated else None)
#         return Response({"message": "Promotion created successfully", "data": serializer.data},
#                         status=status.HTTP_201_CREATED)

#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"message": "Promotion updated successfully", "data": serializer.data},
#                         status=status.HTTP_200_OK)

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         instance.delete()
#         return Response({"message": "Promotion deleted successfully"}, status=status.HTTP_200_OK)
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from .models import HeroPromotion, HeroPromotions
# from .serializers import HeroPromotionSerializer, HeroPromotionsSerializer


# class BaseHeroPromotionView(generics.GenericAPIView):
#     parser_classes = [MultiPartParser, FormParser, JSONParser]

#     def get_permissions(self):
#         if self.request.method in ["GET"]:
#             return [permissions.AllowAny()]
#         return [permissions.IsAdminUser()]

#     def get_object_or_none(self, model_class):
#         """Return the first object or None"""
#         return model_class.objects.first()

#     def create_or_update(self, request, model_class, serializer_class):
#         """Create a record if it doesn't exist, otherwise update"""
#         instance = model_class.objects.first()
#         serializer = serializer_class(
#             instance, data=request.data, partial=True, context={'request': request}
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         msg = "created" if instance is None else "updated"
#         return Response(
#             {"message": f"Promotion {msg} successfully", "data": serializer.data},
#             status=status.HTTP_201_CREATED if instance is None else status.HTTP_200_OK
#         )


# # ---------------- HeroPromotion ----------------
# class HeroPromotionView(BaseHeroPromotionView):
#     serializer_class = HeroPromotionSerializer

#     def get(self, request):
#         obj = self.get_object_or_none(HeroPromotion)
#         if not obj:
#             return Response({"error": "No Hero Promotion found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = self.serializer_class(obj, context={'request': request})
#         return Response(serializer.data)

#     def post(self, request):
#         return self.create_or_update(request, HeroPromotion, self.serializer_class)

#     def patch(self, request):
#         return self.create_or_update(request, HeroPromotion, self.serializer_class)


# # ---------------- HeroPromotions ----------------
# class HeroPromotionsView(BaseHeroPromotionView):
#     serializer_class = HeroPromotionsSerializer

#     def get(self, request):
#         obj = self.get_object_or_none(HeroPromotions)
#         if not obj:
#             return Response({"error": "No Hero Promotions found"}, status=status.HTTP_404_NOT_FOUND)
#         serializer = self.serializer_class(obj, context={'request': request})
#         return Response(serializer.data)

#     def post(self, request):
#         return self.create_or_update(request, HeroPromotions, self.serializer_class)

#     def patch(self, request):
#         return self.create_or_update(request, HeroPromotions, self.serializer_class)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import HeroPromotion, HeroPromotions
from .serializers import HeroPromotionSerializer, HeroPromotionsSerializer


class BaseHeroPromotionView(generics.GenericAPIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method in ["GET"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object_or_create_default(self, model_class, default_data=None):
        """
        Return the first object or create a default one if none exists.
        Only include fields that exist in the model.
        """
        obj = model_class.objects.first()
        if not obj and default_data:
            # Filter default_data to include only valid model fields
            valid_fields = {
                k: v for k, v in default_data.items()
                if k in [f.name for f in model_class._meta.get_fields()]
            }
            obj = model_class.objects.create(**valid_fields)
        return obj

    def create_or_update(self, request, model_class, serializer_class):
        """
        Create a record if it doesn't exist, otherwise update
        """
        instance = model_class.objects.first()
        serializer = serializer_class(
            instance, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        msg = "created" if instance is None else "updated"
        return Response(
            {"message": f"Promotion {msg} successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED if instance is None else status.HTTP_200_OK
        )


# ---------------- HeroPromotion ----------------
class HeroPromotionView(BaseHeroPromotionView):
    serializer_class = HeroPromotionSerializer

    def get(self, request):
        # Only include fields that exist in HeroPromotion
        default_data = {
            "description": "This is a default hero promotion",
            "image": None,
            "is_active": True,
            # Add any other required fields here
        }
        obj = self.get_object_or_create_default(HeroPromotion, default_data=default_data)
        serializer = self.serializer_class(obj, context={'request': request})
        return Response({"data": serializer.data})

    def post(self, request):
        return self.create_or_update(request, HeroPromotion, self.serializer_class)

    def patch(self, request):
        return self.create_or_update(request, HeroPromotion, self.serializer_class)


# ---------------- HeroPromotions ----------------
class HeroPromotionsView(BaseHeroPromotionView):
    serializer_class = HeroPromotionsSerializer

    def get(self, request):
        # Only include fields that exist in HeroPromotions
        default_data = {
            "description": "This is a default promotions list",
            "banners": [],  # JSONField or related field
            "is_active": True,
            # Add any other required fields here
        }
        obj = self.get_object_or_create_default(HeroPromotions, default_data=default_data)
        serializer = self.serializer_class(obj, context={'request': request})
        return Response({"data": serializer.data})

    def post(self, request):
        return self.create_or_update(request, HeroPromotions, self.serializer_class)

    def patch(self, request):
        return self.create_or_update(request, HeroPromotions, self.serializer_class)
