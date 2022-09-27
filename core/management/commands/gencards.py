from django.core.management.base import BaseCommand, CommandError
from core.models import Book, BookPoint
import fitz
import os
from PIL import Image
from time import time
import genanki


BOTTOM = 89.5
TOP = 0


class Command(BaseCommand):
    help = "Gen cards"

    def add_arguments(self, parser):
        parser.add_argument("book_id", type=int)
        parser.add_argument("book_unique_codename", type=str)

    def handle(self, *args, **options):
        book_unique_codename = options["book_unique_codename"]
        mkcards(options["book_id"], book_unique_codename)
        mkanki(options["book_id"], book_unique_codename)
        self.stdout.write(self.style.SUCCESS("done!"))


def page_img(pdf, page):
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)

    p = fitz.open(pdf)
    pg = p.load_page(page - 1)
    pix = pg.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def mkcards(bookId, book_unique_codename):
    book = Book.objects.get(id=bookId)
    coords = (
        BookPoint.objects.filter(book=book).order_by("page", "h").values("page", "h")
    )

    # coords = coords[:2] #REMOVE SOON
    # coords = [*coords]

    pdf = book.pdf

    os.makedirs("temp", exist_ok=True)
    os.makedirs(f"temp/{book_unique_codename}", exist_ok=True)

    glob_name_sys = 1
    for i in range(len(coords) - 1):
        ia, ib = coords[i], coords[i + 1]

        if ia["page"] == ib["page"]:
            # simple box
            im = page_img(pdf, ia["page"])

            w, h = im.size
            im = im.crop((0, (ia["h"] * h / 100), w, (ib["h"] * h / 100)))

            im.save(
                f"temp/{book_unique_codename}/{book_unique_codename}-{str(glob_name_sys).zfill(4)}-p{ia['page']}.jpg"
            )
        else:
            ims = []
            stw = 0

            for j in range(ia["page"], ib["page"] + 1):
                im = page_img(pdf, j)
                w, h = im.size
                stw = w

                if book.type in ["A", "B"]:
                    if j == ia["page"]:
                        ims.append(
                            im.crop((0, (ia["h"] * h / 100), w, (BOTTOM * h / 100)))
                        )
                    elif j == ib["page"]:
                        ims.append(
                            im.crop((0, (TOP * h / 100), w, (ib["h"] * h / 100)))
                        )
                    else:
                        ims.append(im.crop((0, (TOP * h / 100), w, (BOTTOM * h / 100))))
                else:
                    if j == ia["page"]:
                        ims.append(im.crop((0, (ia["h"] * h / 100), w, h)))
                    elif j == ib["page"]:
                        ims.append(im.crop((0, 0, w, (ib["h"] * h / 100))))
                    else:
                        ims.append(im.crop((0, 0, w, h)))

            total_h = 0
            for i in ims:
                total_h += i.size[1]

            calc_total_h = 0

            lg_im = Image.new("RGB", (stw, total_h))
            for i in range(len(ims)):
                lg_im.paste(ims[i], (0, calc_total_h))
                calc_total_h += ims[i].size[1]

            lg_im.save(
                f"temp/{book_unique_codename}/{book_unique_codename}-{str(glob_name_sys).zfill(4)}-p{ia['page']}.jpg"
            )

        glob_name_sys += 1


def mkanki(bookId, book_unique_codename):

    ddeck = genanki.Deck(int(time()), name=Book.objects.get(id=bookId).name)

    ld = os.listdir(f"temp/{book_unique_codename}/")
    if len(ld) % 2 != 0:
        print("WARNING: odd number of cards found")
    for i in range(0, len(ld), 2):
        try:
            ddeck.add_note(
                genanki.Note(
                    model=genanki.BASIC_MODEL,
                    fields=[f'<img src="{ld[i]}">', f'<img src="{ld[i+1]}">'],
                )
            )
        except IndexError:
            pass

    pkg = genanki.Package()
    pkg.media_files = [
        f"temp/{book_unique_codename}/" + i
        for i in os.listdir(f"temp/{book_unique_codename}/")
    ]

    pkg.decks = [ddeck]

    pkg.write_to_file(f"temp/{book_unique_codename}.apkg")
