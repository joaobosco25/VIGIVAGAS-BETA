--
-- PostgreSQL database dump
--

\restrict SpbUo5X84b74xCK38khrRsQGCfxlr7wH3QFn39aF53uRMNcKBTyP3Kkce4knWQP

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

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
-- Name: administradores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.administradores (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    nome_exibicao text
);


ALTER TABLE public.administradores OWNER TO postgres;

--
-- Name: administradores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.administradores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.administradores_id_seq OWNER TO postgres;

--
-- Name: administradores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.administradores_id_seq OWNED BY public.administradores.id;


--
-- Name: candidatos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidatos (
    id integer NOT NULL,
    nome text NOT NULL,
    cpf text NOT NULL,
    telefone text NOT NULL,
    email text NOT NULL,
    cidade text NOT NULL,
    endereco text,
    cep text,
    curso text NOT NULL,
    reciclagem text,
    area text,
    mensagem text,
    ip_cadastro text,
    user_agent text,
    antifraude_score integer DEFAULT 0 NOT NULL,
    antifraude_flags text,
    antifraude_status text DEFAULT 'normal'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estado text
);


ALTER TABLE public.candidatos OWNER TO postgres;

--
-- Name: candidatos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidatos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidatos_id_seq OWNER TO postgres;

--
-- Name: candidatos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidatos_id_seq OWNED BY public.candidatos.id;


--
-- Name: candidaturas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidaturas (
    id integer NOT NULL,
    vigilante_id integer NOT NULL,
    vaga_id integer NOT NULL,
    status text DEFAULT 'Recebida'::text NOT NULL,
    observacoes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.candidaturas OWNER TO postgres;

--
-- Name: candidaturas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidaturas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidaturas_id_seq OWNER TO postgres;

--
-- Name: candidaturas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidaturas_id_seq OWNED BY public.candidaturas.id;


--
-- Name: mauricio_usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mauricio_usuarios (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    nome_exibicao text,
    ativo integer DEFAULT 1 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.mauricio_usuarios OWNER TO postgres;

--
-- Name: mauricio_usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mauricio_usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mauricio_usuarios_id_seq OWNER TO postgres;

--
-- Name: mauricio_usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mauricio_usuarios_id_seq OWNED BY public.mauricio_usuarios.id;


--
-- Name: recrutadores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recrutadores (
    id integer NOT NULL,
    nome_empresa text,
    nome_responsavel text NOT NULL,
    email text NOT NULL,
    telefone text,
    cnpj text,
    razao_social text,
    situacao_cadastral text,
    site_empresa text,
    descricao_empresa text,
    cnpj_modo_validacao text DEFAULT 'online'::text NOT NULL,
    email_verificado integer DEFAULT 0 NOT NULL,
    email_token text,
    email_token_expires_at text,
    email_ultimo_envio_em text,
    ip_cadastro text,
    user_agent text,
    antifraude_score integer DEFAULT 0 NOT NULL,
    antifraude_flags text,
    antifraude_status text DEFAULT 'normal'::text NOT NULL,
    password text NOT NULL,
    status text DEFAULT 'pendente'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    cidade text,
    estado text
);


ALTER TABLE public.recrutadores OWNER TO postgres;

--
-- Name: recrutadores_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recrutadores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recrutadores_id_seq OWNER TO postgres;

--
-- Name: recrutadores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recrutadores_id_seq OWNED BY public.recrutadores.id;


--
-- Name: vagas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vagas (
    id integer NOT NULL,
    titulo text NOT NULL,
    empresa text NOT NULL,
    cidade text NOT NULL,
    estado text NOT NULL,
    escala text,
    salario text,
    descricao text NOT NULL,
    requisitos text,
    contato text,
    link_candidatura text,
    recrutador_id integer,
    status text DEFAULT 'ativa'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.vagas OWNER TO postgres;

--
-- Name: vagas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vagas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vagas_id_seq OWNER TO postgres;

--
-- Name: vagas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vagas_id_seq OWNED BY public.vagas.id;


--
-- Name: vigilantes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vigilantes (
    id integer NOT NULL,
    nome text NOT NULL,
    cpf text NOT NULL,
    telefone text NOT NULL,
    email text NOT NULL,
    cidade text NOT NULL,
    endereco text,
    cep text,
    curso text,
    reciclagem text,
    area_interesse text,
    resumo_profissional text,
    objetivo_cargo text,
    escolaridade text,
    possui_cfv text,
    instituicao_formacao text,
    ext_ctv text,
    ext_cea text,
    ext_csp text,
    ext_cnl1 text,
    ext_ces text,
    data_ultima_reciclagem text,
    curso_ultima_reciclagem text,
    ultima_experiencia_profissional text,
    ip_cadastro text,
    user_agent text,
    antifraude_score integer DEFAULT 0 NOT NULL,
    antifraude_flags text,
    antifraude_status text DEFAULT 'normal'::text NOT NULL,
    password text NOT NULL,
    status text DEFAULT 'ativo'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estado text
);


ALTER TABLE public.vigilantes OWNER TO postgres;

--
-- Name: vigilantes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vigilantes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vigilantes_id_seq OWNER TO postgres;

--
-- Name: vigilantes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vigilantes_id_seq OWNED BY public.vigilantes.id;


--
-- Name: administradores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.administradores ALTER COLUMN id SET DEFAULT nextval('public.administradores_id_seq'::regclass);


--
-- Name: candidatos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos ALTER COLUMN id SET DEFAULT nextval('public.candidatos_id_seq'::regclass);


--
-- Name: candidaturas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidaturas ALTER COLUMN id SET DEFAULT nextval('public.candidaturas_id_seq'::regclass);


--
-- Name: mauricio_usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mauricio_usuarios ALTER COLUMN id SET DEFAULT nextval('public.mauricio_usuarios_id_seq'::regclass);


--
-- Name: recrutadores id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recrutadores ALTER COLUMN id SET DEFAULT nextval('public.recrutadores_id_seq'::regclass);


--
-- Name: vagas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vagas ALTER COLUMN id SET DEFAULT nextval('public.vagas_id_seq'::regclass);


--
-- Name: vigilantes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vigilantes ALTER COLUMN id SET DEFAULT nextval('public.vigilantes_id_seq'::regclass);


--
-- Data for Name: administradores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.administradores (id, username, password, nome_exibicao) FROM stdin;
\.


--
-- Data for Name: candidatos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidatos (id, nome, cpf, telefone, email, cidade, endereco, cep, curso, reciclagem, area, mensagem, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status, created_at, estado) FROM stdin;
\.


--
-- Data for Name: candidaturas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidaturas (id, vigilante_id, vaga_id, status, observacoes, created_at, updated_at) FROM stdin;
1	1	1	Aprovado		2026-04-22 21:53:19.122588	2026-04-22 21:59:30.010782
2	1	2	Entrevista		2026-04-22 21:53:22.287277	2026-04-22 22:00:45.963883
4	2	2	Recebida	\N	2026-04-22 22:05:14.538246	2026-04-22 22:05:14.538246
3	2	1	Entrevista		2026-04-22 22:05:11.372154	2026-04-23 15:52:46.185178
\.


--
-- Data for Name: mauricio_usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mauricio_usuarios (id, username, password, nome_exibicao, ativo, created_at) FROM stdin;
1	mauricio	scrypt:32768:8:1$JA5c9Fn4yywc4AL6$624bfed8fafb2b62972d64359228aed1c480dc58b3f9d367b5585cafbf49c09aea076cac9755d24de18b54d514981150a958b79168bd5b62b6f93adfe9810da4	Maurício	1	2026-04-22 15:22:29.127139
2	painel_mauricio	scrypt:32768:8:1$hq5SawUbKjqio9On$a7ea743e8f1087c1edebff315dc42bca153daef223ec262500f62b338f6bb50dcf6d119ba98fd8fd487e10e9665b920a5004ed56823a0032df965f1e1c8a2b87	Maurício	1	2026-04-22 21:32:23.377178
\.


--
-- Data for Name: recrutadores; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recrutadores (id, nome_empresa, nome_responsavel, email, telefone, cnpj, razao_social, situacao_cadastral, site_empresa, descricao_empresa, cnpj_modo_validacao, email_verificado, email_token, email_token_expires_at, email_ultimo_envio_em, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status, password, status, created_at, cidade, estado) FROM stdin;
3	MORTY BUSINESS	MORTY SMITH	mortyciencia@hotmail.com	(34) 98857-7832	18.236.120/0001-58	VALIDACAO PENDENTE	VALIDACAO PENDENTE	\N	\N	fallback_local	0	FGCykHJprt1RSfWbDUVgFEt6NHhmxEvscxRZUSlSjuk	2026-04-27T20:09:28.391876	2026-04-26T20:09:28.391890	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2	email_generico, ip_reincidente	suspeito	scrypt:32768:8:1$ywTqxqNjUxamv7RX$b16ec165950c45c58cbcdd9af7a1ee5b33fed485f9c3359a762a03cf0c39355ccf48650c02d9e25ab1e0fcd1a0aeb0cc8dc917246849fd188baf13a33c2957ce	pendente	2026-04-26 17:09:28.285531	UBERLÂNDIA	MG
1	RODRIGO STUDIO	RODRIGO FERREIRA	aguiafenix@hotmail.com	(32) 99942-2365	06.981.176/0003-10	VALIDACAO PENDENTE	VALIDACAO PENDENTE	\N	\N	fallback_local	1	\N	\N	2026-04-23T00:48:20.397004	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	1	email_generico	normal	scrypt:32768:8:1$J0E8HC5snshWVhNV$4565d22f4d905e31804390b3703e18c6ffd724b637cb9e1fe18acaeb2f1652e900d26700841fddb9c309dc327893d0bd3c60e04f787f83945ee60fa4485d7921	verificado	2026-04-22 21:48:20.291907	UBERLÂNDIA	MG
2	AUTÔNOMO	MARCOS MANOEL	marcos.manoel@hotmail.com	(34) 99557-7834	60.746.948/0001-12	VALIDACAO PENDENTE	VALIDACAO PENDENTE	\N	\N	fallback_local	1	\N	\N	2026-04-23T00:51:26.489632	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2	email_generico, ip_reincidente	normal	scrypt:32768:8:1$fT3qShnowfumhMxw$218ef6e495cff31130351f4fa0bc94d1374ab194c2668dff8259976c310d0b8861c27551aba85671c36eb45010c0d1c03f64b11cb0f65e242a048c9fed873d33	validado	2026-04-22 21:51:26.385695	UBERLÂNDIA	MG
\.


--
-- Data for Name: vagas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vagas (id, titulo, empresa, cidade, estado, escala, salario, descricao, requisitos, contato, link_candidatura, recrutador_id, status, created_at) FROM stdin;
2	NINJA	AUTÔNOMO	UBERLÂNDIA	MG	12X36	3.000 + BENEFICIOS	ERER	RECICLAGEM EM DIA	34999667786	\N	2	ativa	2026-04-22 21:52:51.771031
1	MARCO POLO	RODRIGO STUDIO	UBERLÂNDIA	MG	12X36	3.000 + BENEFICIOS	CABELO E BIGODA	RECICLAGEM EM DIA	34999667787	\N	1	ativa	2026-04-22 21:49:30.296808
\.


--
-- Data for Name: vigilantes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vigilantes (id, nome, cpf, telefone, email, cidade, endereco, cep, curso, reciclagem, area_interesse, resumo_profissional, objetivo_cargo, escolaridade, possui_cfv, instituicao_formacao, ext_ctv, ext_cea, ext_csp, ext_cnl1, ext_ces, data_ultima_reciclagem, curso_ultima_reciclagem, ultima_experiencia_profissional, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status, password, status, created_at, estado) FROM stdin;
1	JOÃO BOSCO FERREIRA	140.741.086-58	(32) 98456-0451	bosko.dev@hotmail.com	UBERLÂNDIA	RUA VITAL JOSÉ CARRIJO	38400-078	CFV - EFASEG	2000-05-24 - FORMACAO DE VIGILANTES			VIGILANTE	ENSINO SUPERIOR COMPLETO	SIM	EFASEG	NAO	NAO	NAO	NAO	NAO	2000-05-24	FORMACAO DE VIGILANTES	FED	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	0		normal	scrypt:32768:8:1$2AKzOrDev8Y1hDrL$150beefb24a038b82ca8034b123310bb2a3e9f76baa4d91847e20fc785ec9076e62a65cd83eab9f377bf2222de6abb92d645be1e3ac90d812a68d5556703f7b5	ativo	2026-04-22 21:39:47.783738	MG
2	LULA DA SILVA	685.660.188-34	(32) 98557-7332	luizinacio@hotmail.com	UBERLÂNDIA	RUA VITAL JOSÉ CARRIJO	38400-078	CFV - EPROC	2025-04-23 - SEGURANCA PESSOAL PRIVADA			VIGILANTE	ENSINO MEDIO COMPLETO	SIM	EPROC	NAO	NAO	SIM	NAO	NAO	2025-04-23	SEGURANCA PESSOAL PRIVADA	EFEFEFE	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	1	ip_reincidente	normal	scrypt:32768:8:1$UdtFwrw5JD6wLmY5$bd9da00dce4306c57fa73f04b714d5222fd8d9cb70a59f0ab591320334f2a4af512c38473ac08d0977c2fc81dda33b8f9530be5acd4045a3577cc301c648c8d3	ativo	2026-04-22 22:05:01.777475	MG
\.


--
-- Name: administradores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.administradores_id_seq', 1, false);


--
-- Name: candidatos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidatos_id_seq', 1, false);


--
-- Name: candidaturas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidaturas_id_seq', 4, true);


--
-- Name: mauricio_usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mauricio_usuarios_id_seq', 2, true);


--
-- Name: recrutadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recrutadores_id_seq', 3, true);


--
-- Name: vagas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vagas_id_seq', 2, true);


--
-- Name: vigilantes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vigilantes_id_seq', 2, true);


--
-- Name: administradores administradores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.administradores
    ADD CONSTRAINT administradores_pkey PRIMARY KEY (id);


--
-- Name: administradores administradores_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.administradores
    ADD CONSTRAINT administradores_username_key UNIQUE (username);


--
-- Name: candidatos candidatos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_pkey PRIMARY KEY (id);


--
-- Name: candidaturas candidaturas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_pkey PRIMARY KEY (id);


--
-- Name: candidaturas candidaturas_vigilante_id_vaga_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_vigilante_id_vaga_id_key UNIQUE (vigilante_id, vaga_id);


--
-- Name: mauricio_usuarios mauricio_usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mauricio_usuarios
    ADD CONSTRAINT mauricio_usuarios_pkey PRIMARY KEY (id);


--
-- Name: mauricio_usuarios mauricio_usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mauricio_usuarios
    ADD CONSTRAINT mauricio_usuarios_username_key UNIQUE (username);


--
-- Name: recrutadores recrutadores_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recrutadores
    ADD CONSTRAINT recrutadores_email_key UNIQUE (email);


--
-- Name: recrutadores recrutadores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recrutadores
    ADD CONSTRAINT recrutadores_pkey PRIMARY KEY (id);


--
-- Name: vagas vagas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vagas
    ADD CONSTRAINT vagas_pkey PRIMARY KEY (id);


--
-- Name: vigilantes vigilantes_cpf_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vigilantes
    ADD CONSTRAINT vigilantes_cpf_key UNIQUE (cpf);


--
-- Name: vigilantes vigilantes_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vigilantes
    ADD CONSTRAINT vigilantes_email_key UNIQUE (email);


--
-- Name: vigilantes vigilantes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vigilantes
    ADD CONSTRAINT vigilantes_pkey PRIMARY KEY (id);


--
-- Name: idx_candidatos_cidade; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candidatos_cidade ON public.candidatos USING btree (cidade);


--
-- Name: idx_candidaturas_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candidaturas_status ON public.candidaturas USING btree (status);


--
-- Name: idx_candidaturas_vaga_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candidaturas_vaga_id ON public.candidaturas USING btree (vaga_id);


--
-- Name: idx_candidaturas_vigilante_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_candidaturas_vigilante_id ON public.candidaturas USING btree (vigilante_id);


--
-- Name: idx_recrutadores_antifraude_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recrutadores_antifraude_status ON public.recrutadores USING btree (antifraude_status);


--
-- Name: idx_recrutadores_nome_empresa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recrutadores_nome_empresa ON public.recrutadores USING btree (nome_empresa);


--
-- Name: idx_recrutadores_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recrutadores_status ON public.recrutadores USING btree (status);


--
-- Name: idx_vagas_cidade; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vagas_cidade ON public.vagas USING btree (cidade);


--
-- Name: idx_vagas_recrutador_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vagas_recrutador_id ON public.vagas USING btree (recrutador_id);


--
-- Name: idx_vagas_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vagas_status ON public.vagas USING btree (status);


--
-- Name: idx_vigilantes_antifraude_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vigilantes_antifraude_status ON public.vigilantes USING btree (antifraude_status);


--
-- Name: idx_vigilantes_cidade; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vigilantes_cidade ON public.vigilantes USING btree (cidade);


--
-- Name: idx_vigilantes_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vigilantes_created_at ON public.vigilantes USING btree (created_at);


--
-- Name: idx_vigilantes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vigilantes_status ON public.vigilantes USING btree (status);


--
-- Name: candidaturas candidaturas_vaga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_vaga_id_fkey FOREIGN KEY (vaga_id) REFERENCES public.vagas(id);


--
-- Name: candidaturas candidaturas_vigilante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_vigilante_id_fkey FOREIGN KEY (vigilante_id) REFERENCES public.vigilantes(id);


--
-- Name: vagas vagas_recrutador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vagas
    ADD CONSTRAINT vagas_recrutador_id_fkey FOREIGN KEY (recrutador_id) REFERENCES public.recrutadores(id);


--
-- PostgreSQL database dump complete
--

\unrestrict SpbUo5X84b74xCK38khrRsQGCfxlr7wH3QFn39aF53uRMNcKBTyP3Kkce4knWQP

