# from rest_framework import serializers
# from .models import CartItem
# from b2c.products.models import Products

# class ProductInfoSerializer(serializers.ModelSerializer):
#     discounted_price = serializers.SerializerMethodField()

#     class Meta:
#         model = Products
#         fields = ['id', 'title', 'price', 'available_stock', 'discounted_price']

#     def get_discounted_price(self, obj):
#         return obj.discounted_price

# class CartItemSerializer(serializers.ModelSerializer):
#     product = ProductInfoSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Products.objects.all(),
#         source='product',
#         write_only=True
#     )
#     total_price = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'product_id', 'quantity', 'added_at', 'total_price']

#     def get_total_price(self, obj):
#         # Calculate total price dynamically: discounted_price * quantity
#         return obj.product.discounted_price * obj.quantity

#     def validate(self, data):
#         request = self.context.get('request')
#         user = request.user if request else None

#         product = data.get('product')
#         quantity = data.get('quantity')

#         # Check if product is already in the user's cart
#         if user and CartItem.objects.filter(user=user, product=product).exists():
#             raise serializers.ValidationError({
#                 "detail": "This product is already in your cart. You can update the quantity instead."
#             })

#         # Check if product exists
#         if not product:
#             raise serializers.ValidationError({"product_id": "Product not found."})

#         # Quantity validations
#         if quantity <= 0:
#             raise serializers.ValidationError({"quantity": "Quantity must be greater than zero."})

#         if product.available_stock < quantity:
#             raise serializers.ValidationError({
#                 "quantity": f"Only {product.available_stock} items available in stock."
#             })

#         return data
from rest_framework import serializers
from .models import CartItem
from b2c.products.models import Products

class ProductInfoSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = ['id', 'title', 'price', 'available_stock', 'discounted_price']

    def get_discounted_price(self, obj):
        return obj.discounted_price

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductInfoSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source='product',
        write_only=True
    )
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'added_at', 'total_price']

    def get_total_price(self, obj):
        return obj.product.discounted_price * obj.quantity

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')

        if product.available_stock < quantity:
            raise serializers.ValidationError({
                "quantity": f"Only {product.available_stock} items available in stock."
            })
        return data
