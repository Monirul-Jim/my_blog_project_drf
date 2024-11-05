from rest_framework.routers import DefaultRouter
from signup_login.views import UserRegistrationView, UserLoginView
router = DefaultRouter()

router = DefaultRouter()
router.register(r'signup', UserRegistrationView, basename='signup')
router.register(r'login', UserLoginView, basename='login')

urlpatterns = router.urls
