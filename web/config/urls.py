from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.public.urls", namespace="public")),
    path("app/", include("apps.dashboard.urls", namespace="dashboard")),
    path("contas/", include("apps.accounts.urls", namespace="accounts")),
    path("buscas/", include("apps.searches.urls", namespace="searches")),
    path("documentos/", include("apps.documents.urls", namespace="documents")),
    path("revisao/", include("apps.reviews.urls", namespace="reviews")),
    path("validacao/", include("apps.validations.urls", namespace="validations")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
