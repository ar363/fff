from django.core.management.base import BaseCommand, CommandError
from core.models import Book, BookPoint
import fitz
# from PIL import Image

# from core.views import sugg_a_pts
import math


# BOTTOM = 89.5
# TOP = 6


class Command(BaseCommand):
    help = "Pregenerate Arihant math (others not tested yet) suggested points"

    def add_arguments(self, parser):
        parser.add_argument("book_id", type=int)

    def handle(self, *args, **options):

        book_id = options["book_id"]
        book = Book.objects.get(id=book_id)

        o = fitz.open(book.pdf)

        prev_blk = None
        leng = 0
        for page in o:
            lns = []
            tx = page.get_text("dict")
            _,_,_, h = page.rect

            for t in tx['blocks']:

                if t['lines'][0]['spans'][0]['font'] in ['Akzidenz-GroteskBQ-Bold', 'Akzidenz-GroteskBQ', 'LiberationSans-Bold']:
                    if prev_blk == True:
                        lns.pop()
                        lns.append(math.floor(t['bbox'][3]) + 1)
                    else:
                        lns.append(math.floor(t['bbox'][1]) - 1)
                        lns.append(math.floor(t['bbox'][3]) + 1)

                    prev_blk = True
                else:
                    prev_blk = False
            
            BookPoint.objects.bulk_create(
                [BookPoint(book=book, page=page.number + 1, h=pt*100/h) for pt in lns]
            )
            leng += len(lns)

        o.close()            

        self.stdout.write(self.style.SUCCESS(f"done! generated {leng} pts"))
