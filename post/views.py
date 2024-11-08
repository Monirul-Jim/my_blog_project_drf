
from rest_framework import viewsets, status
from rest_framework.response import Response
from post.models import CategoryModel, PostModel
from post.serializers import CategorySerializer, PostModelSerializer
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request):
        categories = CategoryModel.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Category created successfully!',
                 'category': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'message': 'Category creation failed.', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def retrieve(self, request, pk=None):
        try:
            category = CategoryModel.objects.get(id=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except CategoryModel.DoesNotExist:
            return Response({'detail': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        try:
            category = CategoryModel.objects.get(id=pk)
        except CategoryModel.DoesNotExist:
            return Response({'detail': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(
            category, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Category updated successfully!',
                    'category': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': 'Category update failed.', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class PostViewSet(viewsets.ModelViewSet):
    queryset = PostModel.objects.all()
    serializer_class = PostModelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        categories = self.request.query_params.getlist('category')
        if categories:
            queryset = queryset.filter(category__id__in=categories).distinct()

        time_filter = self.request.query_params.get('time')
        now = timezone.now()

        if time_filter == 'last_year':
            queryset = queryset.filter(
                created_at__gte=now - timedelta(days=365))
        elif time_filter == 'last_month':
            queryset = queryset.filter(
                created_at__gte=now - timedelta(days=30))
        elif time_filter == 'last_week':
            queryset = queryset.filter(
                created_at__gte=now - timedelta(weeks=1))
        elif time_filter == 'today':
            queryset = queryset.filter(created_at__date=now.date())

        return queryset

    def create(self, request, *args, **kwargs):
        # Check if the user has the 'writer' role
        if 'writer' not in [group.name for group in request.user.groups.all()]:
            return Response(
                {"error": "Only users with the 'writer' role can create posts."},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        categories = data.pop('category_ids', [])

        # Fetch the user instance using the user ID from request data
        user_id = data.pop('user', None)  # Pop user field from the data
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User with the provided ID does not exist."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # If no user ID is provided, return an error
            return Response(
                {"error": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create the post with the user instance and other data
            post = PostModel.objects.create(user=user, **data)
            post.category.set(categories)
            serializer = self.get_serializer(post)
            return Response(
                {"message": "Post created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"error": "Failed to create post.", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        categories = data.pop('category_ids', None)

        try:
            instance.title = data.get('title', instance.title)
            instance.description = data.get(
                'description', instance.description)
            instance.image = data.get('image', instance.image)
            instance.save()

            if categories is not None:
                instance.category.set(categories)

            serializer = self.get_serializer(instance)
            return Response(
                {"message": "Post updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"error": "Failed to update post.", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
