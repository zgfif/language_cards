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
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view()),
    path('signup', views.SignUpView.as_view()),
    path('signin', views.SignInView.as_view()),
    path('signout', views.SignOutView.as_view()),
    path('profile', views.AccountView.as_view()),
    path('add_word', views.AddWordView.as_view()),
    path('words', views.WordListView.as_view(), name='words'),
    path('training', views.LearningPageView.as_view()),
    path('learn_word/en-ru/<int:id>/', views.FromEng.as_view()),
    path('learn_word/ru-en/<int:id>/', views.FromRu.as_view()),
    path('words/<int:id>/delete/', views.DeleteWordView.as_view()),
    path('words/<int:id>/edit/', views.EditWordView.as_view()),
    path('words/<int:id>/reset/', views.ResetWordView.as_view()),
    path('translate', views.TranslateWord.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
