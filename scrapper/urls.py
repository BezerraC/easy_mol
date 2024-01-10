# from django.conf import settings
# from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
            path('', views.home, name='home'),
            path('search/', views.search, name='search'),
            path('download/', views.download_file, name='download_file'),
            path('features/', views.features, name='features'),
            path('about/', views.about, name='about'),
            #path('test/', views.test, name='test'),

        ]

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)