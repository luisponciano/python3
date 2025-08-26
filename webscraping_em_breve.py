import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import sqlite3
import datetime
import os

# --- Configurações Iniciais ---

# Headers para simular um navegador real e evitar bloqueios.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

# URL do site com a lista de shows
baseURL = "https://sampaingressos.com.br/templates/ajax/lista_espetaculo.php"

# Lista para armazenar os dados coletados
shows = []

# Geração de nomes de arquivo com base na data atual
data_hoje = datetime.date.today().strftime("%d-%m-%Y")
agora = datetime.datetime.now()

# --- Configuração de Caminhos para Salvar Arquivos ---
# Cria um caminho para uma pasta na área de trabalho do usuário para evitar erros de permissão.
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'SampaIngressos_Shows')
if not os.path.exists(desktop_path):
    os.makedirs(desktop_path)

bancoDados = os.path.join(desktop_path, f"sampa_ingressos_shows_{data_hoje}.db")
saidaCSV = os.path.join(desktop_path, f"sampa_ingressos_shows_{data_hoje}.csv")


# Intervalos de tempo para pausas, para não sobrecarregar o servidor
card_temp_min = 1
card_temp_max = 3

# --- Início do Processo de Coleta ---

print(f"Coletando dados da página: {baseURL}")
resposta = requests.get(baseURL, headers=headers)

# Verifica se a página foi carregada com sucesso
if resposta.status_code == 200:
    soup = BeautifulSoup(resposta.text, "html.parser")

    # Encontra todos os contêineres de shows. Cada show está em uma tag <div> com a classe 'item'.
    cards = soup.find_all("div", class_="item")
    print(f"Encontrados {len(cards)} shows para coletar.")

    # Itera sobre cada card de show encontrado
    for card in cards:
        try:
            # Captura o link do show
            link_tag = card.find('a')
            link = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
            
            if not link:
                print("Card sem link, pulando...")
                continue

            # Captura o título do show
            titulo_tag = card.find("h4")
            titulo = titulo_tag.text.strip() if titulo_tag else "N/A"

            # Captura o local/teatro do show
            local_tag = card.find("p", class_="cat-teatro")
            local = local_tag.text.strip() if local_tag else "N/A"
            
            # Captura o gênero do show
            genero_tag = card.find("p", class_="cat-genero")
            genero = genero_tag.text.strip() if genero_tag else "N/A"
            
            # Adiciona os dados coletados à lista se o título e o link existirem
            if titulo != "N/A" and link is not None:
                shows.append({
                    "Titulo": titulo,
                    "Local": local,
                    "Genero": genero,
                    "Link": link
                })
                print(f"Coletado: {titulo}")
            else:
                print(f"Show com dados incompletos, pulando: {titulo}")

            # Aguarda um tempo aleatório para não sobrecarregar o site
            tempo_espera = random.uniform(card_temp_min, card_temp_max)
            time.sleep(tempo_espera)

        except Exception as e:
            print(f"Erro ao processar o show '{titulo if 'titulo' in locals() else 'Desconhecido'}'. Erro: {e}")
            continue
else:
    print(f"Erro ao carregar a página. Código do erro: {resposta.status_code}")

# --- Salvando os Dados ---

# Converte a lista de dados para um DataFrame do Pandas
df = pd.DataFrame(shows)
print("\n--- Amostra dos Dados Coletados ---")
print(df.head())
print("-----------------------------------\n")

# Salva os dados em um arquivo CSV, se o DataFrame não estiver vazio
if not df.empty:
    df.to_csv(saidaCSV, index=False, encoding="utf-8-sig")

    # Conecta a um banco de dados SQLite (cria o arquivo se não existir)
    conn = sqlite3.connect(bancoDados)
    cursor = conn.cursor()

    # Cria a tabela para armazenar os shows, se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Titulo TEXT,
            Local TEXT,
            Genero TEXT,
            Link TEXT UNIQUE
        )
    ''')

    # Insere cada show coletado na tabela do banco de dados
    for show in shows:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO shows (Titulo, Local, Genero, Link) 
                VALUES (?, ?, ?, ?)''', (
                show['Titulo'],
                show['Local'],
                show['Genero'],
                show['Link']
            ))
        except Exception as e:
            print(f"Erro ao inserir o show '{show['Titulo']}' no banco de dados: {e}")

    # Salva (commita) as alterações e fecha a conexão com o banco
    conn.commit()
    conn.close()
else:
    print("Nenhum dado foi coletado para salvar.")

# --- Mensagens Finais ---
print("------------------------------------------------------")
if not df.empty:
    print("Dados coletados e salvos com sucesso!")
    print(f"Arquivo CSV salvo em: {saidaCSV}")
    print(f"Banco de dados salvo em: {bancoDados}")
else:
    print("O script foi finalizado, mas nenhum show foi encontrado ou salvo.")
print(f"Finalizado em: {agora.strftime('%d-%m-%Y %H:%M:%S')}")
print("------------------------------------------------------")
