from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'PracticaFinal.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL}),
    url(r'^todas(.*)$', "appfinal.views.todas"),
    url(r'^actividades(.*)$', "appfinal.views.actividades"),
    url(r'^actualizar(.*)$', "appfinal.views.todas"),
    url(r'^ayuda$', "appfinal.views.ayuda"),
    url(r'^login$', "appfinal.views.login_page", name="login"),
    url(r'^logout$', "appfinal.views.logout_page", name="logout"),
    url(r'^apuntarse(.*)$', "appfinal.views.apuntarse"),
    url(r'^(.*)$', "appfinal.views.inicio"),
)
