from django.core.management.base import BaseCommand, CommandError
from core.models import Book, BookPoint
import fitz
from PIL import Image

from core.views import sugg_b_pts


BOTTOM = 89.5
TOP = 6


class Command(BaseCommand):
    help = "Pregenerate suggested points"

    def add_arguments(self, parser):
        parser.add_argument("book_id", type=int)

    def handle(self, *args, **options):

        book_id = options["book_id"]
        book = Book.objects.get(id=book_id)

        o = fitz.open(book.pdf)
        page_count = o.page_count
        o.close()

        for i in range(1, page_count + 1):
            pts = sugg_b_pts(book, i)
            pts = list(set(pts))

            BookPoint.objects.bulk_create(
                [BookPoint(book=book, page=i, h=pt) for pt in pts]
            )

        self.stdout.write(self.style.SUCCESS("done!"))
