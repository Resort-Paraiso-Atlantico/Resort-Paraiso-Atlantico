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

## 🔄 Restauração do Banco de Dados

Para carregar a estrutura das tabelas e a massa de dados inicial de teste:

### Opção A: Usando os Arquivos SQL (`schema.sql` e `dados.sql`)

**Se estiver usando PostgreSQL Nativo (Sem Docker):**
```bash
psql -U postgres -d resort -f schema.sql
psql -U postgres -d resort -f dados.sql
```

**Se estiver usando via Docker (Windows PowerShell):**
```powershell
Get-Content schema.sql | docker exec -i postgres-resort psql -U postgres -d resort
Get-Content dados.sql | docker exec -i postgres-resort psql -U postgres -d resort
```

**Se estiver usando via Docker (Linux / Git Bash / macOS):**
```bash
docker exec -i postgres-resort psql -U postgres -d resort < schema.sql
docker exec -i postgres-resort psql -U postgres -d resort < dados.sql
```

### Opção B: Usando o Arquivo de Backup Completo (`banco.backup`)

**Se estiver usando PostgreSQL Nativo (Sem Docker):**
```bash
pg_restore -U postgres -d resort banco.backup
```

**Se estiver usando via Docker:**
```bash
docker exec -i postgres-resort pg_restore -U postgres -d resort banco.backup
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

## 📂 Arquivos Entregues do Banco de Dados

- **`schema.sql`**: Arquivo com a estrutura completa do banco de dados (tabelas, chaves primárias/estrangeiras, sequências e restrições).
- **`dados.sql`**: Arquivo com a massa de dados inicial de teste para todas as tabelas.
- **`banco.backup`**: Arquivo de backup completo em formato customizado do PostgreSQL (`pg_dump -Fc`).
- **`.env.exemplo`**: Modelo do arquivo de configurações de variáveis de ambiente do banco de dados.
- **`.streamlit/secrets.toml.exemplo`**: Modelo do arquivo de segredos de autenticação do Streamlit.
