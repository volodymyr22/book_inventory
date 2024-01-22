import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from inventory.models import Author, Book, StoringInformation


def validate_birth_date(value):
    if value <= datetime.date(1900, 1, 1):
        raise ValidationError('Birth date must be greater than 1900.')


class AuthorSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(write_only=True, format='%Y-%m-%d', validators=[validate_birth_date])

    class Meta:
        model = Author
        fields = ['id', 'name', 'birth_date']


class AuthorBirthDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["name", 'birth_date']


class BookSerializer(serializers.ModelSerializer):
    publish_year = serializers.IntegerField(min_value=1900)

    class Meta:
        model = Book
        fields = ['id', 'barcode', 'title', 'publish_year', 'author']


class BookStoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'barcode', 'title']


class StoringInformationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = StoringInformation
        fields = ['quantity', 'timestamp']
