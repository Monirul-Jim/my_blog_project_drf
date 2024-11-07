from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import CategoryModel
from .serializers import CategorySerializer


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
