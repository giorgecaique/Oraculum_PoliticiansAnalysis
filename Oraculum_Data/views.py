from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.shortcuts import render, HttpResponse
import requests
import json
import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response

user = None

def home(request):
    global user
    #if user is None:
    #    return login(request)
    return render(request, 'Pages/HomePage.html')

def login(request):
    return render(request, 'Pages/login.html')

def saude(request):
    global user
    if user is None:
        return login(request)
    return render(request, 'Pages/Saude.html')

def deputados(request):
    global user
    if user is None:
        return login(request)
    return render(request, 'Pages/Deputados.html')

def partidos(request):
    global user
    if user is None:
        return login(request)
    return render(request, 'Pages/Partidos.html')

def cancerColo(request):
    global user
    if user is None:
        return login(request)
    return render(request, 'Pages/CancerColo.html')

class CancerColo(APIView):
    def get(self, request, format=None):
        try:
            response = requests.get('http://sage.saude.gov.br/graficos/cancerMamaColo/cancerColo3544.php?output=json')
            response_json = response.json()
            df = pd.DataFrame(response_json['resultset'], columns=['Ano', 'Branca', 'Amarela', 'Ignorada', 'Indigena', 'Parda', 'Preta']).astype(float)
            
            data = {'labels':df.Ano, 'dataframe' : df[request.query_params['dataset']], 'total' : df[request.query_params['dataset']].sum(), 'mean': round(df[request.query_params['dataset']].mean(), 2), 'std': round(df[request.query_params['dataset']].std(), 2), 'count': df[request.query_params['dataset']].count() }
            return Response(data)
        except Exception as ex:
            return Response(data)

class Users(APIView):
    def get(self, request, format=None):
        global user
        user = authenticate(username=request.query_params['user'], password=request.query_params['secret'])
        result = {'result':user is not None}
        return Response(result)

class Deputados(APIView):
    def get(self, request, format=None):
        url = "https://dadosabertos.camara.leg.br/api/v2/partidos"

        querystring = {"ordem":"ASC","ordenarPor":"sigla"}

        headers = {
            'accept': "application/json",
            'cache-control': "no-cache",
            'postman-token': "70af4e86-7056-65bf-f443-804378a0aa72"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        return Response(response)