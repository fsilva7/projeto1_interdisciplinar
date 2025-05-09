import flet as ft
from datetime import datetime, timedelta
import db
import auth
from utils import (
    STATUS_CORES, 
    HORARIOS_DISPONIVEIS,
    criar_mensagem_erro, 
    criar_mensagem_sucesso, 
    validar_data, 
    validar_hora,
    formatar_telefone
)

class BarbeariaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Barbearia - Sistema de Agendamento"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1000
        self.page.window_height = 800
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 20
        
        # Inicializar banco de dados e tabelas
        db.criar_tabelas()
        auth.criar_tabela_usuarios()
        
        # Estado do usuário
        self.barbeiro_atual = None
        
        # Componentes de login do barbeiro
        self.email_login = ft.TextField(
            label="Email",
            keyboard_type=ft.KeyboardType.EMAIL,
            expand=True
        )
        self.senha_login = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            expand=True
        )
        
        # Componentes do formulário de agendamento
        self.nome_cliente = ft.TextField(
            label="Nome completo",
            expand=True
        )
        self.telefone_cliente = ft.TextField(
            label="Telefone",
            expand=True,
            on_change=self.formatar_telefone_input
        )
        self.servicos_dropdown = ft.Dropdown(
            label="Serviço",
            expand=True,
            options=[
                ft.dropdown.Option(key=str(s.id), text=str(s))
                for s in db.listar_servicos()
            ]
        )
        
        # Gerar próximos 30 dias disponíveis (exceto domingos)
        dias_disponiveis = []
        data_atual = datetime.now()
        for i in range(30):
            data = data_atual + timedelta(days=i)
            if data.weekday() < 6:  # Segunda a Sábado
                dias_disponiveis.append(
                    ft.dropdown.Option(data.strftime("%Y-%m-%d"))
                )
        
        self.dias_disponiveis = ft.Dropdown(
            label="Dia",
            options=dias_disponiveis,
            expand=True
        )
        
        self.horarios_disponiveis = ft.Dropdown(
            label="Horário",
            options=[ft.dropdown.Option(hora) for hora in HORARIOS_DISPONIVEIS],
            expand=True
        )
        
        # Container para mensagens
        self.mensagem_container = ft.Container(visible=False)
        
        # Mostrar tela inicial de agendamento
        self.mostrar_tela_agendamento()
    
    def formatar_telefone_input(self, e):
        """Formata o número de telefone enquanto o usuário digita"""
        self.telefone_cliente.value = formatar_telefone(e.control.value)
        self.page.update()
    
    def mostrar_mensagem(self, mensagem, tipo="erro"):
        """Exibe uma mensagem na interface."""
        self.mensagem_container.visible = True
        if tipo == "erro":
            self.mensagem_container.content = criar_mensagem_erro(mensagem)
        else:
            self.mensagem_container.content = criar_mensagem_sucesso(mensagem)
        self.page.update()
    
    def mostrar_tela_agendamento(self):
        """Mostra a tela principal de agendamento para clientes."""
        self.page.clean()
        
        # Cabeçalho
        titulo = ft.Text("Barbearia", size=32, weight=ft.FontWeight.BOLD)
        subtitulo = ft.Text("Faça seu agendamento", size=16)
        
        # Link para área administrativa
        link_admin = ft.TextButton(
            "Área do Barbeiro",
            on_click=lambda _: self.mostrar_tela_login()
        )
        
        # Formulário de agendamento
        form_agendamento = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Novo Agendamento", size=20, weight=ft.FontWeight.BOLD),
                    self.nome_cliente,
                    self.telefone_cliente,
                    self.servicos_dropdown,
                    ft.Row([
                        self.dias_disponiveis,
                        self.horarios_disponiveis
                    ], spacing=10),
                    self.mensagem_container,
                    ft.ElevatedButton(
                        "Agendar",
                        icon=ft.icons.CALENDAR_TODAY,
                        on_click=self.fazer_agendamento
                    )
                ], spacing=20),
                padding=20
            )
        )
        
        self.page.add(
            ft.Column([
                ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([subtitulo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([link_admin], alignment=ft.MainAxisAlignment.END),
                form_agendamento
            ], spacing=20)
        )
    
    def mostrar_tela_login(self):
        """Mostra a tela de login para o barbeiro."""
        self.page.clean()
        
        titulo = ft.Text("Área Administrativa", size=32, weight=ft.FontWeight.BOLD)
        subtitulo = ft.Text("Login do Barbeiro", size=16)
        
        form_login = ft.Container(
            content=ft.Column([
                ft.Text("Login", size=20, weight=ft.FontWeight.BOLD),
                self.email_login,
                self.senha_login,
                self.mensagem_container,
                ft.ElevatedButton(
                    "Entrar",
                    on_click=self.fazer_login,
                    expand=True
                ),
                ft.TextButton(
                    "Voltar para Agendamentos",
                    on_click=lambda _: self.mostrar_tela_agendamento()
                )
            ], spacing=20),
            padding=30,
            border_radius=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            width=400
        )
        
        self.page.add(
            ft.Column([
                ft.Row([titulo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([subtitulo], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([form_login], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=20)
        )
    
    def fazer_login(self, e):
        """Processa o login do barbeiro."""
        email = self.email_login.value
        senha = self.senha_login.value
        
        if not email or not senha:
            self.mostrar_mensagem("Preencha todos os campos")
            return
        
        barbeiro = auth.validar_login(email, senha)
        if barbeiro:
            self.barbeiro_atual = barbeiro
            self.mostrar_mensagem("Login realizado com sucesso!", tipo="sucesso")
            self.mostrar_tela_barbeiro()
        else:
            self.mostrar_mensagem("Email ou senha inválidos")
    
    def mostrar_tela_barbeiro(self):
        """Mostra a tela principal para barbeiros."""
        self.page.clean()
        
        # Cabeçalho
        cabecalho = ft.AppBar(
            leading=ft.Icon(ft.icons.CONTENT_CUT),
            leading_width=40,
            title=ft.Text(f"Área do Barbeiro - {self.barbeiro_atual['nome']}"),
            center_title=False,
            actions=[
                ft.IconButton(ft.icons.LOGOUT, on_click=self.fazer_logout)
            ],
        )
        
        # Filtros
        filtros = ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Dropdown(
                        label="Filtrar por data",
                        options=[
                            ft.dropdown.Option("hoje", "Hoje"),
                            ft.dropdown.Option("semana", "Esta semana"),
                            ft.dropdown.Option("todos", "Todos")
                        ],
                        value="hoje",
                        on_change=self.filtrar_agendamentos
                    ),
                    ft.Dropdown(
                        label="Status",
                        options=[
                            ft.dropdown.Option("todos", "Todos"),
                            ft.dropdown.Option("Pendente", "Pendentes"),
                            ft.dropdown.Option("Confirmado", "Confirmados"),
                            ft.dropdown.Option("Cancelado", "Cancelados")
                        ],
                        value="todos",
                        on_change=self.filtrar_agendamentos
                    )
                ], spacing=20),
                padding=20
            )
        )
          # Lista de todos os agendamentos
        self.lista_agendamentos = ft.Column(spacing=10)
        self.carregar_agendamentos()
        
        card_agendamentos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Agendamentos", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.icons.REFRESH,
                            tooltip="Atualizar",
                            on_click=lambda _: self.carregar_agendamentos()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    self.lista_agendamentos
                ]),
                padding=20
            )
        )
        
        self.page.add(
            cabecalho,
            ft.Column([filtros, card_agendamentos], spacing=20)
        )
    
    def fazer_logout(self, e):
        """Realiza o logout do barbeiro."""
        self.barbeiro_atual = None
        self.mostrar_tela_agendamento()
    
    def fazer_agendamento(self, e):
        """Processa um novo agendamento."""
        nome = self.nome_cliente.value
        telefone = self.telefone_cliente.value
        servico_id = self.servicos_dropdown.value
        data = self.dias_disponiveis.value
        hora = self.horarios_disponiveis.value
        
        # Validações do lado do cliente
        if not nome or len(nome.strip()) < 3:
            self.mostrar_mensagem("Nome deve ter pelo menos 3 caracteres")
            return
        
        if not telefone or len(''.join(filter(str.isdigit, telefone))) < 10:
            self.mostrar_mensagem("Digite um telefone válido")
            return
        
        if not servico_id:
            self.mostrar_mensagem("Selecione um serviço")
            return
        
        if not data:
            self.mostrar_mensagem("Selecione uma data")
            return
        
        # Validar se a data não é passada
        try:
            data_agendamento = datetime.strptime(data, "%Y-%m-%d").date()
            if data_agendamento < datetime.now().date():
                self.mostrar_mensagem("Selecione uma data futura")
                return
        except ValueError:
            self.mostrar_mensagem("Data inválida")
            return
        
        if not hora:
            self.mostrar_mensagem("Selecione um horário")
            return
        
        # Validar horário comercial
        if not validar_hora(hora):
            self.mostrar_mensagem("Horário inválido ou fora do horário comercial")
            return
        
        try:
            # Tenta adicionar o agendamento no banco
            # Converte servico_id para inteiro já que vem como string do dropdown
            db.adicionar_agendamento(
                nome.strip(),  # Remove espaços extras
                telefone,
                int(servico_id),  # Convertendo para inteiro
                data,
                hora
            )
            
            # Se chegou aqui, deu tudo certo
            self.mostrar_mensagem("Agendamento realizado com sucesso!", tipo="sucesso")
            
            # Limpar campos após sucesso
            self.nome_cliente.value = ""
            self.telefone_cliente.value = ""
            self.servicos_dropdown.value = None
            self.dias_disponiveis.value = None
            self.horarios_disponiveis.value = None
            self.page.update()
        except db.DatabaseError as erro:
            self.mostrar_mensagem(str(erro))
        except Exception as erro:
            self.mostrar_mensagem(f"Erro ao realizar agendamento: {str(erro)}")
    
    def carregar_agendamentos(self, e=None):
        """Carrega todos os agendamentos para visualização do barbeiro."""
        self.lista_agendamentos.controls.clear()
        
        try:
            agendamentos = db.listar_agendamentos()
            
            if not agendamentos:
                self.lista_agendamentos.controls.append(
                    ft.Text("Nenhum agendamento encontrado", italic=True)
                )
            else:
                for agendamento in agendamentos:
                    self.lista_agendamentos.controls.append(
                        self.criar_card_agendamento(agendamento)
                    )
        except Exception as erro:
            self.mostrar_mensagem(f"Erro ao carregar agendamentos: {str(erro)}")
        
        self.page.update()
    
    def filtrar_agendamentos(self, e):
        """Filtra os agendamentos por data e status."""
        # TODO: Implementar filtros
        self.carregar_agendamentos()
    
    def criar_card_agendamento(self, agendamento):
        """Cria um card para exibir um agendamento."""
        def atualizar_status(e):
            try:
                db.atualizar_status(agendamento.id, e.control.value)
                self.carregar_agendamentos()
            except Exception as erro:
                self.mostrar_mensagem(f"Erro ao atualizar status: {str(erro)}")
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON),
                        title=ft.Text(
                            agendamento.cliente.nome,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(f"Tel: {formatar_telefone(agendamento.cliente.telefone)}")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.CALENDAR_TODAY),
                        title=ft.Text(f"Data: {agendamento.data}"),
                        subtitle=ft.Text(f"Hora: {agendamento.hora}")
                    ),
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.BUSINESS_CENTER),
                        title=ft.Text(f"Serviço: {agendamento.servico}")
                    ),
                    ft.Row([
                        ft.Text("Status:"),
                        ft.Dropdown(
                            value=agendamento.status,
                            options=[
                                ft.dropdown.Option(status)
                                for status in ["Pendente", "Confirmado", "Cancelado"]
                            ],
                            on_change=atualizar_status
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=10
            ),
            color=STATUS_CORES.get(agendamento.status)
        )

def main(page: ft.Page):
    app = BarbeariaApp(page)

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)