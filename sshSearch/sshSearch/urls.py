"""sshSearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from search.views import SearchSuggest, SearchView, ListView, AssociationView, CompanyView, CompetitionView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',ListView.as_view(),name="index"),
    url(r'^suggest/$',SearchSuggest.as_view(),name="suggest"),
    url(r'^search/$',SearchView.as_view(),name="search"),
    url(r'^list/$',ListView.as_view(),name="list"),
    url(r'^association/$',AssociationView.as_view(),name="association"),
    url(r'^company/$',CompanyView.as_view(),name="company"),
    url(r'^competition/$',CompetitionView.as_view(),name="competition")
]
