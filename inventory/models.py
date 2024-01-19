from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)
    birth_date = models.DateField()


class Book(models.Model):
    barcode = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    publish_year = models.PositiveIntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Storing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def history(self):
        history_entries = StoringHistory.objects.filter(book=self.book).order_by(
            "-date"
        )
        return [
            {"date": entry.date, "quantity": entry.quantity}
            for entry in history_entries
        ]


class StoringHistory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
