from django.contrib import admin
from .models import Book, BookPoint

class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'pdf']

admin.site.register(Book, BookAdmin)
admin.site.register(BookPoint)
