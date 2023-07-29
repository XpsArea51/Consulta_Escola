import os
import sys
import webbrowser
import urllib.parse
import pandas as pd
from difflib import SequenceMatcher
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QLineEdit, QPushButton, QCompleter, QScrollArea, QScrollArea, QWidget
from PyQt5.QtCore import QSize, QTimer
import time

# metodo para carregar os arquivos de imagem e csv de forma que o pyinstaller consiga acessar
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# variaveis com os caminhos dos arquivos
icone_path = resource_path('placeholder.ico')
mapa_icon_path = resource_path('mapa.ico')
csv_censo_path = resource_path('novo_censo.csv')
csv_ufs_path = resource_path('base_ufs.csv')

# metodo para abrir a localizacao caso a IE não tenha latitude e longitude
def open_map(self):
        if pd.isna(self.latitude) or pd.isna(self.longitude):
            query = f'{self.nome_label.text()} {self.municipio} {self.uf}'
            url = 'https://www.google.com/maps/search/' + urllib.parse.quote(query)
            webbrowser.open(url)
        else:
            self.abrir_localizacao()

# metodo para abrir o mapa com base na latitude e longitude
def abrir_localizacao(self):
        gmap = gmplot.GoogleMapPlotter(float(self.latitude), float(self.longitude), 15, apikey="AIzaSyALZGyVtICuk8rlvPcWXH_IBngvZbzLvrc")
        gmap.marker(float(self.latitude), float(self.longitude), 'red')

        map_file = "mapa.html"
        gmap.draw(map_file)

        webbrowser.open_new_tab(map_file)

# metodo que le a UF selecionada e procura a faculdade com base nesta UF na base do censo
def load_data(self):
    for file in self.csv_files:
        if os.path.exists(file):
            self.df = pd.read_csv(file, delimiter=';', dtype={'Código INEP': str})
            self.df['UF'] = self.df['UF'].astype(str)  # Convert 'UF' column to string
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV não encontrado')
            if hasattr(self, 'button_codigo') and hasattr(self, 'button_nome'):
                self.button_codigo.setDisabled(True)
                self.button_nome.setDisabled(True)

        self.uf_mapping = pd.read_csv(csv_ufs_path, index_col='nome_completo')['uf'].to_dict()

# método que busca a faculdade com base no código censo e se conecta com botão de buscar por código
def buscar_codigo(self):
        codigo_censo = self.entry.text()
        
        # Remove todos os widgets anteriores
        self.clear_widgets()

        rows = self.df[self.df['Código INEP'].astype(str) == codigo_censo]
        if not rows.empty:
            # Adiciona os novos widgets
            for index, row in rows.iterrows():
                school_widget = SchoolWidget(row['Escola'], row['Endereço'], row['Código INEP'], row['Latitude'], row['Longitude'], row['Município'], row['UF'])
                self.scroll_layout.addWidget(school_widget)
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Código do censo não encontrado')

# método que busca a faculdade com base no nome e se conecta com botão de buscar nome
def buscar_nome(self):
    nome_escola = self.entry.text().lower()
    uf = self.uf_entry.currentText().upper()

    # Validação dos dados de entrada
    if not nome_escola:
        QtWidgets.QMessageBox.critical(self, 'Erro', 'Nome da escola é inválido')
        return

    # Remove acentos, caracteres especiais e converte para minúsculas
    self.df['Escola_normalized'] = self.df['Escola'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower()

    # Busca a escola pelo nome normalizado e pela UF
    words = nome_escola.split()
    query = ' & '.join(f'Escola_normalized.str.contains("{word}")' for word in words)  # join the words with AND operator
    
    # Se a UF não for 'Todos', adicione isso à consulta
    if uf != 'TODOS':
        query += f' and UF == "{uf}"'

    rows = self.df.query(query)
    rows.loc[:, 'match_score'] = rows['Escola'].apply(lambda x: SequenceMatcher(None, x, nome_escola).ratio())
    rows = rows.sort_values('match_score', ascending=False)
    
    if rows.empty:
        QtWidgets.QMessageBox.critical(self, 'Erro', 'Nenhuma escola encontrada')
        return

    # Remove todos os widgets anteriores
    self.clear_widgets()

    # Adiciona os novos widgets
    for _, row in rows.iterrows():
        school_widget = SchoolWidget(row['Escola'], row['Endereço'], row['Código INEP'], row['Latitude'], row['Longitude'], row['Município'], row['UF'])
        self.scroll_layout.addWidget(school_widget)

# método que limpa os widgets anteriores
def clear_widgets(self):
    for i in reversed(range(self.scroll_layout.count())):
        widgetToRemove = self.scroll_layout.itemAt(i).widget()
        # remove it from the layout list
        self.scroll_layout.removeWidget(widgetToRemove)
        # remove it from the gui
        widgetToRemove.setParent(None)

# método realiza a busca com base nos critérios fornecidos pelo usuário
def abrir_localizacao(self):
        nome_escola = self.entry.text().lower()
        uf = self.uf_entry.currentText().upper()
        municipio = 'SEU_MUNICIPIO'

        # Validação dos dados de entrada
        if not nome_escola or not uf:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nome da escola ou UF inválidos')
            return

        query = f'Escola.str.lower().str.contains("{nome_escola}") and UF == "{uf}" and Município == "{municipio}"'
        rows = self.df.query(query)
        if rows.empty:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nenhuma escola encontrada')
            return

        # Remove todos os widgets anteriores
        self.clear_widgets()

        # Adiciona os novos widgets
        for _, row in rows.iterrows():
            school_widget = SchoolWidget(row['Escola'], row['Endereço'], row['Código INEP'], row['Latitude'], row['Longitude'], row['Município'], row['UF'])
            self.scroll_layout.addWidget(school_widget)

# metodo responsável por manter a janela sempre no topo
def toggle_topmost(self):
        if self.button.isChecked():
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.button.setText("Janela Travada")
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.button.setText("Travar Janela")
        self.show()

