import psycopg2
from psycopg2 import sql
from models import Cliente, Agendamento, Servico
from datetime import datetime

DB_CONFIG = {
    'dbname': 'agendamentos',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432,
    'client_encoding': 'utf8'  # Força a codificação UTF-8
}

class DatabaseError(Exception):
    """Exceção personalizada para erros do banco de dados"""
    pass

def conectar():
    """Estabelece conexão com o banco de dados PostgreSQL."""
    try:
        print("DB_CONFIG:", DB_CONFIG)  # Adicionado para depuração
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        raise DatabaseError(f"Erro ao conectar ao banco de dados: {str(e)}")

def criar_tabelas():
    """Cria as tabelas necessárias no banco de dados se não existirem."""
    conn = None  # Initialize conn to None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            duracao INTEGER NOT NULL,
            descricao TEXT
        );
        """)

        # Inserir serviços padrão se não existirem
        servicos_padrao = [
            ("Corte de Cabelo", 35.00, 30, "Corte masculino tradicional"),
            ("Barba", 25.00, 20, "Barba com acabamento"),
            ("Corte + Barba", 55.00, 50, "Pacote completo"),
            ("Acabamento", 15.00, 15, "Acabamento na máquina"),
        ]

        for servico in servicos_padrao:
            cursor.execute("SELECT id FROM servicos WHERE nome = %s", (servico[0],))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO servicos (nome, preco, duracao, descricao)
                VALUES (%s, %s, %s, %s)
                """, servico)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id SERIAL PRIMARY KEY,
            cliente_nome TEXT NOT NULL,
            cliente_telefone TEXT NOT NULL,
            servico_id INTEGER REFERENCES servicos (id),
            data DATE NOT NULL,
            hora TIME NOT NULL,
            status TEXT DEFAULT 'Pendente'
        );
        """)
        
        conn.commit()
    except psycopg2.Error as e:
        raise DatabaseError(f"Erro ao criar tabelas: {str(e)}")
    finally:
        if conn:  # Ensure conn is not None before closing
            conn.close()

def verificar_conflito_horario(data, hora, agendamento_id=None):
    """Checks if there is already an appointment at the same time."""
    try:
        conn = conectar()
        cursor = conn.cursor()

        if agendamento_id:
            cursor.execute("""
                SELECT COUNT(*) FROM agendamentos 
                WHERE data = %s AND hora = %s AND id != %s AND status != 'Cancelado'
            """, (data, hora, agendamento_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM agendamentos 
                WHERE data = %s AND hora = %s AND status != 'Cancelado'
            """, (data, hora))

        count = cursor.fetchone()[0]
        return count > 0
    finally:
        if conn:
            conn.close()

def adicionar_agendamento(nome, telefone, servico_id, data, hora):
    """Adds a new appointment to the database."""
    conn = None
    try:
        # Basic validations
        if not nome or len(nome.strip()) < 3:
            raise DatabaseError("Name must have at least 3 characters")

        if not telefone or len(''.join(filter(str.isdigit, telefone))) < 10:
            raise DatabaseError("Invalid phone number")

        if not servico_id:
            raise DatabaseError("Service not selected")

        if not data or not hora:
            raise DatabaseError("Date and time are required")

        # Establish connection to the database
        conn = conectar()
        cursor = conn.cursor()

        # Check if the service exists
        cursor.execute("SELECT id FROM servicos WHERE id = %s", (servico_id,))
        if not cursor.fetchone():
            raise DatabaseError(f"Service with ID {servico_id} not found")

        # Check for time conflicts
        if verificar_conflito_horario(data, hora):
            raise DatabaseError("There is already an appointment for this time")

        # Insert the appointment
        cursor.execute("""
        INSERT INTO agendamentos (cliente_nome, cliente_telefone, servico_id, data, hora, status)
        VALUES (%s, %s, %s, %s, %s, 'Pendente')
        """, (nome.strip(), telefone, servico_id, data, hora))

        conn.commit()
        return cursor.lastrowid

    except psycopg2.IntegrityError:
        raise DatabaseError("Error saving appointment. Check the data and try again.")
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

def listar_servicos():
    """Returns all available services."""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome, preco, duracao, descricao FROM servicos")
        servicos = cursor.fetchall()

        return [Servico(*servico) for servico in servicos]
    except psycopg2.Error as e:
        raise DatabaseError(f"Error listing services: {str(e)}")
    finally:
        if conn:
            conn.close()

def listar_agendamentos():
    """Returns all appointments with client and service information."""
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
    except psycopg2.Error as e:
        raise DatabaseError(f"Error listing appointments: {str(e)}")
    finally:
        if conn:
            conn.close()

def atualizar_status(agendamento_id, novo_status):
    """Atualiza o status de um agendamento específico."""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE agendamentos SET status = %s WHERE id = %s", 
                      (novo_status, agendamento_id))
        
        if cursor.rowcount == 0:
            raise DatabaseError("Agendamento não encontrado")
            
        conn.commit()
    except psycopg2.Error as e:
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
        WHERE ag.cliente_nome LIKE %s
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
    except psycopg2.Error as e:
        raise DatabaseError(f"Erro ao buscar agendamentos: {str(e)}")
    finally:
        if conn:
            conn.close()