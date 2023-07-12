from django.urls import include, path
from .views import *
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('users', UserViewset)
router.register('movies', MoviesViewset, basename="movies")
router.register('collections', CollectionViewset, basename="collections")


urlpatterns = [
    path('samp/', samp, name="samp"),
    path('', include(router.urls)),
    path('token/', ObtainJWTToken.as_view(), name='obtain_token'),
    path('protected/', ProtectedView.as_view(), name='protected_view'),
    path('request-count/', get_request_count, name='get_request_count'),
    path('request-count/reset/', reset_request_count, name='reset_request_count'),
    ]
