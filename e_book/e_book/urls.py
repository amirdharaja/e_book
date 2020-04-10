from django.urls import include, path
from django.conf import settings

urlpatterns = [
    path('', include('book_service.urls.common_urls')),
    path('user/', include('book_service.urls.user_urls')),
    path('admin/', include('book_service.urls.admin_urls')),
    path('author/', include('book_service.urls.author_urls')),
]
