"""
URL configuration for Maha_Intern project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  
from django.conf.urls.static import static 
from rest_framework_simplejwt import views as jwt_views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger UI settings
schema_view = get_schema_view(
   openapi.Info(
      title="MahaIntern swagger api ",
      default_version='v1',
      description="API list for MahaIntern",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="tajjmul@mandates.in"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/config/', include('core_app.urls')),
    path('api/student/', include('student_app.urls')),
     path('api/admin-app/', include('admin_app.urls')),
    
    path('api/organization/', include('organization_app.urls')),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

