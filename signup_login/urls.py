from rest_framework.routers import DefaultRouter
from signup_login.views import UserRegistrationView, UserLoginView, UserViewSet, BecomeWriterViewSet, AdminApproveWriterViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
router = DefaultRouter()

router = DefaultRouter()
router.register(r'signup', UserRegistrationView, basename='signup')
router.register(r'login', UserLoginView, basename='login')
# router.register(r'users', UserViewSet, basename='users')
router.register(r'user', UserViewSet, basename='user')
router.register(r'apply-to-become-writer',
                BecomeWriterViewSet, basename='become_writer')
router.register(r'admin/approve-writer',
                AdminApproveWriterViewSet, basename='approve_writer')
urlpatterns = router.urls + [
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
