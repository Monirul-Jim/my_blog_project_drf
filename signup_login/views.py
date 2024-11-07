
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from signup_login.serializers import UserRegistrationSerializers, UserLoginSerializers, UserWithRoleSerializer, UserRoleUpdateSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework.decorators import action
from .models import WriterApplication
from .serializers import WriterApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from django.middleware.csrf import get_token
from django.db.models import Q
# Create your views here.


class UserRegistrationView(viewsets.ViewSet):
    def create(self, request):
        serializer = UserRegistrationSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User Registered Successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(viewsets.ViewSet):
    def create(self, request):
        serializer = UserLoginSerializers(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                user.last_login = now()
                user.save(update_fields=['last_login'])
                roles = [group.name for group in user.groups.all()]
                response = Response({
                    'message': 'User logged in successfully',
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'is_superuser': user.is_superuser,
                    'roles': roles
                }, status=status.HTTP_200_OK)
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                    value=str(refresh),
                    httponly=True,
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    samesite='Lax'
                )
                csrf_token = get_token(request)
                response.set_cookie(
                    key="csrftoken",
                    value=csrf_token,
                    httponly=False,
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    samesite='Lax'
                )
                return response
            else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutViewSet(viewsets.ViewSet):
    def create(self, request):
        logout(request)
        response = Response(
            {'message': 'User logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('refresh')
        return response


# class UserViewSet(viewsets.ViewSet):
#     def list(self, request):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)


class UserViewSet(viewsets.ViewSet):
    @action(detail=True, methods=['put'], url_path='update-role')
    def update_role(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserRoleUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": "User role updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='all-users')
    def list_users_with_roles(self, request):
        users = User.objects.all()
        serializer = UserWithRoleSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class BecomeWriterViewSet(viewsets.ModelViewSet):
#     queryset = WriterApplication.objects.all()
#     serializer_class = WriterApplicationSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         data = request.data

#         if WriterApplication.objects.filter(user=user).exists():
#             return Response({"detail": "You have already applied to become a writer."}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = self.get_serializer(data=data)
#         if serializer.is_valid():
#             serializer.save(user=user)
#             return Response({"detail": "Application submitted successfully."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def list(self, request, *args, **kwargs):
#         self.permission_classes = [IsAdminUser]
#         self.check_permissions(request)

#         applications = self.get_queryset()
#         serializer = self.get_serializer(applications, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

class BecomeWriterViewSet(viewsets.ModelViewSet):
    queryset = WriterApplication.objects.all()
    serializer_class = WriterApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)

        # Apply filters if search query is provided
        if search_query:
            queryset = queryset.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query)
            )
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        if WriterApplication.objects.filter(user=user).exists():
            return Response({"detail": "You have already applied to become a writer."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"detail": "Application submitted successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)
        applications = self.get_queryset()
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminApproveWriterViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({"detail": "Only admin can approve applications."}, status=status.HTTP_403_FORBIDDEN)
        try:
            writer_application = WriterApplication.objects.get(id=pk)
        except WriterApplication.DoesNotExist:
            return Response({"detail": "Writer application not found."}, status=status.HTTP_404_NOT_FOUND)

        is_approved = request.data.get(
            'is_approved', writer_application.is_approved)
        writer_application.is_approved = is_approved
        writer_application.save()

        status_msg = "approved" if writer_application.is_approved else "set to pending"
        return Response({"detail": f"Application {status_msg}."}, status=status.HTTP_200_OK)
