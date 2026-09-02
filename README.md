# 🏨 Resort Paraíso Atlântico — Sistema de Gestão Hoteleira

**Universidade Federal do Agreste de Pernambuco (UFAPE)**  
**Disciplina:** Sistemas de Informação  
**Docente:** Prof. Assuero Fonseca Ximenes  

---

## 👨‍💻 Integrantes da Equipe

- **Guilherme de Almeida Gama**
- **Renato Moreira Beltrão Filho**
- **Ruan Diego Alves da Paz**
- **Ryan Oliveira Marques**

---

## 📝 Sobre o Projeto

O **Resort Paraíso Atlântico** é um sistema de gestão hoteleira desenvolvido em **Python (Streamlit)** com persistência em **PostgreSQL**. O sistema centraliza e automatiza as rotinas operacionais de um resort de praia, abrangendo:

- 👤 **Gestão de Hóspedes**: Cadastro e consulta de hóspedes com validações de dados.
- 🛏️ **Reserva de Suítes**: Controle de disponibilidade, alocação de suítes (Standard, Luxo, Master, Presidencial, Bangalô) e controle de check-in / check-out.
- 🎉 **Eventos e Experiências**: Agendamento de eventos do resort (luaus, workshops, torneios) e inscrição de hóspedes.
- 📦 **Gestão de Estoque e Compras**: Cadastro de produtos, pontos de reposição, cadastro de fornecedores e controle de pedidos de compra.
- 📊 **Painel Financeiro & Dashboards**: Visualização em tempo real da ocupação, faturamento das reservas, compras e saúde financeira do resort.

---

## ⚙️ Pré-requisitos

Antes de iniciar o projeto, certifique-se de ter instalado:

- Python 3.10+ (Recomendado 3.13.5)
- PostgreSQL (Instalação Local Nativa **ou** via Docker)

---

## 🗄️ Banco de Dados PostgreSQL

Você pode executar o PostgreSQL de duas formas:

### Opção 1: Via Docker (Recomendado)
Com o Docker em execução, crie o container do PostgreSQL com o comando abaixo:

```bash
docker run --name postgres-resort \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=resort \
  -p 5555:5432 \
  -d postgres
```

### Opção 2: Sem Docker (Instalação Nativa Local)
Certifique-se de ter o PostgreSQL rodando localmente e crie o banco de dados com:

```bash
psql -U postgres -c "CREATE DATABASE resort;"
```

### Informações da Conexão Padrão

| Propriedade | Valor (Docker) | Valor (Nativo Local) |
| :--- | :--- | :--- |
| **Host** | `localhost` | `localhost` |
| **Porta** | `5555` | `5432` |
| **Banco** | `resort` | `resort` |
| **Usuário** | `postgres` | `postgres` |
| **Senha** | `postgres` | `sua_senha_local` |

---

## 🔄 Configuração Inicial do Banco de Dados

### 1️⃣ Primeira Execução (Criação Automática do Schema)

Na **primeira execução**, o SQLAlchemy criará automaticamente todas as tabelas do banco. Execute:

```bash
streamlit run main.py
```

O arquivo `main.py` contém a seguinte instrução que cria o schema automaticamente:
```python
from app.models.Base import Base
Base.metadata.create_all(engine)  # Cria todas as tabelas
```

> ✅ **Verificar**: Você verá as tabelas criadas no PostgreSQL após esta primeira execução.

---

### 2️⃣ Carregar Dados de Teste (Opcional)

Após criar o schema, você pode popularo banco com dados de teste usando o arquivo `dados_backup.sql`:

**Se estiver usando PostgreSQL Nativo (Sem Docker):**
```bash
psql -U postgres -d resort -f dados_backup.sql
```

**Se estiver usando via Docker (Windows PowerShell):**
```powershell
Get-Content dados_backup.sql | docker exec -i postgres-resort psql -U postgres -d resort
```

**Se estiver usando via Docker (Linux / Git Bash / macOS):**
```bash
docker exec -i postgres-resort psql -U postgres -d resort < dados_backup.sql
```

---

### 3️⃣ Backup Completo (Restauração Futura)

Se precisar fazer backup ou restaurar o banco completo, use `backup_banco.sql`:

**Exportar todo o banco:**
```bash
docker exec postgres-resort pg_dump -U postgres resort > backup_banco.sql
```

**Restaurar a partir do backup:**
```powershell
# Windows PowerShell
Get-Content backup_banco.sql | docker exec -i postgres-resort psql -U postgres -d resort
```

```bash
# Linux / macOS
docker exec -i postgres-resort psql -U postgres -d resort < backup_banco.sql
```

---

## 🔑 Variáveis de Ambiente

Copie o arquivo `.env.exemplo` criando o arquivo `.env` na raiz do projeto:

```bash
cp .env.exemplo .env
```

Conteúdo do arquivo `.env`:

```env
DB_HOST=localhost
DB_PORT=5555
DB_NAME=resort
DB_USER=postgres
DB_PASSWORD=postgres
```
*(Ajuste a porta `DB_PORT` para `5432` e a `DB_PASSWORD` caso esteja rodando o PostgreSQL nativo sem Docker)*.

### Configuração de Autenticação Streamlit (`.streamlit/secrets.toml`)

O projeto utiliza autenticação nativa do Streamlit (Google OAuth2). As credenciais de login e chaves de sessão ficam armazenadas na pasta `.streamlit/secrets.toml`.

Caso esteja configurando do zero, copie o arquivo de exemplo:
```bash
cp .streamlit/secrets.toml.exemplo .streamlit/secrets.toml
```

---

## 📦 Instalação das Dependências

Instale as dependências do projeto com:

```bash
pip install -r requirements.txt
```

---

## 🚀 Executando o Programa

Execute o comando abaixo na raiz do projeto:

```bash
streamlit run main.py
```

Se tudo estiver configurado corretamente, o sistema irá se conectar ao banco PostgreSQL com todas as tabelas e dados pré-carregados.

---

## 📂 Arquivos de Banco de Dados

- **`backup_banco.sql`**: Backup completo do banco (schema + dados). Use este arquivo para restaurar o banco em caso de perda de dados.
- **`dados_backup.sql`**: Somente os dados (sem schema). Use após criar o schema pela primeira execução do sistema.
- **`.env.exemplo`**: Modelo do arquivo de configurações de variáveis de ambiente do banco de dados.
- **`.streamlit/secrets.toml.exemplo`**: Modelo do arquivo de segredos de autenticação do Streamlit.

---

## ⚡ Quick Start (Configuração Rápida)

Siga os passos abaixo para começar a usar o sistema em minutos:

### Passo 1: Preparar o Ambiente
```bash
# Clonar ou abrir o projeto
cd c:\Faculdade\SI\Resort-Paraiso-Atlantico

# Criar e ativar o ambiente virtual
python -m venv venv
.\venv\Scripts\Activate

# Instalar dependências
pip install -r requirements.txt
```

### Passo 2: Configurar PostgreSQL (Docker)
```bash
# Criar o container (se não existir)
docker run --name postgres-resort \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=resort \
  -p 5555:5432 \
  -d postgres

# Verificar se o container está rodando
docker ps
```

### Passo 3: Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.exemplo .env

# Verificar se o arquivo foi criado com os valores:
# DB_HOST=localhost
# DB_PORT=5555
# DB_NAME=resort
# DB_USER=postgres
# DB_PASSWORD=postgres
```

### Passo 4: Primeira Execução (Cria o Schema)
```bash
streamlit run main.py
# O sistema criará automaticamente todas as tabelas no banco de dados
# Pressione Ctrl+C para parar quando desejar
```

### Passo 5: Carregar Dados de Teste (Opcional)
```powershell
# No PowerShell, na pasta do projeto
Get-Content dados_backup.sql | docker exec -i postgres-resort psql -U postgres -d resort
```

### Passo 6: Executar o Sistema
```bash
streamlit run main.py
# Abra o navegador em http://localhost:8501
```

---

## ✅ Checklist de Verificação

Antes de reportar problemas, verifique:

- [ ] PostgreSQL está rodando (`docker ps` deve listar `postgres-resort`)
- [ ] `.env` foi criado com os valores corretos
- [ ] Primeira execução foi feita (`streamlit run main.py`)
- [ ] Tabelas foram criadas no banco (verifique com `psql` ou DBeaver)
- [ ] Dados de teste foram carregados (opcional, verifique com `SELECT COUNT(*) FROM hospedes;`)
- [ ] Porta 5555 (PostgreSQL) e 8501 (Streamlit) estão livres

---
