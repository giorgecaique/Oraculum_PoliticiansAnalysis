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

import pymysql

user = None

def home(request):
    global user
    if user is None:
        return login(request)
    users = User.objects.all()
    args = {'user' : user, 'users' : users}
    return render(request, 'Pages/index.html', args)

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

    args = {'dataframe': df_despesas.to_html(classes="table table-striped"), 'valor' : df_despesas['valorLiquido'].astype(float).tolist(), 'data_documento' : json.dumps(df_despesas['dataDocumento'].astype(str).tolist()), 'total': "R$ " + str(total), 'deputado' : deputado, 'user' : user}

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

def doacao(request):
    global user
    if user is None:
        return login(request)

    args = {'user' : user}
    return render(request, 'Pages/Doacao.html', args)

# API

@api_view(['GET'])
def api_getdeputados(request):
    global user
    if user is None:
        return login(request)

    if request.method == 'GET':
        try:
            dp = deputado_persistencia()
            df = dp.get()
            #df = pd.read_excel("Oraculum_Data/deputados.xlsx")
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
        
        pt = partido_persistencia()
        df = pt.get()
        #df = pd.read_excel("Oraculum_Data/partidos.xlsx")
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



cnx = pymysql.connect(user='bf20c9d4f7c87d', password='2332efd2',
                        host='br-cdbr-azure-south-b.cloudapp.net',
                        database='oraculumdb')

cursor = cnx.cursor()


class deputado_persistencia:
    def __init__(self):
        self.DEPUTADOS_ID = []
        self.IMG_DEPUTADO = []
        self.NOME = []
        self.DATA_NASCIMENTO = []
        self.ESCOLARIDADE = []
        self.MUNICIPIO_NASCIMENTO = []
        self.SEXO = []
        self.UF_NASCIMENTO = []
        self.SIGLA_PARTIDO = []
        self.SIGLA_UF = []
        self.SITUACAO = []
        self.CONDICAO_ELEITORAL = []
        self.EMAIL = []
        self.SITE = []

    def get(self):
        select_deputados = "SELECT DEPUTADOS_ID, IMG_DEPUTADO, NOME, DATA_NASCIMENTO, ESCOLARIDADE, MUNICIPIO_NASCIMENTO, SEXO, UF_NASCIMENTO, SIGLA_PARTIDO, SIGLA_UF, SITUACAO, CONDICAO_ELEITORAL, EMAIL, SITE FROM DEPUTADOS"

        cursor.execute(select_deputados)

        for (_DEPUTADOS_ID, _IMG_DEPUTADO, _NOME, _DATA_NASCIMENTO, _ESCOLARIDADE, _MUNICIPIO_NASCIMENTO, _SEXO, _UF_NASCIMENTO, _SIGLA_PARTIDO, _SIGLA_UF, _SITUACAO, _CONDICAO_ELEITORAL, _EMAIL, _SITE) in cursor:
            self.DEPUTADOS_ID.append(_DEPUTADOS_ID)
            self.IMG_DEPUTADO.append(_IMG_DEPUTADO)
            self.NOME.append(_NOME)
            self.DATA_NASCIMENTO.append(_DATA_NASCIMENTO)
            self.ESCOLARIDADE.append(_ESCOLARIDADE)
            self.MUNICIPIO_NASCIMENTO.append(_MUNICIPIO_NASCIMENTO)
            self.SEXO.append(_SEXO)
            self.UF_NASCIMENTO.append(_UF_NASCIMENTO)
            self.SIGLA_PARTIDO.append(_SIGLA_PARTIDO)
            self.SIGLA_UF.append(_SIGLA_UF)
            self.SITUACAO.append(_SITUACAO)
            self.CONDICAO_ELEITORAL.append(_CONDICAO_ELEITORAL)
            self.EMAIL.append(_EMAIL)
            self.SITE.append(_SITE)

        data_deputados = {
        "DEPUTADOS_ID" : self.DEPUTADOS_ID,
        "IMG_DEPUTADO" : self.IMG_DEPUTADO,
        "NOME" : self.NOME,
        "DATA_NASCIMENTO" : self.DATA_NASCIMENTO,
        "ESCOLARIDADE" : self.ESCOLARIDADE,
        "MUNICIPIO_NASCIMENTO" : self.MUNICIPIO_NASCIMENTO,
        "SEXO" : self.SEXO,
        "UF_NASCIMENTO" : self.UF_NASCIMENTO,
        "SIGLA_PARTIDO" : self.SIGLA_PARTIDO,
        "SIGLA_UF" : self.SIGLA_UF,
        "SITUACAO" : self.SITUACAO,
        "CONDICAO_ELEITORAL" : self.CONDICAO_ELEITORAL,
        "EMAIL" : self.EMAIL,
        "SITE" : self.SITE
        }

        deputados_df = pd.DataFrame(data_deputados)
        return deputados_df

class partido_persistencia:
    def __init__(self):
        self.PARTIDO_ID = []
        self.PARTIDO_SIGLA = []
        self.PARTIDO_NOME = []
        self.PARTIDO_URI = []
        self.PARTIDO_TOTAL_POSSE = []
        self.PARTIDO_TOTAL_MEMBROS = []
        self.PARTIDO_NOME_LIDER = []
        self.PARTIDO_UF_LIDER = []
        self.PARTIDO_URL_FOTO_LIDER = []
        self.PARTIDO_NUMERO_ELEITORAL = []
        self.PARTIDO_URL_LOGO = []
        self.PARTIDO_URL_SITE = []
        self.PARTIDO_URL_FACEBOOK = []

    def get(self):
        select_partidos = "SELECT PARTIDO_ID, PARTIDO_SIGLA, PARTIDO_NOME, PARTIDO_URI, PARTIDO_TOTAL_POSSE, PARTIDO_TOTAL_MEMBROS, PARTIDO_NOME_LIDER, PARTIDO_UF_LIDER, PARTIDO_URL_FOTO_LIDER, PARTIDO_NUMERO_ELEITORAL, PARTIDO_URL_LOGO, PARTIDO_URL_SITE, PARTIDO_URL_FACEBOOK FROM PARTIDOS"

        cursor.execute(select_partidos)

        for (_PARTIDO_ID, _PARTIDO_SIGLA, _PARTIDO_NOME, _PARTIDO_URI, _PARTIDO_TOTAL_POSSE, _PARTIDO_TOTAL_MEMBROS, _PARTIDO_NOME_LIDER, _PARTIDO_UF_LIDER, _PARTIDO_URL_FOTO_LIDER, _PARTIDO_NUMERO_ELEITORAL, _PARTIDO_URL_LOGO, _PARTIDO_URL_SITE, _PARTIDO_URL_FACEBOOK) in cursor:
            self.PARTIDO_ID.append(_PARTIDO_ID)
            self.PARTIDO_SIGLA.append(_PARTIDO_SIGLA)
            self.PARTIDO_NOME.append(_PARTIDO_NOME)
            self.PARTIDO_URI.append(_PARTIDO_URI)
            self.PARTIDO_TOTAL_POSSE.append(_PARTIDO_TOTAL_POSSE)
            self.PARTIDO_TOTAL_MEMBROS.append(_PARTIDO_TOTAL_MEMBROS)
            self.PARTIDO_NOME_LIDER.append(_PARTIDO_NOME_LIDER)
            self.PARTIDO_UF_LIDER.append(_PARTIDO_UF_LIDER)
            self.PARTIDO_URL_FOTO_LIDER.append(_PARTIDO_URL_FOTO_LIDER)
            self.PARTIDO_NUMERO_ELEITORAL.append(_PARTIDO_NUMERO_ELEITORAL)
            self.PARTIDO_URL_LOGO.append(_PARTIDO_URL_LOGO)
            self.PARTIDO_URL_SITE.append(_PARTIDO_URL_SITE)
            self.PARTIDO_URL_FACEBOOK.append(_PARTIDO_URL_FACEBOOK)

        data_partidos = {
        "PARTIDO_ID": self.PARTIDO_ID,
        "PARTIDO_SIGLA": self.PARTIDO_SIGLA,
        "PARTIDO_NOME": self.PARTIDO_NOME,
        "PARTIDO_URI": self.PARTIDO_URI,
        "PARTIDO_TOTAL_POSSE": self.PARTIDO_TOTAL_POSSE,
        "PARTIDO_TOTAL_MEMBROS": self.PARTIDO_TOTAL_MEMBROS,
        "PARTIDO_NOME_LIDER": self.PARTIDO_NOME_LIDER,
        "PARTIDO_UF_LIDER": self.PARTIDO_UF_LIDER,
        "PARTIDO_URL_FOTO_LIDER": self.PARTIDO_URL_FOTO_LIDER,
        "PARTIDO_NUMERO_ELEITORAL": self.PARTIDO_NUMERO_ELEITORAL,
        "PARTIDO_URL_LOGO": self.PARTIDO_URL_LOGO,
        "PARTIDO_URL_SITE": self.PARTIDO_URL_SITE,
        "PARTIDO_URL_FACEBOOK": self.PARTIDO_URL_FACEBOOK
        }

        partidos_df = pd.DataFrame(data_partidos)
        return partidos_df