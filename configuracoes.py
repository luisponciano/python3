#https://www.asciiart.eu/
#  __  __ _       _                    _         _                 _      
# |  \/  (_)_ __ | |__   __ _ ___     / \  _   _| | __ _ ___    __| | ___ 
# | |\/| | | '_ \| '_ \ / _` / __|   / _ \| | | | |/ _` / __|  / _` |/ _ \
# | |  | | | | | | | | | (_| \__ \  / ___ \ |_| | | (_| \__ \ | (_| |  __/
# |_|__|_|_|_| |_|_| |_|\__,_|___/ /_/   \_\__,_|_|\__,_|___/  \__,_|\___|
# |  _ \ _   _| |_| |__   ___  _ __                                       
# | |_) | | | | __| '_ \ / _ \| '_ \                                      
# |  __/| |_| | |_| | | | (_) | | | |                                     
# |_|    \__, |\__|_| |_|\___/|_| |_|                                     
#        |___/                                                            
#                                                      
#Autor: Nome do Aluno
#Versão:0.0.1v 2025
#caminho da pasta
db_path = "C:/Users/noturno/Desktop/python2 luis/bancodados.db"

#----------------------------------------
#Consultas SQL
#----------------------------------------

consulta01 = "SELECT * FROM vingadores"
consulta02 = """ 
            SELECT country, total_litres_of_pure_alcohol
            FROM bebidas
            ORDER BY total_litres_of_pure_alcohol DESC
            LIMIT 10
            """
# Exclui a tabela de vingadores se existir
consulta03 = "DROP TABLE IF EXISTS vingadores"