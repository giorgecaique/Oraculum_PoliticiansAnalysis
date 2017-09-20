from django.conf.urls import url
from . import views
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^alteruser/$', views.alteruser),
    url(r'^signup/$', views.signup),
    url(r'^deputados/$', views.deputados),
    url(r'^partidos/$', views.partidos),
    url(r'^api/deputados/$', views.Deputados.as_view()),
    url(r'^api/login/$', views.Users.as_view()),
    url(r'^api/alteruser/$', views.api_alteruser),
    url(r'^api/deleteuser/$', views.api_deleteuser),
    url(r'^deputados/dados/(?P<deputado>[0-9]+)/$', views.deputado_dados),
]
