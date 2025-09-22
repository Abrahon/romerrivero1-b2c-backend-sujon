

from rest_framework import serializers
from b2c.products.models import Products
from .models import CartItem
# from b2c.products.serializers import ProductInfoSerializer



# class ProductInfoSerializer(serializers.ModelSerializer):
#     discounted_price = serializers.SerializerMethodField()
#     # product = ProductInfoSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Products.objects.all(),
#         source="product",
#         write_only=True
#     )

#     class Meta:
#         model = Products
#         fields = ["id", "title", "price", "available_stock", "discounted_price","product", "product_id",]
    

#     def get_discounted_price(self, obj):
#         return float(obj.discounted_price)
    
#     def get_image(self, obj):
#         if obj.images:  
#             # return first image URL
#             return obj.images[0]
#         return None


class CartItemSerializer(serializers.ModelSerializer):
    # product = ProductInfoSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source="product",
        write_only=True
    )
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "added_at", "total_price"]
        read_only_fields = ["id", "added_at", "product", "total_price"]

    def get_total_price(self, obj):
        return float(obj.product.discounted_price * obj.quantity)

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        product = data.get("product") or getattr(self.instance, "product", None)
        quantity = data.get("quantity", getattr(self.instance, "quantity", None))

        if not product:
            raise serializers.ValidationError({"product": "Product must be specified."})

        if quantity > product.available_stock:
            raise serializers.ValidationError({
                "quantity": f"Only {product.available_stock} items available in stock."
            })
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        product = validated_data["product"]
        quantity = validated_data.get("quantity", 1)

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity = min(cart_item.quantity + quantity, product.available_stock)
            cart_item.save()
        return cart_item

    def update(self, instance, validated_data):
        quantity = validated_data.get("quantity", instance.quantity)
        if quantity <= 0:
            raise serializers.ValidationError({"quantity": "Quantity must be greater than zero."})

        instance.quantity = min(quantity, instance.product.available_stock)
        instance.save()
        return instance
