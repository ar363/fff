from django.urls import path

from . import views

urlpatterns = [
    path("book_cap/<int:id>/<int:pageNo>/", views.book_cap, name="book_cap"),
    path("save-pts", views.save_pts),
    path("clrsave-pts", views.clrsave_pts),
    path("get-pts/<int:bookid>/<int:pageid>/", views.get_pts),
]
