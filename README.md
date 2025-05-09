# Este projeto utiliza um banco de dados PostgreSQL chamado agendamentos. Abaixo estão os comandos SQL necessários para criar as tabelas essenciais do sistema.

🗂️ Tabelas do Sistema

### clientes : Armazena os dados dos clientes, incluindo nome e telefone.

### serviços: Guarda as informações sobre os serviços disponíveis, como nome, preço, duração e descrição.

### agendamentos: Registra os agendamentos feitos pelos clientes, relacionando com os serviços escolhidos, data, hora e status.

### usuários: Responsável por armazenar os dados de login e perfil dos usuários do sistema.

Os comandos SQL abaixo devem ser executados para criar essas tabelas no banco de dados:


CREATE TABLE clientes (  
    id SERIAL PRIMARY KEY,  
    nome TEXT NOT NULL,  
    telefone TEXT  
);

CREATE TABLE servicos (  
    id SERIAL PRIMARY KEY,  
    nome TEXT NOT NULL,  
    preco REAL NOT NULL,  
    duracao INTEGER NOT NULL,  
    descricao TEXT  
);

CREATE TABLE agendamentos (  
    id SERIAL PRIMARY KEY,  
    cliente_nome TEXT NOT NULL,  
     cliente_telefone TEXT NOT NULL,  
    servico_id INTEGER REFERENCES servicos (id),  
    data DATE NOT NULL,  
    hora TIME NOT NULL,  
    status TEXT DEFAULT 'Pendente'  
);

CREATE TABLE usuarios (  
    id SERIAL PRIMARY KEY,  
    email TEXT UNIQUE NOT NULL,  
    senha TEXT NOT NULL,  
    nome TEXT NOT NULL  
);

