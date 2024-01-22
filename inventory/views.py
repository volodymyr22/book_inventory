import xlrd
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Author, Book, StoringInformation
from .serializers import AuthorSerializer, BookSerializer, StoringInformationSerializer, BookStoringSerializer
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
        last = StoringInformation.objects.filter(book=book).last()
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

        book = get_object_or_404(Book, id=book_key)

        if book_key:
            history_query = history_query.filter(book__id=book_key)
        if start_date:
            history_query = history_query.filter(timestamp__gte=start_date)
        if end_date:
            history_query = history_query.filter(timestamp__lte=end_date)

        history_data = {
            "book": BookStoringSerializer(book).data,
            "start_balance": history_query.first().quantity if history_query.first() else 0,
            "history": []
        }
        end_balance = 0
        for storing_info in history_query:
            end_balance += storing_info.quantity
            history_data['history'].append(self.get_serializer(storing_info).data)
        history_data['end_balance'] = end_balance
        return Response(history_data)

    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            try:
                file_extension = uploaded_file.name.split('.')[-1].lower()

                if file_extension == 'xls':
                    data = self.parse_excel_file(uploaded_file)
                elif file_extension == 'txt':
                    data = self.parse_txt_file(uploaded_file)
                else:
                    return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
                serializer = self.get_serializer(data=data, many=True)
                if serializer.is_valid():
                    serializer.save()
                return Response(data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    def parse_excel_file(self, uploaded_file):
        data = []
        try:
            workbook = xlrd.open_workbook(file_contents=uploaded_file.read())
            sheet = workbook.sheet_by_index(0)

            for row_index in range(1, sheet.nrows):
                barcode = sheet.cell(row_index, 0).value.strip()
                quantity = sheet.cell(row_index, 1).value

                if not barcode:
                    continue

                try:
                    quantity = int(quantity)
                except ValueError:
                    raise ValueError(f'Row {row_index + 1}: Quantity must be a valid integer')

                book = Book.objects.filter(barcode=barcode).first()
                if not book:
                    raise ValueError(f'Row {row_index + 1}: Barcode not found in the database')

                data.append({'book': book.id, 'quantity': quantity})

        except Exception as e:
            raise e

        return data

    def parse_txt_file(self, uploaded_file):
        data = []
        lines = uploaded_file.read().decode('utf-8').splitlines()
        print(lines)
        current_barcode = None
        current_quantity = None

        for line in lines:
            line = line.strip()
            if line.startswith("BRC"):
                current_barcode = line[3:]
            elif line.startswith("QNT"):
                try:
                    current_quantity = int(line[3:])
                    data.append({'book': current_barcode, 'quantity': current_quantity})
                except ValueError:
                    raise ValueError(f'Invalid quantity format: {line}')

        return data
