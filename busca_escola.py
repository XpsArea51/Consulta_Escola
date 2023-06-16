import os
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
import webbrowser
import requests
from gmplot import gmplot
import sys
import traceback

def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open('error_log.txt', 'a') as f:
        f.write(error_string)
        
sys.excepthook = handle_unhandled_exception

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Busca Inteligente de Escolas')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)  # permite minimizar e fechar a janela
        self.setGeometry(500, 200, 500, 250)  # define o tamanho e a posição inicial da janela

        self.setWindowIcon(QIcon('logo.ico'))  # Adiciona um ícone à janela

        # layout vertical
        layout = QtWidgets.QVBoxLayout(self)

        # campo de entrada
        self.entry_label = QtWidgets.QLabel("Insira o Código do Censo ou Nome da Escola:", self)
        layout.addWidget(self.entry_label)
        self.entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.entry)

        # campo de entrada para a UF
        self.uf_label = QtWidgets.QLabel("Insira a UF:", self)
        layout.addWidget(self.uf_label)
        self.uf_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.uf_entry)

        # botões
        self.button_codigo = QtWidgets.QPushButton('Buscar Código', self)
        layout.addWidget(self.button_codigo)
        self.button_codigo.clicked.connect(self.buscar_codigo)

        self.button_nome = QtWidgets.QPushButton('Buscar Por Nome', self)
        layout.addWidget(self.button_nome)
        self.button_nome.clicked.connect(self.buscar_nome)

        # labels para o nome e o endereço da escola
        self.nome_label = QtWidgets.QLabel("", self)
        layout.addWidget(self.nome_label)
        self.endereco_label = QtWidgets.QLabel("", self)
        layout.addWidget(self.endereco_label)

        # check button para manter a janela no topo
        self.topmost_check = QtWidgets.QCheckBox("Sempre no topo", self)
        self.topmost_check.stateChanged.connect(self.toggle_topmost)
        layout.addWidget(self.topmost_check)

        # Assinatura
        self.signature_label = QtWidgets.QLabel("Criado por Lucas Ribeiro®️", self)
        self.signature_label.setStyleSheet("color: gray;")
        self.signature_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.signature_label)

        if getattr(sys, 'frozen', False):
            csv_file = os.path.join(sys._MEIPASS, 'Análise - Tabela da lista das escolas - Detalhado.csv')
        else:
            csv_file = 'Análise - Tabela da lista das escolas - Detalhado.csv'

        if os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file, delimiter=';')
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV não encontrado')
            self.button_codigo.setDisabled(True)
            self.button_nome.setDisabled(True)
    
        

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
        nome_escola = self.entry.text()
        uf = self.uf_entry.text()

        # Validação dos dados de entrada
        if not nome_escola or not uf:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nome da escola ou UF inválidos')
            return

        # Busca o endereço da escola usando a API do Google Maps
        endereco = f"{nome_escola}, {uf}, Brasil"
        self.latitude, self.longitude = self.get_lat_lng(endereco)
        if self.latitude and self.longitude:
            self.nome_label.setText(f"Nome da Escola: {nome_escola}")
            self.endereco_label.setText(f"Endereço: {endereco}")
            self.abrir_localizacao()
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Endereço não encontrado')

    def get_lat_lng(self, endereco):
        GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {
            'address': endereco,
            'sensor': 'false',
            'region': 'br',
            'key': 'AIzaSyAS4cGtz7RQtDY-lJt4OKTO_klh3UYwDkI'
        }

        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()

        result = res['results'][0]
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']

        return lat, lng

    def abrir_localizacao(self):
        gmap = gmplot.GoogleMapPlotter(float(self.latitude), float(self.longitude), 15, apikey="codigo da API")
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
