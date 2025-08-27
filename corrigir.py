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
caminhoBD = config.DB_PATH

def init_db():
    with sqlite3.connect(caminhoBD) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS inadimplencia (
                    mes TEXT PRIMARY KEY,
                    inadimplencia REAL
            )       
        ''')
        conn.execute('''
                CREATE TABLE IF NOT EXISTS selic (
                    mes TEXT PRIMARY KEY,
                    selic_diaria REAL
                     )
        ''')
        conn.commit()
vazio = 0

@app.route('/')
def index():
    return render_template_string('''
        <h1>Upload de dados Economicos</h1>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <label for="campo_inadimplencia">Arquivo de inadimplencia (CSV)</label>
            <input name="campo_inadimplencia" type="file"required>
                                  
            <label for="campo_selic">Arquivo da taxa selic (CSV)</label>
            <input name="campo_selic" type="file" required>
            <input type="submit" value="Fazer Upload">
        </form>
        <br></br>
        <hr>
        <a href="/consultar">Consultar dados Armazenados</a><br>
        <a href="/graficos">Visualizar Graficos</a><br>
        <a href="/editar_inadimplentes"> Editar dados dos inadimplentes</a><br>
        <a href="/correlacao">Analisar correlação </a><br>
        <a href="/grafico3d">Observalidade em 3d</a><br>
''')
@app.route('/upload', methods=['POST', 'GET'])
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
        seep = ';',
        names = ['data','selic_diaria'],
        header = 0
    )

    inad_df['data'] = pd.to_datetime(
        inad_df['data'],
        format="%d/%m/%Y"
        )

    selic_df['data'] = pd.to_datetime(
        selic_df['data'],
        format="%d/%m/%Y"
            )
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes","inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(caminhoBD) as conn:
        inad_df.to_sql('inadimplencia',
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
    
@app.route('/consultar', methods=['GET','POST'])
def consultar():
    return render_template_string('''
        <h1>Consulta de Tabelas </h1>
        <form method="POST">
            <label for="campo_tabela"> Escolha uma tabela: </label>
            <select name=" campo>
                <option></option>
                <option></option>
            </select>
            <input>
        </form>
        <br><a href="/"> Voltar </a>
    ''')













if __name__ == '__main__':
    init_db()
    app.run(
        debug = config.FLASK_DEBUG,
        host = config.FLASK_HOST,
        port = config.FLASK_PORT
        )
