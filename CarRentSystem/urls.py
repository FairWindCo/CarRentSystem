"""CarRentSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from car_management import urls as car_urls
from car_rent import urls as rent_urls
from trips import urls as trips_urls
from trip_stat import urls as trip_stat_urls

admin.autodiscover()

urlpatterns = [
                  # place it at whatever base url you like
                  url(r'^ajax_select/', include(ajax_select_urls)),
                  path('admin/', admin.site.urls),
                  url('', include(car_urls)),
                  url('', include(rent_urls)),
                  url('', include(trips_urls)),
                  url('', include(trip_stat_urls)),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
