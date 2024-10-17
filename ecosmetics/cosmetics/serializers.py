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
        fields = ['id', 'code', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'role']
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