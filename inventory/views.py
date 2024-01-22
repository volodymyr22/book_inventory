from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Author, Book, StoringInformation
from .serializers import AuthorSerializer, BookSerializer, StoringInformationSerializer
from django.shortcuts import get_object_or_404
from datetime import datetime


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def list(self, request, *args, **kwargs):
        barcode = request.query_params.get('barcode', None)
        if barcode is not None:
            books = self.queryset.filter(Q(barcode__startswith=barcode)).order_by('barcode')
            serializer = self.get_serializer(books, many=True)
            return Response({'found': len(books), 'items': serializer.data})
        else:
            return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer_data = self.get_serializer(instance).data

        storing_info = StoringInformation.objects.filter(book=instance).last()
        if storing_info:
            serializer_data['quantity'] = storing_info.quantity
        else:
            serializer_data['quantity'] = 0

        return Response(serializer_data)


class StoringInformationViewSet(viewsets.ModelViewSet):
    queryset = StoringInformation.objects.all()
    serializer_class = StoringInformationSerializer

    @action(detail=False, methods=['post'])
    def add(self, request):
        barcode = request.data.get('barcode')
        quantity = request.data.get('quantity', 0)

        book = get_object_or_404(Book, barcode=barcode)
        StoringInformation.objects.create(book=book, quantity=quantity)
        return Response({'status': 'quantity added'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        barcode = request.data.get('barcode')
        quantity = request.data.get('quantity', 0)

        book = get_object_or_404(Book, barcode=barcode)
        StoringInformation.objects.create(book=book, quantity=-quantity)
        return Response({'status': 'quantity removed'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def history(self, request):
        start_date = request.query_params.get('start', None)
        end_date = request.query_params.get('end', None)
        book_key = request.query_params.get('book', None)

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        history_query = StoringInformation.objects.all()

        if book_key:
            history_query = history_query.filter(book__id=book_key)
        if start_date:
            history_query = history_query.filter(timestamp__gte=start_date)
        if end_date:
            history_query = history_query.filter(timestamp__lte=end_date)

        serializer = StoringInformationSerializer(history_query, many=True)
        return Response(serializer.data)
