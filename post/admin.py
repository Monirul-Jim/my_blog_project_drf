from django.contrib import admin
from post.models import CategoryModel, PostModel
# Register your models here.
admin.site.register(CategoryModel)
admin.site.register(PostModel)
