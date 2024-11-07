
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
# Create your models here.


class CategoryModel(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if a category with the same name exists
        if CategoryModel.objects.filter(name=self.name).exists():
            raise ValidationError(f"A category with the name '{
                                  self.name}' already exists.")

        # If slug is not set, generate one from the name
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)
# class PostModel(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=300)
#     description = models.TextField()
