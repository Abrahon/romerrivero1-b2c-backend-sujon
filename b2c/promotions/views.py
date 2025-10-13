
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
