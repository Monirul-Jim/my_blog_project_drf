from rest_framework.routers import DefaultRouter
from post.views import CategoryViewSet
router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
urlpatterns = router.urls
