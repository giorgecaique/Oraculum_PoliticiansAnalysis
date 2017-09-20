from django.http import JsonResponse
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
import requests, json
import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

user = None

def home(request):
    global user
    #if user is None:
    #    return login(request)
    users = User.objects.all()
    args = {'user' : user, 'users' : users}
    return render(request, 'Pages/HomePage.html', args)

def login(request):
    return render(request, 'Pages/login.html')

def logout(request):
    auth_logout(request)
    return render(request, "Pages/login.html")

def alteruser(request):
    global user

    if user is None:
        return login(request)
    
    args = {'user' : user}
    return render(request, "Pages/alterUser.html", args)

def signup(request):
    global user
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            auth_login(request, user) 
            return redirect('/Oraculum_Data/')
    else:
        form = UserCreationForm()
    return render(request, 'Pages/Signup.html', {'form': form})

def deputados(request):
    global user
    if user is None:
        return login(request)
    args = {'user' : user}
    return render(request, 'Pages/Deputados.html', args)

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

    args = {'dataframe': df_despesas.to_html(classes="table table-striped"), 'valor' : df_despesas['valorLiquido'].astype(float).tolist(), 'data_documento' : json.dumps(df_despesas['dataDocumento'].astype(str).tolist()), 'total': "R$ " + str(total), 'deputado' : deputado, 'user' : user}

    return render(request, 'Pages/Despesas.html', args)

def partidos(request):
    global user
    if user is None:
        return login(request)
    return render(request, 'Pages/Partidos.html')

# API

@api_view(['GET'])
def api_alteruser(request):
    global user
    
    if request.method == 'GET':
        if user is not None:
            try:
                user.username = request.query_params['user']
                user.set_password(request.query_params['secret'])
                user.save()
                result = {'result': True}
                return Response(result)
            except Exception as ex:
                return Response({'result': ex})

@api_view(['GET'])
def api_deleteuser(request):
    global user
    
    if request.method == 'GET':
        if user is not None:
            try:
                user.delete()
                user = None
                result = {'result': True}
                return Response(result)
            except Exception as ex:
                return Response({'result': ex})            

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