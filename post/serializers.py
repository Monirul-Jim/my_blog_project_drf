import django.contrib.auth.models
from rest_framework import serializers
from post.models import CategoryModel, PostModel
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Replace with the actual User model if it's custom
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name']  # Include other fields as needed


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ['id', 'name', 'slug']

    def validate_name(self, value):
        if CategoryModel.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"A category with the name '{value}' already exists.")
        return value


class PostModelSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=CategoryModel.objects.all(),
        many=True,
        write_only=True,
        source='category'
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostModel
        fields = ['id', 'image', 'user', 'title', 'description',
                  'category', 'category_ids', 'created_at']

        def create(self, validated_data):
            # Extract the user from validated data and fetch the full user instance using the ID
            user = validated_data.pop('user')
            post = PostModel.objects.create(user=user, **validated_data)
            return post

        def validate(self, data):
            if not data.get('title'):
                raise serializers.ValidationError(
                    {"title": "Title is required."})
            if not data.get('description'):
                raise serializers.ValidationError(
                    {"description": "Description is required."})
            if not data.get('category_ids'):
                raise serializers.ValidationError(
                    {"category_ids": "At least one category must be selected."})
            if not data.get('image'):
                raise serializers.ValidationError(
                    {"image": "Image URL is required."})

            # Optional: Validate that user is included
            if not data.get('user'):
                raise serializers.ValidationError(
                    {"user": "User is required."})

            return data

    def create(self, validated_data):
        user = validated_data.pop('user')
        categories = validated_data.pop('category_ids', [])

        # Ensure user exists (you can validate this in the view instead, but this is an example)
        if not user:
            raise serializers.ValidationError("User is required.")

        post = PostModel.objects.create(user=user, **validated_data)
        post.category.set(categories)
        return post
