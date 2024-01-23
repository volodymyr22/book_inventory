import os
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Author, Book, StoringInformation


class InventoryAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.author = Author.objects.create(name='Test Author', birth_date='1980-01-01')
        self.book = Book.objects.create(title='Test Book', publish_year=2020, author=self.author, barcode='12345')
        self.storing_info = StoringInformation.objects.create(book=self.book, quantity=10)

    def test_get_book_list(self):
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_book_detail(self):
        url = reverse('book-detail', args=[self.book.id])
        response = self.client.get(url)
        res = {
            'id': self.book.id,
            'barcode': self.book.barcode,
            'title': self.book.title,
            'publish_year': self.book.publish_year,
            'author': {
                'name': self.author.name,
                'birth_date': self.author.birth_date
            },
            'quantity': self.storing_info.quantity,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, res)

    def test_create_book(self):
        url = reverse('book-list')
        data = {'title': 'New Book', 'publish_year': 2021, 'author_id': self.author.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_create_book_error_year(self):
        url = reverse('book-list')
        data = {'title': 'New Book', 'publish_year': 1000, 'author_id': self.author.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 1)

    def test_create_author(self):
        author_data = {'name': 'John Doe', 'birth_date': '1980-01-01'}
        url = reverse('author-list')
        response = self.client.post(url, author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 2)

    def test_get_authors(self):
        url = reverse('author-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Author')

    def test_get_author_detail(self):
        url = reverse('author-detail', args=[self.author.id])
        response = self.client.get(url)
        res = {
            'id': self.author.id,
            'name': self.author.name
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, res)

    def test_add_quantity(self):
        url = reverse('storinginformation-add')
        data = {'barcode': self.book.barcode, 'quantity': 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StoringInformation.objects.count(), 2)
        self.assertEqual(StoringInformation.objects.last().quantity, 5)

    def test_remove_quantity(self):
        url = reverse('storinginformation-remove')
        data = {'barcode': self.book.barcode, 'quantity': 3}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StoringInformation.objects.count(), 2)
        self.assertEqual(StoringInformation.objects.last().quantity, -3)

    def test_view_history(self):
        url = reverse('storinginformation-history') + '?book=' + str(self.book.id) + '&start=2024-01-01&end=2025-01-01'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('history', response.data)

    def test_bulk(self):
        path_to_file = os.path.join(os.path.dirname(__file__), 'test_data.xlsx')
        url = reverse('storinginformation-bulk')
        with open(path_to_file, 'rb') as file:
            response = self.client.post(url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(StoringInformation.objects.count(), 3)
        self.assertEqual(StoringInformation.objects.last().quantity, -2)
