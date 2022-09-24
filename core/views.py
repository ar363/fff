from django.shortcuts import render, get_object_or_404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from core.models import Book, BookPoint

try:
    import simplejson as json
except ImportError:
    import json

@staff_member_required
def book_cap(request, id, pageNo):
    b = get_object_or_404(Book, pk=id)
    return render(request, "core/book_cap.html", {
        "book": b,
        "pageNo": pageNo,
        "prevPageNo": pageNo - 1,
        "nextPageNo": pageNo + 1,
    })

@csrf_exempt
def save_pts(request):
    j = json.loads(request.body)

    for pt in j['pts']:
        BookPoint.objects.create(
            book=Book.objects.get(id=j['id']),
            page=j['page'],
            h=pt
        )
    
    return JsonResponse({"ok": 1})



@csrf_exempt
def clrsave_pts(request):
    j = json.loads(request.body)

    BookPoint.objects.filter(book=Book.objects.get(id=j['id']), page=j['page']).delete()

    for pt in j['pts']:
        BookPoint.objects.create(
            book=Book.objects.get(id=j['id']),
            page=j['page'],
            h=pt
        )
    
    return JsonResponse({"ok": 1})


@csrf_exempt
def get_pts(request, bookid, pageid):
    bps = BookPoint.objects.filter(book=Book.objects.get(id=bookid), page=pageid)
    bps = [i.h for i in bps]
    return JsonResponse({"pts": bps})