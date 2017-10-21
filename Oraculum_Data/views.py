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
    if user is None:
        return login(request)
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

def deputados_relatorio(request):
    global user
    if user is None:
        return login(request)
    args = {'user' : user}
    return render(request, 'Pages/Deputados_Relatorio.html', args)

def deputados_lista(request):
    global user
    if user is None:
        return login(request)
    args = {'user' : user}
    return render(request, 'Pages/Deputados_Lista.html', args)

def deputado_dados(request, deputado = None):
    global user
    if user is None:
        return login(request)
    
    if deputado is None:
        return render(request, 'Pages/DadosDeputados.html')

    url = "https://dadosabertos.camara.leg.br/api/v2/deputados/" + deputado + "/despesas?itens=100&ordem=DESC&ordenarPor=numAno"
   
    querystring = {"ordem":"DESC","ordenarPor":"numAno"}

    headers = {
        'accept': "application/json"
    }

    json_response = requests.request("GET", url, headers=headers, params=querystring)
    response = json_response.json()

    df_despesas = pd.DataFrame(response['dados'])

    total = df_despesas['valorLiquido'].astype(float).sum()

    args = {'user' : user}

    return render(request, 'Pages/DadosDeputados.html', args)

def partido_dados(request, partido = None):
    global user
    if user is None:
        return login(request)
    
    if partido is None:
        return render(request, 'Pages/DadosPartidos.html')

    args = {'partido' : partido, 'user' : user}

    return render(request, 'Pages/DadosPartidos.html', args)

def partidos_relatorio(request):
    global user
    if user is None:
        return login(request)

    args = {'user' : user}
    return render(request, 'Pages/Partidos_Relatorio.html', args)

def partidos_lista(request):
    global user
    if user is None:
        return login(request)

    args = {'user' : user}
    return render(request, 'Pages/Partidos_Lista.html', args)

# API

@api_view(['GET'])
def api_getdeputados(request):
    global user
    if user is None:
        return login(request)

    if request.method == 'GET':
        try:
            df = pd.read_excel("//Users//giorgecaique//Documents//TI//Data//deputados.xlsx")
            df['CPF'] = df['CPF'].astype(str)
            df['DEPUTADOS_ID'] = df['DEPUTADOS_ID'].astype(str)
            df['SITE'] = df['SITE'].astype(str)
            df['ESCOLARIDADE'] = df['ESCOLARIDADE'].astype(str)
            df['UF_NASCIMENTO'] = df['UF_NASCIMENTO'].astype(str)
            result = {'dados' : df.T.to_dict().values()}
            return Response(result)
        except Exception as ex:
            return Response({'result' : ex.args[0]})

@api_view(['GET'])
def api_getpartidos(request):
    global user
    if user is None:
        return login(request)

    if request.method == 'GET':
        try:
            df = pd.read_excel("//Users//giorgecaique//Documents//TI//Data//partidos.xlsx")
            partido = request.GET.get('partido', None)
            if partido is not None:
                df = df[df['PARTIDO_SIGLA'].astype(str) == str(partido)]
            df['PARTIDO_ID'] = df['PARTIDO_ID'].astype(str)
            df['PARTIDO_NUMERO_ELEITORAL'] = df['PARTIDO_NUMERO_ELEITORAL'].astype(str)
            df['PARTIDO_SIGLA'] = df['PARTIDO_SIGLA'].astype(str)
            df['PARTIDO_TOTAL_MEMBROS'] = df['PARTIDO_TOTAL_MEMBROS'].astype(str)
            df['PARTIDO_TOTAL_POSSE'] = df['PARTIDO_TOTAL_POSSE'].astype(str)
            df['PARTIDO_URL_FACEBOOK'] = df['PARTIDO_URL_FACEBOOK'].astype(str)
            df['PARTIDO_URL_SITE'] = df['PARTIDO_URL_SITE'].astype(str)
            df['PARTIDO_URL_FOTO_LIDER'] = df['PARTIDO_URL_FOTO_LIDER'].astype(str)
            df['PARTIDO_NOME_LIDER'] = df['PARTIDO_NOME_LIDER'].astype(str)
            df['PARTIDO_UF_LIDER'] = df['PARTIDO_UF_LIDER'].astype(str)
            result = {'dados' : df.T.to_dict().values()}
            return Response(result)
        except Exception as ex:
            return Response({'result' : ex.args[0]})

@api_view(['GET'])
def api_alteruser(request):
    global user
    
    if request.method == 'GET':
        if user is not None:
            try:
                user.username = request.query_params['user']
                password = request.query_params['secret']
                if len(password) < 8:
                    raise Exception('Senha muito pequena')
                float(password) # check if the password is tottaly numeric
    
                result = {'result': "Senha não pode conter só números"}
                return Response(result)
            except ValueError as ex:
                user.set_password(request.query_params['secret'])
                user.save()
                result = {'result': True}
                return Response(result)
            except Exception as ex:
                return Response({'result': ex.args[0]})

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
                return Response({'result': ex.args[0]})            

@api_view(['GET'])
def api_login(request):
    try:
        global user

        user = authenticate(username=request.query_params['user'], password=request.query_params['secret'])
        result = {'result':user is not None}
        return Response(result)
    except Exception as ex:
        return Response({'result': ex.args[0]})
