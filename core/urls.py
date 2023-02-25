from django.urls import path

from . import views

urlpatterns = [
    path("book_cap/<int:id>/<int:pageNo>/", views.book_cap, name="book_cap"),
    path("save-pts", views.save_pts),
    path("clrsave-pts", views.clrsave_pts),
    path("get-pts/<int:bookid>/<int:pageid>/", views.get_pts),
    path("sugg_pts/<int:book_id>/<int:page_no>/", views.sugg_pts),
    path(
        "api/imprev/<int:book_id>/<int:page_no>/",
        views.page_img_preview,
    ),
    path("inf/<int:book_id>/", views.preview_inf_scroll),
]
