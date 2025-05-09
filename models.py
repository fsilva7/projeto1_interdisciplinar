class Cliente:
    """Classe que representa um cliente no sistema de agendamento."""
    
    def __init__(self, nome, telefone, id=None):
        self.id = id
        self.nome = nome
        self.telefone = telefone
    
    def __str__(self):
        return f"{self.nome} ({self.telefone})"

class Servico:
    """Classe que representa um serviço da barbearia."""
    
    def __init__(self, id, nome, preco, duracao, descricao=None):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.duracao = duracao
        self.descricao = descricao
    
    def __str__(self):
        return f"{self.nome} - R${self.preco:.2f} ({self.duracao} min)"

class Agendamento:
    """Classe que representa um agendamento no sistema."""
    
    STATUS_OPCOES = ["Pendente", "Confirmado", "Cancelado"]
    
    def __init__(self, id, cliente, servico, duracao, data, hora, status="Pendente"):
        self.id = id
        self.cliente = cliente
        self.servico = servico
        self.duracao = duracao
        self.data = data
        self.hora = hora
        self.status = status if status in self.STATUS_OPCOES else "Pendente"
    
    def __str__(self):
        return f"{self.cliente.nome} - {self.servico} - {self.data} {self.hora} [{self.status}]"