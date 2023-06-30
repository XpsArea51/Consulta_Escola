import os
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QPushButton, QCompleter
from PyQt5.QtGui import QIcon
import webbrowser
import requests
from gmplot import gmplot
import sys
import traceback

class SchoolWidget(QtWidgets.QWidget):
    def __init__(self, nome, endereco, codigo_censo, latitude, longitude):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)

        self.nome_label = QLabel(f"Nome da Escola: {nome}")
        self.nome_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.nome_label)

        self.endereco_label = QLabel(f"Endereço: {endereco}")
        self.endereco_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.endereco_label)

        self.codigo_censo_label = QLabel(f"Código do Censo: {codigo_censo}")
        self.codigo_censo_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.codigo_censo_label)

        self.latitude = latitude
        self.longitude = longitude

        self.show_map_button = QPushButton()
        self.show_map_button.setIcon(QIcon('icons\mapa.ico'))  # Substitua 'caminho_para_seu_ico' pelo caminho para o ícone desejado
        self.show_map_button.clicked.connect(self.open_map)
        layout.addWidget(self.show_map_button)

        layout.addSpacing(20)  # Adiciona espaço entre os widgets de escola

    def open_map(self):
        if self.latitude and self.longitude:
            self.abrir_localizacao()
        else:
            webbrowser.open(f'https://www.google.com/maps/search/{self.endereco}')

    def abrir_localizacao(self):
        gmap = gmplot.GoogleMapPlotter(float(self.latitude), float(self.longitude), 15, apikey="AIzaSyALZGyVtICuk8rlvPcWXH_IBngvZbzLvrc")
        gmap.marker(float(self.latitude), float(self.longitude), 'red')

        map_file = "mapa.html"
        gmap.draw(map_file)

        webbrowser.open_new_tab(map_file)



class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            csv_file = os.path.join(sys._MEIPASS, 'data/novo_censo.csv')
        else:
            csv_file = 'data/novo_censo.csv'

        if os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file, delimiter=';')
            self.df['UF'] = self.df['UF'].astype(str)  # Convert 'UF' column to string
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV não encontrado')
            self.button_codigo.setDisabled(True)
            self.button_nome.setDisabled(True)

        self.uf_mapping = pd.read_csv('data/base_ufs.csv', index_col='nome_completo')['uf'].to_dict()

        self.setWindowTitle('Busca Inteligente de Escolas')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)  # permite minimizar e fechar a janela
        self.setGeometry(500, 200, 500, 250)  # define o tamanho e a posição inicial da janela

        self.setWindowIcon(QIcon('icons/placeholder.ico'))  # Adiciona um ícone à janela

        # layout vertical
        layout = QtWidgets.QVBoxLayout(self)

        # campo de entrada
        self.entry_label = QLabel("Insira o Código do Censo ou Nome da Escola:", self)
        layout.addWidget(self.entry_label)
        self.entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.entry)

        # campo de entrada para a UF
        self.uf_label = QLabel("Selecione a UF:", self)
        layout.addWidget(self.uf_label)
        self.uf_entry = QtWidgets.QComboBox(self)
        self.uf_entry.addItems(sorted(list(self.uf_mapping.values())))
        layout.addWidget(self.uf_entry)

        # cria uma lista de UFs únicas a partir da planilha
        self.ufs = self.df['UF'].unique().tolist()

        # adiciona todas as formas possíveis de entrada para a UF à lista de UFs
        self.ufs += [uf.lower() for uf in self.ufs] + list(self.uf_mapping.keys())

        # Configurando o autocompletar para a entrada de texto da UF
        self.uf_completer = QCompleter(self.ufs, self)
        self.uf_entry.setCompleter(self.uf_completer)

        # botões
        button_layout = QtWidgets.QHBoxLayout()

        self.button_codigo = QPushButton('Buscar Código', self)
        self.button_codigo.setStyleSheet("background-color: blue; color: white;")
        button_layout.addWidget(self.button_codigo)
        self.button_codigo.clicked.connect(self.buscar_codigo)

        self.button_nome = QPushButton('Buscar Por Nome', self)
        self.button_nome.setStyleSheet("background-color: green; color: white;")
        button_layout.addWidget(self.button_nome)
        self.button_nome.clicked.connect(self.buscar_nome)

        layout.addLayout(button_layout)

        # labels para o nome e o endereço da escola
        self.nome_label = QLabel("", self)
        self.nome_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.nome_label)
        self.endereco_label = QLabel("", self)
        self.endereco_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.endereco_label)
        self.codigo_censo_label = QLabel("", self)
        self.codigo_censo_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.codigo_censo_label)

        # check button para manter a janela no topo
        self.topmost_check = QtWidgets.QCheckBox("Travar Janela", self)
        self.topmost_check.stateChanged.connect(self.toggle_topmost)
        layout.addWidget(self.topmost_check)

        # scroll area
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.scroll_content = QtWidgets.QWidget(self.scroll_area)
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        # Assinatura
        self.signature_label = QLabel("Desenvolvido por Lucas Gabriel©", self)
        self.signature_label.setStyleSheet("color: gray;")
        self.signature_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.signature_label)

        if getattr(sys, 'frozen', False):
            csv_file = os.path.join(sys._MEIPASS, 'data/Análise - Tabela da lista das escolas - Detalhado.csv')
        else:
            csv_file = 'data/Análise - Tabela da lista das escolas - Detalhado.csv'

        if os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file, delimiter=';')
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV não encontrado')
            self.button_codigo.setDisabled(True)
            self.button_nome.setDisabled(True)

        self.uf_mapping = pd.read_csv('data/base_ufs.csv', index_col='nome_completo')['uf'].to_dict()

    def buscar_codigo(self):
        try:
            codigo_censo = int(self.entry.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Código do censo inválido')
            return

        row = self.df[self.df['Código INEP'] == codigo_censo]
        if not row.empty:
            self.latitude = row['Latitude'].values[0]
            self.longitude = row['Longitude'].values[0]
            self.nome_label.setText(f"Nome da Escola: {row['Escola'].values[0]}")
            self.endereco_label.setText(f"Endereço: {row['Endereço'].values[0]}")
            self.abrir_localizacao()
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Código do censo não encontrado')

    def buscar_nome(self):
        nome_escola = self.entry.text().lower()
        uf = self.uf_entry.currentText().upper()

        # Validação dos dados de entrada
        if not nome_escola or not uf:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nome da escola ou UF inválidos')
            return

        # Busca a escola pelo nome, insensível a maiúsculas/minúsculas, e pela UF
        words = nome_escola.split()
        query = "|".join(words)  # join the words with OR operator
        rows = self.df[(self.df['Escola'].str.lower().str.contains(query)) & (self.df['UF'] == uf)]
        if rows.empty:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nenhuma escola encontrada')
            return

        # Remove todos os widgets anteriores
        for i in reversed(range(self.scroll_layout.count())):
            widgetToRemove = self.scroll_layout.itemAt(i).widget()
            # remove it from the layout list
            self.scroll_layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

        # Adiciona os novos widgets
        for _, row in rows.iterrows():
            school_widget = SchoolWidget(row['Escola'], row['Endereço'], row['Código INEP'], row['Latitude'], row['Longitude'])
            self.scroll_layout.addWidget(school_widget)

    def get_lat_lng(self, endereco):
        GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': endereco,
            'sensor': 'false',
            'region': 'br',
            'key': ''
        }

        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()

        result = res['results'][0]
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']

        return lat, lng

    def abrir_localizacao(self):
        gmap = gmplot.GoogleMapPlotter(float(self.latitude), float(self.longitude), 15, apikey="AIzaSyALZGyVtICuk8rlvPcWXH_IBngvZbzLvrc")
        gmap.marker(float(self.latitude), float(self.longitude), 'red')

        map_file = "mapa.html"
        gmap.draw(map_file)

        webbrowser.open_new_tab(map_file)

    def toggle_topmost(self, state):
        if state == QtCore.Qt.Checked:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

app = QtWidgets.QApplication([])
window = App()
window.show()
app.exec_()


