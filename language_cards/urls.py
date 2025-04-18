"""
URL configuration for language_cards project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import routers

from core import views
from core.api import views as api_views

router = routers.DefaultRouter()
router.register('words', api_views.WordViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view()),
    path('signup', views.SignUpView.as_view()),
    path('signin', views.SignInView.as_view()),
    path('signout', views.SignOutView.as_view()),
    path('profile', views.ProfileView.as_view()),
    path('add_word', views.AddWordView.as_view(), name='add_word'),
    path('words', views.WordListView.as_view(), name='words'),
    path('exercises', views.ExercisesPageView.as_view()),
    path('studying_to_native/<int:id>/', views.StudyingToNativeCard.as_view()),
    path('native_to_studying/<int:id>/', views.NativeToStudyingCard.as_view()),
    path('words/<int:id>/delete/', views.DeleteWordView.as_view()),
    path('words/<int:id>/edit/', views.EditWordView.as_view()),
    path('words/<int:id>/reset/', views.ResetWordView.as_view()),
    path('translate', views.TranslateApi.as_view()),
    path('toggle_lang', api_views.ToggleLanguage.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
