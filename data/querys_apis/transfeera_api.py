import time
import pandas as pd
import requests
import streamlit as st
import requests
import os
import zipfile

@st.cache_data
def query_transfeera_payments(day1, day2):
    token = create_authorization().get("access_token")
    request_id = request_report(token, f"{day1}", f"{day2}").get("id")
    time.sleep(5)
    file_url = get_report_url(token, request_id).get("file_url")
    response = download_report(file_url)
    if response:
        report = read_report()
    
    return report

#Functions:
def create_authorization():
    url_token = "https://login-api.transfeera.com/authorization"
    access_token = st.secrets["transfeera_api"]
    headers_token = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url_token, json=dict(access_token), headers=headers_token)
    return response.json()


def request_report(token, start_date, end_date):
    url = "https://api.transfeera.com/statement_report"
    authorization = "Bearer " + token
    payload = {
        "format": "csv",
        "created_at__gte": start_date,
        "created_at__lte": end_date
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": authorization
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def get_report_url(token, request_id):
    url = "https://api.transfeera.com/statement_report/" + request_id
    authorization = "Bearer " + token
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": authorization
    }
    response = requests.get(url, headers=headers)
    return response.json()


def download_report(file_url):
    try:
        response = requests.get(file_url)
        diretorio_destino = "./assets/csvs"

        if not os.path.exists(diretorio_destino):
            os.makedirs(diretorio_destino)

        with open(os.path.join(diretorio_destino, "relatorio.zip"), 'wb') as f:
            f.write(response.content)

        with zipfile.ZipFile(os.path.join(diretorio_destino, "relatorio.zip"),
                            'r') as zip_ref:
            filename = zip_ref.namelist()[0]
            zip_ref.extractall(diretorio_destino)
            os.rename(os.path.join(diretorio_destino, filename),
                    os.path.join(diretorio_destino, "extrato.csv"))
        return True
    except Exception as e:
        print(e)
        return False

def read_report():
    df = pd.read_csv("./assets/csvs/extrato.csv")
    os.remove('./assets/csvs/extrato.csv')
    os.remove('./assets/csvs/relatorio.zip')

    df["Data Pgto"] = pd.to_datetime(df["Data"], format="%Y-%m-%d").dt.strftime("%d/%m/%Y")
    df["Chave / Dado bancário"] = df["Chave / Dado bancário"].apply(
        lambda x: x.split(' ') if isinstance(x, str) else x)
    df["Banco"] = df["Chave / Dado bancário"].apply(
        lambda x: x[1] if isinstance(x, list) and len(x) > 1 else None)
    df["Agencia"] = df["Chave / Dado bancário"].apply(
        lambda x: x[3] if isinstance(x, list) and len(x) > 3 else None)
    df["Tipo de Conta"] = df["Chave / Dado bancário"].apply(
        lambda x: x[-4] if isinstance(x, list) and len(x) >= 4 else None)
    df["Conta"] = df["Chave / Dado bancário"].apply(
        lambda x: x[-3] if isinstance(x, list) and len(x) >= 3 else None)
    df["Digito"] = df["Chave / Dado bancário"].apply(
        lambda x: x[-1] if isinstance(x, list) and len(x) > 0 else None)
    df["Titular"] = df["Descrição"].apply(
        lambda x: x.split('"')[1] if isinstance(x, str) and '"' in x else None)
    
    df = df[(df["Tipo"] != "Depósito")]
    df["Valor Transfeera"] = df["Valor"]
    df = df[df["Valor Transfeera"].notnull()]

    df.loc[df["Tipo"] == "Estorno", "Valor Transfeera"] = df["Valor Transfeera"] / -1
    df.loc[df["Tipo"] == "Pagamento", "Valor Transfeera"] = df["Valor Transfeera"].abs()

    df = df[[
        "Data Pgto", "Crédito / Débito", "Tipo", "ID do pagamento", "Valor Transfeera",
        "ID de integração", "Banco", "Agencia", "Tipo de Conta", "Conta",
        "Digito", "Titular"
    ]]

    return df





