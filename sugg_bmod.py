import fitz
from PIL import Image, ImageFilter, ImageDraw

def page_img(pdf, page):
    zoom = 2 
    mat = fitz.Matrix(zoom, zoom)

    p = fitz.open(pdf)
    pg = p.load_page(page - 1)
    pix = pg.get_pixmap(matrix = mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def show(im):
    import matplotlib.pyplot as plt
    plt.imshow(im)
    plt.show()

p = page_img('b-halo.pdf', 18)


w,h = p.size
pzq = p.crop((107, 0, 135, h)).filter(ImageFilter.MinFilter(27))

pzw, pzh = pzq.size

MIN_QWDIF = 50

bls = []

prevpx = (255,255,255)
for i in range(pzh):
    px = pzq.getpixel((int(pzw / 2), i))
    if px == (0,0,0) and prevpx != (0,0,0):
        bls.append(i)

    prevpx = px

pd = ImageDraw.Draw(p)
for b in bls:
    pd.line([(0,b), (w,b)], fill="green")

# show(p)

pza = p.crop((145, 0, 190, h))

import cv2
import numpy

pza_cv = numpy.array(pza)
pza_cv = pza_cv[:, :, ::-1].copy()

tpl_im = cv2.imread('ans.png')

pza_tpl = cv2.matchTemplate(tpl_im, pza_cv, cv2.TM_CCORR)
print(pza_tpl)