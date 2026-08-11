--
-- PostgreSQL database dump
--

\restrict 5OGk5R7UugG8D8pCBEbZ3C5SZ4mprG3ZkkR3PIIlgYMp7jOOxinrJnzecsQJHKc

-- Dumped from database version 18.4 (Debian 18.4-1.pgdg13+1)
-- Dumped by pg_dump version 18.4 (Debian 18.4-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: eventos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.eventos (id, nome_evento, descricao, data_criacao, inicio_evento, fim_evento, capacidade, status) FROM stdin;
\.


--
-- Data for Name: fornecedor; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fornecedor (cnpj, nome, telefone, email, endereco) FROM stdin;
\.


--
-- Data for Name: hospedes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hospedes (cpf, nome, telefone, email, endereco, data_cadastro) FROM stdin;
\.


--
-- Data for Name: hospede_evento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.hospede_evento (id, cpf_hospede, id_evento, data_inscricao) FROM stdin;
\.


--
-- Data for Name: pedido_compra; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedido_compra (id_pedido, cnpj_fornecedor, data_pedido, valor_total, status) FROM stdin;
\.


--
-- Data for Name: produto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.produto (id_produto, nome, categoria, quantidade, estoque_minimo, valor_unitario, preco_venda, estoque_maximo, ponto_reposicao, lead_time) FROM stdin;
\.


--
-- Data for Name: pedido_item; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedido_item (id_pedido_item, id_pedido, id_produto, quantidade, valor_unitario, valor_total) FROM stdin;
\.


--
-- Data for Name: reservas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reservas (id_reserva, cpf_hospede, data_reserva, checkin_previsto, checkout_previsto, status, valor_total, checkin_realizado, checkout_realizado, checkin_por, checkout_por) FROM stdin;
\.


--
-- Data for Name: suites; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.suites (id_suite, numero, tipo, capacidade, valor_diaria, status, ultima_limpeza) FROM stdin;
\.


--
-- Data for Name: reserva_suite; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reserva_suite (id, id_reserva, id_suite, data_entrada, data_saida, valor_diaria) FROM stdin;
\.


--
-- Name: eventos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.eventos_id_seq', 1, false);


--
-- Name: hospede_evento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.hospede_evento_id_seq', 1, false);


--
-- Name: pedido_compra_id_pedido_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pedido_compra_id_pedido_seq', 1, false);


--
-- Name: pedido_item_id_pedido_item_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pedido_item_id_pedido_item_seq', 1, false);


--
-- Name: produto_id_produto_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.produto_id_produto_seq', 1, false);


--
-- Name: reserva_suite_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reserva_suite_id_seq', 1, false);


--
-- Name: reservas_id_reserva_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reservas_id_reserva_seq', 1, false);


--
-- Name: suites_id_suite_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.suites_id_suite_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict 5OGk5R7UugG8D8pCBEbZ3C5SZ4mprG3ZkkR3PIIlgYMp7jOOxinrJnzecsQJHKc

