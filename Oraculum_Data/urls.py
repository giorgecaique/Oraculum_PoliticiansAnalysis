from django.conf.urls import url
from . import views
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', views.login),
    url(r'^cancerColo/$', views.cancerColo),
    url(r'^deputados/$', views.deputados),
    url(r'^partidos/$', views.partidos),
    url(r'^saude/$', views.saude),
    url(r'^api/chart/data/$', views.CancerColo.as_view()),
    url(r'^api/deputados/$', views.Deputados.as_view()),
    url(r'^api/login/$', views.Users.as_view()),
    url(r'^deputados/despesas/$', views.despesas),
]
