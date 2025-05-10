import flet as ft
from datetime import datetime, time

STATUS_CORES = {
    "Pendente": ft.colors.ORANGE_100,
    "Confirmado": ft.colors.GREEN_100,
    "Cancelado": ft.colors.RED_100,
}

# Horários disponíveis para agendamento (de 30 em 30 minutos)
HORARIOS_DISPONIVEIS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"
]

def validar_data(data_str):
    """Valida se a string está no formato de data YYYY-MM-DD e é uma data futura."""
    try:
        if not data_str or len(data_str) != 10:
            return False
        data = datetime.strptime(data_str, "%Y-%m-%d")
        return data >= datetime.now()
    except ValueError:
        return False

def validar_hora(hora_str):
    """Valida se a string está no formato de hora HH:MM e está dentro dos horários disponíveis."""
    try:
        if not hora_str or len(hora_str) != 5:
            return False
        hora = datetime.strptime(hora_str, "%H:%M").time()
        return hora_str in HORARIOS_DISPONIVEIS
    except ValueError:
        return False

def criar_mensagem_erro(mensagem):
    """Cria um componente de mensagem de erro."""
    return ft.Container(
        content=ft.Text(mensagem, color=ft.colors.RED),
        padding=10,
        border_radius=5,
        bgcolor=ft.colors.RED_50
    )

def criar_mensagem_sucesso(mensagem):
    """Cria um componente de mensagem de sucesso."""
    return ft.Container(
        content=ft.Text(mensagem, color=ft.colors.GREEN),
        padding=10,
        border_radius=5,
        bgcolor=ft.colors.GREEN_50
    )

def formatar_telefone(telefone):
    """Formata o número de telefone para o padrão (XX) XXXXX-XXXX."""
    if not telefone:
        return ""
    # Remove todos os caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, telefone))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    return telefone

def verificar_horario_comercial(hora_str):
    """Verifica se o horário está dentro do horário comercial (9h às 18h)."""
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
        hora_inicio = time(9, 0)
        hora_fim = time(18, 0)
        return hora_inicio <= hora <= hora_fim
    except ValueError:
        return False