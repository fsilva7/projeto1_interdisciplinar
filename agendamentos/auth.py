import sqlite3
import hashlib
from db import conectar

def hash_senha(senha):
    """Cria um hash da senha usando SHA-256"""
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_tabela_usuarios():
    """Cria a tabela de usuários se não existir"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        nome TEXT NOT NULL
    )
    """)
    
    # Criar usuário admin padrão se não existir
    cursor.execute("SELECT id FROM usuarios WHERE email = 'admin@barbearia.com'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (email, senha, nome) VALUES (?, ?, ?)",
            ('admin@barbearia.com', hash_senha('admin123'), 'Administrador')
        )
    
    conn.commit()
    conn.close()

def validar_login(email, senha):
    """Valida as credenciais do barbeiro"""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?",
        (email, hash_senha(senha))
    )
    
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return {'id': usuario[0], 'nome': usuario[1]}
    return None