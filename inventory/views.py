# views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Author, Book, Storing, StoringHistory
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    StoringSerializer,
    StoringHistorySerializer,
)


class AuthorAPIView(generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class BookAPIView(generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class StoringAPIView(generics.CreateAPIView):
    queryset = Storing.objects.all()
    serializer_class = StoringSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class StoringHistoryAPIView(generics.RetrieveAPIView):
    queryset = Storing.objects.all()
    serializer_class = StoringHistorySerializer
    lookup_field = "book__id"

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Storing.DoesNotExist:
            return Response(
                {"error": "Entity not found"}, status=status.HTTP_404_NOT_FOUND
            )
