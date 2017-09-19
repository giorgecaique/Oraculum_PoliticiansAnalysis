from django.http import JsonResponse
from django.contrib.auth import login as l, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
import requests, json
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

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            l(request, user)
            return redirect('/Oraculum_Data/')
    else:
        form = UserCreationForm()
    return render(request, 'Pages/Signup.html', {'form': form})

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

def deputado_dados(request, deputado = None):
    global user
    if user is None:
        return login(request)
    
    if deputado is None:
        return render(request, 'Pages/Despesas.html')

    url = "https://dadosabertos.camara.leg.br/api/v2/deputados/" + deputado + "/despesas?itens=100&ordem=DESC&ordenarPor=numAno"
   
    querystring = {"ordem":"DESC","ordenarPor":"numAno"}

    headers = {
        'accept': "application/json"
    }

    json_response = requests.request("GET", url, headers=headers, params=querystring)
    response = json_response.json()

    df_despesas = pd.DataFrame(response['dados'])

    total = df_despesas['valorLiquido'].astype(float).sum()

    args = {'dataframe': df_despesas.to_html(classes="table table-striped"), 'valor' : df_despesas['valorLiquido'].astype(float).tolist(), 'data_documento' : json.dumps(df_despesas['dataDocumento'].astype(str).tolist()), 'total': "R$ " + str(total), 'deputado' : deputado}

    return render(request, 'Pages/Despesas.html', args)

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

# API

class CancerColo(APIView):
    def get(self, request, format=None):
        try:
            response = requests.get('http://sage.saude.gov.br/graficos/cancerMamaColo/cancerColo3544.php?output=json')
            response_json = response.json()
            df = pd.DataFrame(response_json['resultset'], columns=['Ano', 'Branca', 'Amarela', 'Ignorada', 'Indigena', 'Parda', 'Preta']).astype(float)
            
            data = {'labels':df.Ano, 'dataframe' : df[request.query_params['dataset']], 'total' : df[request.query_params['dataset']].sum(), 'mean': round(df[request.query_params['dataset']].mean(), 2), 'std': round(df[request.query_params['dataset']].std(), 2), 'count': df[request.query_params['dataset']].count() }
            return Response(data)
        except Exception as ex:
            return Response({'ERROR': ex})

class Users(APIView):
    def get(self, request, format=None):
        try:
            global user
            user = authenticate(username=request.query_params['user'], password=request.query_params['secret'])
            result = {'result':user is not None}
            return Response(result)
        except Exception as ex:
            return Response({'result': ex})

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

class Despesas(APIView):
    def get(self, request, format=None):
        pass