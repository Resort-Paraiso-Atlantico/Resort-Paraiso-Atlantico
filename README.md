# Configuração do Ambiente

## Pré-requisitos

Antes de iniciar o projeto, certifique-se de ter instalado:

- Docker
- Python 3.13.5 (ou a versão utilizada pelo projeto)

---

## Banco de Dados PostgreSQL

Com o Docker em execução, crie o container do PostgreSQL utilizando o comando abaixo:

```bash
docker run --name postgres-resort \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=postgres \
-e POSTGRES_DB=resort \
-p 5555:5432 \
-d postgres
```

### Informações da conexão

| Propriedade | Valor |
|------------|--------|
| Host | localhost |
| Porta | 5555 |
| Banco | resort |
| Usuário | postgres |
| Senha | postgres |

---

## Variáveis de Ambiente

Na raiz do projeto, crie um arquivo chamado `.env` com o seguinte conteúdo:

```env
DB_HOST=localhost
DB_PORT=5555
DB_NAME=resort
DB_USER=postgres
DB_PASSWORD=postgres
```

---

## Instalação das Dependências

Instale as dependências do projeto com:

```bash
pip install -r requirements.txt
```

---

Se tudo estiver configurado corretamente, o sistema deverá se conectar ao banco PostgreSQL e criar as tabelas definidas pelos modelos da aplicação.
