"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

import coreapp.page_views


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),
    # Frotend
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('', coreapp.page_views.index, name='index'),
    # API
    path('api/v1/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ])),
] + (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

if settings.ENABLE_DJANGO_TOOLBAR:
    import debug_toolbar  # noqa

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
