from django.core.management.base import BaseCommand, CommandError
from core.models import Book, BookPoint
import fitz
from PIL import Image

from core.views import sugg_a_pts


BOTTOM = 89.5
TOP = 6


class Command(BaseCommand):
    help = "Pregenerate A module suggested points"

    def add_arguments(self, parser):
        parser.add_argument("book_id", type=int)

    def handle(self, *args, **options):

        book_id = options["book_id"]
        book = Book.objects.get(id=book_id)

        o = fitz.open(book.pdf)
        page_count = o.page_count
        o.close()

        tlen_pts = 0
        for i in range(1, page_count + 1):
            pts = sugg_a_pts(book, i)
            tlen_pts += len(pts)
            
            BookPoint.objects.bulk_create(
                [BookPoint(book=book, page=i, h=pt) for pt in pts]
            )

        self.stdout.write(self.style.SUCCESS(f"done! generated {tlen_pts} pts"))
