from django.contrib import admin
from django.urls import path, re_path
from core import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.shortcuts import redirect
from django.views.static import serve
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Web3 Trust Guard MCP Server",
        default_version='v1',
        description="MCP Server exposing 8 Web3 security and donation verification tools.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', lambda request: redirect('swagger/', permanent=False)),

    path("openapi.json", lambda request: serve(request, "openapi.json", document_root=settings.BASE_DIR / "static")),
    path('.well-known/ai-plugin.json', lambda request: serve(request, '.well-known/ai-plugin.json', document_root=settings.BASE_DIR / 'static/.well-known')),

    path('admin/', admin.site.urls),
    path('mcp.json', views.mcp_manifest),
    path('check_token/', views.check_token),
    path('check_wallet/', views.check_wallet),
    path('check_nft/', views.check_nft),
    path('check_url/', views.check_url),
    path('simulate_sol_tx/', views.simulate_sol_tx),
    path('check_sol_token/', views.check_sol_token),
    path('verify_donation/', views.verify_donation),
    path('causes/', views.list_verified_causes),

    # Swagger docs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
