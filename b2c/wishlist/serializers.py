from rest_framework import serializers
from .models import WishlistItem
from b2c.products.serializers import ProductSerializer
from b2c.reviews.models import Review
from django.db.models import Avg


class WishlistItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    in_wishlist = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_details', "average_rating", "in_wishlist", 'added_at']
        read_only_fields = ['id', 'product_details', 'added_at']
    
    def get_in_wishlist(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            # check if this product is in wishlist for the user
            return WishlistItem.objects.filter(user=user, product=obj.product).exists()
        return False

    def get_average_rating(self, obj):
        avg = Review.objects.filter(product=obj.product).aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 1) if avg else 0.0
    

    def get_image_url(self, obj):  
        request = self.context.get('request')
        if obj.product.image:
            return request.build_absolute_uri(obj.product.image.url)
        return None



