import sqlite3
from models import Cliente, Agendamento, Servico
from datetime import datetime

DB_PATH = "agendamentos.db"

class DatabaseError(Exception):
    """Exceção personalizada para erros do banco de dados"""
    pass

def conectar():
    """Estabelece conexão com o banco de dados SQLite."""
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro ao conectar ao banco de dados: {str(e)}")

def criar_tabelas():
    """Cria as tabelas necessárias no banco de dados se não existirem."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            duracao INTEGER NOT NULL,
            descricao TEXT
        )
        """)

        # Inserir serviços padrão se não existirem
        servicos_padrao = [
            ("Corte de Cabelo", 35.00, 30, "Corte masculino tradicional"),
            ("Barba", 25.00, 20, "Barba com acabamento"),
            ("Corte + Barba", 55.00, 50, "Pacote completo"),
            ("Acabamento", 15.00, 15, "Acabamento na máquina"),
        ]

        for servico in servicos_padrao:
            cursor.execute("SELECT id FROM servicos WHERE nome = ?", (servico[0],))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO servicos (nome, preco, duracao, descricao)
                VALUES (?, ?, ?, ?)
                """, servico)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT NOT NULL,
            cliente_telefone TEXT NOT NULL,
            servico_id INTEGER,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            FOREIGN KEY (servico_id) REFERENCES servicos (id)
        )
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro ao criar tabelas: {str(e)}")
    finally:
        conn.close()

def verificar_conflito_horario(data, hora, agendamento_id=None):
    """Verifica se já existe um agendamento no mesmo horário."""
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        if agendamento_id:
            cursor.execute("""
                SELECT COUNT(*) FROM agendamentos 
                WHERE data = ? AND hora = ? AND id != ? AND status != 'Cancelado'
            """, (data, hora, agendamento_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM agendamentos 
                WHERE data = ? AND hora = ? AND status != 'Cancelado'
            """, (data, hora))
        
        count = cursor.fetchone()[0]
        return count > 0
    finally:
        conn.close()

def adicionar_agendamento(nome, telefone, servico_id, data, hora):
    """Adiciona um novo agendamento ao banco de dados."""
    conn = None
    try:
        # Validações básicas
        if not nome or len(nome.strip()) < 3:
            raise DatabaseError("Nome deve ter pelo menos 3 caracteres")
            
        if not telefone or len(''.join(filter(str.isdigit, telefone))) < 10:
            raise DatabaseError("Telefone inválido")
            
        if not servico_id:
            raise DatabaseError("Serviço não selecionado")
            
        if not data or not hora:
            raise DatabaseError("Data e hora são obrigatórios")
            
        # Estabelece conexão com o banco
        conn = conectar()
        cursor = conn.cursor()
        
        # Verifica se o serviço existe
        cursor.execute("SELECT id FROM servicos WHERE id = ?", (servico_id,))
        if not cursor.fetchone():
            raise DatabaseError(f"Serviço com ID {servico_id} não encontrado")
            
        # Verifica conflito de horário
        if verificar_conflito_horario(data, hora):
            raise DatabaseError("Já existe um agendamento para este horário")
        
        # Insere o agendamento
        cursor.execute("""
        INSERT INTO agendamentos (cliente_nome, cliente_telefone, servico_id, data, hora, status)
        VALUES (?, ?, ?, ?, ?, 'Pendente')
        """, (nome.strip(), telefone, servico_id, data, hora))
        
        conn.commit()
        return cursor.lastrowid
        
    except sqlite3.IntegrityError:
        raise DatabaseError("Erro ao salvar agendamento. Verifique os dados e tente novamente.")
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro no banco de dados: {str(e)}")
    finally:
        if conn:
            conn.close()

def listar_servicos():
    """Retorna todos os serviços disponíveis."""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome, preco, duracao, descricao FROM servicos")
        servicos = cursor.fetchall()
        
        return [Servico(*servico) for servico in servicos]
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro ao listar serviços: {str(e)}")
    finally:
        if conn:
            conn.close()

def listar_agendamentos():
    """Retorna todos os agendamentos com informações dos clientes e serviços."""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            ag.id,
            ag.cliente_nome,
            ag.cliente_telefone,
            s.nome,
            s.duracao,
            ag.data,
            ag.hora,
            ag.status
        FROM agendamentos ag
        JOIN servicos s ON ag.servico_id = s.id
        ORDER BY ag.data, ag.hora
        """)
        
        rows = cursor.fetchall()
        
        agendamentos = []
        for row in rows:
            ag_id, nome, telefone, servico, duracao, data, hora, status = row
            cliente = Cliente(nome=nome, telefone=telefone)
            agendamento = Agendamento(
                id=ag_id,
                cliente=cliente,
                servico=servico,
                duracao=duracao,
                data=data,
                hora=hora,
                status=status
            )
            agendamentos.append(agendamento)
        
        return agendamentos
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro ao listar agendamentos: {str(e)}")
    finally:
        if conn:
            conn.close()

def atualizar_status(agendamento_id, novo_status):
    """Atualiza o status de um agendamento específico."""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE agendamentos SET status = ? WHERE id = ?", 
                      (novo_status, agendamento_id))
        
        if cursor.rowcount == 0:
            raise DatabaseError("Agendamento não encontrado")
            
        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro ao atualizar status: {str(e)}")
    finally:
        if conn:
            conn.close()

def buscar_agendamentos_por_cliente(cliente_nome):
    """Busca agendamentos pelo nome do cliente."""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT 
            ag.id,
            ag.cliente_nome,
            ag.cliente_telefone,
            s.nome,
            s.duracao,
            ag.data,
            ag.hora,
            ag.status
        FROM agendamentos ag
        JOIN servicos s ON ag.servico_id = s.id
        WHERE ag.cliente_nome LIKE ?
        ORDER BY ag.data, ag.hora
        """, (f"%{cliente_nome}%",))
        
        rows = cursor.fetchall()
        
        agendamentos = []
        for row in rows:
            ag_id, nome, telefone, servico, duracao, data, hora, status = row
            cliente = Cliente(nome=nome, telefone=telefone)
            agendamento = Agendamento(
                id=ag_id,
                cliente=cliente,
                servico=servico,
                duracao=duracao,
                data=data,
                hora=hora,
                status=status
            )
            agendamentos.append(agendamento)
        
        return agendamentos
    except sqlite3.Error as e:
        raise DatabaseError(f"Erro ao buscar agendamentos: {str(e)}")
    finally:
        if conn:
            conn.close()