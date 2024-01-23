import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import DateField, IntegerField, DateTimeField
from rest_framework.relations import PrimaryKeyRelatedField

from inventory.models import Author, Book, StoringInformation


def validate_birth_date(value):
    if value <= datetime.date(1900, 1, 1):
        raise ValidationError('Birth date must be greater than 1900.')


class AuthorSerializer(serializers.ModelSerializer):
    birth_date = DateField(write_only=True, format='%Y-%m-%d', validators=[validate_birth_date])

    class Meta:
        model = Author
        fields = ['id', 'name', 'birth_date']


class AuthorBirthDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["name", 'birth_date']


class BookSerializer(serializers.ModelSerializer):
    publish_year = IntegerField(min_value=1900)
    author = AuthorBirthDateSerializer(read_only=True)
    author_id = PrimaryKeyRelatedField(queryset=Author.objects.all(), write_only=True, source='author')

    class Meta:
        model = Book
        fields = ['id', 'barcode', 'title', 'publish_year', 'author', 'author_id']


class BookStoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'barcode', 'title']


class StoringInformationSerializer(serializers.ModelSerializer):
    timestamp = DateTimeField(format='%Y-%m-%d', read_only=True)
    book = PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)

    class Meta:
        model = StoringInformation
        fields = ['quantity', 'timestamp', 'book']
