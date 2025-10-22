
from rest_framework import serializers
from django.utils import timezone
from .models import Coupon, CouponRedemption, Products, ProductCategory
from .enums import DiscountType
from decimal import Decimal


# class CouponSerializer(serializers.ModelSerializer):
#     products = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=Products.objects.all(), required=False
#     )
#     categories = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=ProductCategory.objects.all(), required=False
#     )

#     class Meta:
#         model = Coupon
#         fields = '__all__'

#     def validate(self, attrs):
#         products = attrs.get('products', [])
#         categories = attrs.get('categories', [])

#         # ✅ Must select at least one
#         if not products and not categories:
#             raise serializers.ValidationError(
#                 {"non_field_errors": ["At least one product or category must be selected."]}
#             )

#         # ✅ Extra check for percentage coupons
#         if attrs['discount_type'] == DiscountType.PERCENTAGE and attrs['discount_value'] > 100:
#             raise serializers.ValidationError(
#                 {"discount_value": "Percentage discount cannot exceed 100%."}
#             )

#         return attrs

#     def create(self, validated_data):
#         products = validated_data.pop('products', [])
#         categories = validated_data.pop('categories', [])

#         coupon = Coupon.objects.create(**validated_data)

#         if products:
#             coupon.products.set(products)
#         if categories:
#             coupon.categories.set(categories)

#         return coupon

#     def update(self, instance, validated_data):
#         products = validated_data.pop('products', None)
#         categories = validated_data.pop('categories', None)

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if products is not None:
#             instance.products.set(products)
#         if categories is not None:
#             instance.categories.set(categories)

#         return instance
from rest_framework import serializers
from .models import Coupon, DiscountType


class CouponSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Products.objects.all(), required=False
    )
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ProductCategory.objects.all(), required=False
    )

    class Meta:
        model = Coupon
        fields = "__all__"

    def validate(self, attrs):
        products = attrs.get('products', [])
        categories = attrs.get('categories', [])

        # Must select at least one
        if not products and not categories:
            raise serializers.ValidationError(
                {"non_field_errors": ["At least one product or category must be selected."]}
            )

        # Percentage discount should not exceed 100%
        if attrs['discount_type'] == DiscountType.PERCENTAGE and attrs['discount_value'] > 100:
            raise serializers.ValidationError(
                {"discount_value": "Percentage discount cannot exceed 100%."}
            )

        return attrs

    def create(self, validated_data):
        products = validated_data.pop('products', [])
        categories = validated_data.pop('categories', [])
        coupon = Coupon.objects.create(**validated_data)

        if products:
            coupon.products.set(products)
        if categories:
            coupon.categories.set(categories)

        return coupon

    def update(self, instance, validated_data):
        products = validated_data.pop('products', None)
        categories = validated_data.pop('categories', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if products is not None:
            instance.products.set(products)
        if categories is not None:
            instance.categories.set(categories)

        return instance




# class ApplyCouponSerializer(serializers.Serializer):
#     code = serializers.CharField()
#     product_ids = serializers.ListField(
#         child=serializers.IntegerField(), required=True
#     )

#     def validate(self, attrs):
#         code = attrs.get("code")
#         product_ids = attrs.get("product_ids")

#         # Check coupon existence
#         try:
#             coupon = Coupon.objects.get(code=code, active=True)
#         except Coupon.DoesNotExist:
#             raise serializers.ValidationError({"code": "Invalid or inactive coupon."})

#         # Expiry check
#         now = timezone.now()
#         if coupon.valid_from and coupon.valid_from > now:
#             raise serializers.ValidationError({"code": "Coupon is not yet valid."})
#         if coupon.valid_to and coupon.valid_to < now:
#             raise serializers.ValidationError({"code": "Coupon has expired."})

#         # Product validation
#         products = Products.objects.filter(id__in=product_ids)
#         if products.count() != len(product_ids):
#             raise serializers.ValidationError({"product_ids": "One or more product IDs are invalid."})

#         # Restriction checks
#         if coupon.products.exists():
#             allowed_ids = set(coupon.products.values_list("id", flat=True))
#             for pid in product_ids:
#                 if pid not in allowed_ids:
#                     raise serializers.ValidationError({
#                         "product_ids": f"Coupon not valid for product {pid}."
#                     })
#         if coupon.categories.exists():
#             allowed_cats = set(coupon.categories.values_list("id", flat=True))
#             for product in products:
#                 if product.category_id not in allowed_cats:
#                     raise serializers.ValidationError({
#                         "product_ids": f"Coupon not valid for category of product {product.id}."
#                     })

#         # ✅ Calculate total amount based on discounted_price if present, else original price
#         total_amount = Decimal("0.00")
#         for p in products:
#             base_price = getattr(p, "discounted_price", None) or p.price
#             total_amount += base_price

#         # Apply coupon on top of total_amount
#         if coupon.discount_type == "percentage":
#             coupon_discount = (total_amount * Decimal(coupon.discount_value) / 100)
#         else:  # fixed
#             coupon_discount = Decimal(coupon.discount_value)

#         final_amount = max(total_amount - coupon_discount, Decimal("0.00"))

#         # Save validated data
#         attrs["coupon"] = coupon
#         attrs["products"] = products
#         attrs["total_amount"] = total_amount
#         attrs["coupon_discount_value"] = coupon_discount
#         attrs["final_amount"] = final_amount

#         return attrs

#     def create(self, validated_data):
#         coupon = validated_data["coupon"]
#         user = self.context["request"].user

#         # Record redemption to prevent duplicates
#         CouponRedemption.objects.get_or_create(coupon=coupon, user=user)

#         return {
#             "message": f"Coupon applied successfully! You get {validated_data['coupon_discount_value']} {coupon.discount_type} discount.",
#             "discount_type": coupon.discount_type,
#             "coupon_discount_value": str(validated_data["coupon_discount_value"]),
#             "total_amount": str(validated_data["total_amount"]),
#             "final_amount": str(validated_data["final_amount"]),
#             "applied_products": [p.id for p in validated_data["products"]]
#         }


# # for multiple product an dqunatity
# class ApplyCouponSerializer(serializers.Serializer):
#     code = serializers.CharField()
#     products = serializers.ListField(
#         child=serializers.DictField(child=serializers.IntegerField()), required=True
#     )

#     def validate(self, attrs):
#         code = attrs.get("code")
#         products_data = attrs.get("products")

#         product_ids = [p["id"] for p in products_data if "id" in p]

#         try:
#             coupon = Coupon.objects.get(code=code, active=True)
#         except Coupon.DoesNotExist:
#             raise serializers.ValidationError({"code": "Invalid or inactive coupon."})

#         now = timezone.now()
#         if coupon.valid_from and coupon.valid_from > now:
#             raise serializers.ValidationError({"code": "Coupon is not yet valid."})
#         if coupon.valid_to and coupon.valid_to < now:
#             raise serializers.ValidationError({"code": "Coupon has expired."})

#         products = Products.objects.filter(id__in=product_ids)
#         if products.count() != len(product_ids):
#             raise serializers.ValidationError({"products": "One or more product IDs are invalid."})

#         if coupon.products.exists():
#             allowed_ids = set(coupon.products.values_list("id", flat=True))
#             for pid in product_ids:
#                 if pid not in allowed_ids:
#                     raise serializers.ValidationError({
#                         "products": f"Coupon not valid for product {pid}."
#                     })

#         if coupon.categories.exists():
#             allowed_cats = set(coupon.categories.values_list("id", flat=True))
#             for product in products:
#                 if product.category_id not in allowed_cats:
#                     raise serializers.ValidationError({
#                         "products": f"Coupon not valid for category of product {product.id}."
#                     })

#         total_amount = Decimal("0.00")
#         product_quantities = {}  # 🟩 FIX: store quantity per product ID

#         for p in products_data:
#             product_quantities[p["id"]] = p.get("quantity", 1)  # default to 1

#         for p in products:
#             base_price = getattr(p, "discounted_price", None) or p.price
#             quantity = product_quantities.get(p.id, 1)  # 🟩 FIX: get actual quantity
#             total_amount += Decimal(base_price) * quantity

#         if coupon.discount_type == "percentage":
#             coupon_discount = (total_amount * Decimal(coupon.discount_value) / 100)
#         else:
#             coupon_discount = Decimal(coupon.discount_value)

#         final_amount = max(total_amount - coupon_discount, Decimal("0.00"))

#         # 🟩 FIX: include product quantities in validated data
#         attrs.update({
#             "coupon": coupon,
#             "products": products,
#             "total_amount": total_amount,
#             "coupon_discount_value": coupon_discount,
#             "final_amount": final_amount,
#             "product_quantities": product_quantities,  # 🟩 store for view use
#         })

#         return attrs



class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()
    products = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()), required=True
    )

    def validate(self, attrs):
        code = attrs.get("code")
        products_data = attrs.get("products", [])

        if not products_data:
            raise serializers.ValidationError({"products": "Products data is required."})

        product_ids = [p.get("id") for p in products_data if "id" in p]

        # ✅ Fetch coupon
        try:
            coupon = Coupon.objects.get(code=code, active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid or inactive coupon."})

        now = timezone.now()
        if coupon.valid_from and coupon.valid_from > now:
            raise serializers.ValidationError({"code": "Coupon is not yet valid."})
        if coupon.valid_to and coupon.valid_to < now:
            raise serializers.ValidationError({"code": "Coupon has expired."})

        # ✅ Fetch products and validate
        products = Products.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            raise serializers.ValidationError({"products": "One or more product IDs are invalid."})

        # Check if coupon is valid for products
        if coupon.products.exists():
            allowed_ids = set(coupon.products.values_list("id", flat=True))
            for pid in product_ids:
                if pid not in allowed_ids:
                    raise serializers.ValidationError({
                        "products": f"Coupon not valid for product {pid}."
                    })

        # Check if coupon is valid for categories
        if coupon.categories.exists():
            allowed_categories = set(coupon.categories.values_list("id", flat=True))
            for product in products:
                if product.category_id not in allowed_categories:
                    raise serializers.ValidationError({
                        "products": f"Coupon not valid for category of product {product.id}."
                    })

        # ✅ Calculate total amount considering quantities
        total_amount = Decimal("0.00")
        product_quantities = {}

        for p in products_data:
            pid = p.get("id")
            qty = p.get("quantity", 1)
            product_quantities[pid] = qty

        for product in products:
            base_price = getattr(product, "discounted_price", None) or product.price
            qty = product_quantities.get(product.id, 1)
            total_amount += Decimal(base_price) * qty

        # ✅ Apply coupon discount
        if coupon.discount_type == "percentage":
            coupon_discount = (total_amount * Decimal(coupon.discount_value) / 100)
        else:
            coupon_discount = Decimal(coupon.discount_value)

        final_amount = max(total_amount - coupon_discount, Decimal("0.00"))

        # Add computed fields to attrs
        attrs.update({
            "coupon": coupon,
            "products": products,
            "product_quantities": product_quantities,
            "total_amount": total_amount,
            "coupon_discount_value": coupon_discount,
            "final_amount": final_amount,
        })

        return attrs
