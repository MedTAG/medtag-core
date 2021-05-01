--This file contains the sql queries to create the types and the tables of groundtruthdb
-- Database: ground_truth
--DROP DATABASE ground_truth;

CREATE DATABASE ground_truth_db WITH OWNER = postgres ENCODING = 'UTF8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
	
	
--DROP SCHEMA public CASCADE;
GRANT ALL PRIVILEGES ON DATABASE ground_truth_db TO postgres;
\connect ground_truth_db;
--CREATE SCHEMA public;

-- DROP ELEMENTS--
-- DROP TYPE public.usecases;
-- DROP TYPE public.sem_area;
-- DROP TYPE public.gtypes;
-- DROP TYPE public.languages;
-- DROP TYPE public.profile;

-- DROP TABLE public.annotation_label;
-- DROP TABLE public.associate;
-- DROP TABLE public.belong_to;
-- DROP TABLE public.concept;
-- DROP TABLE public.concept_has_uc;
-- DROP TABLE public.contains;
-- DROP TABLE public.ground_truth_log_file;
-- DROP TABLE public.linked;
-- DROP TABLE public.mention;
-- DROP TABLE public.report;
-- DROP TABLE public.semantic_area;
-- DROP TABLE public.use_case;
-- DROP TABLE public."user";

-- END DROP --

-- DEFINITION TYPES --


CREATE TYPE public.gtypes AS ENUM
    ('concepts', 'mentions', 'labels', 'concept-mention');

CREATE TYPE public.profile AS ENUM
    ('Admin', 'Tech', 'Expert', 'Beginner');
	
-- END TYPES --	
-- TABLES --


CREATE TABLE public.semantic_area
(
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT semantic_area_pkey PRIMARY KEY (name)
)

TABLESPACE pg_default;

COPY public.semantic_area (name) FROM stdin;
Anatomical Location
Test
Procedure
Diagnosis
General Entity
\.

CREATE TABLE public.use_case
(
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT use_case_pkey PRIMARY KEY (name)
)

TABLESPACE pg_default;

COPY public.use_case (name) FROM stdin;
Colon
\.


CREATE TABLE public.report
(
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    report_json jsonb NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    institute text COLLATE pg_catalog."default",
    CONSTRAINT report_pkey PRIMARY KEY (id_report, language),
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.use_case (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
 
COPY public.report (id_report, name, report_json, language, institute) FROM stdin;
e2b7198565b7044022ac9fd60b807970	Colon	{"age": 52, "codint": "19/5725", "gender": "F", "materials": "blind polypectomy", "report_id": "19/5725", "internalid": 1, "raw_diagnoses": "tubular adenoma with low-grade dysplasia.", "report_id_hashed": "e2b7198565b7044022ac9fd60b807970", "target_diagnosis": "tubular adenoma with low-grade dysplasia."}	English	default_hospital
6eb209760544eb3d07945accd0453359	Colon	{"age": 34, "codint": "19/4087", "gender": "M", "materials": "blind octopus", "report_id": "19/4087", "internalid": 1, "raw_diagnoses": "villous adenoma with moderate dysplasia. resection margin where assessable unscathed", "report_id_hashed": "6eb209760544eb3d07945accd0453359", "target_diagnosis": "villous adenoma with moderate dysplasia. resection margin where assessable unscathed"}	English	default_hospital
7213be298db51ebc954d8a22d9006614	Colon	{"age": 63, "codint": "19/3437", "gender": "M", "materials": "rectal biopsy", "report_id": "19/3437", "internalid": 1, "raw_diagnoses": "tubular adenoma with mild to moderate dysplasia. the lesion extends deep resection margin.", "report_id_hashed": "7213be298db51ebc954d8a22d9006614", "target_diagnosis": "tubular adenoma with mild to moderate dysplasia. the lesion extends deep resection margin."}	English	default_hospital
768c6e343e92d8da0d4fe86b3ebcdc3b	Colon	{"age": 83, "codint": "19/2272", "gender": "M", "materials": "left colon polyp", "report_id": "19/2272", "internalid": 1, "raw_diagnoses": "tubular adenoma with low-grade dysplasia.", "report_id_hashed": "768c6e343e92d8da0d4fe86b3ebcdc3b", "target_diagnosis": "tubular adenoma with low-grade dysplasia."}	English	default_hospital
40a078a849ffc479343b8cc48dc7d973	Colon	{"age": 50, "codint": "19/4971_1", "gender": "M", "materials": "+ blind octopus octopus transverse", "report_id": "19/4971_1", "internalid": 1, "raw_diagnoses": "1) tubular adenoma with moderate dysplasia.", "report_id_hashed": "40a078a849ffc479343b8cc48dc7d973", "target_diagnosis": "tubular adenoma with moderate dysplasia."}	English	default_hospital
0b7d30ad70f68e389187495f96643a27	Colon	{"age": null, "codint": "19/4971_2", "gender": "", "materials": "", "report_id": "19/4971_2", "internalid": 2, "raw_diagnoses": "2) hyperplastic polyp-adenomatous with mild-to-moderate dysplasia.", "report_id_hashed": "0b7d30ad70f68e389187495f96643a27", "target_diagnosis": "hyperplastic polyp-adenomatous with mild-to-moderate dysplasia."}	English	default_hospital
c30685f9e468d1ea109d49ddbb229805	Colon	{"age": 64, "codint": "19/2643", "gender": "M", "materials": "rectosigmoid biopsy", "report_id": "19/2643", "internalid": 1, "raw_diagnoses": "a hyperplastic polyp and a tubular adenoma with low-grade dysplasia.", "report_id_hashed": "c30685f9e468d1ea109d49ddbb229805", "target_diagnosis": "a hyperplastic polyp and a tubular adenoma with low-grade dysplasia."}	English	default_hospital
97cd684cb49d9a99ae99a05a02c7515e	Colon	{"age": 70, "codint": "19/7145_1", "gender": "M", "materials": "biopsy ascending colon", "report_id": "19/7145_1", "internalid": 1, "raw_diagnoses": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin.", "report_id_hashed": "97cd684cb49d9a99ae99a05a02c7515e", "target_diagnosis": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin."}	English	default_hospital
61be79bcaa3dbb2c5a5508e49ba3f57e	Colon	{"age": null, "codint": "19/7145_2", "gender": "", "materials": "", "report_id": "19/7145_2", "internalid": 2, "raw_diagnoses": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin.", "report_id_hashed": "61be79bcaa3dbb2c5a5508e49ba3f57e", "target_diagnosis": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin."}	English	default_hospital
8092927e72d676c677316e0faef0cdc5	Colon	{"age": 64, "codint": "19/4918", "gender": "M", "materials": "blind octopus", "report_id": "19/4918", "internalid": 1, "raw_diagnoses": "tubular adenoma with moderate dysplasia.", "report_id_hashed": "8092927e72d676c677316e0faef0cdc5", "target_diagnosis": "tubular adenoma with moderate dysplasia."}	English	default_hospital
a67858b81f3edee7db268e04511a5121	Colon	{"age": 73, "codint": "18/19956", "gender": "F", "materials": "biopsy sigma", "report_id": "18/19956", "internalid": 1, "raw_diagnoses": "tubular adenoma with mild dysplasia glandular epithelium.", "report_id_hashed": "a67858b81f3edee7db268e04511a5121", "target_diagnosis": "tubular adenoma with mild dysplasia glandular epithelium."}	English	default_hospital
\.


CREATE TABLE public."user"
(
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    password character varying(32) COLLATE pg_catalog."default" NOT NULL,
    profile profile NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (username)
)

TABLESPACE pg_default;

COPY public."user" (username, password, profile) FROM stdin;
Test	0cbc6611f5540bd0809a388dc95a615b	Tech
\.

CREATE TABLE public.concept
(
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    name character varying(1000) COLLATE pg_catalog."default",
    json_concept jsonb,
    CONSTRAINT concept_pkey PRIMARY KEY (concept_url)
)

TABLESPACE pg_default;

COPY public.concept (concept_url, name) FROM stdin;
http://purl.obolibrary.org/obo/UBERON_0003346	Rectal mucous membrane
http://purl.obolibrary.org/obo/UBERON_0001157	Transverse Colon
http://purl.obolibrary.org/obo/UBERON_0001052	Rectum, NOS
http://purl.obolibrary.org/obo/UBERON_0001158	Descending colon
http://purl.obolibrary.org/obo/UBERON_0001153	Caecum
http://purl.obolibrary.org/obo/UBERON_0012652	colorectum
http://purl.obolibrary.org/obo/UBERON_0001156	Ascending Colon
http://purl.obolibrary.org/obo/UBERON_0002116	Ileum
http://purl.obolibrary.org/obo/UBERON_0036214	Rectosigmoid junction
http://purl.obolibrary.org/obo/UBERON_0008971	Left colon
http://purl.obolibrary.org/obo/UBERON_0001155	Colon, NOS
http://purl.obolibrary.org/obo/UBERON_0008972	Right colon
http://purl.obolibrary.org/obo/UBERON_0001159	Sigmoid colon
http://purl.obolibrary.org/obo/UBERON_0000916	Abdomen
https://w3id.org/examode/ontology/SevereColonDysplasia	Severe Colon Dysplasia
http://purl.obolibrary.org/obo/NCIT_C4848	Mild Colon Dysplasia
http://purl.obolibrary.org/obo/OAE_0001850	Granuloma
http://purl.obolibrary.org/obo/NCIT_C4849	Moderate Colon Dysplasia
http://purl.obolibrary.org/obo/MONDO_0021271	Colon Villous Adenoma
http://purl.obolibrary.org/obo/NCIT_C7041	Colon Tubular Adenoma
http://purl.obolibrary.org/obo/NCIT_C4124	Metastatic Adenocarcinoma
http://purl.obolibrary.org/obo/MONDO_0005292	Colitis
http://purl.obolibrary.org/obo/MONDO_0006152	Colon Inflammatory Polyp
http://purl.obolibrary.org/obo/MONDO_0002271	Colon Adenocarcinoma
http://purl.obolibrary.org/obo/NCIT_C156083	High Grade Dysplasia
http://purl.obolibrary.org/obo/MONDO_0006498	Adenoma
http://purl.obolibrary.org/obo/NCIT_C5496	Colon Tubulovillous Adenoma
http://purl.obolibrary.org/obo/NCIT_C3426	Ulcer
http://purl.obolibrary.org/obo/NCIT_C4847	Colon Dysplasia
http://purl.obolibrary.org/obo/NCIT_C38458	Serrated Adenoma
http://linkedlifedata.com/resource/umls/id/C0521191	Pre-Cancerous Dysplasia
http://purl.obolibrary.org/obo/MONDO_0021400	Polyp of Colon
http://purl.obolibrary.org/obo/NCIT_C4930	Colon Hyperplastic Polyp
http://purl.obolibrary.org/obo/NCIT_C51678	Biopsy of Colon
http://purl.obolibrary.org/obo/NCIT_C15609	Anastomosis
http://purl.obolibrary.org/obo/NCIT_C86074	Hemicolectomy
http://purl.obolibrary.org/obo/NCIT_C25349	Polypectomy
http://purl.obolibrary.org/obo/NCIT_C158758	Resection
http://purl.obolibrary.org/obo/NCIT_C15389	Endoscopic Biopsy
http://purl.obolibrary.org/obo/NCIT_C15189	Biopsy
http://purl.obolibrary.org/obo/NCIT_C51688	Colonoscopic polypectomy
http://purl.obolibrary.org/obo/NCIT_C51944	Immunohistochemical Test
http://purl.obolibrary.org/obo/NCIT_C16724	Immunoprecipitation
\.

CREATE TABLE public.annotation_label
(
    name text COLLATE pg_catalog."default" NOT NULL,
    seq_number integer NOT NULL,
    label text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT annotation_label_pkey PRIMARY KEY (label, seq_number),
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.use_case (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

COPY public.annotation_label (name, seq_number, label) FROM stdin;
Colon	1	Cancer
Colon	2	Adenomatous polyp - high grade dysplasia
Colon	3	Adenomatous polyp - low grade dysplasia
Colon	4	Hyperplastic polyp
Colon	5	Non-informative
\.

CREATE TABLE public.mention
(
    mention_text text COLLATE pg_catalog."default",
    start integer NOT NULL,
    stop integer NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT mention_pkey PRIMARY KEY (id_report, language, start, stop),
    CONSTRAINT mention_id_report_language_fkey FOREIGN KEY (language, id_report)
        REFERENCES public.report (language, id_report) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


CREATE TABLE public.ground_truth_log_file
(
    insertion_time timestamp with time zone NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    gt_type gtypes NOT NULL,
    gt_json jsonb NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT ground_truth_log_file_pkey PRIMARY KEY (id_report, language, username, insertion_time),
    CONSTRAINT ground_truth_log_file_id_report_language_fkey FOREIGN KEY (language, id_report)
        REFERENCES public.report (language, id_report) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT username_fkey FOREIGN KEY (username)
        REFERENCES public."user" (username) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


CREATE TABLE public.linked
(
    name text COLLATE pg_catalog."default" NOT NULL,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    start integer NOT NULL,
    stop integer NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    insertion_time timestamp with time zone,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT linked_pkey PRIMARY KEY (name, username, concept_url, start, stop, id_report, language),
    CONSTRAINT concept_url_fkey FOREIGN KEY (concept_url)
        REFERENCES public.concept (concept_url) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT mention_fkey FOREIGN KEY (start, id_report, language, stop)
        REFERENCES public.mention (start, id_report, language, stop) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.semantic_area (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT username_fkey FOREIGN KEY (username)
        REFERENCES public."user" (username) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


CREATE TABLE public.contains
(
    insertion_time timestamp with time zone,
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT contains_pkey PRIMARY KEY (id_report, language, username, concept_url, name),
    CONSTRAINT concept_url_fkey FOREIGN KEY (concept_url)
        REFERENCES public.concept (concept_url) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT contains_id_report_language_fkey FOREIGN KEY (language, id_report)
        REFERENCES public.report (language, id_report) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.semantic_area (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT username_fkey FOREIGN KEY (username)
        REFERENCES public."user" (username) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE TABLE public.concept_has_uc
(
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT concept_has_uc_pkey PRIMARY KEY (concept_url, name),
    CONSTRAINT concept_url_fkey FOREIGN KEY (concept_url)
        REFERENCES public.concept (concept_url) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.use_case (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


COPY public.concept_has_uc (concept_url, name) FROM stdin;
http://purl.obolibrary.org/obo/UBERON_0003346	Colon
http://purl.obolibrary.org/obo/UBERON_0001157	Colon
http://purl.obolibrary.org/obo/UBERON_0001052	Colon
http://purl.obolibrary.org/obo/UBERON_0001158	Colon
http://purl.obolibrary.org/obo/UBERON_0001153	Colon
http://purl.obolibrary.org/obo/UBERON_0012652	Colon
http://purl.obolibrary.org/obo/UBERON_0001156	Colon
http://purl.obolibrary.org/obo/UBERON_0002116	Colon
http://purl.obolibrary.org/obo/UBERON_0036214	Colon
http://purl.obolibrary.org/obo/UBERON_0008971	Colon
http://purl.obolibrary.org/obo/UBERON_0001155	Colon
http://purl.obolibrary.org/obo/UBERON_0008972	Colon
http://purl.obolibrary.org/obo/UBERON_0001159	Colon
http://purl.obolibrary.org/obo/UBERON_0000916	Colon
https://w3id.org/examode/ontology/SevereColonDysplasia	Colon
http://purl.obolibrary.org/obo/NCIT_C4848	Colon
http://purl.obolibrary.org/obo/OAE_0001850	Colon
http://purl.obolibrary.org/obo/NCIT_C4849	Colon
http://purl.obolibrary.org/obo/MONDO_0021271	Colon
http://purl.obolibrary.org/obo/NCIT_C7041	Colon
http://purl.obolibrary.org/obo/NCIT_C4124	Colon
http://purl.obolibrary.org/obo/MONDO_0005292	Colon
http://purl.obolibrary.org/obo/MONDO_0006152	Colon
http://purl.obolibrary.org/obo/MONDO_0002271	Colon
http://purl.obolibrary.org/obo/NCIT_C156083	Colon
http://purl.obolibrary.org/obo/MONDO_0006498	Colon
http://purl.obolibrary.org/obo/NCIT_C5496	Colon
http://purl.obolibrary.org/obo/NCIT_C3426	Colon
http://purl.obolibrary.org/obo/NCIT_C4847	Colon
http://purl.obolibrary.org/obo/NCIT_C38458	Colon
http://linkedlifedata.com/resource/umls/id/C0521191	Colon
http://purl.obolibrary.org/obo/MONDO_0021400	Colon
http://purl.obolibrary.org/obo/NCIT_C4930	Colon
http://purl.obolibrary.org/obo/NCIT_C51678	Colon
http://purl.obolibrary.org/obo/NCIT_C15609	Colon
http://purl.obolibrary.org/obo/NCIT_C86074	Colon
http://purl.obolibrary.org/obo/NCIT_C25349	Colon
http://purl.obolibrary.org/obo/NCIT_C158758	Colon
http://purl.obolibrary.org/obo/NCIT_C15389	Colon
http://purl.obolibrary.org/obo/NCIT_C15189	Colon
http://purl.obolibrary.org/obo/NCIT_C51688	Colon
http://purl.obolibrary.org/obo/NCIT_C51944	Colon
http://purl.obolibrary.org/obo/NCIT_C16724	Colon
\.

CREATE TABLE public.annotate
(
    insertion_time timestamp with time zone,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    start integer NOT NULL,
    stop integer NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT annotate_pkey PRIMARY KEY (id_report, language, username, start, stop),
    CONSTRAINT mention_fkey FOREIGN KEY (start, id_report, language, stop)
        REFERENCES public.mention (start, id_report, language, stop) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT user_fkey FOREIGN KEY (username)
        REFERENCES public."user" (username) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE TABLE public.associate
(
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    seq_number integer NOT NULL,
    label text COLLATE pg_catalog."default" NOT NULL,
    insertion_time timestamp with time zone,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT associate_pkey PRIMARY KEY (id_report, language, username, label, seq_number),
    CONSTRAINT associate_id_report_language_fkey FOREIGN KEY (id_report, language)
        REFERENCES public.report (id_report, language) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT label_fkey FOREIGN KEY (label, seq_number)
        REFERENCES public.annotation_label (label, seq_number) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT username_fkey FOREIGN KEY (username)
        REFERENCES public."user" (username) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE TABLE public.belong_to
(
    name text COLLATE pg_catalog."default" NOT NULL,
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT belong_to_pkey PRIMARY KEY (name, concept_url),
    CONSTRAINT concept_url_fkey FOREIGN KEY (concept_url)
        REFERENCES public.concept (concept_url) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.semantic_area (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

COPY public.belong_to (name, concept_url) FROM stdin;
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0003346
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001157
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001052
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001158
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001153
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0012652
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001156
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0002116
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0036214
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0008971
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001155
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0008972
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0001159
Anatomical Location	http://purl.obolibrary.org/obo/UBERON_0000916
Diagnosis	https://w3id.org/examode/ontology/SevereColonDysplasia
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C4848
Diagnosis	http://purl.obolibrary.org/obo/OAE_0001850
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C4849
Diagnosis	http://purl.obolibrary.org/obo/MONDO_0021271
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C7041
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C4124
Diagnosis	http://purl.obolibrary.org/obo/MONDO_0005292
Diagnosis	http://purl.obolibrary.org/obo/MONDO_0006152
Diagnosis	http://purl.obolibrary.org/obo/MONDO_0002271
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C156083
Diagnosis	http://purl.obolibrary.org/obo/MONDO_0006498
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C5496
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C3426
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C4847
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C38458
Diagnosis	http://linkedlifedata.com/resource/umls/id/C0521191
Diagnosis	http://purl.obolibrary.org/obo/MONDO_0021400
Diagnosis	http://purl.obolibrary.org/obo/NCIT_C4930
Procedure	http://purl.obolibrary.org/obo/NCIT_C51678
Procedure	http://purl.obolibrary.org/obo/NCIT_C15609
Procedure	http://purl.obolibrary.org/obo/NCIT_C86074
Procedure	http://purl.obolibrary.org/obo/NCIT_C25349
Procedure	http://purl.obolibrary.org/obo/NCIT_C158758
Procedure	http://purl.obolibrary.org/obo/NCIT_C15389
Procedure	http://purl.obolibrary.org/obo/NCIT_C15189
Procedure	http://purl.obolibrary.org/obo/NCIT_C51688
Test	http://purl.obolibrary.org/obo/NCIT_C51944
Test	http://purl.obolibrary.org/obo/NCIT_C16724
\.


