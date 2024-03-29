from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new",views.create_listing,name="new"),
    path("<int:listing_id>",views.listing,name="listing"), 
    path("<int:listing_id>/addcomment",views.comment,name="addcomment"),
    path("<int:listing_id>/adddelwl",views.watchlist_add_del,name="adddelwl"),
    path("watchlist",views.watchlist,name="watchlist"),
    path("<int:listing_id>/closelisting",views.close_listing,name="closelisting"),
    path("categories",views.categories,name="categories"),
    path("category/<str:category>",views.category,name="category"),
    path("closed", views.closed_listings, name="closed")
]
