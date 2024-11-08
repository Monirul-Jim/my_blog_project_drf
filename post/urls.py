from rest_framework.routers import DefaultRouter
from post.views import CategoryViewSet, PostViewSet
router = DefaultRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'post', PostViewSet, basename='post')
urlpatterns = router.urls
