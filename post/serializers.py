from rest_framework import serializers
from post.models import CategoryModel


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ['id', 'name', 'slug']

    def validate_name(self, value):
        if CategoryModel.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"A category with the name '{value}' already exists.")
        return value
