from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('', include('taskManager.urls')),
]