import os
import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap
import webbrowser
import requests
from gmplot import gmplot
import sys
import traceback
import unicodedata


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

        self.setWindowIcon(QIcon('placeholder.ico'))
        self.setWindowTitle('Busca Inteligente de Escolas e IES')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setGeometry(500, 200, 500, 300)

        layout = QtWidgets.QVBoxLayout(self)

        self.institution_group = QtWidgets.QButtonGroup(self)

        self.institution_school = QtWidgets.QRadioButton("Escola", self)
        self.institution_group.addButton(self.institution_school)
        layout.addWidget(self.institution_school)

        self.institution_college = QtWidgets.QRadioButton("IES", self)
        self.institution_group.addButton(self.institution_college)
        layout.addWidget(self.institution_college)

        # Adicionar opção para 'Nenhum'
        self.institution_none = QtWidgets.QRadioButton("Geral", self)
        self.institution_group.addButton(self.institution_none)
        self.institution_none.setChecked(True)  # Define 'Nenhum' como selecionado por padrão
        layout.addWidget(self.institution_none)

        self.entry_label = QtWidgets.QLabel("Insira o Código do Censo ou Nome da Instituição:", self)
        layout.addWidget(self.entry_label)
        self.entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.entry)

        self.df_municipios = pd.read_excel('base_munic.xlsx')

        self.uf_combo = QtWidgets.QComboBox(self)
        self.uf_combo.addItems(["Todos", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                                "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
                                "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        layout.addWidget(self.uf_combo)

        self.uf_combo.currentIndexChanged.connect(self.toggle_municipio_combo)

        self.municipio_combo = QtWidgets.QComboBox(self)
        self.municipio_combo.setVisible(False)  # Inicialmente escondido
        layout.addWidget(self.municipio_combo)

        self.button_layout = QtWidgets.QHBoxLayout()  # Novo layout horizontal

        self.button_codigo = QtWidgets.QPushButton('Buscar por Código', self)
        self.button_codigo.setStyleSheet("background-color: blue; color: white;")  # Estilo CSS para o botão azul
        self.button_codigo.clicked.connect(self.buscar_codigo)
        self.button_layout.addWidget(self.button_codigo)  # Adicionando ao novo layout horizontal

        self.button_nome = QtWidgets.QPushButton('Buscar Por Nome', self)
        self.button_nome.setStyleSheet("background-color: green; color: white;")  # Estilo CSS para o botão verde
        self.button_nome.clicked.connect(self.buscar_nome)
        self.button_layout.addWidget(self.button_nome)  # Adicionando ao novo layout horizontal

        layout.addLayout(self.button_layout)  # Adicionando o layout horizontal ao layout principal

        self.nome_label = QtWidgets.QLabel("", self)
        self.nome_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # Adicionado
        layout.addWidget(self.nome_label)
        self.endereco_label = QtWidgets.QLabel("", self)
        self.endereco_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # Adicionado
        layout.addWidget(self.endereco_label)
        self.codigo_censo_label = QtWidgets.QLabel("", self)
        self.codigo_censo_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # Adicionado
        layout.addWidget(self.codigo_censo_label)

        self.topmost_check = QtWidgets.QCheckBox("Travar Janela", self)
        self.topmost_check.stateChanged.connect(self.toggle_topmost)
        layout.addWidget(self.topmost_check)

        self.signature_label = QtWidgets.QLabel("Desenvolvido por Lucas Gabriel©", self)
        self.signature_label.setStyleSheet("color: gray;")
        self.signature_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.signature_label)

        if getattr(sys, 'frozen', False):
            csv_file_school = os.path.join(sys._MEIPASS, 'Análise - Tabela da lista das escolas - Detalhado.csv')
            csv_file_college = os.path.join(sys._MEIPASS, 'PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC (1).csv')
        else:
            csv_file_school = 'Análise - Tabela da lista das escolas - Detalhado.csv'
            csv_file_college = 'PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC (1).csv'

        if os.path.exists(csv_file_school):
            self.df_school = pd.read_csv(csv_file_school, delimiter=';')
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV das escolas não encontrado')
            self.button_codigo.setDisabled(True)
            self.button_nome.setDisabled(True)

        if os.path.exists(csv_file_college):
            self.df_college = pd.read_csv(csv_file_college, delimiter=';')
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Arquivo CSV das faculdades não encontrado')
            self.button_codigo.setDisabled(True)

    @staticmethod
    def normalize_string(string):
        return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII').lower()

    def update_municipios(self):
        uf = self.uf_combo.currentText()
        if uf != "Todos":
            self.municipio_combo.setEnabled(True)
            municipios = self.df_municipios[self.df_municipios['UF'] == uf]['MUNICIPIO'].values
            self.municipio_combo.clear()
            self.municipio_combo.addItem("Todos")
            self.municipio_combo.addItems(municipios)
        else:
            self.municipio_combo.setEnabled(False)

    # Função para mostrar/ocultar a lista de municípios de acordo com a seleção da UF
    def toggle_municipio_combo(self, index):
        uf = self.uf_combo.itemText(index)
        if uf != "Todos" and not self.institution_none.isChecked():  # Verifica se a opção "Geral" não está selecionada
            self.municipio_combo.clear()
            municipios = self.df_municipios[self.df_municipios['UF'] == uf]['MUNICIPIO'].tolist()
            self.municipio_combo.addItems(municipios)
            self.municipio_combo.setVisible(True)
        else:
            self.municipio_combo.setVisible(False)

    def buscar_codigo(self):
        institution = None
        if self.institution_school.isChecked():
            institution = "Escola"
        elif self.institution_college.isChecked():
            institution = "Faculdade"
        else:
            institution = None

        try:
            codigo_censo = int(self.entry.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Código do censo inválido')
            return

        if institution == "Escola":
            row = self.df_school[self.df_school['Código INEP'] == codigo_censo]
        elif institution == "Faculdade":
            row = self.df_college[self.df_college['CODIGO_DA_IES'] == codigo_censo]

        # Filtra por município, se escolhido
        municipio = self.municipio_combo.currentText()
        if municipio != "Todos":
            row = row[row['Municipio'] == municipio]

        if not row.empty:
            if institution == "Escola":
                nome_instituicao = row['Escola'].values[0]
                endereco = row['Endereço'].values[0]
                self.latitude = row['Latitude'].values[0]
                self.longitude = row['Longitude'].values[0]
            else:
                nome_instituicao = row['NOME_DA_IES'].values[0]
                sigla_instituicao = row['SIGLA'].values[0]
                municipio = row['MUNICIPIO'].values[0]
                uf = row['UF'].values[0]
                endereco = f"{nome_instituicao} ({sigla_instituicao}), {municipio}, {uf}, Brasil"
                self.latitude, self.longitude = self.get_lat_lng(endereco)

            if self.latitude and self.longitude:
                self.nome_label.setText(f"Nome da {institution}: {nome_instituicao}")
                self.endereco_label.setText(f"Endereço: {endereco}")
                self.codigo_censo_label.setText(f"Código do Censo: {codigo_censo}")
                self.abrir_localizacao()
            else:
                QtWidgets.QMessageBox.critical(self, 'Erro', 'Endereço não encontrado')
        else:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Código do censo não encontrado')

    def buscar_nome(self):
        nome_ou_sigla_instituicao = self.normalize_string(self.entry.text())  # Convertendo a entrada para minúsculas
        row = pd.DataFrame()  # Define um DataFrame vazio como valor padrão para 'row'

        if not nome_ou_sigla_instituicao:
            QtWidgets.QMessageBox.critical(self, 'Erro', 'Nome da instituição inválido')
            return

        uf = self.uf_combo.currentText()

        institution = None
        if self.institution_school.isChecked():
            institution = "Escola"
            df = self.df_school
            nome_col = 'Escola'
        elif self.institution_college.isChecked():
            institution = "Faculdade"
            df = self.df_college
            nome_col = 'NOME_DA_IES'
        else:
            institution = None

        if institution is not None:
            # Primeiro, tenta encontrar a instituição pelo nome
            row = df[df[nome_col].str.lower().str.contains(nome_ou_sigla_instituicao, case=False)]  # Convertendo o nome para minúsculas antes da comparação

            # Filtrar por UF, se escolhida
            if uf != "Todos":
                row = row[row['UF'] == uf]

            # Se não encontrar, tenta encontrar a instituição pela sigla
            if row.empty and institution == "Faculdade":
                row = df[df['SIGLA'].fillna('').str.lower().str.contains(nome_ou_sigla_instituicao, case=False)]  # Convertendo a sigla para minúsculas antes da comparação

        municipio = self.municipio_combo.currentText()
        
        # Filtra por município, se escolhido
        if municipio != "Todos":
            row = row[row['Municipio'] == municipio]

        if not row.empty:
            if institution == "Escola":
                nome_instituicao = row['Escola'].values[0]
                endereco = row['Endereço'].values[0]
                self.latitude = row['Latitude'].values[0]
                self.longitude = row['Longitude'].values[0]
                codigo_censo = row['Código INEP'].values[0]
            elif institution == "Faculdade":
                nome_instituicao = row['NOME_DA_IES'].values[0]
                sigla_instituicao = row['SIGLA'].values[0]
                municipio = row['MUNICIPIO'].values[0]
                uf = row['UF'].values[0]
                endereco = f"{nome_instituicao} ({sigla_instituicao}), {municipio}, {uf}, Brasil"
                codigo_censo = row['CODIGO_DA_IES'].values[0]
                self.latitude, self.longitude = self.get_lat_lng(endereco)

            if self.latitude and self.longitude:
                self.nome_label.setText(f"Nome da {institution}: {nome_instituicao}")
                self.endereco_label.setText(f"Endereço: {endereco}")
                self.codigo_censo_label.setText(f"Código do Censo: {codigo_censo}")
                self.abrir_localizacao()
            else:
                QtWidgets.QMessageBox.critical(self, 'Erro', 'Endereço não encontrado')
        else:
            if institution is None:
                endereco = nome_ou_sigla_instituicao
                if uf != "Todos":
                    endereco = f"{endereco}, {uf}"
                self.latitude, self.longitude = self.get_lat_lng(endereco)
                if self.latitude and self.longitude:
                    self.nome_label.setText(f"Localização: {nome_ou_sigla_instituicao}")
                    self.endereco_label.setText(f"Endereço: {endereco}")
                    self.codigo_censo_label.setText("")
                    self.abrir_localizacao()
                else:
                    QtWidgets.QMessageBox.critical(self, 'Erro', 'Endereço não encontrado')

            else:
                QtWidgets.QMessageBox.critical(self, 'Erro', 'Nenhuma instituição encontrada')

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
        gmap = gmplot.GoogleMapPlotter(float(self.latitude), float(self.longitude), 15, apikey="AIzaSyAS4cGtz7RQtDY-lJt4OKTO_klh3UYwDkI")
        gmap.marker(float(self.latitude), float(self.longitude), 'red')
        gmap.draw("mapa.html")
        webbrowser.open("mapa.html")

    def toggle_topmost(self, state):
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, state == QtCore.Qt.Checked)
        self.show()

    def closeEvent(self, event):
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # Cria uma janela de inicialização
    splash_pix = QPixmap('placeholder.ico')
    splash = QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()  # Processa eventos antes do main loop
    
    window = App()
    window.show()

    splash.finish(window)  # Fecha a janela de inicialização após a janela principal ser carregada

    sys.exit(app.exec_())
