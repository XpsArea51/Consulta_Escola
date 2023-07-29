from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QLineEdit, QPushButton, QCompleter, QScrollArea, QScrollArea, QWidget
from PyQt5.QtCore import QSize, QTimer

from backend import App

# classe que cria a interface principal do programa
class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Define arquivos CSV
        self.csv_files = [csv_censo_path]
        
        self.load_data()
        self.init_ui()

    def init_ui(self):

        self.setWindowTitle('Busca Inteligente de Escolas')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)  # permite minimizar e fechar a janela
        self.setGeometry(750, 300, 500, 550)  # define o tamanho e a posição inicial da janela

        self.setWindowIcon(QIcon(icone_path))  # Adiciona um ícone à janela

        # layout vertical
        layout = QtWidgets.QVBoxLayout(self)

        # campo de entrada
        self.entry_label = QLabel("Código Censo ou Nome da IE:", self)
        layout.addWidget(self.entry_label)
        self.entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.entry)

        # Definir a largura desejada para a combobox
        largura_desejada = 100

        # Campo de entrada para a UF
        self.uf_label = QLabel("Selecione a UF:", self)
        layout.addWidget(self.uf_label)

        self.uf_entry = QtWidgets.QComboBox(self)
        self.uf_entry.addItems(sorted(['Todos'] + list(self.uf_mapping.values())))
        self.uf_entry.setCurrentText('Todos')

        # Definir a largura da combobox
        self.uf_entry.setFixedWidth(largura_desejada)

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

        self.button_codigo = QPushButton('Buscar código censo', self)
        self.button_codigo.setFixedSize(250, 45)  # Ajuste esses números para o tamanho que você deseja
        self.button_codigo.setStyleSheet("""
            QPushButton {
                color: #FFF;
                background-color: #116A7B;
                border-radius: 5px;
                font-size: 17px;
            }
            QPushButton:hover {
                background-color: #64CCC5;
            }
            QPushButton:pressed {
                background-color: #A2FF86;
            }
        """)

        button_layout.addWidget(self.button_codigo)
        self.button_codigo.clicked.connect(self.buscar_codigo)

        self.button_nome = QPushButton('Buscar Nome', self)
        self.button_nome.setFixedSize(250, 45)  # Ajuste esses números para o tamanho que você deseja
        self.button_nome.setStyleSheet("""
            QPushButton {
                color: #FFF;
                background-color: #F24C3D;
                border-radius: 5px;
                font-size: 17px;
            }
            QPushButton:hover {
                background-color: #22A699;
            }
            QPushButton:pressed {
                background-color: #A2FF86;
            }
        """)

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

        self.button = QtWidgets.QPushButton("Travar Janela", self)
        self.button.setFixedSize(115, 22)
        self.button.setCheckable(True)  # torna o botão toggle
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: #fff;
                border: 2px solid #333;
                font: 15px sans-serif;
            }
            QPushButton:hover {
                background-color: #ff003b;
                color: #fff;
            }
            QPushButton:pressed {
                background-color: #ff003b;
                color: #fff;
            }
            QPushButton:checked {
                background-color: #ff003b;
                color: #fff;
            }
        """)

        # Conecta o sinal 'clicked' ou 'toggled' ao slot 'toggle_topmost'
        self.button.toggled.connect(self.toggle_topmost)

        layout.addWidget(self.button)

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


# classe que criar o widget de escola com base nos dados do censo
class SchoolWidget(QtWidgets.QWidget):
    def __init__(self, nome, endereco, codigo_censo, latitude, longitude, municipio, uf):
        super().__init__()

        self.setWindowIcon(QIcon(icone_path))

        layout = QtWidgets.QVBoxLayout(self)

        self.nome_label = QLabel(shorten(f"Nome: {str(nome)}", width=50, placeholder="..."))
        self.nome_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.nome_label)

        if pd.notnull(uf):
            self.uf_label = QLabel(f"UF: {uf}")
            self.uf_label.setToolTip(uf)
        else:
            self.uf_label = QLabel("UF: Não disponível")
            self.uf_label.setToolTip("UF: Não disponível")
        
        self.uf_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.uf_label)

        if pd.notnull(municipio):
            self.municipio_label = QLabel(f"Município: {municipio}")
            self.municipio_label.setToolTip(municipio)
        else:
            self.municipio_label = QLabel("Município: Não disponível")
            self.municipio_label.setToolTip("Município: Não disponível")
        
        self.municipio_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.municipio_label)

        if pd.notnull(endereco):
            self.endereco_label = QLabel(shorten(f"Endereço: {str(endereco)}", width=50, placeholder="..."))
            self.endereco_label.setToolTip(endereco)
        else:
            self.endereco_label = QLabel("Endereço: Não disponível")
            self.endereco_label.setToolTip("Endereço: Não disponível")
        
        self.endereco_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.endereco_label)

        self.codigo_censo_label = QLabel(f"Código do Censo: {codigo_censo}")
        self.codigo_censo_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.codigo_censo_label)

        self.municipio = municipio
        self.uf = uf
        self.latitude = latitude
        self.longitude = longitude

        self.show_map_button = QPushButton()
        self.show_map_button.setIcon(QIcon(mapa_icon_path))
        # Configura o tamanho do ícone para 64x64
        self.show_map_button.setIconSize(QSize(40, 40))  
        self.show_map_button.setFixedSize(50, 50)
        self.show_map_button.clicked.connect(self.open_map)
        layout.addWidget(self.show_map_button)

        layout.addSpacing(20)  # Adiciona espaço entre os widgets de escola

# Código para conectar o frontend ao backend.
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])

    # Defina o pixmap para o splash screen e exiba-o
    splash_pix = QPixmap(icone_path)  # Coloque aqui o caminho para a sua logo
    splash = QSplashScreen(splash_pix)
    splash.show()

    backend_app = App()  # Instancia a classe do backend

    window = backend_app  # Janela do frontend é controlada pelo backend
    window.show()

    while not window.isVisible():
        app.processEvents()
        time.sleep(0.1)

    splash.finish(window)  # Fechar o splash screen

    sys.exit(app.exec_())
