import cloudinary.uploader
from rest_framework import serializers
from cosmetics.models import *


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'dob', 'sex', 'address', 'phone', 'email',
                  'avatar', 'role']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        # Access the request from self.context
        request = self.context.get('request')
        data = validated_data.copy()

        # Check if an image file is provided in the request
        avatar_file = request.FILES.get('avatar') if request else None
        if avatar_file:
            # Upload the image to Cloudinary and get the secure URL
            upload_result = cloudinary.uploader.upload(avatar_file)
            data['avatar'] = upload_result['secure_url']

        # Create the user instance and hash the password
        user = User(**data)
        user.set_password(data["password"])
        user.save()

        return user

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['avatar'] = instance.avatar.url
    #     return rep


class PromotionTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = PromotionTicket
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    origins = serializers.PrimaryKeyRelatedField(queryset=Origin.objects.all(), many=True)

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        # Extract many-to-many fields before creating the Product instance
        tags = validated_data.pop('tags', [])
        origins = validated_data.pop('origins', [])

        # Handle image upload if provided
        request = self.context.get('request')
        image_file = request.FILES.get('image') if request else None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result['secure_url']

        # Create the product instance without the many-to-many fields
        product = Product.objects.create(**validated_data)

        # Assign many-to-many fields using set()
        product.tags.set(tags)
        product.origins.set(origins)

        return product

    def update(self, instance, validated_data):
        # Extract many-to-many fields
        tags = validated_data.pop('tags', None)
        origins = validated_data.pop('origins', None)

        # Handle image upload if a new image is provided
        request = self.context.get('request')
        image_file = request.FILES.get('image') if request else None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result['secure_url']

        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update many-to-many fields if provided
        if tags is not None:
            instance.tags.set(tags)
        if origins is not None:
            instance.origins.set(origins)

        return instance

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     # Include image URL if it exists
    #     rep['image'] = instance.image if instance.image else instance.image.url
    #     return rep


class BlogSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Blog
        fields = '__all__'

    def create(self, validated_data):
        # Handle image upload if provided
        request = self.context.get('request')
        image_file = request.FILES.get('image') if request else None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result['secure_url']

        # Create the blog instance
        blog = Blog.objects.create(**validated_data)

        return blog

    def update(self, instance, validated_data):
        # Handle image upload if a new image is provided
        request = self.context.get('request')
        image_file = request.FILES.get('image') if request else None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            validated_data['image'] = upload_result['secure_url']

        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['image'] = instance.image.url if instance.image.url else instance.image
    #     return rep


class BlogsSerializer(serializers.Serializer):
    blog_id = serializers.IntegerField()
    blog_title = serializers.CharField()
    blog_image = serializers.CharField()
    blog_created_date = serializers.DateTimeField()
    blog_description = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class OriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Origin
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class OrderDetailOfCustomerSerializer(serializers.Serializer):
    order_detail_id = serializers.IntegerField()
    order_detail_product_image = serializers.CharField()
    order_detail_product_name = serializers.CharField()
    order_detail_product_unit_price = serializers.FloatField()
    order_detail_product_quantity = serializers.IntegerField()
    order_detail_product_discount = serializers.IntegerField()
    order_detail_discount_price = serializers.FloatField()
    order_detail_total_amount = serializers.FloatField()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class ProductHomeSerializer(serializers.Serializer):
    id_product = serializers.IntegerField()
    id_category = serializers.IntegerField()
    name_category = serializers.CharField()
    image_product = serializers.CharField()
    name_product = serializers.CharField()
    # unit_price_product = serializers.DecimalField(max_digits=20, decimal_places=3)
    unit_price_product = serializers.FloatField()
    discount_product = serializers.IntegerField()
    # present_price = serializers.DecimalField(max_digits=20, decimal_places=3)
    present_price = serializers.FloatField()
    tags_product = TagSerializer(many=True)


class RelatedProductSerializer(serializers.Serializer):
    id_product = serializers.IntegerField()
    image_product = serializers.CharField()
    name_product = serializers.CharField()
    name_category = serializers.CharField()
    # unit_price_product = serializers.DecimalField(max_digits=20, decimal_places=3)
    unit_price_product = serializers.FloatField()
    discount_product = serializers.IntegerField()
    # present_price = serializers.DecimalField(max_digits=20, decimal_places=3)
    present_price = serializers.FloatField()


class ListColorSerializer(serializers.Serializer):
    color_name = serializers.CharField()


class ListReviewSerializer(serializers.Serializer):
    user_avatar = serializers.CharField()
    user_fullname = serializers.CharField()
    comment_id = serializers.IntegerField()
    comment_star = serializers.IntegerField()
    comment_content = serializers.CharField()


class ProductDetailsSerializer(serializers.Serializer):
    id_product = serializers.IntegerField()
    active_product = serializers.BooleanField()
    image_product = serializers.CharField()
    name_product = serializers.CharField()
    color_product = ListColorSerializer(many=True)
    # unit_price_product = serializers.DecimalField(max_digits=20, decimal_places=3)
    unit_price_product = serializers.FloatField()
    discount_product = serializers.CharField()
    # present_price = serializers.DecimalField(max_digits=20, decimal_places=3)
    present_price = serializers.FloatField()
    description_product = serializers.CharField()
    reviews = ListReviewSerializer(many=True)
    related_products = RelatedProductSerializer(many=True)


class BlogDetailsSerializer(serializers.Serializer):
    blog_id = serializers.IntegerField()
    blog_title = serializers.CharField()
    blog_content = serializers.CharField()
    blog_created_date = serializers.DateTimeField()


class OrdersOfCustomerSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_created_date = serializers.DateTimeField()
    order_total_amount = serializers.FloatField()
    order_shipping_fee = serializers.FloatField()
    order_payment_type = serializers.CharField()
    order_shipment_type = serializers.CharField()
    order_shipment_address = serializers.CharField()
    order_is_payment = serializers.BooleanField()
    order_note = serializers.CharField()
    order_status = serializers.CharField()
    order_updated_date = serializers.DateTimeField()