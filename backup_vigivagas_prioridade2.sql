--
-- PostgreSQL database dump
--

\restrict rfRcUDhioy46XLfgHL6Sphd9eE5g3vo26J4ZQLWW25HLf5hSbbNCSNjxDQgaxAr

-- Dumped from database version 18.3 (Debian 18.3-1.pgdg12+1)
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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: vigivagas_db_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO vigivagas_db_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administradores; Type: TABLE; Schema: public; Owner: vigivagas_db_user
--

CREATE TABLE public.administradores (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    nome_exibicao text
);


ALTER TABLE public.administradores OWNER TO vigivagas_db_user;

--
-- Name: administradores_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.administradores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.administradores_id_seq OWNER TO vigivagas_db_user;

--
-- Name: administradores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.administradores_id_seq OWNED BY public.administradores.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: vigivagas_db_user
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    usuario text,
    acao text,
    detalhes text,
    ip text,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    actor_type text,
    actor_id text,
    action text,
    entity_type text,
    entity_id text,
    details text,
    ip_address text,
    user_agent text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.audit_logs OWNER TO vigivagas_db_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO vigivagas_db_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: candidatos; Type: TABLE; Schema: public; Owner: vigivagas_db_user
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


ALTER TABLE public.candidatos OWNER TO vigivagas_db_user;

--
-- Name: candidatos_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.candidatos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidatos_id_seq OWNER TO vigivagas_db_user;

--
-- Name: candidatos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.candidatos_id_seq OWNED BY public.candidatos.id;


--
-- Name: candidaturas; Type: TABLE; Schema: public; Owner: vigivagas_db_user
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


ALTER TABLE public.candidaturas OWNER TO vigivagas_db_user;

--
-- Name: candidaturas_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.candidaturas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidaturas_id_seq OWNER TO vigivagas_db_user;

--
-- Name: candidaturas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.candidaturas_id_seq OWNED BY public.candidaturas.id;


--
-- Name: lgpd_consents; Type: TABLE; Schema: public; Owner: vigivagas_db_user
--

CREATE TABLE public.lgpd_consents (
    id integer NOT NULL,
    usuario_id integer,
    tipo_usuario text,
    ip text,
    user_agent text,
    aceito_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_type text,
    user_id integer,
    email text,
    consent_type text,
    consent_text text,
    ip_address text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    policy_version text,
    consent_given boolean DEFAULT true,
    source text,
    terms_version text DEFAULT '1.0'::text
);


ALTER TABLE public.lgpd_consents OWNER TO vigivagas_db_user;

--
-- Name: lgpd_consents_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.lgpd_consents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lgpd_consents_id_seq OWNER TO vigivagas_db_user;

--
-- Name: lgpd_consents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.lgpd_consents_id_seq OWNED BY public.lgpd_consents.id;


--
-- Name: lgpd_requests; Type: TABLE; Schema: public; Owner: vigivagas_db_user
--

CREATE TABLE public.lgpd_requests (
    id integer NOT NULL,
    user_type text NOT NULL,
    user_id integer,
    email text NOT NULL,
    request_type text NOT NULL,
    status text DEFAULT 'pendente'::text NOT NULL,
    details text,
    ip_address text,
    user_agent text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    resolved_at timestamp without time zone
);


ALTER TABLE public.lgpd_requests OWNER TO vigivagas_db_user;

--
-- Name: lgpd_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.lgpd_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lgpd_requests_id_seq OWNER TO vigivagas_db_user;

--
-- Name: lgpd_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.lgpd_requests_id_seq OWNED BY public.lgpd_requests.id;


--
-- Name: mauricio_usuarios; Type: TABLE; Schema: public; Owner: vigivagas_db_user
--

CREATE TABLE public.mauricio_usuarios (
    id integer NOT NULL,
    username text NOT NULL,
    password text NOT NULL,
    nome_exibicao text,
    ativo integer DEFAULT 1 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.mauricio_usuarios OWNER TO vigivagas_db_user;

--
-- Name: mauricio_usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.mauricio_usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mauricio_usuarios_id_seq OWNER TO vigivagas_db_user;

--
-- Name: mauricio_usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.mauricio_usuarios_id_seq OWNED BY public.mauricio_usuarios.id;


--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: vigivagas_db_user
--

CREATE TABLE public.password_resets (
    id integer NOT NULL,
    email text,
    token text,
    expira_em timestamp without time zone,
    usado boolean DEFAULT false,
    token_hash text,
    criado_em timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    usado_em timestamp without time zone,
    user_type text,
    user_id integer,
    expires_at text,
    used_at text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.password_resets OWNER TO vigivagas_db_user;

--
-- Name: password_resets_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.password_resets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_resets_id_seq OWNER TO vigivagas_db_user;

--
-- Name: password_resets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.password_resets_id_seq OWNED BY public.password_resets.id;


--
-- Name: recrutadores; Type: TABLE; Schema: public; Owner: vigivagas_db_user
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


ALTER TABLE public.recrutadores OWNER TO vigivagas_db_user;

--
-- Name: recrutadores_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.recrutadores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recrutadores_id_seq OWNER TO vigivagas_db_user;

--
-- Name: recrutadores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.recrutadores_id_seq OWNED BY public.recrutadores.id;


--
-- Name: vagas; Type: TABLE; Schema: public; Owner: vigivagas_db_user
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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    encerrada_em timestamp without time zone,
    encerrada_motivo_tipo text,
    encerrada_motivo text,
    vigivagas_ajudou_contratacao text,
    contratacoes_quantidade integer DEFAULT 0,
    encerrada_observacoes text
);


ALTER TABLE public.vagas OWNER TO vigivagas_db_user;

--
-- Name: vagas_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.vagas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vagas_id_seq OWNER TO vigivagas_db_user;

--
-- Name: vagas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.vagas_id_seq OWNED BY public.vagas.id;


--
-- Name: vigilantes; Type: TABLE; Schema: public; Owner: vigivagas_db_user
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


ALTER TABLE public.vigilantes OWNER TO vigivagas_db_user;

--
-- Name: vigilantes_id_seq; Type: SEQUENCE; Schema: public; Owner: vigivagas_db_user
--

CREATE SEQUENCE public.vigilantes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vigilantes_id_seq OWNER TO vigivagas_db_user;

--
-- Name: vigilantes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vigivagas_db_user
--

ALTER SEQUENCE public.vigilantes_id_seq OWNED BY public.vigilantes.id;


--
-- Name: administradores id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.administradores ALTER COLUMN id SET DEFAULT nextval('public.administradores_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: candidatos id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidatos ALTER COLUMN id SET DEFAULT nextval('public.candidatos_id_seq'::regclass);


--
-- Name: candidaturas id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidaturas ALTER COLUMN id SET DEFAULT nextval('public.candidaturas_id_seq'::regclass);


--
-- Name: lgpd_consents id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.lgpd_consents ALTER COLUMN id SET DEFAULT nextval('public.lgpd_consents_id_seq'::regclass);


--
-- Name: lgpd_requests id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.lgpd_requests ALTER COLUMN id SET DEFAULT nextval('public.lgpd_requests_id_seq'::regclass);


--
-- Name: mauricio_usuarios id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.mauricio_usuarios ALTER COLUMN id SET DEFAULT nextval('public.mauricio_usuarios_id_seq'::regclass);


--
-- Name: password_resets id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.password_resets ALTER COLUMN id SET DEFAULT nextval('public.password_resets_id_seq'::regclass);


--
-- Name: recrutadores id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.recrutadores ALTER COLUMN id SET DEFAULT nextval('public.recrutadores_id_seq'::regclass);


--
-- Name: vagas id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vagas ALTER COLUMN id SET DEFAULT nextval('public.vagas_id_seq'::regclass);


--
-- Name: vigilantes id; Type: DEFAULT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vigilantes ALTER COLUMN id SET DEFAULT nextval('public.vigilantes_id_seq'::regclass);


--
-- Data for Name: administradores; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.administradores (id, username, password, nome_exibicao) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.audit_logs (id, usuario, acao, detalhes, ip, criado_em, actor_type, actor_id, action, entity_type, entity_id, details, ip_address, user_agent, created_at) FROM stdin;
1	\N	\N	\N	\N	2026-05-05 13:05:50.29139	mauricio	3	alterou_status_recrutador	recrutador	1	Novo status: validado	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 13:05:50.276982
2	\N	\N	\N	\N	2026-05-05 13:07:31.017544	mauricio	3	alterou_antifraude_recrutador	recrutador	1	Novo antifraude: bloqueado	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 13:07:31.000174
3	\N	\N	\N	\N	2026-05-05 13:08:06.443808	mauricio	3	alterou_status_recrutador	recrutador	2	Novo status: validado	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 13:08:06.429156
4	\N	\N	\N	\N	2026-05-06 16:50:23.977065	mauricio	3	exportou_xlsx	recrutadores		Exportação de recrutadores.xlsx com 2 linhas	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-06 16:50:23.953286
5	\N	\N	\N	\N	2026-05-06 16:50:27.659267	mauricio	3	exportou_xlsx	vigilantes		Exportação de vigilantes.xlsx com 5 linhas	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-06 16:50:27.63826
\.


--
-- Data for Name: candidatos; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.candidatos (id, nome, cpf, telefone, email, cidade, endereco, cep, curso, reciclagem, area, mensagem, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status, created_at, estado) FROM stdin;
\.


--
-- Data for Name: candidaturas; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.candidaturas (id, vigilante_id, vaga_id, status, observacoes, created_at, updated_at) FROM stdin;
2	4	1	Em análise	SUA CANDIDATURA ESTÁ EM ANÁLISE	2026-05-05 13:24:05.39872	2026-05-05 13:26:06.8647
1	5	1	Reprovado	NÃO CONTRATAMOS QUEM BATE EM MULHER	2026-05-05 13:23:30.434066	2026-05-05 13:26:27.339707
3	6	1	Recebida	\N	2026-05-05 17:41:54.597317	2026-05-05 17:41:54.597317
4	7	1	Reprovado	VOCE E FEIO	2026-05-05 18:06:49.006417	2026-05-05 18:08:35.959599
\.


--
-- Data for Name: lgpd_consents; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.lgpd_consents (id, usuario_id, tipo_usuario, ip, user_agent, aceito_em, user_type, user_id, email, consent_type, consent_text, ip_address, created_at, policy_version, consent_given, source, terms_version) FROM stdin;
1	\N	\N	\N	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 13:00:25.518598	vigilante	4	anaisadora@hotmail.com	\N	Aceite da Política de Privacidade e Termos de Uso do VigiVagas.	177.191.116.246	2026-05-05 13:00:25.518598	1.0	t	\N	1.0
2	\N	\N	\N	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 13:22:39.184963	vigilante	5	cicerosilva@hotmail.com	\N	Aceite da Política de Privacidade e Termos de Uso do VigiVagas.	177.191.116.246	2026-05-05 13:22:39.184963	1.0	t	\N	1.0
3	\N	\N	\N	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 17:41:28.300036	vigilante	6	joaolundin@hotmail.com	\N	Aceite da Política de Privacidade e Termos de Uso do VigiVagas.	177.191.116.246	2026-05-05 17:41:28.300036	1.0	t	\N	1.0
4	\N	\N	\N	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-05 18:06:35.785065	vigilante	7	waldinei@gmail.com	\N	Aceite da Política de Privacidade e Termos de Uso do VigiVagas.	177.191.116.246	2026-05-05 18:06:35.785065	1.0	t	\N	1.0
5	\N	\N	\N	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36	2026-05-05 19:39:55.461709	vigilante	8	joaobosco.profissional25@gmail.com	\N	Aceite da Política de Privacidade e Termos de Uso do VigiVagas.	177.191.116.246	2026-05-05 19:39:55.461709	1.0	t	\N	1.0
\.


--
-- Data for Name: lgpd_requests; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.lgpd_requests (id, user_type, user_id, email, request_type, status, details, ip_address, user_agent, created_at, resolved_at) FROM stdin;
1	recrutador	3	joaoboscodev@hotmail.com	exclusao_anonimizacao	concluida	Solicitação feita pela área logada do recrutador; vagas desativadas.	177.191.112.35	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	2026-05-04 20:37:37.058341	\N
\.


--
-- Data for Name: mauricio_usuarios; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.mauricio_usuarios (id, username, password, nome_exibicao, ativo, created_at) FROM stdin;
1	mauricio	scrypt:32768:8:1$JA5c9Fn4yywc4AL6$624bfed8fafb2b62972d64359228aed1c480dc58b3f9d367b5585cafbf49c09aea076cac9755d24de18b54d514981150a958b79168bd5b62b6f93adfe9810da4	Maurício	1	2026-04-22 15:22:29.127139
2	painel_mauricio	scrypt:32768:8:1$hq5SawUbKjqio9On$a7ea743e8f1087c1edebff315dc42bca153daef223ec262500f62b338f6bb50dcf6d119ba98fd8fd487e10e9665b920a5004ed56823a0032df965f1e1c8a2b87	Maurício	1	2026-04-22 21:32:23.377178
3	mauricio_admin	scrypt:32768:8:1$NYIqa0WcYguhpTPd$ddaa3b5717260e6787ef1e4f87036d1375fdeb4e0f915893f23ca0ced2f10d19dbdc89f22eba05d698f1f90f2a0bac5554b8ad7536a040551d3578a0b6ae9d08	Maurício	1	2026-04-28 01:06:21.290536
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.password_resets (id, email, token, expira_em, usado, token_hash, criado_em, usado_em, user_type, user_id, expires_at, used_at, created_at) FROM stdin;
1	\N	\N	\N	f	d4f7c9e21dbfaa2ce245905d692a0c500abaccfae5238fd418955850531498f6	2026-05-04 18:26:53.128045	\N	recrutador	3	2026-05-04T19:26:53.174193	2026-05-04T18:27:55.542504	2026-05-04 18:26:53.128045
2	\N	\N	\N	f	b63253d6aa25a4a3e3535f55510c8122af7344c2bbe49118c17d79a1389a2035	2026-05-04 20:26:01.885706	\N	recrutador	3	2026-05-04T21:26:01.932991	2026-05-04T20:27:13.698001	2026-05-04 20:26:01.885706
3	\N	\N	\N	f	21320769c97e98b9cc094c4dbdfa762f583cbc9cb67c304d8c315eca3c4f02bd	2026-05-04 20:32:07.285927	\N	vigilante	1	2026-05-04T21:32:07.334173	2026-05-04T20:32:48.386953	2026-05-04 20:32:07.285927
\.


--
-- Data for Name: recrutadores; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.recrutadores (id, nome_empresa, nome_responsavel, email, telefone, cnpj, razao_social, situacao_cadastral, site_empresa, descricao_empresa, cnpj_modo_validacao, email_verificado, email_token, email_token_expires_at, email_ultimo_envio_em, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status, password, status, created_at, cidade, estado) FROM stdin;
1	GRAPER	ANDERSON ABADIO	aguiafenix@hotmail.com	(32) 98456-0451	87.169.900/0001-45	VALIDACAO PENDENTE	VALIDACAO PENDENTE	\N	\N	fallback_local	0	20422	2026-05-05T13:18:03.651279	2026-05-05T13:03:03.651303	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	1	email_generico	bloqueado	scrypt:32768:8:1$vVY9GSlItUvbOEk4$f1dca54dcfd76a24e376f8e906fa02b0e47695320686e46812e77b5b0e59110ad2bb66181bc0013a2706335c6a68d9af61bfe4e3e16d9a8ce2f3327c375ac08f	validado	2026-05-05 13:03:02.669737	MACAÉ	RJ
2	FUERIZA	BURRO IRRESPONSÁVEL	redman-37@hotmail.com	(32) 98456-0451	33.924.772/0001-79	VALIDACAO PENDENTE	VALIDACAO PENDENTE	\N	\N	fallback_local	1	\N	\N	2026-05-05T13:07:11.768395	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	3	email_generico, telefone_repetido, ip_reincidente	suspeito	scrypt:32768:8:1$G6lXyRnbtUSovA47$1cad0f19afae1d88fdf5153242ec564a9c21caea549f1bb3327b80c10951e8a310d2859ef28aef1955fcc3757f371f55026364786bc443f55024ca60e3f20d39	validado	2026-05-05 13:07:10.954697	UBERLÂNDIA	MG
\.


--
-- Data for Name: vagas; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.vagas (id, titulo, empresa, cidade, estado, escala, salario, descricao, requisitos, contato, link_candidatura, recrutador_id, status, created_at, encerrada_em, encerrada_motivo_tipo, encerrada_motivo, vigivagas_ajudou_contratacao, contratacoes_quantidade, encerrada_observacoes) FROM stdin;
1	VIGILANTE	FUERIZA	ARAGUARI	MG	12X36	500,00	SER MUITO BURRO; SER IRRESPONSÁVEL COM SEUS PRÓPRIOS DOCUMENTOS; SER IGNORANTE SENTAR A PORRADA NA ESPOSA E FILHOS TER UM QI INFERIOR AO DE UM RATO	RECICLAGEM EM DIA	34999667786	\N	2	encerrada	2026-05-05 13:09:53.375287	2026-05-05 18:09:44.920634	processo_finalizado	Processo seletivo finalizado	sim	1	
\.


--
-- Data for Name: vigilantes; Type: TABLE DATA; Schema: public; Owner: vigivagas_db_user
--

COPY public.vigilantes (id, nome, cpf, telefone, email, cidade, endereco, cep, curso, reciclagem, area_interesse, resumo_profissional, objetivo_cargo, escolaridade, possui_cfv, instituicao_formacao, ext_ctv, ext_cea, ext_csp, ext_cnl1, ext_ces, data_ultima_reciclagem, curso_ultima_reciclagem, ultima_experiencia_profissional, ip_cadastro, user_agent, antifraude_score, antifraude_flags, antifraude_status, password, status, created_at, estado) FROM stdin;
4	ANA ISADORA FERNANDES	134.870.286-97	(34) 99733-3702	anaisadora@hotmail.com	ARAXÁ	RUA JOAQUIM ALVES FERREIRA, URCIANO LEMOS	38181-138	SIM	2024-04-10			VIGILANTE	ENSINO MEDIO COMPLETO	SIM	ANAISADORA@HOTMAIL.COM	NAO	NAO	NAO	NAO	NAO	2024-04-10	FORMACAO DE VIGILANTES	NAO PREENCHI AQUI, ENTAO VOU TOMAR A ATITUDE AGORA	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	0		normal	scrypt:32768:8:1$BKWjja9eOBXfbeo1$9305cc9c517de3253bc3492604a61cfcf1436e6a1d9ac3adfc60362267eab078e759b82c15a7476d929a9bd35a629962c930c684dfc2158e0491a384524d592a	ativo	2026-05-05 13:00:25.518598	MG
5	CICERO JOSE DE QUEIROZ	055.059.033-12	(34) 9952-9245	cicerosilva@hotmail.com	UBERLÂNDIA	RUA ANTÔNIO BERNARDES DA COSTA, LARANJEIRAS	38410-230	SIM	1980-04-20			VIGILANTE	ENSINO FUNDAMENTAL INCOMPLETO	SIM	EFASEG	NAO	NAO	NAO	NAO	NAO	1980-04-20	FORMACAO DE VIGILANTES	MUITAS	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	1	ip_reincidente	normal	scrypt:32768:8:1$MFldjDv0mTHUNggl$731f06f84cfd5b7b712d053e304d76e55b1562167e6e2f602f98143adf5a2b15c0a5b6a1bd4b29b9a89f5ce8577647a04f978c92ebd794baa3e35645bc93188c	ativo	2026-05-05 13:22:39.184963	MG
6	ELOM JORGE DA SILVA	088.683.676-02	(34) 9135-6699	joaolundin@hotmail.com	UBERLÂNDIA	RUA ROQUE FIDALE, RESIDENCIAL INTEGRAÇÃO	38407-580	SIM	2025-03-12			VIGILANTE	ENSINO FUNDAMENTAL INCOMPLETO	SIM	JOAOLUNDIN@HOTMAIL.COM	NAO	NAO	NAO	NAO	NAO	2025-03-12	FORMACAO DE VIGILANTES	EFEEFEFEEFEFEF	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	1	ip_reincidente	normal	scrypt:32768:8:1$997k2WcMlN71G07t$4880986aa022aa2057aaa5191eee389fcc371f53aaec6649cd21bc8153b55291241488bc1760c775607c2c71aa2bd6ba9950a376eaf6e5c51167e78e9dc6edbd	ativo	2026-05-05 17:41:28.300036	MG
7	WALDINEI APARECIDO DA COSTA	049.778.416-54	(34) 9656-0461	waldinei@gmail.com	NOVA PONTE	AV FLORIANO PEIXOTO 930 CS	38160-000	NAO				VIGILANTE	ENSINO FUNDAMENTAL INCOMPLETO	NAO		NAO	NAO	NAO	NAO	NAO			SOU VIGIA. AINDA NAO TENHO EXPERIÊNCIA NA AREA DE VIGILANTE, MAS QUERO FAZER O CURSO.	177.191.116.246	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36	1	ip_reincidente	normal	scrypt:32768:8:1$f0E83fGLWSZfl32h$a76fafb342ade9be503cf270217aa1eb8c046ab642ff7d8c9c70f05528f4c9ac33075622a52612cf025a4282848ac5a3dd5dae6c05024fcabb6171f0869dd525	ativo	2026-05-05 18:06:35.785065	MG
8	JOAO BOSCO FERREIRA	140.741.086-58	(32) 98456-0451	joaobosco.profissional25@gmail.com	MACAÉ	RUA CONDE DE ARARUAMA, CENTRO	27910-640	NAO				JOAOBOSCO.PROFISSIONAL25@GMAIL.COM	ENSINO FUNDAMENTAL INCOMPLETO	NAO		NAO	NAO	NAO	NAO	NAO			GGVG	177.191.116.246	Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36	1	ip_reincidente	normal	scrypt:32768:8:1$KAWVVxP0XQmCIQ3s$2ee93fd6b2ac9b2aecc2e5a5705927834d7ee9382aacb16ac400573c1c0477b2f31332dea3293ec2a5727ae21397fe13ddac65a41ab870d7304135ea9a420a7a	ativo	2026-05-05 19:39:55.461709	RJ
\.


--
-- Name: administradores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.administradores_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 5, true);


--
-- Name: candidatos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.candidatos_id_seq', 1, false);


--
-- Name: candidaturas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.candidaturas_id_seq', 4, true);


--
-- Name: lgpd_consents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.lgpd_consents_id_seq', 5, true);


--
-- Name: lgpd_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.lgpd_requests_id_seq', 1, true);


--
-- Name: mauricio_usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.mauricio_usuarios_id_seq', 3, true);


--
-- Name: password_resets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.password_resets_id_seq', 3, true);


--
-- Name: recrutadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.recrutadores_id_seq', 2, true);


--
-- Name: vagas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.vagas_id_seq', 1, true);


--
-- Name: vigilantes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vigivagas_db_user
--

SELECT pg_catalog.setval('public.vigilantes_id_seq', 8, true);


--
-- Name: administradores administradores_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.administradores
    ADD CONSTRAINT administradores_pkey PRIMARY KEY (id);


--
-- Name: administradores administradores_username_key; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.administradores
    ADD CONSTRAINT administradores_username_key UNIQUE (username);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: candidatos candidatos_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_pkey PRIMARY KEY (id);


--
-- Name: candidaturas candidaturas_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_pkey PRIMARY KEY (id);


--
-- Name: candidaturas candidaturas_vigilante_id_vaga_id_key; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_vigilante_id_vaga_id_key UNIQUE (vigilante_id, vaga_id);


--
-- Name: lgpd_consents lgpd_consents_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.lgpd_consents
    ADD CONSTRAINT lgpd_consents_pkey PRIMARY KEY (id);


--
-- Name: lgpd_requests lgpd_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.lgpd_requests
    ADD CONSTRAINT lgpd_requests_pkey PRIMARY KEY (id);


--
-- Name: mauricio_usuarios mauricio_usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.mauricio_usuarios
    ADD CONSTRAINT mauricio_usuarios_pkey PRIMARY KEY (id);


--
-- Name: mauricio_usuarios mauricio_usuarios_username_key; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.mauricio_usuarios
    ADD CONSTRAINT mauricio_usuarios_username_key UNIQUE (username);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: recrutadores recrutadores_email_key; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.recrutadores
    ADD CONSTRAINT recrutadores_email_key UNIQUE (email);


--
-- Name: recrutadores recrutadores_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.recrutadores
    ADD CONSTRAINT recrutadores_pkey PRIMARY KEY (id);


--
-- Name: vagas vagas_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vagas
    ADD CONSTRAINT vagas_pkey PRIMARY KEY (id);


--
-- Name: vigilantes vigilantes_cpf_key; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vigilantes
    ADD CONSTRAINT vigilantes_cpf_key UNIQUE (cpf);


--
-- Name: vigilantes vigilantes_email_key; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vigilantes
    ADD CONSTRAINT vigilantes_email_key UNIQUE (email);


--
-- Name: vigilantes vigilantes_pkey; Type: CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vigilantes
    ADD CONSTRAINT vigilantes_pkey PRIMARY KEY (id);


--
-- Name: idx_candidatos_cidade; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_candidatos_cidade ON public.candidatos USING btree (cidade);


--
-- Name: idx_candidaturas_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_candidaturas_status ON public.candidaturas USING btree (status);


--
-- Name: idx_candidaturas_vaga_id; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_candidaturas_vaga_id ON public.candidaturas USING btree (vaga_id);


--
-- Name: idx_candidaturas_vigilante_id; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_candidaturas_vigilante_id ON public.candidaturas USING btree (vigilante_id);


--
-- Name: idx_lgpd_requests_email; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_lgpd_requests_email ON public.lgpd_requests USING btree (email);


--
-- Name: idx_lgpd_requests_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_lgpd_requests_status ON public.lgpd_requests USING btree (status);


--
-- Name: idx_password_resets_token_hash; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_password_resets_token_hash ON public.password_resets USING btree (token_hash);


--
-- Name: idx_password_resets_user; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_password_resets_user ON public.password_resets USING btree (user_type, user_id);


--
-- Name: idx_recrutadores_antifraude_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_recrutadores_antifraude_status ON public.recrutadores USING btree (antifraude_status);


--
-- Name: idx_recrutadores_nome_empresa; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_recrutadores_nome_empresa ON public.recrutadores USING btree (nome_empresa);


--
-- Name: idx_recrutadores_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_recrutadores_status ON public.recrutadores USING btree (status);


--
-- Name: idx_vagas_cidade; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vagas_cidade ON public.vagas USING btree (cidade);


--
-- Name: idx_vagas_encerrada_em; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vagas_encerrada_em ON public.vagas USING btree (encerrada_em);


--
-- Name: idx_vagas_recrutador_id; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vagas_recrutador_id ON public.vagas USING btree (recrutador_id);


--
-- Name: idx_vagas_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vagas_status ON public.vagas USING btree (status);


--
-- Name: idx_vigilantes_antifraude_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vigilantes_antifraude_status ON public.vigilantes USING btree (antifraude_status);


--
-- Name: idx_vigilantes_cidade; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vigilantes_cidade ON public.vigilantes USING btree (cidade);


--
-- Name: idx_vigilantes_created_at; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vigilantes_created_at ON public.vigilantes USING btree (created_at);


--
-- Name: idx_vigilantes_status; Type: INDEX; Schema: public; Owner: vigivagas_db_user
--

CREATE INDEX idx_vigilantes_status ON public.vigilantes USING btree (status);


--
-- Name: candidaturas candidaturas_vaga_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_vaga_id_fkey FOREIGN KEY (vaga_id) REFERENCES public.vagas(id);


--
-- Name: candidaturas candidaturas_vigilante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.candidaturas
    ADD CONSTRAINT candidaturas_vigilante_id_fkey FOREIGN KEY (vigilante_id) REFERENCES public.vigilantes(id);


--
-- Name: vagas vagas_recrutador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vigivagas_db_user
--

ALTER TABLE ONLY public.vagas
    ADD CONSTRAINT vagas_recrutador_id_fkey FOREIGN KEY (recrutador_id) REFERENCES public.recrutadores(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO vigivagas_db_user;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO vigivagas_db_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO vigivagas_db_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TABLES TO vigivagas_db_user;


--
-- PostgreSQL database dump complete
--

\unrestrict rfRcUDhioy46XLfgHL6Sphd9eE5g3vo26J4ZQLWW25HLf5hSbbNCSNjxDQgaxAr

