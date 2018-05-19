from django.conf.urls import url
from . import views
from django.contrib.auth.views import login, logout

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^alteruser/$', views.alteruser),
    url(r'^signup/$', views.signup),
    url(r'^deputados_relatorio/$', views.deputados_relatorio),
    url(r'^deputados_lista/$', views.deputados_lista),
    url(r'^partidos_relatorio/$', views.partidos_relatorio),
    url(r'^partidos_lista/$', views.partidos_lista),
    url(r'^api/login/$', views.api_login),
    url(r'^api/alteruser/$', views.api_alteruser),
    url(r'^api/deleteuser/$', views.api_deleteuser),
    url(r'^api/getdeputados/$', views.api_getdeputados),
    url(r'^api/getpartidos/$', views.api_getpartidos),
    url(r'^api/getproposicoes/$', views.api_getproposicoes),
    url(r'^doacao/$', views.doacao),
    url(r'^deputados/dados/(?P<deputado>[0-9]+)/$', views.deputado_dados),
    url(r'^partidos/dados/(?P<partido>[0-9]+)/$', views.partido_dados),
]
