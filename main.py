import os
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QPushButton, QCompleter, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap
import webbrowser
from gmplot import gmplot
import sys
from difflib import SequenceMatcher
from textwrap import shorten
import time

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# em seguida, para carregar os arquivos:
icone_path = resource_path('placeholder.ico')
mapa_icon_path = resource_path('mapa.ico')
csv_censo_path = resource_path('novo_censo.csv')
csv_ufs_path = resource_path('base_ufs.csv')

class SchoolWidget(QtWidgets.QWidget):
    def __init__(self, nome, endereco, codigo_censo, latitude, longitude):
        super().__init__()

        self.setWindowIcon(QIcon(icone_path))

        layout = QtWidgets.QVBoxLayout(self)

        self.nome_label = QLabel(shorten(nome, width=50, placeholder="..."))
        self.nome_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.nome_label)

        if pd.notnull(endereco):
            self.endereco_label = QLabel(shorten(str(endereco), width=50, placeholder="..."))
            self.endereco_label.setToolTip(endereco)
        else:
            self.endereco_label = QLabel("Endereço não disponível")
            self.endereco_label.setToolTip("Endereço não disponível")
        
        self.endereco_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.endereco_label)

        # Adiciona a opção de selecionar o texto com o mouse
        self.nome_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        # Defina o tooltip como o nome da escola/endereço completo
        self.nome_label.setToolTip(nome)

        self.codigo_censo_label = QLabel(f"Código do Censo: {codigo_censo}")
        self.codigo_censo_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.codigo_censo_label)

        self.latitude = latitude
        self.longitude = longitude

        self.show_map_button = QPushButton()
        self.show_map_button.setIcon(QIcon(mapa_icon_path))
        self.show_map_button.setFixedSize(50, 50)
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

        # Define arquivos CSV
        self.csv_files = [csv_censo_path]
        
        self.load_data()  # mover esta chamada para antes de init_ui()
        self.init_ui()

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

    def init_ui(self):

        self.setWindowTitle('Busca Inteligente de Escolas')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)  # permite minimizar e fechar a janela
        self.setGeometry(750, 300, 500, 550)  # define o tamanho e a posição inicial da janela

        self.setWindowIcon(QIcon(icone_path))  # Adiciona um ícone à janela

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
        self.uf_entry.addItems(sorted(['Todos'] + list(self.uf_mapping.values())))
        self.uf_entry.setCurrentText('Todos')
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
            csv_file = os.path.join(sys._MEIPASS, 'novo_censo.csv')
        else:
            csv_file = 'novo_censo.csv'

        if os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file, delimiter=';', dtype={'Código INEP': str})
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV não encontrado')
            self.button_codigo.setDisabled(True)
            self.button_nome.setDisabled(True)

        self.uf_mapping = pd.read_csv(csv_ufs_path, index_col='nome_completo')['uf'].to_dict()


    def buscar_codigo(self):
        codigo_censo = self.entry.text()
        
        # Remove todos os widgets anteriores
        self.clear_widgets()

        row = self.df[self.df['Código INEP'].astype(str) == codigo_censo]
        if not row.empty:

            # Adiciona o novo widget
            school_widget = SchoolWidget(row['Escola'].values[0], row['Endereço'].values[0], row['Código INEP'].values[0], row['Latitude'].values[0], row['Longitude'].values[0])
            self.scroll_layout.addWidget(school_widget)
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Código do censo não encontrado')


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
        rows['match_score'] = rows['Escola'].apply(lambda x: SequenceMatcher(None, x, nome_escola).ratio())
        rows = rows.sort_values('match_score', ascending=False)
        
        if rows.empty:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nenhuma escola encontrada')
            return

        # Remove todos os widgets anteriores
        self.clear_widgets()

        # Adiciona os novos widgets
        for _, row in rows.iterrows():
            school_widget = SchoolWidget(row['Escola'], row['Endereço'], row['Código INEP'], row['Latitude'], row['Longitude'])
            self.scroll_layout.addWidget(school_widget)


    def clear_widgets(self):
        # Remove todos os widgets anteriores
        for i in reversed(range(self.scroll_layout.count())):
            widgetToRemove = self.scroll_layout.itemAt(i).widget()
            # remove it from the layout list
            self.scroll_layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    def abrir_localizacao(self):
        nome_escola = self.entry.text().lower()
        uf = self.uf_entry.currentText().upper()
        municipio = 'SEU_MUNICIPIO'  # Substitua pelo município adequado

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
            school_widget = SchoolWidget(row['Escola'], row['Endereço'], row['Código INEP'], '', '')
            self.scroll_layout.addWidget(school_widget)

    def toggle_topmost(self, state):
        if state == QtCore.Qt.Checked:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.show()

app = QtWidgets.QApplication([])

# Defina o pixmap para o splash screen e exiba-o
splash_pix = QPixmap(icone_path)  # Coloque aqui o caminho para a sua logo
splash = QSplashScreen(splash_pix)
splash.show()

window = App()
window.show()

while not window.isVisible():
    app.processEvents()
    time.sleep(0.1)

splash.finish(window)  # Fechar o splash screen

app.exec_()
 .