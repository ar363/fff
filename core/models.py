from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=150)
    pdf = models.FileField(help_text=".PDF type only")
    type = models.CharField(
        max_length=5,
        choices=[
            ("A", "A module"),
            ("B", "B module"),
            ("O", "Other"),
        ],
        default="O",
    )

    def __str__(self):
        return self.name


class BookPoint(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    page = models.PositiveIntegerField()
    h = models.FloatField(unique=True)

    def __str__(self) -> str:
        return self.book.name + " - " + str(self.page) + ": " + str(self.h)
