from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, StoringInformationViewSet
from .views import ping

router = DefaultRouter()
router.register(r'author', AuthorViewSet)
router.register(r'book', BookViewSet)
router.register(r'leftover', StoringInformationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ping', ping, name='ping'),
]
