from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
#pip install scikit-learn
#Para lista todas as libs instaladas no python use pip list

app = Flask(__name__)
caminhoBd = config.DB_PATH
rotas = config.ROTAS

def init_db():
    with sqlite3.connect(caminhoBd) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS inadimplencia (
                    mes TEXT PRIMARY KEY,
                    inadimplencia REAL
            )       
        ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS selic (
                    mes TEXT PRIMARY KEY,
                    selic_diaria REAL
                     )
        ''')
        conn.commit()
vazio = 0

@app.route(rotas[0])
def index():
    return render_template_string(f'''
        <h1>Upload de dados Economicos</h1>
        <form action="{rotas[1]}" method="POST" enctype="multipart/form-data">
            <label for="campo_inadimplencia">Arquivo de inadimplencia (CSV)</label>
            <input name="campo_inadimplencia" type="file"required>
            <label for="campo_selic">Arquivo da taxa selic (CSV)</label>
            <input name="campo_selic" type="file" required>
            <input type="submit" value="Fazer Upload">
        </form>
        <br><br>
        <hr>
        <a href="{rotas[2]}">Consultar dados Armazenados</a><br>
        <a href="{rotas[3]}">Visualizar Graficos</a><br>
        <a href="{rotas[4]}"> Editar dados dos inadimplencia</a><br>
        <a href="{rotas[5]}">Analisar correlação </a><br>
        <a href="{rotas[6]}">Observabilidade em 3d</a><br>
        <a href="{rotas[7]}">editar selic</a><br>
    ''')

@app.route(rotas[1], methods=['POST', 'GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados!"})
    
    inad_df = pd.read_csv(
        inad_file,
        sep = ';',
        names = ['data','inadimplencia'],
        header = 0
    )
    selic_df = pd.read_csv(
        selic_file,
        sep = ';',
        names = ['data','selic_diaria'],
        header = 0
    )

    inad_df['data'] = pd.to_datetime(
        inad_df['data'],
        format = "%d/%m/%Y"
    )
    selic_df['data'] = pd.to_datetime(
        selic_df['data'],
        format = "%d/%m/%Y"
        )
    
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(caminhoBd) as conn:
        inad_df.to_sql(
            'inadimplencia',
            conn,
            if_exists = 'replace',
            index = False
        )
        selic_df.to_sql(
            'selic',
            conn,
            if_exists = 'replace',
            index = False
        )
        return jsonify({"Mensagem":"Dados cadastrados com sucesso!"})
    
@app.route(rotas[2], methods=['GET','POST'])
def consultar():

    if request.method == "POST":
        tabela = request.form.get('campo_tabela')
        if tabela not in ["inadimplencia","selic"]:
            return jsonify({"Erro":"Tabela Invalida"}), 400
        with sqlite3.connect(caminhoBd) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        return df.to_html(index=False)

    return render_template_string(f'''
        <h1> Consulta de Tabelas </h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </label>
            <select name="campo_tabela">
                <option value="inadimplencia"> Inadimplencia </option>
                <option value="selic"> Taxa Selic </option>
            </select>
            <input type="submit" value="Consultar">
        </form>
        <br><a href="{rotas[0]}"> Voltar </a>
    ''')

@app.route(rotas[3])
def graficos():
    with sqlite3.connect(caminhoBd) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)

    ### Aqui criei um grafico para inadimplencia    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
            x = inad_df['mes'],
            y = inad_df['inadimplencia'],
            mode = 'lines+markers',
            name = 'Inadimplencia'
    )
    )
    #'ggplot2', 'seaborn', 'simple_white','plotly','plotly_white', 'plotly_dark', 'presentatio','xgridoff','ygridoff','gridon','nome'
    fig1.update_layout(
        title = 'Evolução da Inadimplencia',
        xaxis_title = 'Mês',
        yaxis_title = '%',
        template = 'plotly_dark'
    )

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
            x = selic_df['mes'],
            y = selic_df['selic_diaria'],
            mode = 'lines+markers',
            name = 'selic'
        )
    )
    fig2.update_layout(
        title = "Media mensal da Selic",
        xaxis_title = 'Mês',
        yaxis_title = 'Taxa',
        template = 'plotly_dark'
    )   
    graph_html_1 = fig1.to_html(
        full_html = False,
        include_plotlyjs = "cdn"
    )
    graph_html_2 = fig2.to_html(
        full_html = False,
        include_plotlyjs = False
        )

    return render_template_string('''
        <html>
            <head>
                <title> Graficos Economicos</title>
                <style>
                    .container{
                        display:flex;
                        justify-content:content:space-around;
                    }
                    .graph{
                            width: 48%;
                    }

                </style>
            </head>
            <body>
                <h1>
                    <marquee> Graficos Economicos </marquee>
                </h1>
                <div class="container">
                    <div class="graph">{{ reserva01|safe}}</div>
                    <div class="graph">{{ reserva02|safe }}</div>
                </div>
            </body>
        </html>
    ''', reserva01 = graph_html_1, reserva02 = graph_html_2)
@app.route(rotas[4], methods=['GET','POST'])
def editar_inadimplencia(): 
    if request.method == 'POST':
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({"Erro":"Valor Invalido"}),
        with sqlite3.connect(caminhoBd) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inadimplencia 
                SET inadimplencia = ? 
                WHERE mes = ?
            ''', (novo_valor, mes))
            conn.commit()
        return jsonify({"Mensagem":f"Valor atualizado para o mes{mes} com sucesso!"})
            
        return render_templates_string(f'''
        <h1> Editar dados de Inadimplencia </h1>
        <form method="POST" action="{rotas[4]}">
            <label for="campo_mes"> Mês (Formato AAAA-MM): </label>
            <input name="campo_mes" type="text" name="campos_mes"><br>
                                   
            <label for="campo_valor"> Novo valor de Inadimplencia : </label>
            <input name="campo_inadimplencia" type="number" step="0.01" required>

            <input type="submit" value="Atualizar"> 
        </form>
        <br>
        <a href="{rotas[0]}"> Voltar </a>

                                   ''')
        




if __name__ == '__main__':
    init_db()
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
    )
