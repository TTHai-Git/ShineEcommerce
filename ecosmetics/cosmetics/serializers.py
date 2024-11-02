import cloudinary.uploader
from rest_framework import serializers
from cosmetics.models import *


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'dob', 'address', 'phone', 'email',
                  'avatar', 'role']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data, request=None):
        data = validated_data.copy()
        avatar_file = request.data.get('avatar', None) if request else None
        if avatar_file:
            new_avatar = cloudinary.uploader.upload(avatar_file)
            data['avatar'] = new_avatar['secure_url']
        user = User(**data)
        user.set_password(data["password"])
        user.save()
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url
        return rep


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data, request=None):
        data = validated_data.copy()
        image_file = request.data.get('image', None) if request else None
        if image_file:
            new_image_file = cloudinary.uploader.upload(image_file)
            data['image'] = new_image_file['secure_url']
        product = Product(**data)
        product.save()
        return product

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url
        return rep


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

    def create(self, validated_data, request=None):
        data = validated_data.copy()
        image_file = request.data.get('image', None) if request else None
        if image_file:
            new_image_file = cloudinary.uploader.upload(image_file)
            data['image'] = new_image_file['secure_url']
        blog = Blog(**data)
        blog.save()
        return blog

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url
        return rep


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


class ProductHomeSerializer(serializers.Serializer):
    id_product = serializers.IntegerField()
    id_category = serializers.IntegerField()
    name_category = serializers.CharField()
    image_product = serializers.CharField()
    name_product = serializers.CharField()
    # unit_price_product = serializers.DecimalField(max_digits=20, decimal_places=3)
    unit_price_product = serializers.FloatField()
    discount_product = serializers.CharField()
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
    discount_product = serializers.CharField()
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

