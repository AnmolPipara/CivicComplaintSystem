--
-- PostgreSQL database dump
--

\restrict PcdjbqIJdfzyLxtkiexvTnaZC6Tgcpvp8jrpTONc2oUn4n899tkdcw4UnOqln5N

-- Dumped from database version 15.19
-- Dumped by pg_dump version 15.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.votes DROP CONSTRAINT IF EXISTS votes_complaint_id_fkey;
ALTER TABLE IF EXISTS ONLY public.votes DROP CONSTRAINT IF EXISTS votes_citizen_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_recipient_id_fkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_complaint_id_fkey;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.complaints DROP CONSTRAINT IF EXISTS complaints_department_id_fkey;
ALTER TABLE IF EXISTS ONLY public.complaints DROP CONSTRAINT IF EXISTS complaints_citizen_id_fkey;
ALTER TABLE IF EXISTS ONLY public.complaints DROP CONSTRAINT IF EXISTS complaints_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.complaint_status_history DROP CONSTRAINT IF EXISTS complaint_status_history_complaint_id_fkey;
ALTER TABLE IF EXISTS ONLY public.complaint_status_history DROP CONSTRAINT IF EXISTS complaint_status_history_changed_by_fkey;
ALTER TABLE IF EXISTS ONLY public.clusters DROP CONSTRAINT IF EXISTS clusters_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.citizens DROP CONSTRAINT IF EXISTS citizens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_department_id_fkey;
ALTER TABLE IF EXISTS ONLY public.admins DROP CONSTRAINT IF EXISTS admins_user_id_fkey;
DROP INDEX IF EXISTS public.ix_votes_id;
DROP INDEX IF EXISTS public.ix_votes_complaint_id;
DROP INDEX IF EXISTS public.ix_votes_complaint_created;
DROP INDEX IF EXISTS public.ix_votes_citizen_id;
DROP INDEX IF EXISTS public.ix_users_phone;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_notifications_recipient_status;
DROP INDEX IF EXISTS public.ix_notifications_recipient_id;
DROP INDEX IF EXISTS public.ix_notifications_id;
DROP INDEX IF EXISTS public.ix_notifications_complaint_id;
DROP INDEX IF EXISTS public.ix_notifications_complaint_channel;
DROP INDEX IF EXISTS public.ix_locations_pincode;
DROP INDEX IF EXISTS public.ix_locations_id;
DROP INDEX IF EXISTS public.ix_locations_coordinates;
DROP INDEX IF EXISTS public.ix_locations_area_name;
DROP INDEX IF EXISTS public.ix_locations_area_city;
DROP INDEX IF EXISTS public.ix_departments_id;
DROP INDEX IF EXISTS public.ix_complaints_status;
DROP INDEX IF EXISTS public.ix_complaints_priority_score;
DROP INDEX IF EXISTS public.ix_complaints_priority_level;
DROP INDEX IF EXISTS public.ix_complaints_needs_human_review;
DROP INDEX IF EXISTS public.ix_complaints_id;
DROP INDEX IF EXISTS public.ix_complaints_department_id;
DROP INDEX IF EXISTS public.ix_complaints_created_at;
DROP INDEX IF EXISTS public.ix_complaints_citizen_status;
DROP INDEX IF EXISTS public.ix_complaints_citizen_id;
DROP INDEX IF EXISTS public.ix_complaints_category_id;
DROP INDEX IF EXISTS public.ix_complaint_status_history_id;
DROP INDEX IF EXISTS public.ix_complaint_status_history_complaint_id;
DROP INDEX IF EXISTS public.ix_clusters_id;
DROP INDEX IF EXISTS public.ix_clusters_center;
DROP INDEX IF EXISTS public.ix_clusters_category_id;
DROP INDEX IF EXISTS public.ix_clusters_category;
DROP INDEX IF EXISTS public.ix_citizens_user_id;
DROP INDEX IF EXISTS public.ix_citizens_id;
DROP INDEX IF EXISTS public.ix_categories_id;
DROP INDEX IF EXISTS public.ix_admins_user_id;
DROP INDEX IF EXISTS public.ix_admins_id;
ALTER TABLE IF EXISTS ONLY public.votes DROP CONSTRAINT IF EXISTS votes_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.votes DROP CONSTRAINT IF EXISTS uq_citizen_complaint_vote;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.locations DROP CONSTRAINT IF EXISTS locations_pkey;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_user_id_key;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_pkey;
ALTER TABLE IF EXISTS ONLY public.departments DROP CONSTRAINT IF EXISTS departments_name_key;
ALTER TABLE IF EXISTS ONLY public.complaints DROP CONSTRAINT IF EXISTS complaints_pkey;
ALTER TABLE IF EXISTS ONLY public.complaint_status_history DROP CONSTRAINT IF EXISTS complaint_status_history_pkey;
ALTER TABLE IF EXISTS ONLY public.clusters DROP CONSTRAINT IF EXISTS clusters_pkey;
ALTER TABLE IF EXISTS ONLY public.citizens DROP CONSTRAINT IF EXISTS citizens_pkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_pkey;
ALTER TABLE IF EXISTS ONLY public.categories DROP CONSTRAINT IF EXISTS categories_name_key;
ALTER TABLE IF EXISTS ONLY public.admins DROP CONSTRAINT IF EXISTS admins_pkey;
ALTER TABLE IF EXISTS public.votes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.notifications ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.locations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.departments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.complaints ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.complaint_status_history ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.clusters ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.citizens ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.categories ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.admins ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.votes_id_seq;
DROP TABLE IF EXISTS public.votes;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.notifications_id_seq;
DROP TABLE IF EXISTS public.notifications;
DROP SEQUENCE IF EXISTS public.locations_id_seq;
DROP TABLE IF EXISTS public.locations;
DROP SEQUENCE IF EXISTS public.departments_id_seq;
DROP TABLE IF EXISTS public.departments;
DROP SEQUENCE IF EXISTS public.complaints_id_seq;
DROP TABLE IF EXISTS public.complaints;
DROP SEQUENCE IF EXISTS public.complaint_status_history_id_seq;
DROP TABLE IF EXISTS public.complaint_status_history;
DROP SEQUENCE IF EXISTS public.clusters_id_seq;
DROP TABLE IF EXISTS public.clusters;
DROP SEQUENCE IF EXISTS public.citizens_id_seq;
DROP TABLE IF EXISTS public.citizens;
DROP SEQUENCE IF EXISTS public.categories_id_seq;
DROP TABLE IF EXISTS public.categories;
DROP SEQUENCE IF EXISTS public.admins_id_seq;
DROP TABLE IF EXISTS public.admins;
DROP TYPE IF EXISTS public.userrole;
DROP TYPE IF EXISTS public.prioritylevel;
DROP TYPE IF EXISTS public.notificationchannel;
DROP TYPE IF EXISTS public.complaintstatus;
--
-- Name: complaintstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.complaintstatus AS ENUM (
    'SUBMITTED',
    'PRIORITIZED',
    'ASSIGNED',
    'IN_PROGRESS',
    'RESOLVED',
    'REJECTED'
);


--
-- Name: notificationchannel; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.notificationchannel AS ENUM (
    'EMAIL',
    'SMS',
    'PUSH',
    'IN_APP'
);


--
-- Name: prioritylevel; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.prioritylevel AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH'
);


--
-- Name: userrole; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.userrole AS ENUM (
    'CITIZEN',
    'ADMIN',
    'DEPARTMENT'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admins (
    id integer NOT NULL,
    user_id integer NOT NULL,
    department_id integer,
    permissions character varying(500)
);


--
-- Name: admins_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    icon character varying(50),
    base_severity double precision NOT NULL,
    department_id integer,
    is_active boolean,
    created_at timestamp without time zone
);


--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: citizens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.citizens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    address text,
    preferred_notification_channels character varying(100),
    latitude double precision,
    longitude double precision
);


--
-- Name: citizens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.citizens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: citizens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.citizens_id_seq OWNED BY public.citizens.id;


--
-- Name: clusters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clusters (
    id integer NOT NULL,
    name character varying(100),
    center_latitude double precision NOT NULL,
    center_longitude double precision NOT NULL,
    radius_km double precision NOT NULL,
    category_id integer,
    complaint_count integer NOT NULL,
    created_at double precision,
    updated_at double precision
);


--
-- Name: clusters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clusters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clusters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clusters_id_seq OWNED BY public.clusters.id;


--
-- Name: complaint_status_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.complaint_status_history (
    id integer NOT NULL,
    complaint_id integer NOT NULL,
    previous_status character varying,
    new_status character varying NOT NULL,
    changed_by integer,
    notes text,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: complaint_status_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.complaint_status_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: complaint_status_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.complaint_status_history_id_seq OWNED BY public.complaint_status_history.id;


--
-- Name: complaints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.complaints (
    id integer NOT NULL,
    citizen_id integer NOT NULL,
    category_id integer NOT NULL,
    department_id integer,
    description text NOT NULL,
    status character varying NOT NULL,
    evidence_urls text,
    upvote_count integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone,
    resolved_at timestamp without time zone,
    assigned_at timestamp without time zone,
    started_at timestamp without time zone,
    location character varying(255) NOT NULL,
    latitude double precision,
    longitude double precision,
    severity_score integer,
    impact_score integer,
    urgency_score integer,
    priority_score double precision,
    priority_level character varying(20),
    assessment_status character varying(20) DEFAULT 'pending'::character varying,
    assessment_reason text,
    assessment_confidence character varying(20),
    missing_information json,
    needs_human_review boolean DEFAULT false,
    is_safety_escalated boolean DEFAULT false,
    ai_severity_score integer,
    ai_impact_score integer,
    ai_urgency_score integer,
    ai_reason text,
    admin_override boolean DEFAULT false,
    admin_override_reason text
);


--
-- Name: complaints_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.complaints_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: complaints_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.complaints_id_seq OWNED BY public.complaints.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    email character varying(255),
    phone character varying(20),
    head_name character varying(100),
    is_active boolean,
    created_at double precision,
    user_id integer
);


--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    address text,
    landmark character varying(255),
    area_name character varying(100),
    city character varying(100) NOT NULL,
    state character varying(100) NOT NULL,
    pincode character varying(10),
    is_sensitive_zone integer,
    created_at double precision
);


--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    recipient_id integer NOT NULL,
    complaint_id integer,
    channel public.notificationchannel NOT NULL,
    subject character varying(255),
    message text NOT NULL,
    status character varying(50) NOT NULL,
    sent_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    password_hash character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    role public.userrole NOT NULL,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.votes (
    id integer NOT NULL,
    citizen_id integer NOT NULL,
    complaint_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.votes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.votes_id_seq OWNED BY public.votes.id;


--
-- Name: admins id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: citizens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.citizens ALTER COLUMN id SET DEFAULT nextval('public.citizens_id_seq'::regclass);


--
-- Name: clusters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clusters ALTER COLUMN id SET DEFAULT nextval('public.clusters_id_seq'::regclass);


--
-- Name: complaint_status_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaint_status_history ALTER COLUMN id SET DEFAULT nextval('public.complaint_status_history_id_seq'::regclass);


--
-- Name: complaints id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaints ALTER COLUMN id SET DEFAULT nextval('public.complaints_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: votes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes ALTER COLUMN id SET DEFAULT nextval('public.votes_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.admins (id, user_id, department_id, permissions) FROM stdin;
1	2	\N	all
14	3	1	dept
15	4	2	dept
16	5	3	dept
17	6	4	dept
18	7	5	dept
19	47	6	dept
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (id, name, display_name, description, icon, base_severity, department_id, is_active, created_at) FROM stdin;
1	pothole	Pothole / Road Damage	Potholes, cracks, and road surface damage	road	0.7	1	t	2026-09-09 20:16:22.333499
2	garbage	Garbage / Waste	Uncollected garbage, overflowing bins, illegal dumping	trash	0.4	2	t	2026-09-09 20:16:22.333503
3	water_leakage	Water Leakage	Leaking pipes, water main breaks, low pressure	water	0.6	3	t	2026-09-09 20:16:22.333504
4	streetlight	Streetlight Issue	Broken, flickering, or missing streetlights	lightbulb	0.5	4	t	2026-09-09 20:16:22.333505
5	sewage_overflow	Sewage Overflow	Sewage backup, overflowing manholes, drainage issues	alert-triangle	0.9	5	t	2026-09-09 20:16:22.333506
6	traffic_signal	Traffic Signal	Malfunctioning traffic lights, missing signage	traffic-light	0.6	4	t	2026-09-09 20:16:22.333507
7	footpath	Footpath / Sidewalk	Broken footpaths, encroachment, accessibility issues	footprints	0.4	1	t	2026-09-09 20:16:22.333508
8	drainage	Drainage / Waterlogging	Clogged drains, waterlogging after rain	droplet	0.6	5	t	2026-09-09 20:16:22.333508
10	pot_6081	Potholes	\N	\N	0.5	\N	t	2026-09-15 06:04:12.264803
11	pot_4312	Potholes	\N	\N	0.5	\N	t	2026-09-15 06:05:17.4707
12	pot_9213	Potholes	\N	\N	0.5	\N	t	2026-09-15 06:06:49.394619
13	pot_7331	Potholes	\N	\N	0.5	\N	t	2026-09-25 04:30:54.716992
14	pot_7370	Potholes	\N	\N	0.5	\N	t	2026-09-25 04:59:37.574949
15	pot_9369	Potholes	\N	\N	0.5	\N	t	2026-09-25 05:13:10.998716
16	pot_3464	Potholes	\N	\N	0.5	\N	t	2026-09-25 05:33:07.632742
\.


--
-- Data for Name: citizens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.citizens (id, user_id, address, preferred_notification_channels, latitude, longitude) FROM stdin;
9	15	Shoppers Stop, Kottaramattom, Pala, Kerala, 686575	email,push	9.7130742	76.6831302
2	8	123 Main Street, Andheri West, Mumbai	email,push	\N	\N
26	46	\N	email,push	\N	\N
\.


--
-- Data for Name: clusters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clusters (id, name, center_latitude, center_longitude, radius_km, category_id, complaint_count, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: complaint_status_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.complaint_status_history (id, complaint_id, previous_status, new_status, changed_by, notes, created_at) FROM stdin;
22	10	PENDING	PENDING	2	Assigned to Road Maintenance Department	2026-09-27 08:29:31.327084
23	10	PENDING	WORKING	2	\N	2026-09-27 08:48:57.631302
24	10	WORKING	PENDING	2	\N	2026-09-27 08:49:04.205778
25	10	PENDING	WORKING	3	\N	2026-09-27 08:50:47.049293
26	10	WORKING	PENDING	2	\N	2026-09-27 08:50:56.103876
27	10	PENDING	WORKING	3	\N	2026-09-27 09:29:14.475543
28	10	WORKING	COMPLETED	3	\N	2026-09-27 09:31:01.01503
29	13	PENDING	PENDING	2	Assigned to Road Maintenance Department	2026-09-27 10:00:15.765436
30	13	PENDING	WORKING	3	\N	2026-09-27 10:00:52.011906
31	13	WORKING	COMPLETED	3	\N	2026-09-27 10:00:58.654489
32	14	PENDING	PENDING	2	Assigned to Sewerage Department	2026-09-27 10:05:42.258185
33	14	PENDING	WORKING	7	\N	2026-09-27 10:08:14.731299
34	14	WORKING	COMPLETED	7	\N	2026-09-27 10:08:40.063983
46	46	PENDING	WORKING	2	\N	2026-09-29 18:38:49.428865
47	46	WORKING	PENDING	2	\N	2026-09-29 18:38:49.748072
48	46	PENDING	WORKING	2	\N	2026-09-29 18:39:57.128713
49	46	WORKING	PENDING	2	\N	2026-09-29 18:39:57.423092
52	46	PENDING	WORKING	2	\N	2026-09-29 18:51:54.20897
53	46	WORKING	PENDING	2	\N	2026-09-29 18:51:54.519928
54	52	PENDING	PENDING	2	Assigned to Sanitation Department	2026-09-29 19:27:27.164359
55	52	PENDING	WORKING	4	\N	2026-09-29 19:30:45.998742
56	52	WORKING	COMPLETED	4	\N	2026-09-29 19:47:18.352714
57	46	PENDING	WORKING	2	\N	2026-09-29 19:57:33.830732
58	46	WORKING	PENDING	2	\N	2026-09-29 19:57:34.267241
\.


--
-- Data for Name: complaints; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.complaints (id, citizen_id, category_id, department_id, description, status, evidence_urls, upvote_count, created_at, updated_at, resolved_at, assigned_at, started_at, location, latitude, longitude, severity_score, impact_score, urgency_score, priority_score, priority_level, assessment_status, assessment_reason, assessment_confidence, missing_information, needs_human_review, is_safety_escalated, ai_severity_score, ai_impact_score, ai_urgency_score, ai_reason, admin_override, admin_override_reason) FROM stdin;
52	9	2	2	a lot of garbage waste has been dumped around the hostel	COMPLETED	[]	0	2026-09-29 19:05:13.466159	2026-09-29 19:47:18.346603	2026-09-29 19:47:18.334414	2026-09-29 19:27:27.15354	2026-09-29 19:30:45.949187	Manimala Hostel, Valavoor, Meenachil, Kerala, 686635	9.755966633218963	76.64833118962228	59	42	49	43.9	medium	completed	The dumped garbage around the hostel creates a moderate sanitation concern for residents but does not indicate structural damage or immediate danger; its effect is limited to the hostel vicinity.	low	["exact volume of waste", "type of waste (hazardous or non\\u2011hazardous)", "duration of accumulation", "any reported health issues or pest infestation", "access for collection vehicles"]	f	f	48	35	45	The dumped garbage around the hostel creates a moderate sanitation concern for residents but does not indicate structural damage or immediate danger; its effect is limited to the hostel vicinity.	t	\N
10	9	1	1	roads are broken , causing inconvinience	COMPLETED	[]	1	2026-09-25 05:04:15.121954	2026-09-29 18:39:37.862962	2026-09-27 09:31:01.009334	2026-09-27 08:29:30.823644	2026-09-27 08:48:57.608893	IIIT Kottayam, Valavoor, Meenachil, Kerala, 686635	9.755382813599137	76.64989885120033	40	35	35	39.68	medium	completed	Municipal road safety baseline applied.	medium	\N	f	f	\N	\N	\N	\N	f	\N
13	9	1	1	roads are very damaged	COMPLETED	[]	2	2026-09-27 09:59:19.209306	2026-09-28 20:10:08.237559	2026-09-27 10:00:58.651408	2026-09-27 10:00:15.760508	2026-09-27 10:00:52.007716	NH53, Belora Hirapur, Nandgaon-Khandeshwar, Maharashtra, 444701	20.79541211175597	77.69179614506042	40	35	35	35.12	medium	completed	Municipal road safety baseline applied.	medium	\N	f	f	\N	\N	\N	\N	f	\N
14	26	5	5	drains are completely choked\r\n	COMPLETED	[]	2	2026-09-27 10:04:16.557351	2026-09-29 07:10:09.219547	2026-09-27 10:08:40.060947	2026-09-27 10:05:42.256021	2026-09-27 10:08:14.729728	SH50, Takli Dhokeshwar, Parner, Maharashtra, 414304	19.269665296502332	74.35874557421566	55	40	70	50.19	medium	completed	The report indicates fully blocked drains, which can lead to sewage backup and health hazards. Without details on overflow extent or affected households, the damage is assessed as moderate (severity ~55). Public disruption is likely limited to the immediate area, giving a moderate impact (40). Prompt action is advisable to prevent overflow and contamination, resulting in a higher urgency (70).	medium	["extent and length of blockage", "whether sewage overflow is already occurring", "number of affected households", "presence of standing water or foul odor", "recent rainfall conditions", "any reported health complaints"]	t	f	55	40	70	The report indicates fully blocked drains, which can lead to sewage backup and health hazards. Without details on overflow extent or affected households, the damage is assessed as moderate (severity ~55). Public disruption is likely limited to the immediate area, giving a moderate impact (40). Prompt action is advisable to prevent overflow and contamination, resulting in a higher urgency (70).	f	\N
45	9	6	\N	traffic signal broken	PENDING	[]	0	2026-09-29 08:21:08.485905	2026-09-29 08:21:08.48945	\N	\N	\N	SH63, Bamhori, Damoh Tahsil, Madhya Pradesh	23.845649887659352	79.59926725604927	45	40	60	40	medium	completed	A non‑functional traffic signal can create safety risks and disrupt vehicle flow, but the description lacks details on the extent of failure, traffic volume, or any accidents, so scores are set to moderate levels.	low	["exact condition of the signal (off, flashing, stuck)", "traffic volume at the intersection", "any reported accidents or near\\u2011misses", "time of day when issue observed", "presence of temporary traffic control measures"]	t	f	45	40	60	A non‑functional traffic signal can create safety risks and disrupt vehicle flow, but the description lacks details on the extent of failure, traffic volume, or any accidents, so scores are set to moderate levels.	f	\N
46	9	1	\N	big pothole in the road.	PENDING	[]	1	2026-09-29 09:09:32.999775	2026-09-29 19:57:46.091125	\N	\N	2026-09-29 18:38:49.42575	Chakkampuzha Church - Valavoor Road, Chakkampuzha, Meenachil, Kerala, 686635	9.755833626396837	76.65183321583172	55	30	40	42.79	medium	completed	The report mentions a "big" pothole but provides no details on dimensions, depth, traffic volume, or safety incidents, so a moderate severity is assigned with limited impact and urgency pending more data.	low	["pothole dimensions (length, width, depth)", "road classification and traffic volume", "any reported accidents or near\\u2011misses", "presence of drainage or water accumulation", "any immediate safety hazards"]	t	f	55	30	40	The report mentions a "big" pothole but provides no details on dimensions, depth, traffic volume, or safety incidents, so a moderate severity is assigned with limited impact and urgency pending more data.	f	\N
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.departments (id, name, display_name, description, email, phone, head_name, is_active, created_at, user_id) FROM stdin;
1	road_maintenance	Road Maintenance Department	Handles potholes, road damage, and infrastructure repair	roads@city.gov	+91-22-1234-5678	Rajesh Kumar	t	1700000000	\N
2	sanitation	Sanitation Department	Handles garbage collection, waste management, and cleanliness	sanitation@city.gov	+91-22-1234-5679	Priya Sharma	t	1700000000	\N
3	water_supply	Water Supply Department	Handles water leakage, supply issues, and quality concerns	water@city.gov	+91-22-1234-5680	Amit Patel	t	1700000000	\N
4	electrical	Electrical Department	Handles streetlights, power lines, and electrical infrastructure	electrical@city.gov	+91-22-1234-5681	Sunita Reddy	t	1700000000	\N
5	sewerage	Sewerage Department	Handles sewage overflow, drainage, and wastewater management	sewerage@city.gov	+91-22-1234-5682	Vikram Singh	t	1700000000	\N
6	public_works	Public Works	Roads	\N	\N	\N	\N	\N	47
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.locations (id, latitude, longitude, address, landmark, area_name, city, state, pincode, is_sensitive_zone, created_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, recipient_id, complaint_id, channel, subject, message, status, sent_at, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, phone, password_hash, full_name, role, is_active, created_at, updated_at) FROM stdin;
2	admin@city.gov	+91-9876543210	$2b$12$bHNhLo9xl.i3eg5lqy6Zm./8CDkCp.do9eUFyoMikw9x1mWgl5hnW	City Administrator	ADMIN	t	2026-09-09 20:16:22.343249	2026-09-09 20:16:22.343252
3	roads@city.gov	\N	$2b$12$LsQNKL57W0LRs/Dv1TK0reP6aMNhPh7e1WIpcZoMHYI6VtzfUabrm	Road Dept Head	DEPARTMENT	t	2026-09-09 20:16:22.568813	2026-09-09 20:16:22.568816
4	sanitation@city.gov	\N	$2b$12$XiVdKI0zy24tm06boQrgPu6SLltMWwdfUunfZY84KRdS7FlIY5OMG	Sanitation Dept Head	DEPARTMENT	t	2026-09-09 20:16:22.794946	2026-09-09 20:16:22.794949
5	water@city.gov	\N	$2b$12$HcfFtH4SrBJ8mfnkr3dDIuC2ItvSeTPa2lK5P/106cAuCgwPCsv3W	Water Dept Head	DEPARTMENT	t	2026-09-09 20:16:23.015393	2026-09-09 20:16:23.015396
6	electrical@city.gov	\N	$2b$12$2Z0P3WoJQhCSdXdNeu7eHOEAc43GAHleZQ/lFl7IduyJ3dEoz6M92	Electrical Dept Head	DEPARTMENT	t	2026-09-09 20:16:23.247239	2026-09-09 20:16:23.247242
7	sewerage@city.gov	\N	$2b$12$GlaMWd8LW9XiD6cwT7eD6et22jpB6xODv/.SmL1zUQ4raeJOL15AW	Sewerage Dept Head	DEPARTMENT	t	2026-09-09 20:16:23.48145	2026-09-09 20:16:23.481453
8	citizen@example.com	+91-9876543211	$2b$12$rHg10DVfbeAPhYvmuzSlmu.2R2M9MxrlrDiB9o5vg0ip4KBLLMtJG	Rahul Citizen	CITIZEN	t	2026-09-09 20:16:23.725749	2026-09-09 20:16:23.725752
15	anmolpipara@gmail.com	9818821860	$2b$12$USUqLM7vTfndcQmuOkBK4exh6YGkDGOmK4ibyPvQmTNfVaXox5RDm	Anmol Pipara	CITIZEN	t	2026-09-10 06:20:17.394745	2026-09-10 06:20:17.3948
46	teste@gmail.com	1234567891	$2b$12$Ko0NWKo3IgGBUPPmdpa4E.g0oEZOwYpFz5cbJIVItr5FftAfuWg4e	teste	CITIZEN	t	2026-09-27 10:03:54.905049	2026-09-27 10:03:54.905071
47	publicworks@city.gov	\N	$2b$12$W/IGuHFcd61kb17KdyDf3.gHmjLghknLf..ylwSRV.TOp.O8tOdie	Public Works Dept Head	DEPARTMENT	t	2026-09-27 10:07:00.898933	2026-09-27 10:07:00.898937
\.


--
-- Data for Name: votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.votes (id, citizen_id, complaint_id, created_at) FROM stdin;
8	9	10	2026-09-25 06:06:40.887438
9	26	13	2026-09-27 10:04:37.424445
10	26	14	2026-09-27 10:04:39.434196
12	9	13	2026-09-28 20:10:08.240485
13	9	14	2026-09-28 20:11:24.972395
26	9	46	2026-09-29 18:34:20.76527
\.


--
-- Name: admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.admins_id_seq', 30, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_id_seq', 16, true);


--
-- Name: citizens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.citizens_id_seq', 81, true);


--
-- Name: clusters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clusters_id_seq', 1, false);


--
-- Name: complaint_status_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.complaint_status_history_id_seq', 61, true);


--
-- Name: complaints_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.complaints_id_seq', 54, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.departments_id_seq', 13, true);


--
-- Name: locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.locations_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 113, true);


--
-- Name: votes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.votes_id_seq', 41, true);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: citizens citizens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.citizens
    ADD CONSTRAINT citizens_pkey PRIMARY KEY (id);


--
-- Name: clusters clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_pkey PRIMARY KEY (id);


--
-- Name: complaint_status_history complaint_status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaint_status_history
    ADD CONSTRAINT complaint_status_history_pkey PRIMARY KEY (id);


--
-- Name: complaints complaints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaints
    ADD CONSTRAINT complaints_pkey PRIMARY KEY (id);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: departments departments_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_user_id_key UNIQUE (user_id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: votes uq_citizen_complaint_vote; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT uq_citizen_complaint_vote UNIQUE (citizen_id, complaint_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: votes votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (id);


--
-- Name: ix_admins_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_admins_id ON public.admins USING btree (id);


--
-- Name: ix_admins_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_admins_user_id ON public.admins USING btree (user_id);


--
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_categories_id ON public.categories USING btree (id);


--
-- Name: ix_citizens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_citizens_id ON public.citizens USING btree (id);


--
-- Name: ix_citizens_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_citizens_user_id ON public.citizens USING btree (user_id);


--
-- Name: ix_clusters_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clusters_category ON public.clusters USING btree (category_id);


--
-- Name: ix_clusters_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clusters_category_id ON public.clusters USING btree (category_id);


--
-- Name: ix_clusters_center; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clusters_center ON public.clusters USING btree (center_latitude, center_longitude);


--
-- Name: ix_clusters_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clusters_id ON public.clusters USING btree (id);


--
-- Name: ix_complaint_status_history_complaint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaint_status_history_complaint_id ON public.complaint_status_history USING btree (complaint_id);


--
-- Name: ix_complaint_status_history_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaint_status_history_id ON public.complaint_status_history USING btree (id);


--
-- Name: ix_complaints_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_category_id ON public.complaints USING btree (category_id);


--
-- Name: ix_complaints_citizen_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_citizen_id ON public.complaints USING btree (citizen_id);


--
-- Name: ix_complaints_citizen_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_citizen_status ON public.complaints USING btree (citizen_id, status);


--
-- Name: ix_complaints_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_created_at ON public.complaints USING btree (created_at);


--
-- Name: ix_complaints_department_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_department_id ON public.complaints USING btree (department_id);


--
-- Name: ix_complaints_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_id ON public.complaints USING btree (id);


--
-- Name: ix_complaints_needs_human_review; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_needs_human_review ON public.complaints USING btree (needs_human_review);


--
-- Name: ix_complaints_priority_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_priority_level ON public.complaints USING btree (priority_level);


--
-- Name: ix_complaints_priority_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_priority_score ON public.complaints USING btree (priority_score DESC);


--
-- Name: ix_complaints_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_complaints_status ON public.complaints USING btree (status);


--
-- Name: ix_departments_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_departments_id ON public.departments USING btree (id);


--
-- Name: ix_locations_area_city; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_area_city ON public.locations USING btree (area_name, city);


--
-- Name: ix_locations_area_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_area_name ON public.locations USING btree (area_name);


--
-- Name: ix_locations_coordinates; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_coordinates ON public.locations USING btree (latitude, longitude);


--
-- Name: ix_locations_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_id ON public.locations USING btree (id);


--
-- Name: ix_locations_pincode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_pincode ON public.locations USING btree (pincode);


--
-- Name: ix_notifications_complaint_channel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_complaint_channel ON public.notifications USING btree (complaint_id, channel);


--
-- Name: ix_notifications_complaint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_complaint_id ON public.notifications USING btree (complaint_id);


--
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_id ON public.notifications USING btree (id);


--
-- Name: ix_notifications_recipient_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_recipient_id ON public.notifications USING btree (recipient_id);


--
-- Name: ix_notifications_recipient_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_recipient_status ON public.notifications USING btree (recipient_id, status);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_phone; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_phone ON public.users USING btree (phone);


--
-- Name: ix_votes_citizen_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_votes_citizen_id ON public.votes USING btree (citizen_id);


--
-- Name: ix_votes_complaint_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_votes_complaint_created ON public.votes USING btree (complaint_id, created_at);


--
-- Name: ix_votes_complaint_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_votes_complaint_id ON public.votes USING btree (complaint_id);


--
-- Name: ix_votes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_votes_id ON public.votes USING btree (id);


--
-- Name: admins admins_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: categories categories_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: citizens citizens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.citizens
    ADD CONSTRAINT citizens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: clusters clusters_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: complaint_status_history complaint_status_history_changed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaint_status_history
    ADD CONSTRAINT complaint_status_history_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES public.users(id);


--
-- Name: complaint_status_history complaint_status_history_complaint_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaint_status_history
    ADD CONSTRAINT complaint_status_history_complaint_id_fkey FOREIGN KEY (complaint_id) REFERENCES public.complaints(id);


--
-- Name: complaints complaints_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaints
    ADD CONSTRAINT complaints_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: complaints complaints_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaints
    ADD CONSTRAINT complaints_citizen_id_fkey FOREIGN KEY (citizen_id) REFERENCES public.citizens(id);


--
-- Name: complaints complaints_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.complaints
    ADD CONSTRAINT complaints_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: departments departments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_complaint_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_complaint_id_fkey FOREIGN KEY (complaint_id) REFERENCES public.complaints(id);


--
-- Name: notifications notifications_recipient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_recipient_id_fkey FOREIGN KEY (recipient_id) REFERENCES public.users(id);


--
-- Name: votes votes_citizen_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_citizen_id_fkey FOREIGN KEY (citizen_id) REFERENCES public.citizens(id);


--
-- Name: votes votes_complaint_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.votes
    ADD CONSTRAINT votes_complaint_id_fkey FOREIGN KEY (complaint_id) REFERENCES public.complaints(id);


--
-- PostgreSQL database dump complete
--

\unrestrict PcdjbqIJdfzyLxtkiexvTnaZC6Tgcpvp8jrpTONc2oUn4n899tkdcw4UnOqln5N

