import hashlib
import psycopg2
from db import conectar
import bcrypt

def hash_senha(senha):
    """Cria um hash seguro da senha usando bcrypt"""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def verificar_senha(senha, hash_armazenado):
    """Verifica se a senha corresponde ao hash armazenado usando bcrypt"""
    return bcrypt.checkpw(senha.encode(), hash_armazenado.encode())

def criar_tabela_usuarios():
    """Cria a tabela de usuários se não existir"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nome TEXT NOT NULL
    );
    """)
    
    # Criar usuário admin padrão se não existir
    cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@barbearia.com'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (email, senha, nome) VALUES (%s, %s, %s)",
            ('admin@barbearia.com', hash_senha('admin123'), 'Administrador')
        )
    
    conn.commit()
    conn.close()

def validar_login(email, senha):
    """Valida as credenciais do barbeiro na tabela usuarios."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, senha FROM usuarios WHERE email = %s",
        (email,)
    )
    usuario = cursor.fetchone()
    conn.close()
    if usuario and verificar_senha(senha, usuario[2]):
        return {'id': usuario[0], 'nome': usuario[1]}
    return None

def registrar_usuario(email, senha, nome):
    """Registra um novo usuário barbeiro na tabela usuarios."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        raise Exception("Já existe um usuário com este email.")
    hash_senha_usuario = hash_senha(senha)
    cursor.execute(
        "INSERT INTO usuarios (email, senha, nome) VALUES (%s, %s, %s)",
        (email, hash_senha_usuario, nome)
    )
    conn.commit()
    conn.close()