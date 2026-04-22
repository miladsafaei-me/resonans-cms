from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from resonans_cms.apps.core.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("cms/", include("resonans_cms.apps.cms_admin.urls")),
    path("blog/", include("resonans_cms.apps.blog.urls")),
    path("news/", include("resonans_cms.apps.news.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
