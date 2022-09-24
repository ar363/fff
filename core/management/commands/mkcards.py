from django.core.management.base import BaseCommand, CommandError
from core.models import Book, BookPoint
import fitz
from PIL import Image



BOTTOM = 89.5
TOP = 6


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        mkcards(2)
        self.stdout.write(self.style.SUCCESS('done!'))


def page_img(pdf, page):
    zoom = 2 
    mat = fitz.Matrix(zoom, zoom)

    p = fitz.open(pdf)
    pg = p.load_page(page - 1)
    pix = pg.get_pixmap(matrix = mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def mkcards(bookId):
    folname = 'bhnh'
    book = Book.objects.get(id=bookId)
    coords = BookPoint.objects.filter(book=book).order_by('page', 'h').values('page', 'h')

    # coords = coords[:2] #REMOVE SOON
    coords = [{'page': 1, 'h': TOP}, *coords]




    pdf = book.pdf

    
    glob_name_sys = 1
    for i in range(len(coords) - 1):
        ia, ib = coords[i], coords[i+1]

        if ia['page'] == ib['page']:
            # simple box
            im = page_img(pdf, ia['page'])

            w,h = im.size

            im = im.crop((0, (ia['h'] * h / 100), w, (ib['h'] * h / 100)))
            im.save(f'temp/{folname}/b-halo-{str(glob_name_sys).zfill(4)}.jpg')
        else:
            ims = []
            stw = 0

            for j in range(ia['page'], ib['page'] + 1):
                im = page_img(pdf, j)
                w,h = im.size
                stw = w

                if j == ia['page']:
                    ims.append(im.crop((0, (ia['h'] * h / 100) , w, (BOTTOM * h / 100))))
                elif j == ib['page']:
                    ims.append(im.crop((0, (TOP * h / 100) , w, (ib['h'] * h / 100))))
                else:
                    ims.append(im.crop((0, (TOP * h / 100) , w, (BOTTOM * h / 100))))
            
            total_h = 0
            for i in ims:
                total_h += i.size[1]

            calc_total_h = 0

            lg_im = Image.new("RGB", (stw, total_h))
            for i in range(len(ims)):
                lg_im.paste(ims[i], (0, calc_total_h))
                calc_total_h += ims[i].size[1]
            
            lg_im.save(f'temp/{folname}/b-halo-{str(glob_name_sys).zfill(4)}.jpg')
        
        glob_name_sys += 1
                    
            




