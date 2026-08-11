import os
import psycopg2
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5555'),
        dbname=os.getenv('DB_NAME', 'resort'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )

def seed_database():
    conn = get_connection()
    cur = conn.cursor()

    try:
        print("Limpando dados existentes...")
        tables = [
            "hospede_evento", "pedido_item", "pedido_compra", 
            "reserva_suite", "reservas", "eventos", "produto", 
            "fornecedor", "suites", "hospedes"
        ]
        for t in tables:
            cur.execute(f"TRUNCATE TABLE public.{t} CASCADE;")

        print("1. Inserindo Hóspedes...")
        hospedes_data = [
            ('11122233301', 'Mariana Alencar Ribeiro', '(83) 99123-4567', 'mariana.alencar@email.com', 'Av. Cabo Branco, 1200 - João Pessoa/PB', datetime(2026, 1, 15, 10, 30)),
            ('22233344402', 'Carlos Eduardo Mendonça', '(81) 98877-6655', 'carlos.mendonca@email.com', 'Rua dos Navegantes, 450 - Recife/PE', datetime(2026, 2, 10, 14, 20)),
            ('33344455503', 'Beatriz Souza Vasconcelos', '(11) 97654-3210', 'beatriz.vasconcelos@email.com', 'Alameda Santos, 890 - São Paulo/SP', datetime(2026, 3, 5, 9, 15)),
            ('44455566604', 'Rodrigo Augusto Pereira', '(21) 99811-2233', 'rodrigo.pereira@email.com', 'Av. Atlântica, 2100 - Rio de Janeiro/RJ', datetime(2026, 3, 20, 16, 45)),
            ('55566677705', 'Fernanda Lima Castro', '(31) 99344-5566', 'fernanda.castro@email.com', 'Rua da Bahia, 320 - Belo Horizonte/MG', datetime(2026, 4, 2, 11, 0)),
            ('66677788806', 'Lucas Gabriel Oliveira', '(71) 98765-4321', 'lucas.oliveira@email.com', 'Av. Oceanica, 500 - Salvador/BA', datetime(2026, 4, 18, 15, 10)),
            ('77788899907', 'Camila Martins Duarte', '(85) 99234-5678', 'camila.duarte@email.com', 'Av. Beira Mar, 1500 - Fortaleza/CE', datetime(2026, 5, 12, 8, 50)),
            ('88899900008', 'Thiago Henrique Silva', '(41) 98456-7890', 'thiago.silva@email.com', 'Rua das Flores, 105 - Curitiba/PR', datetime(2026, 5, 25, 13, 30)),
            ('99900011109', 'Juliana Rocha Barbosa', '(61) 99678-1234', 'juliana.barbosa@email.com', 'SQN 208 Bloco B - Brasília/DF', datetime(2026, 6, 1, 10, 0)),
            ('00011122210', 'Rafael Monteiro Costa', '(84) 98123-9876', 'rafael.costa@email.com', 'Av. Eng. Roberto Freire, 800 - Natal/RN', datetime(2026, 6, 10, 17, 15))
        ]
        cur.executemany(
            """INSERT INTO public.hospedes (cpf, nome, telefone, email, endereco, data_cadastro) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            hospedes_data
        )

        print("2. Inserindo Suítes...")
        suites_data = [
            (101, 'Standard', 2, 250.00, 'Livre', datetime(2026, 8, 1, 9, 0)),
            (102, 'Standard', 2, 250.00, 'Ocupada', datetime(2026, 8, 5, 10, 30)),
            (201, 'Luxo Vista Mar', 3, 480.00, 'Ocupada', datetime(2026, 8, 6, 8, 15)),
            (202, 'Luxo Vista Mar', 3, 480.00, 'Livre', datetime(2026, 8, 7, 11, 0)),
            (301, 'Master Family', 4, 750.00, 'Livre', datetime(2026, 8, 4, 14, 0)),
            (302, 'Master Family', 4, 750.00, 'Ocupada', datetime(2026, 8, 8, 9, 45)),
            (401, 'Presidencial Atlântico', 5, 1500.00, 'Livre', datetime(2026, 8, 2, 15, 30)),
            (402, 'Presidencial Atlântico', 5, 1500.00, 'Manutenção', datetime(2026, 7, 28, 16, 0)),
            (501, 'Bangalô Premium', 2, 950.00, 'Livre', datetime(2026, 8, 3, 10, 0)),
            (502, 'Bangalô Premium', 2, 950.00, 'Limpeza', datetime(2026, 8, 10, 11, 15))
        ]
        cur.executemany(
            """INSERT INTO public.suites (numero, tipo, capacidade, valor_diaria, status, ultima_limpeza) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            suites_data
        )

        print("3. Inserindo Eventos...")
        eventos_data = [
            ('Luau de Boas-Vindas à Beira-Mar', 'Festa tropical na praia com música ao vivo e coquetéis inclusos.', datetime(2026, 7, 1), datetime(2026, 8, 15, 20, 0), datetime(2026, 8, 15, 23, 59), 80, 'Agendado'),
            ('Workshop Gastronômico da Costa', 'Aula interativa de frutos do mar com o Chef executivo do resort.', datetime(2026, 7, 10), datetime(2026, 8, 18, 16, 0), datetime(2026, 8, 18, 18, 30), 25, 'Agendado'),
            ('Torneio de Beach Tennis Paraíso', 'Competição amigável de beach tennis com premiação para os finalistas.', datetime(2026, 7, 15), datetime(2026, 8, 20, 8, 30), datetime(2026, 8, 20, 13, 0), 40, 'Agendado'),
            ('Noite de Jazz & Vinhos no Rooftop', 'Degustação guiada de vinhos acompanhada de quarteto de jazz.', datetime(2026, 6, 20), datetime(2026, 8, 5, 21, 0), datetime(2026, 8, 5, 23, 30), 50, 'Concluído'),
            ('Sessão Sunrise Yoga & Meditação', 'Prática matinal de yoga ao nascer do sol com instrutor certificado.', datetime(2026, 7, 5), datetime(2026, 8, 12, 6, 0), datetime(2026, 8, 12, 7, 30), 30, 'Agendado')
        ]
        cur.executemany(
            """INSERT INTO public.eventos (nome_evento, descricao, data_criacao, inicio_evento, fim_evento, capacidade, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            eventos_data
        )

        print("4. Inserindo Fornecedores...")
        fornecedores_data = [
            ('12345678000195', 'Distribuidora Atlântica Alimentos Ltda', '(83) 3244-1000', 'contato@atlanticaalimentos.com.br', 'Distrito Industrial, Lote 45 - João Pessoa/PB'),
            ('98765432000188', 'Bebidas Tropicais Nordeste S/A', '(81) 3456-7890', 'vendas@bebidastropicais.com.br', 'Av. Recife, 3000 - Recife/PE'),
            ('45678912000133', 'Têxtil & Enxovais Resort Prime', '(11) 4004-5544', 'comercial@enxovaisprime.com.br', 'Rua da Mooca, 1500 - São Paulo/SP'),
            ('78912345000122', 'Higiene & Amenity Soluções Hotelaria', '(21) 2500-1122', 'pedidos@amenitysolucoes.com.br', 'Av. Brasil, 18000 - Rio de Janeiro/RJ'),
            ('32165498000177', 'Frutos do Mar & Peixaria Beira-Mar', '(83) 3247-9988', 'atendimento@peixariabeiramar.com.br', 'Mercado de Peixes, Box 12 - Cabedelo/PB')
        ]
        cur.executemany(
            """INSERT INTO public.fornecedor (cnpj, nome, telefone, email, endereco) 
               VALUES (%s, %s, %s, %s, %s)""",
            fornecedores_data
        )

        print("5. Inserindo Produtos no Estoque...")
        produtos_data = [
            ('Água Mineral 500ml sem Gás', 'Bebidas', 250, 50, 1.20, 5.00, 500, 100, 2),
            ('Cerveja Artesanal Paraíso 500ml', 'Bebidas', 120, 30, 4.50, 18.00, 300, 60, 3),
            ('Vinho Sauvignon Blanc 750ml', 'Bebidas', 45, 15, 28.00, 95.00, 100, 25, 5),
            ('Kit Amenities Luxo (Shampoo/Sabonete)', 'Higiene', 180, 40, 3.80, 0.00, 400, 80, 4),
            ('Toalha de Banho Algodão Egípcio 500g', 'Enxoval', 90, 20, 45.00, 0.00, 150, 35, 7),
            ('Jogo de Lençol Percal 300 Fios Casal', 'Enxoval', 40, 10, 120.00, 0.00, 80, 20, 10),
            ('Camarão Rosa GG (kg)', 'Alimentos', 35, 10, 65.00, 0.00, 60, 15, 2),
            ('Filé Mignon Bovino (kg)', 'Alimentos', 28, 8, 52.00, 0.00, 50, 12, 2),
            ('Café Gourmet Torrado 1kg', 'Alimentos', 25, 5, 38.00, 0.00, 50, 10, 3),
            ('Suco Natural Premium Laranja 1L', 'Bebidas', 60, 15, 6.50, 16.00, 120, 30, 1)
        ]
        cur.executemany(
            """INSERT INTO public.produto (nome, categoria, quantidade, estoque_minimo, valor_unitario, preco_venda, estoque_maximo, ponto_reposicao, lead_time) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            produtos_data
        )

        print("6. Inserindo Reservas...")
        reservas_data = [
            ('11122233301', date(2026, 7, 20), date(2026, 8, 1), date(2026, 8, 6), 'Check-out', 1250.00, date(2026, 8, 1), date(2026, 8, 6), 'Atendente Carlos', 'Recepcionista Ana'),
            ('22233344402', date(2026, 7, 25), date(2026, 8, 5), date(2026, 8, 12), 'Check-in', 1750.00, date(2026, 8, 5), None, 'Recepcionista Ana', None),
            ('33344455503', date(2026, 8, 1), date(2026, 8, 6), date(2026, 8, 13), 'Check-in', 3360.00, date(2026, 8, 6), None, 'Atendente Carlos', None),
            ('44455566604', date(2026, 8, 3), date(2026, 8, 8), date(2026, 8, 15), 'Check-in', 5250.00, date(2026, 8, 8), None, 'Recepcionista Ana', None),
            ('55566677705', date(2026, 8, 5), date(2026, 8, 18), date(2026, 8, 22), 'Confirmada', 1920.00, None, None, None, None),
            ('66677788806', date(2026, 8, 7), date(2026, 8, 25), date(2026, 8, 30), 'Confirmada', 3750.00, None, None, None, None),
            ('77788899907', date(2026, 8, 8), date(2026, 9, 1), date(2026, 9, 7), 'Confirmada', 9000.00, None, None, None, None),
            ('88899900008', date(2026, 7, 10), date(2026, 7, 28), date(2026, 8, 2), 'Cancelada', 1440.00, None, None, None, None)
        ]
        cur.executemany(
            """INSERT INTO public.reservas (cpf_hospede, data_reserva, checkin_previsto, checkout_previsto, status, valor_total, checkin_realizado, checkout_realizado, checkin_por, checkout_por) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            reservas_data
        )

        print("7. Inserindo Vinculação Reserva-Suíte...")
        cur.execute("SELECT id_reserva FROM public.reservas ORDER BY id_reserva ASC;")
        res_ids = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT id_suite, numero, valor_diaria FROM public.suites ORDER BY id_suite ASC;")
        suites_dict = {s[1]: (s[0], s[2]) for s in cur.fetchall()} # numero -> (id, diaria)

        reserva_suite_data = [
            (res_ids[0], suites_dict[101][0], date(2026, 8, 1), date(2026, 8, 6), suites_dict[101][1]), # Res 1: Suite 101
            (res_ids[1], suites_dict[102][0], date(2026, 8, 5), date(2026, 8, 12), suites_dict[102][1]), # Res 2: Suite 102
            (res_ids[2], suites_dict[201][0], date(2026, 8, 6), date(2026, 8, 13), suites_dict[201][1]), # Res 3: Suite 201
            (res_ids[3], suites_dict[302][0], date(2026, 8, 8), date(2026, 8, 15), suites_dict[302][1]), # Res 4: Suite 302
            (res_ids[4], suites_dict[202][0], date(2026, 8, 18), date(2026, 8, 22), suites_dict[202][1]), # Res 5: Suite 202
            (res_ids[5], suites_dict[301][0], date(2026, 8, 25), date(2026, 8, 30), suites_dict[301][1]), # Res 6: Suite 301
            (res_ids[6], suites_dict[401][0], date(2026, 9, 1), date(2026, 9, 7), suites_dict[401][1]), # Res 7: Suite 401
            (res_ids[7], suites_dict[201][0], date(2026, 7, 28), date(2026, 8, 2), suites_dict[201][1])  # Res 8: Suite 201
        ]
        cur.executemany(
            """INSERT INTO public.reserva_suite (id_reserva, id_suite, data_entrada, data_saida, valor_diaria) 
               VALUES (%s, %s, %s, %s, %s)""",
            reserva_suite_data
        )

        print("8. Inserindo Inscrições Hóspede-Evento...")
        cur.execute("SELECT id FROM public.eventos ORDER BY id ASC;")
        evt_ids = [e[0] for e in cur.fetchall()]

        hospede_evento_data = [
            ('11122233301', evt_ids[0], datetime(2026, 7, 22, 14, 0)),
            ('22233344402', evt_ids[0], datetime(2026, 7, 26, 11, 30)),
            ('33344455503', evt_ids[0], datetime(2026, 8, 2, 9, 15)),
            ('44455566604', evt_ids[1], datetime(2026, 8, 4, 16, 20)),
            ('55566677705', evt_ids[1], datetime(2026, 8, 6, 10, 0)),
            ('66677788806', evt_ids[2], datetime(2026, 8, 8, 13, 45)),
            ('77788899907', evt_ids[3], datetime(2026, 6, 25, 17, 10)),
            ('88899900008', evt_ids[4], datetime(2026, 7, 12, 8, 30))
        ]
        cur.executemany(
            """INSERT INTO public.hospede_evento (cpf_hospede, id_evento, data_inscricao) 
               VALUES (%s, %s, %s)""",
            hospede_evento_data
        )

        print("9. Inserindo Pedidos de Compra...")
        pedidos_data = [
            ('12345678000195', date(2026, 7, 10), 1250.00, 'Concluído'),
            ('98765432000188', date(2026, 7, 18), 1800.00, 'Entregue'),
            ('45678912000133', date(2026, 7, 25), 4500.00, 'Entregue'),
            ('78912345000122', date(2026, 8, 1), 760.00, 'Concluído'),
            ('32165498000177', date(2026, 8, 5), 1950.00, 'Pendente')
        ]
        cur.executemany(
            """INSERT INTO public.pedido_compra (cnpj_fornecedor, data_pedido, valor_total, status) 
               VALUES (%s, %s, %s, %s)""",
            pedidos_data
        )

        print("10. Inserindo Itens dos Pedidos de Compra...")
        cur.execute("SELECT id_pedido FROM public.pedido_compra ORDER BY id_pedido ASC;")
        ped_ids = [p[0] for p in cur.fetchall()]

        cur.execute("SELECT id_produto, nome FROM public.produto ORDER BY id_produto ASC;")
        prod_dict = {p[1]: p[0] for p in cur.fetchall()} # nome -> id_produto

        pedido_itens_data = [
            (ped_ids[0], prod_dict['Camarão Rosa GG (kg)'], 10, 65.00, 650.00),
            (ped_ids[0], prod_dict['Filé Mignon Bovino (kg)'], 10, 52.00, 520.00),
            (ped_ids[0], prod_dict['Café Gourmet Torrado 1kg'], 2, 40.00, 80.00),
            (ped_ids[1], prod_dict['Cerveja Artesanal Paraíso 500ml'], 200, 4.50, 900.00),
            (ped_ids[1], prod_dict['Vinho Sauvignon Blanc 750ml'], 30, 30.00, 900.00),
            (ped_ids[2], prod_dict['Toalha de Banho Algodão Egípcio 500g'], 50, 45.00, 2250.00),
            (ped_ids[2], prod_dict['Jogo de Lençol Percal 300 Fios Casal'], 20, 112.50, 2250.00),
            (ped_ids[3], prod_dict['Kit Amenities Luxo (Shampoo/Sabonete)'], 200, 3.80, 760.00),
            (ped_ids[4], prod_dict['Camarão Rosa GG (kg)'], 20, 65.00, 1300.00),
            (ped_ids[4], prod_dict['Suco Natural Premium Laranja 1L'], 100, 6.50, 650.00)
        ]
        cur.executemany(
            """INSERT INTO public.pedido_item (id_pedido, id_produto, quantidade, valor_unitario, valor_total) 
               VALUES (%s, %s, %s, %s, %s)""",
            pedido_itens_data
        )

        print("Ajustando PostgreSQL Sequences...")
        sequence_mappings = [
            ("eventos", "id", "eventos_id_seq"),
            ("hospede_evento", "id", "hospede_evento_id_seq"),
            ("pedido_compra", "id_pedido", "pedido_compra_id_pedido_seq"),
            ("pedido_item", "id_pedido_item", "pedido_item_id_pedido_item_seq"),
            ("produto", "id_produto", "produto_id_produto_seq"),
            ("reserva_suite", "id", "reserva_suite_id_seq"),
            ("reservas", "id_reserva", "reservas_id_reserva_seq"),
            ("suites", "id_suite", "suites_id_suite_seq")
        ]
        for tbl, pk, seq in sequence_mappings:
            cur.execute(f"SELECT setval('public.{seq}', COALESCE((SELECT MAX({pk}) FROM public.{tbl}), 1));")

        conn.commit()
        print("Povoamento do banco de dados concluído com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"ERRO durante a gravação: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_database()
