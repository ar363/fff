from sqlite3 import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404

from core.models import Book, BookPoint

import fitz
from PIL import Image, ImageFilter
import numpy as np
import cv2

try:
    import simplejson as json
except ImportError:
    import json


@staff_member_required
def book_cap(request, id, pageNo):
    b = get_object_or_404(Book, pk=id)

    o = fitz.open(b.pdf)
    pct = o.page_count
    o.close()

    if pageNo > pct or pageNo < 1:
        raise Http404

    return render(
        request,
        "core/book_cap.html",
        {
            "book": b,
            "pageNo": pageNo,
            "prevPageNo": pageNo - 1,
            "nextPageNo": pageNo + 1,
            "pageCount": pct,
        },
    )


@csrf_exempt
def save_pts(request):
    j = json.loads(request.body)

    for pt in j["pts"]:
        BookPoint.objects.create(
            book=Book.objects.get(id=j["id"]), page=j["page"], h=pt
        )

    return JsonResponse({"ok": 1})


@csrf_exempt
def clrsave_pts(request):
    j = json.loads(request.body)

    BookPoint.objects.filter(book=Book.objects.get(id=j["id"]), page=j["page"]).delete()

    for pt in j["pts"]:
        try:
            BookPoint.objects.create(
                book=Book.objects.get(id=j["id"]), page=j["page"], h=pt
            )
        except IntegrityError as e:
            pass

    return JsonResponse({"ok": 1})


def get_pts(request, bookid, pageid):
    bps = BookPoint.objects.filter(book=Book.objects.get(id=bookid), page=pageid)
    bps = [round(i.h, 4) for i in bps]
    return JsonResponse({"pts": bps})


def page_img(pdf, page):
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)

    p = fitz.open(pdf)
    pg = p.load_page(page - 1)
    pix = pg.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img


def sugg_b_pts(book, page_no):
    TOP = 100
    BOT = 1490

    p = page_img(book.pdf, page_no)

    w, h = p.size
    pzq = p.crop((107, 0, 135, h)).filter(ImageFilter.MinFilter(27))

    pzw, pzh = pzq.size

    bls = []

    prevpx = (255, 255, 255)
    for i in range(pzh):
        px = pzq.getpixel((int(pzw / 2), i))
        if px == (0, 0, 0) and prevpx != (0, 0, 0):
            mod_i = i
            allwhite = False
            while not allwhite:
                pwc = p.crop((0, mod_i, w, mod_i + 1))
                if pwc.convert("L").getextrema()[0] > 127:
                    allwhite = True
                else:
                    mod_i -= 1

            bls.append(mod_i)

        prevpx = px

    bls = [(i * 100 / h) for i in bls if i < BOT and i > TOP]
    bls = list(set(bls))

    pza = p.crop((140, 0, 200, h))
    pza_cv = np.array(pza)
    pza_cv = pza_cv[:, :, ::-1].copy()

    tpl_im = cv2.imread("ans.png")

    pza_tpl = cv2.matchTemplate(pza_cv, tpl_im, cv2.TM_CCOEFF_NORMED)
    ansY, _ = np.where(pza_tpl >= 0.8)
    ansY = ansY.tolist()
    ansY = [(i * 100 / h) for i in ansY]
    ansY = list(set(ansY))

    return [*ansY, *bls]

def sugg_a_pts(book, page_no):
    TOP = 100
    BOT = 1490

    p = page_img(book.pdf, page_no)

    w, h = p.size
    pzq = p.crop((107, 0, 135, h)).filter(ImageFilter.MinFilter(27))

    pzw, pzh = pzq.size

    bls = []

    prevpx = (255, 255, 255)
    for i in range(pzh):
        px = pzq.getpixel((int(pzw / 2), i))
        if px == (0, 0, 0) and prevpx != (0, 0, 0):
            mod_i = i
            allwhite = False
            while not allwhite:
                pwc = p.crop((0, mod_i, w, mod_i + 1))
                if pwc.convert("L").getextrema()[0] > 127:
                    allwhite = True
                else:
                    mod_i -= 1

            bls.append(mod_i)

        prevpx = px

    bls = [(i * 100 / h) for i in bls if i < BOT and i > TOP]
    bls = list(set(bls))

    pza = p.crop((140, 0, 235, h))
    pza_cv = np.array(pza)
    pza_cv = pza_cv[:, :, ::-1].copy()

    tpl_im = cv2.imread("sol.png")

    pza_tpl = cv2.matchTemplate(pza_cv, tpl_im, cv2.TM_CCOEFF_NORMED)
    ansY, _ = np.where(pza_tpl >= 0.8)
    
    ansY = np.delete(ansY, np.argwhere(np.ediff1d(ansY) <= 10) + 1)

    ansY = ansY.tolist()
    ansY = [(i * 100 / h) for i in ansY]
    ansY = list(set(ansY))

    return [*ansY, *bls]


def sugg_pts(request, book_id, page_no):
    book = get_object_or_404(Book, id=book_id)
    if book.type == "B":
        pts = sugg_b_pts(book, page_no)
        return JsonResponse({"pts": pts})
    if book.type == "A":
        pts = sugg_a_pts(book, page_no)
        return JsonResponse({"pts": pts})
    else:
        return JsonResponse({"pts": ""})
