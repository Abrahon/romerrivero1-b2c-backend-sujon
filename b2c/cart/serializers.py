
from rest_framework import serializers
from b2c.products.models import Products
from .models import CartItem
from rest_framework import serializers
from b2c.cart.models import CartItem
from b2c.products.models import Products




class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source="product",
        write_only=True
    )
    product_name = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "added_at",
            "product_name",
            "price",
            "total_price",
            "image"
        ]
        read_only_fields = ["id", "added_at", "product", "product_name", "price", "total_price", "image"]

    def get_product_name(self, obj):
        return obj.product.title if obj.product else None

    def get_price(self, obj):
        return float(obj.product.discounted_price) if obj.product else 0.0

    def get_total_price(self, obj):
        return self.get_price(obj) * obj.quantity

    def get_image(self, obj):
        try:
            if obj.product.images and len(obj.product.images) > 0:
                return obj.product.images[0]
        except Exception:
            return None
        return None

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
