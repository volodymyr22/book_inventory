from rest_framework import serializers, viewsets

from inventory.models import Author, Book, StoringInformation


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'birth_date']


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ['id', 'barcode', 'title', 'publish_year', 'author']


class StoringInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoringInformation
        fields = ['id', 'book', 'quantity', 'timestamp']
