-- Massa de dados complementar alinhada aos models SQLAlchemy.
-- Execute depois de schema.sql e dados.sql, se eles forem usados.

BEGIN;

INSERT INTO hospedes (cpf, nome, telefone, email, endereco, data_cadastro) VALUES
('10123456789', 'Ana Beatriz Costa', '81991112233', 'ana.costa@example.com', 'Rua das Piscinas, 120 - Recife/PE', '2026-01-10 09:15:00'),
('10234567890', 'Bruno Henrique Lima', '81992223344', 'bruno.lima@example.com', 'Av. Boa Viagem, 845 - Recife/PE', '2026-01-11 10:20:00'),
('10345678901', 'Carolina Mendes Rocha', '81993334455', 'carolina.rocha@example.com', 'Rua do Sol, 58 - Olinda/PE', '2026-01-12 14:05:00'),
('10456789012', 'Daniel Alves Martins', '81994445566', 'daniel.martins@example.com', 'Rua dos Navegantes, 214 - Jaboatao/PE', '2026-01-13 08:40:00'),
('10567890123', 'Eduarda Ferreira Silva', '81995556677', 'eduarda.silva@example.com', 'Rua do Farol, 31 - Porto de Galinhas/PE', '2026-01-14 16:10:00'),
('10678901234', 'Felipe Augusto Nunes', '81996667788', 'felipe.nunes@example.com', 'Av. Beira-Mar, 402 - Maceio/AL', '2026-01-15 11:30:00'),
('10789012345', 'Gabriela Santos Melo', '81997778899', 'gabriela.melo@example.com', 'Rua do Coral, 77 - Natal/RN', '2026-01-16 13:25:00'),
('10890123456', 'Henrique Oliveira Barros', '81998889900', 'henrique.barros@example.com', 'Rua das Conchas, 190 - Joao Pessoa/PB', '2026-01-17 09:50:00'),
('10901234567', 'Isabela Cristina Dias', '81999990011', 'isabela.dias@example.com', 'Av. Atlantica, 615 - Fortaleza/CE', '2026-01-18 15:45:00'),
('11012345678', 'Joao Pedro Carvalho', '81990001122', 'joao.carvalho@example.com', 'Rua dos Coqueiros, 88 - Recife/PE', '2026-01-19 10:05:00'),
('11123456789', 'Larissa Gomes Freire', '81991113344', 'larissa.freire@example.com', 'Rua da Enseada, 143 - Ipojuca/PE', '2026-01-20 12:15:00'),
('11234567890', 'Marcos Vinicius Araujo', '81992224455', 'marcos.araujo@example.com', 'Av. do Sol, 930 - Recife/PE', '2026-01-21 17:00:00'),
('11345678901', 'Natalia Ribeiro Lopes', '81993335566', 'natalia.lopes@example.com', 'Rua das Gaivotas, 29 - Tamandare/PE', '2026-01-22 08:25:00'),
('11456789012', 'Rafael Monteiro Souza', '81994446677', 'rafael.souza@example.com', 'Rua do Mar, 501 - Salvador/BA', '2026-01-23 14:35:00'),
('11567890123', 'Sofia Almeida Torres', '81995557788', 'sofia.torres@example.com', 'Av. dos Corais, 260 - Recife/PE', '2026-01-24 11:55:00')
ON CONFLICT DO NOTHING;

-- O model Suite possui somente estes seis campos.
INSERT INTO suites (id_suite, numero, tipo, capacidade, valor_diaria, status) VALUES
(101, 101, 'Standard', 2, 320.00, 'Disponível'),
(102, 102, 'Standard', 2, 320.00, 'Disponível'),
(103, 103, 'Standard', 3, 380.00, 'Limpeza'),
(104, 104, 'Luxo', 2, 520.00, 'Disponível'),
(105, 105, 'Luxo', 3, 590.00, 'Disponível'),
(106, 106, 'Luxo', 4, 680.00, 'Manutenção'),
(107, 107, 'Master', 2, 760.00, 'Disponível'),
(108, 108, 'Master', 4, 880.00, 'Disponível'),
(109, 109, 'Master', 5, 980.00, 'Disponível'),
(110, 110, 'Standard', 2, 320.00, 'Disponível'),
(111, 111, 'Luxo', 3, 590.00, 'Disponível'),
(112, 112, 'Master', 4, 880.00, 'Disponível'),
(113, 113, 'Standard', 3, 380.00, 'Disponível'),
(114, 114, 'Luxo', 2, 520.00, 'Disponível'),
(115, 115, 'Master', 5, 980.00, 'Disponível')
ON CONFLICT DO NOTHING;

INSERT INTO eventos (id, nome_evento, descricao, data_criacao, inicio_evento, fim_evento, capacidade, status) VALUES
(101, 'Luau ao Por do Sol', 'Musica ao vivo e culinaria regional na praia', '2026-02-01 09:00:00', '2026-08-26 18:00:00', '2026-08-26 22:00:00', 120, 'Agendado'),
(102, 'Yoga na Praia', 'Aula de yoga para todos os niveis', '2026-02-01 09:10:00', '2026-08-27 07:00:00', '2026-08-27 08:00:00', 35, 'Agendado'),
(103, 'Oficina de Coqueteis', 'Preparo de bebidas tropicais com o bartender', '2026-02-01 09:20:00', '2026-08-27 16:00:00', '2026-08-27 18:00:00', 20, 'Agendado'),
(104, 'Torneio de Beach Tennis', 'Competicao recreativa nas quadras do resort', '2026-02-01 09:30:00', '2026-08-28 09:00:00', '2026-08-28 13:00:00', 32, 'Agendado'),
(105, 'Noite do Forro', 'Banda regional e danca no salao principal', '2026-02-01 09:40:00', '2026-08-28 20:00:00', '2026-08-28 23:30:00', 180, 'Agendado'),
(106, 'Trilha Ecologica', 'Caminhada guiada pela reserva ambiental', '2026-02-01 09:50:00', '2026-08-29 06:30:00', '2026-08-29 10:00:00', 25, 'Agendado'),
(107, 'Aula de Culinaria', 'Receitas nordestinas com o chef residente', '2026-02-01 10:00:00', '2026-08-29 15:00:00', '2026-08-29 17:30:00', 18, 'Agendado'),
(108, 'Cinema ao Ar Livre', 'Sessao de filme para toda a familia', '2026-02-01 10:10:00', '2026-08-30 19:00:00', '2026-08-30 21:30:00', 80, 'Agendado'),
(109, 'Massagem Coletiva', 'Sessao de relaxamento e alongamento', '2026-02-01 10:20:00', '2026-08-31 10:00:00', '2026-08-31 11:30:00', 15, 'Agendado'),
(110, 'Festival Infantil', 'Brincadeiras, oficinas e recreacao infantil', '2026-02-01 10:30:00', '2026-09-01 14:00:00', '2026-09-01 18:00:00', 60, 'Agendado'),
(111, 'Observacao das Estrelas', 'Observacao noturna com guia de astronomia', '2026-02-01 10:40:00', '2026-09-02 20:00:00', '2026-09-02 22:00:00', 30, 'Agendado'),
(112, 'Workshop de Fotografia', 'Tecnicas para fotografar paisagens e natureza', '2026-02-01 10:50:00', '2026-09-03 09:00:00', '2026-09-03 12:00:00', 24, 'Agendado'),
(113, 'Aqua Fitness', 'Exercicios aquaticos na piscina principal', '2026-02-01 11:00:00', '2026-09-03 16:00:00', '2026-09-03 17:00:00', 28, 'Agendado'),
(114, 'Jantar Harmonizado', 'Menu degustacao com vinhos selecionados', '2026-02-01 11:10:00', '2026-09-04 20:00:00', '2026-09-04 23:00:00', 40, 'Agendado'),
(115, 'Cafe com Musica', 'Cafe da manha especial com voz e violao', '2026-02-01 11:20:00', '2026-09-05 08:00:00', '2026-09-05 10:00:00', 70, 'Agendado')
ON CONFLICT DO NOTHING;

INSERT INTO hospede_evento (id, cpf_hospede, id_evento, data_inscricao) VALUES
(101, '10123456789', 101, '2026-08-20 10:00:00'),
(102, '10234567890', 101, '2026-08-20 10:05:00'),
(103, '10345678901', 102, '2026-08-20 10:10:00'),
(104, '10456789012', 103, '2026-08-20 10:15:00'),
(105, '10567890123', 104, '2026-08-20 10:20:00'),
(106, '10678901234', 105, '2026-08-20 10:25:00'),
(107, '10789012345', 106, '2026-08-20 10:30:00'),
(108, '10890123456', 107, '2026-08-20 10:35:00'),
(109, '10901234567', 108, '2026-08-20 10:40:00'),
(110, '11012345678', 109, '2026-08-20 10:45:00'),
(111, '11123456789', 110, '2026-08-20 10:50:00'),
(112, '11234567890', 111, '2026-08-20 10:55:00'),
(113, '11345678901', 112, '2026-08-20 11:00:00'),
(114, '11456789012', 113, '2026-08-20 11:05:00'),
(115, '11567890123', 114, '2026-08-20 11:10:00'),
(116, '10123456789', 105, '2026-08-20 11:15:00'),
(117, '10345678901', 108, '2026-08-20 11:20:00'),
(118, '10789012345', 111, '2026-08-20 11:25:00')
ON CONFLICT DO NOTHING;

INSERT INTO produto
    (id_produto, nome, categoria, quantidade, estoque_minimo, valor_unitario,
     preco_venda, estoque_maximo, ponto_reposicao, lead_time)
VALUES
(101, 'Agua mineral 500ml', 'Bebidas', 180, 50, 1.20, 4.00, 300, 80, 3),
(102, 'Suco natural de frutas', 'Bebidas', 75, 20, 4.50, 12.00, 120, 35, 2),
(103, 'Toalha de piscina', 'Enxoval', 90, 30, 28.00, 0.00, 150, 45, 7),
(104, 'Kit amenidades banho', 'Higiene', 220, 60, 6.50, 0.00, 350, 100, 5),
(105, 'Protetor solar FPS 50', 'Loja do resort', 42, 15, 32.00, 59.90, 80, 25, 6),
(106, 'Carvao para churrasqueira', 'Alimentos', 28, 10, 18.00, 0.00, 60, 20, 4)
ON CONFLICT DO NOTHING;

SELECT setval('eventos_id_seq', GREATEST((SELECT COALESCE(MAX(id), 1) FROM eventos), 1), true);
SELECT setval('hospede_evento_id_seq', GREATEST((SELECT COALESCE(MAX(id), 1) FROM hospede_evento), 1), true);
SELECT setval('produto_id_produto_seq', GREATEST((SELECT COALESCE(MAX(id_produto), 1) FROM produto), 1), true);
SELECT setval('suites_id_suite_seq', GREATEST((SELECT COALESCE(MAX(id_suite), 1) FROM suites), 1), true);

COMMIT;
