from django.contrib import admin
from django.urls import path
from petstoreapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.indexpage, name="home"),  # 👈 Home URL path
    path('register/', views.register, name="register"),
    path('login/', views.loginuser, name="login"),
    path('logout', views.loginuser),
    path('footer', views.footer),
    path('about', views.about),
    path('contact', views.contact),
    path('index', views.indexpage),
    path('home', views.home),
    path('catfilter/<cv>', views.catfilter),
    path('sort/<sv>', views.sort),
    path('range', views.range),
    path('pdetails/<pid>', views.product_details),
    path('addtocart/<pid>', views.addtocart),
    path('viewcart', views.viewcart),
    path('remove/<cid>', views.remove),
    path('updateqty/<qv>/<cid>', views.updateqty),
    path('placeorder', views.placeorder),
    path('makepayment', views.makepayment),
    path('sendmail', views.sendusermail),
    path('logoutuser', views.logoutuser, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
