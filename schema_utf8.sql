--
-- PostgreSQL database dump
--

\restrict KGd9srdEOf44QJQS7nH4NPl5L6kcs0gEwuSWvVLURXYHMSwejfx3nwnStuVBbmB

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: eventos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eventos (
    id integer NOT NULL,
    nome_evento character varying(200) NOT NULL,
    descricao character varying(200) NOT NULL,
    data_criacao timestamp without time zone,
    inicio_evento timestamp without time zone,
    fim_evento timestamp without time zone,
    capacidade integer NOT NULL,
    status character varying NOT NULL
);


ALTER TABLE public.eventos OWNER TO postgres;

--
-- Name: eventos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.eventos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eventos_id_seq OWNER TO postgres;

--
-- Name: eventos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.eventos_id_seq OWNED BY public.eventos.id;


--
-- Name: fornecedor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fornecedor (
    cnpj character varying(14) NOT NULL,
    nome character varying(100) NOT NULL,
    telefone character varying(15) NOT NULL,
    email character varying(100) NOT NULL,
    endereco character varying(200) NOT NULL
);


ALTER TABLE public.fornecedor OWNER TO postgres;

--
-- Name: hospede_evento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hospede_evento (
    id integer NOT NULL,
    cpf_hospede character varying(11) NOT NULL,
    id_evento integer NOT NULL,
    data_inscricao timestamp without time zone NOT NULL
);


ALTER TABLE public.hospede_evento OWNER TO postgres;

--
-- Name: hospede_evento_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.hospede_evento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hospede_evento_id_seq OWNER TO postgres;

--
-- Name: hospede_evento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.hospede_evento_id_seq OWNED BY public.hospede_evento.id;


--
-- Name: hospedes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.hospedes (
    cpf character varying(11) NOT NULL,
    nome character varying(100) NOT NULL,
    telefone character varying(15) NOT NULL,
    email character varying(100) NOT NULL,
    endereco character varying(200) NOT NULL,
    data_cadastro timestamp without time zone NOT NULL
);


ALTER TABLE public.hospedes OWNER TO postgres;

--
-- Name: pedido_compra; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedido_compra (
    id_pedido integer NOT NULL,
    cnpj_fornecedor character varying(14) NOT NULL,
    data_pedido date NOT NULL,
    valor_total double precision NOT NULL,
    status character varying(20) NOT NULL
);


ALTER TABLE public.pedido_compra OWNER TO postgres;

--
-- Name: pedido_compra_id_pedido_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pedido_compra_id_pedido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedido_compra_id_pedido_seq OWNER TO postgres;

--
-- Name: pedido_compra_id_pedido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pedido_compra_id_pedido_seq OWNED BY public.pedido_compra.id_pedido;


--
-- Name: pedido_item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedido_item (
    id_pedido_item integer NOT NULL,
    id_pedido integer NOT NULL,
    id_produto integer NOT NULL,
    quantidade integer NOT NULL,
    valor_unitario double precision NOT NULL,
    valor_total double precision NOT NULL
);


ALTER TABLE public.pedido_item OWNER TO postgres;

--
-- Name: pedido_item_id_pedido_item_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pedido_item_id_pedido_item_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedido_item_id_pedido_item_seq OWNER TO postgres;

--
-- Name: pedido_item_id_pedido_item_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pedido_item_id_pedido_item_seq OWNED BY public.pedido_item.id_pedido_item;


--
-- Name: produto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.produto (
    id_produto integer NOT NULL,
    nome character varying(100) NOT NULL,
    categoria character varying(100) NOT NULL,
    quantidade integer NOT NULL,
    estoque_minimo integer NOT NULL,
    valor_unitario double precision NOT NULL,
    preco_venda double precision NOT NULL,
    estoque_maximo integer NOT NULL,
    ponto_reposicao integer NOT NULL,
    lead_time integer NOT NULL
);


ALTER TABLE public.produto OWNER TO postgres;

--
-- Name: produto_id_produto_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.produto_id_produto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.produto_id_produto_seq OWNER TO postgres;

--
-- Name: produto_id_produto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.produto_id_produto_seq OWNED BY public.produto.id_produto;


--
-- Name: reserva_suite; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reserva_suite (
    id integer NOT NULL,
    id_reserva integer NOT NULL,
    id_suite integer NOT NULL,
    data_entrada date NOT NULL,
    data_saida date,
    valor_diaria double precision NOT NULL
);


ALTER TABLE public.reserva_suite OWNER TO postgres;

--
-- Name: reserva_suite_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reserva_suite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reserva_suite_id_seq OWNER TO postgres;

--
-- Name: reserva_suite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reserva_suite_id_seq OWNED BY public.reserva_suite.id;


--
-- Name: reservas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reservas (
    id_reserva integer NOT NULL,
    cpf_hospede character varying(11) NOT NULL,
    data_reserva date NOT NULL,
    checkin_previsto date,
    checkout_previsto date,
    status character varying(20) NOT NULL,
    valor_total double precision,
    checkin_realizado date,
    checkout_realizado date,
    checkin_por character varying(120),
    checkout_por character varying(120)
);


ALTER TABLE public.reservas OWNER TO postgres;

--
-- Name: reservas_id_reserva_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reservas_id_reserva_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reservas_id_reserva_seq OWNER TO postgres;

--
-- Name: reservas_id_reserva_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reservas_id_reserva_seq OWNED BY public.reservas.id_reserva;


--
-- Name: suites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.suites (
    id_suite integer NOT NULL,
    numero integer NOT NULL,
    tipo character varying NOT NULL,
    capacidade integer NOT NULL,
    valor_diaria double precision NOT NULL,
    status character varying NOT NULL,
    ultima_limpeza timestamp without time zone
);


ALTER TABLE public.suites OWNER TO postgres;

--
-- Name: suites_id_suite_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.suites_id_suite_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suites_id_suite_seq OWNER TO postgres;

--
-- Name: suites_id_suite_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.suites_id_suite_seq OWNED BY public.suites.id_suite;


--
-- Name: eventos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos ALTER COLUMN id SET DEFAULT nextval('public.eventos_id_seq'::regclass);


--
-- Name: hospede_evento id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospede_evento ALTER COLUMN id SET DEFAULT nextval('public.hospede_evento_id_seq'::regclass);


--
-- Name: pedido_compra id_pedido; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_compra ALTER COLUMN id_pedido SET DEFAULT nextval('public.pedido_compra_id_pedido_seq'::regclass);


--
-- Name: pedido_item id_pedido_item; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_item ALTER COLUMN id_pedido_item SET DEFAULT nextval('public.pedido_item_id_pedido_item_seq'::regclass);


--
-- Name: produto id_produto; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produto ALTER COLUMN id_produto SET DEFAULT nextval('public.produto_id_produto_seq'::regclass);


--
-- Name: reserva_suite id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_suite ALTER COLUMN id SET DEFAULT nextval('public.reserva_suite_id_seq'::regclass);


--
-- Name: reservas id_reserva; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas ALTER COLUMN id_reserva SET DEFAULT nextval('public.reservas_id_reserva_seq'::regclass);


--
-- Name: suites id_suite; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suites ALTER COLUMN id_suite SET DEFAULT nextval('public.suites_id_suite_seq'::regclass);


--
-- Name: eventos eventos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eventos
    ADD CONSTRAINT eventos_pkey PRIMARY KEY (id);


--
-- Name: fornecedor fornecedor_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fornecedor
    ADD CONSTRAINT fornecedor_email_key UNIQUE (email);


--
-- Name: fornecedor fornecedor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fornecedor
    ADD CONSTRAINT fornecedor_pkey PRIMARY KEY (cnpj);


--
-- Name: hospede_evento hospede_evento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospede_evento
    ADD CONSTRAINT hospede_evento_pkey PRIMARY KEY (id);


--
-- Name: hospedes hospedes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospedes
    ADD CONSTRAINT hospedes_email_key UNIQUE (email);


--
-- Name: hospedes hospedes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospedes
    ADD CONSTRAINT hospedes_pkey PRIMARY KEY (cpf);


--
-- Name: pedido_compra pedido_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_compra
    ADD CONSTRAINT pedido_compra_pkey PRIMARY KEY (id_pedido);


--
-- Name: pedido_item pedido_item_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_item
    ADD CONSTRAINT pedido_item_pkey PRIMARY KEY (id_pedido_item);


--
-- Name: produto produto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produto
    ADD CONSTRAINT produto_pkey PRIMARY KEY (id_produto);


--
-- Name: reserva_suite reserva_suite_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_suite
    ADD CONSTRAINT reserva_suite_pkey PRIMARY KEY (id);


--
-- Name: reservas reservas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_pkey PRIMARY KEY (id_reserva);


--
-- Name: suites suites_numero_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suites
    ADD CONSTRAINT suites_numero_key UNIQUE (numero);


--
-- Name: suites suites_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.suites
    ADD CONSTRAINT suites_pkey PRIMARY KEY (id_suite);


--
-- Name: hospede_evento hospede_evento_cpf_hospede_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospede_evento
    ADD CONSTRAINT hospede_evento_cpf_hospede_fkey FOREIGN KEY (cpf_hospede) REFERENCES public.hospedes(cpf);


--
-- Name: hospede_evento hospede_evento_id_evento_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.hospede_evento
    ADD CONSTRAINT hospede_evento_id_evento_fkey FOREIGN KEY (id_evento) REFERENCES public.eventos(id);


--
-- Name: pedido_compra pedido_compra_cnpj_fornecedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_compra
    ADD CONSTRAINT pedido_compra_cnpj_fornecedor_fkey FOREIGN KEY (cnpj_fornecedor) REFERENCES public.fornecedor(cnpj);


--
-- Name: pedido_item pedido_item_id_pedido_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_item
    ADD CONSTRAINT pedido_item_id_pedido_fkey FOREIGN KEY (id_pedido) REFERENCES public.pedido_compra(id_pedido);


--
-- Name: pedido_item pedido_item_id_produto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedido_item
    ADD CONSTRAINT pedido_item_id_produto_fkey FOREIGN KEY (id_produto) REFERENCES public.produto(id_produto);


--
-- Name: reserva_suite reserva_suite_id_reserva_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_suite
    ADD CONSTRAINT reserva_suite_id_reserva_fkey FOREIGN KEY (id_reserva) REFERENCES public.reservas(id_reserva);


--
-- Name: reserva_suite reserva_suite_id_suite_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reserva_suite
    ADD CONSTRAINT reserva_suite_id_suite_fkey FOREIGN KEY (id_suite) REFERENCES public.suites(id_suite);


--
-- Name: reservas reservas_cpf_hospede_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reservas
    ADD CONSTRAINT reservas_cpf_hospede_fkey FOREIGN KEY (cpf_hospede) REFERENCES public.hospedes(cpf);


--
-- PostgreSQL database dump complete
--

\unrestrict KGd9srdEOf44QJQS7nH4NPl5L6kcs0gEwuSWvVLURXYHMSwejfx3nwnStuVBbmB

