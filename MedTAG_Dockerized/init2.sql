--This file contains the sql queries to create the types and the tables of groundtruthdb
-- Database: ground_truth
--DROP DATABASE ground_truth;

CREATE DATABASE ground_truth WITH OWNER = postgres ENCODING = 'UTF8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
	
	
--DROP SCHEMA public CASCADE;
GRANT ALL PRIVILEGES ON DATABASE ground_truth TO postgres;
\connect ground_truth;
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

CREATE TYPE public.ns_names AS ENUM
    ('Robot', 'Human');

CREATE TYPE public.modes AS ENUM
    ('Manual and Automatic', 'Automatic', 'Manual');



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
colon
uterine cervix
lung
\.


CREATE TABLE public.report
(
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    report_json jsonb NOT NULL,
    batch integer,
    insertion_date date,
    language text COLLATE pg_catalog."default" NOT NULL,
    institute text COLLATE pg_catalog."default",
    CONSTRAINT report_pkey PRIMARY KEY (id_report, language),
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.use_case (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;
 
COPY public.report (id_report, name, report_json, language, institute, batch) FROM stdin;
PUBMED_29691659	colon	{"title":"Colon cancer with perforation.","abstract":"Perforation of the colon is a rare complication for patients with colon cancer and usually requires emergent surgery. The characteristics of perforation differ based on the site of perforation, presenting as either perforation at the cancer site or perforation proximal to the cancer site. Peritonitis due to perforation tends to be more severe in cases of perforation proximal to the cancer site; however, the difference in the outcome between the two types remains unclear. Surgical treatment of colon cancer with perforation has changed over time. Recently, many reports have shown the safety and effectiveness of single-stage operation consisting of resection and primary anastomosis with intraoperative colonic lavage. Under certain conditions, laparoscopic surgery can be feasible and help minimize the invasion. However, emergent surgery for colon cancer with perforation is associated with a high rate of mortality and morbidity. The long-term prognosis seems to have no association with the existence of perforation. Oncologically curative resection may be warranted for perforated colon cancer. In this report, we perform a literature review and investigate the characteristics and surgical strategy for colon cancer with perforation.","volume":"49","journal":"Surg Today","year":"2019","authors":"Otani K, Kawai K, Hata K, Tanaka T, Nishikawa T, Sasaki K, Kaneko M, Murono K, Emoto S, Nozawa H"}	english	PUBMED	1
PUBMED_20138539	colon	{"title":"Colon cancer.","abstract":"Colon cancer is one of the leading tumours in the world and it is considered among the big killers, together with lung, prostate and breast cancer. In the recent years very important advances occurred in the field of treatment of this frequent disease: adjuvant chemotherapy was demonstrated to be effective, chiefly in stage III patients, and surgery was optimized in order to achieve the best results with a low morbidity. Several new target-oriented drugs are under evaluation and some of them (cetuximab and bevacizumab) have already exhibited a good activity/efficacy, mainly in combination with chemotherapy. The development of updated recommendations for the best management of these patients is crucial in order to obtain the best results, not only in clinical research but also in every-day practice. This report summarizes the most important achievements in this field and provides the readers useful suggestions for their professional practice.","volume":"74","journal":"Crit Rev Oncol Hematol","year":"2010","authors":"Labianca R, Beretta GD, Kildani B, Milesi L, Merlin F, Mosconi S, Pessi MA, Prochilo T, Quadri A, Gatta G, de Braud F, Wils J"}	english	PUBMED	1
PUBMED_25918287	colon	{"title":"Personalizing colon cancer adjuvant therapy: selecting optimal treatments for individual patients.","abstract":"For more than three decades, postoperative chemotherapy-initially fluoropyrimidines and more recently combinations with oxaliplatin-has reduced the risk of tumor recurrence and improved survival for patients with resected colon cancer. Although universally recommended for patients with stage III disease, there is no consensus about the survival benefit of postoperative chemotherapy in stage II colon cancer. The most recent adjuvant clinical trials have not shown any value for adding targeted agents, namely bevacizumab and cetuximab, to standard chemotherapies in stage III disease, despite improved outcomes in the metastatic setting. However, biomarker analyses of multiple studies strongly support the feasibility of refining risk stratification in colon cancer by factoring in molecular characteristics with pathologic tumor staging. In stage II disease, for example, microsatellite instability supports observation after surgery. Furthermore, the value of BRAF or KRAS mutations as additional risk factors in stage III disease is greater when microsatellite status and tumor location are taken into account. Validated predictive markers of adjuvant chemotherapy benefit for stage II or III colon cancer are lacking, but intensive research is ongoing. Recent advances in understanding the biologic hallmarks and drivers of early-stage disease as well as the micrometastatic environment are expected to translate into therapeutic strategies tailored to select patients. This review focuses on the pathologic, molecular, and gene expression characterizations of early-stage colon cancer; new insights into prognostication; and emerging predictive biomarkers that could ultimately help define the optimal adjuvant treatments for patients in routine clinical practice.","volume":"33","journal":"J Clin Oncol","year":"2015","authors":"Dienstmann R, Salazar R, Tabernero J"}	english	PUBMED	1
e2b7198565b7044022ac9fd60b807970	colon	{"age": 52, "codint": "19/5725", "gender": "F", "materials": "blind polypectomy", "report_id": "19/5725", "internalid": 1, "raw_diagnoses": "tubular adenoma with low-grade dysplasia.", "report_id_hashed": "e2b7198565b7044022ac9fd60b807970", "target_diagnosis": "tubular adenoma with low-grade dysplasia."}	english	default_hospital	1
6eb209760544eb3d07945accd0453359	colon	{"age": 34, "codint": "19/4087", "gender": "M", "materials": "blind octopus", "report_id": "19/4087", "internalid": 1, "raw_diagnoses": "villous adenoma with moderate dysplasia. resection margin where assessable unscathed", "report_id_hashed": "6eb209760544eb3d07945accd0453359", "target_diagnosis": "villous adenoma with moderate dysplasia. resection margin where assessable unscathed"}	english	default_hospital	1
7213be298db51ebc954d8a22d9006614	colon	{"age": 63, "codint": "19/3437", "gender": "M", "materials": "rectal biopsy", "report_id": "19/3437", "internalid": 1, "raw_diagnoses": "tubular adenoma with mild to moderate dysplasia. the lesion extends deep resection margin.", "report_id_hashed": "7213be298db51ebc954d8a22d9006614", "target_diagnosis": "tubular adenoma with mild to moderate dysplasia. the lesion extends deep resection margin."}	english	default_hospital	1
768c6e343e92d8da0d4fe86b3ebcdc3b	colon	{"age": 83, "codint": "19/2272", "gender": "M", "materials": "left colon polyp", "report_id": "19/2272", "internalid": 1, "raw_diagnoses": "tubular adenoma with low-grade dysplasia.", "report_id_hashed": "768c6e343e92d8da0d4fe86b3ebcdc3b", "target_diagnosis": "tubular adenoma with low-grade dysplasia."}	english	default_hospital	1
40a078a849ffc479343b8cc48dc7d973	colon	{"age": 50, "codint": "19/4971_1", "gender": "M", "materials": "+ blind octopus octopus transverse", "report_id": "19/4971_1", "internalid": 1, "raw_diagnoses": "1) tubular adenoma with moderate dysplasia.", "report_id_hashed": "40a078a849ffc479343b8cc48dc7d973", "target_diagnosis": "tubular adenoma with moderate dysplasia."}	english	default_hospital	1
0b7d30ad70f68e389187495f96643a27	colon	{"age": null, "codint": "19/4971_2", "gender": "", "materials": "", "report_id": "19/4971_2", "internalid": 2, "raw_diagnoses": "2) hyperplastic polyp-adenomatous with mild-to-moderate dysplasia.", "report_id_hashed": "0b7d30ad70f68e389187495f96643a27", "target_diagnosis": "hyperplastic polyp-adenomatous with mild-to-moderate dysplasia."}	english	default_hospital	1
c30685f9e468d1ea109d49ddbb229805	colon	{"age": 64, "codint": "19/2643", "gender": "M", "materials": "rectosigmoid biopsy", "report_id": "19/2643", "internalid": 1, "raw_diagnoses": "a hyperplastic polyp and a tubular adenoma with low-grade dysplasia.", "report_id_hashed": "c30685f9e468d1ea109d49ddbb229805", "target_diagnosis": "a hyperplastic polyp and a tubular adenoma with low-grade dysplasia."}	english	default_hospital	1
97cd684cb49d9a99ae99a05a02c7515e	colon	{"age": 70, "codint": "19/7145_1", "gender": "M", "materials": "biopsy ascending colon", "report_id": "19/7145_1", "internalid": 1, "raw_diagnoses": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin.", "report_id_hashed": "97cd684cb49d9a99ae99a05a02c7515e", "target_diagnosis": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin."}	english	default_hospital	1
61be79bcaa3dbb2c5a5508e49ba3f57e	colon	{"age": null, "codint": "19/7145_2", "gender": "", "materials": "", "report_id": "19/7145_2", "internalid": 2, "raw_diagnoses": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin.", "report_id_hashed": "61be79bcaa3dbb2c5a5508e49ba3f57e", "target_diagnosis": "tubular adenoma with mild and moderate dysplasia. harmless the resection margin."}	english	default_hospital	1
8092927e72d676c677316e0faef0cdc5	colon	{"age": 64, "codint": "19/4918", "gender": "M", "materials": "blind octopus", "report_id": "19/4918", "internalid": 1, "raw_diagnoses": "tubular adenoma with moderate dysplasia.", "report_id_hashed": "8092927e72d676c677316e0faef0cdc5", "target_diagnosis": "tubular adenoma with moderate dysplasia."}	english	default_hospital	1
a67858b81f3edee7db268e04511a5121	colon	{"age": 73, "codint": "18/19956", "gender": "F", "materials": "biopsy sigma", "report_id": "18/19956", "internalid": 1, "raw_diagnoses": "tubular adenoma with mild dysplasia glandular epithelium.", "report_id_hashed": "a67858b81f3edee7db268e04511a5121", "target_diagnosis": "tubular adenoma with mild dysplasia glandular epithelium."}	english	default_hospital	1
\.

CREATE TABLE public.name_space
(
    ns_id ns_names NOT NULL,
    description text COLLATE pg_catalog."default",
    CONSTRAINT name_space_pkey PRIMARY KEY (ns_id)
)
TABLESPACE pg_default;

COPY public.name_space (ns_id) FROM stdin;
Human
Robot
\.
CREATE TABLE public."user"
(
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    password character varying(32) COLLATE pg_catalog."default" NOT NULL,
    ns_id ns_names NOT NULL,
    profile profile NOT NULL,
    CONSTRAINT user_pkey PRIMARY KEY (username, ns_id),
    CONSTRAINT name_space_fkey FOREIGN KEY (ns_id)
        REFERENCES public.name_space (ns_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

COPY public."user" (username, password, profile, ns_id) FROM stdin;
Test	0cbc6611f5540bd0809a388dc95a615b	Tech	Human
Test	0cbc6611f5540bd0809a388dc95a615b	Tech	Robot
Robot_user	5f61a0e9a11ce3a22225b34aa250da2f	Tech	Robot
\.

CREATE TABLE public.concept
(
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    name character varying(1000) COLLATE pg_catalog."default",
    json_concept jsonb,
    annotation_mode modes,
    CONSTRAINT concept_pkey PRIMARY KEY (concept_url)
)

TABLESPACE pg_default;

COPY public.concept (concept_url, name, annotation_mode) FROM stdin;
http://purl.obolibrary.org/obo/UBERON_0003346	Rectal mucous membrane	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001157	Transverse Colon	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001052	Rectum, NOS	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001158	Descending colon	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001153	Caecum	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0012652	colorectum	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001156	Ascending Colon	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0002116	Ileum	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0036214	Rectosigmoid junction	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0008971	Left colon	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001155	Colon, NOS	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0008972	Right colon	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0001159	Sigmoid colon	Manual and Automatic
http://purl.obolibrary.org/obo/UBERON_0000916	Abdomen	Manual and Automatic
https://w3id.org/examode/ontology/SevereColonDysplasia	Severe Colon Dysplasia	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C4848	Mild Colon Dysplasia	Manual and Automatic
http://purl.obolibrary.org/obo/OAE_0001850	Granuloma	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C4849	Moderate Colon Dysplasia	Manual and Automatic
http://purl.obolibrary.org/obo/MONDO_0021271	Colon Villous Adenoma	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C7041	Colon Tubular Adenoma	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C4124	Metastatic Adenocarcinoma	Manual and Automatic
http://purl.obolibrary.org/obo/MONDO_0005292	Colitis	Manual and Automatic
http://purl.obolibrary.org/obo/MONDO_0006152	Colon Inflammatory Polyp	Manual and Automatic
http://purl.obolibrary.org/obo/MONDO_0002271	Colon Adenocarcinoma	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C156083	High Grade Dysplasia	Manual and Automatic
http://purl.obolibrary.org/obo/MONDO_0006498	Adenoma	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C5496	Colon Tubulovillous Adenoma	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C3426	Ulcer	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C4847	Colon Dysplasia	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C38458	Serrated Adenoma	Manual and Automatic
http://linkedlifedata.com/resource/umls/id/C0521191	Pre-Cancerous Dysplasia	Manual and Automatic
http://purl.obolibrary.org/obo/MONDO_0021400	Polyp of Colon	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C4930	Colon Hyperplastic Polyp	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C51678	Biopsy of Colon	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C15609	Anastomosis	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C86074	Hemicolectomy	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C25349	Polypectomy	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C158758	Resection	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C15389	Endoscopic Biopsy	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C15189	Biopsy	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C51688	Colonoscopic polypectomy	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C51944	Immunohistochemical Test	Manual and Automatic
http://purl.obolibrary.org/obo/NCIT_C16724	Immunoprecipitation	Manual and Automatic
\.

CREATE TABLE public.annotation_label
(
    name text COLLATE pg_catalog."default" NOT NULL,
    seq_number integer NOT NULL,
    annotation_mode modes,
    label text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT annotation_label_pkey PRIMARY KEY (label, seq_number),
    CONSTRAINT name_fkey FOREIGN KEY (name)
        REFERENCES public.use_case (name) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;



COPY public.annotation_label (name, seq_number, label, annotation_mode) FROM stdin;
colon	1	Cancer	Manual and Automatic
colon	2	Adenomatous polyp - high grade dysplasia	Manual and Automatic
colon	3	Adenomatous polyp - low grade dysplasia	Manual and Automatic
colon	4	Hyperplastic polyp	Manual and Automatic
colon	5	Non-informative	Manual and Automatic
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
    ns_id ns_names NOT NULL,
    gt_type gtypes NOT NULL,
    gt_json jsonb NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT ground_truth_log_file_pkey PRIMARY KEY (id_report, language, username, ns_id, insertion_time),
    CONSTRAINT ground_truth_log_file_id_report_language_fkey FOREIGN KEY (language, id_report)
        REFERENCES public.report (language, id_report) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT username_fkey FOREIGN KEY (username,ns_id)
        REFERENCES public."user" (username,ns_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;


CREATE TABLE public.linked
(
    name text COLLATE pg_catalog."default" NOT NULL,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    ns_id ns_names NOT NULL,
    concept_url text COLLATE pg_catalog."default" NOT NULL,
    start integer NOT NULL,
    stop integer NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    insertion_time timestamp with time zone,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT linked_pkey PRIMARY KEY (name, username, ns_id, concept_url, start, stop, id_report, language),
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
    CONSTRAINT username_fkey FOREIGN KEY (username,ns_id)
        REFERENCES public."user" (username,ns_id) MATCH SIMPLE
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
    ns_id ns_names NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT contains_pkey PRIMARY KEY (id_report, language, username, ns_id, concept_url, name),
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
    CONSTRAINT username_fkey FOREIGN KEY (username,ns_id)
        REFERENCES public."user" (username,ns_id) MATCH SIMPLE
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
http://purl.obolibrary.org/obo/UBERON_0003346	colon
http://purl.obolibrary.org/obo/UBERON_0001157	colon
http://purl.obolibrary.org/obo/UBERON_0001052	colon
http://purl.obolibrary.org/obo/UBERON_0001158	colon
http://purl.obolibrary.org/obo/UBERON_0001153	colon
http://purl.obolibrary.org/obo/UBERON_0012652	colon
http://purl.obolibrary.org/obo/UBERON_0001156	colon
http://purl.obolibrary.org/obo/UBERON_0002116	colon
http://purl.obolibrary.org/obo/UBERON_0036214	colon
http://purl.obolibrary.org/obo/UBERON_0008971	colon
http://purl.obolibrary.org/obo/UBERON_0001155	colon
http://purl.obolibrary.org/obo/UBERON_0008972	colon
http://purl.obolibrary.org/obo/UBERON_0001159	colon
http://purl.obolibrary.org/obo/UBERON_0000916	colon
https://w3id.org/examode/ontology/SevereColonDysplasia	colon
http://purl.obolibrary.org/obo/NCIT_C4848	colon
http://purl.obolibrary.org/obo/OAE_0001850	colon
http://purl.obolibrary.org/obo/NCIT_C4849	colon
http://purl.obolibrary.org/obo/MONDO_0021271	colon
http://purl.obolibrary.org/obo/NCIT_C7041	colon
http://purl.obolibrary.org/obo/NCIT_C4124	colon
http://purl.obolibrary.org/obo/MONDO_0005292	colon
http://purl.obolibrary.org/obo/MONDO_0006152	colon
http://purl.obolibrary.org/obo/MONDO_0002271	colon
http://purl.obolibrary.org/obo/NCIT_C156083	colon
http://purl.obolibrary.org/obo/MONDO_0006498	colon
http://purl.obolibrary.org/obo/NCIT_C5496	colon
http://purl.obolibrary.org/obo/NCIT_C3426	colon
http://purl.obolibrary.org/obo/NCIT_C4847	colon
http://purl.obolibrary.org/obo/NCIT_C38458	colon
http://linkedlifedata.com/resource/umls/id/C0521191	colon
http://purl.obolibrary.org/obo/MONDO_0021400	colon
http://purl.obolibrary.org/obo/NCIT_C4930	colon
http://purl.obolibrary.org/obo/NCIT_C51678	colon
http://purl.obolibrary.org/obo/NCIT_C15609	colon
http://purl.obolibrary.org/obo/NCIT_C86074	colon
http://purl.obolibrary.org/obo/NCIT_C25349	colon
http://purl.obolibrary.org/obo/NCIT_C158758	colon
http://purl.obolibrary.org/obo/NCIT_C15389	colon
http://purl.obolibrary.org/obo/NCIT_C15189	colon
http://purl.obolibrary.org/obo/NCIT_C51688	colon
http://purl.obolibrary.org/obo/NCIT_C51944	colon
http://purl.obolibrary.org/obo/NCIT_C16724	colon
\.

CREATE TABLE public.annotate
(
    insertion_time timestamp with time zone,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    ns_id ns_names NOT NULL,
    start integer NOT NULL,
    stop integer NOT NULL,
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT annotate_pkey PRIMARY KEY (id_report, language, username, ns_id, start, stop),
    CONSTRAINT mention_fkey FOREIGN KEY (start, id_report, language, stop)
        REFERENCES public.mention (start, id_report, language, stop) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT user_fkey FOREIGN KEY (username,ns_id)
        REFERENCES public."user" (username,ns_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE TABLE public.associate
(
    id_report character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    username character varying(1000) COLLATE pg_catalog."default" NOT NULL,
    seq_number integer NOT NULL,
    ns_id ns_names NOT NULL,
    label text COLLATE pg_catalog."default" NOT NULL,
    insertion_time timestamp with time zone,
    language text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT associate_pkey PRIMARY KEY (id_report, language, username, ns_id, label, seq_number),
    CONSTRAINT associate_id_report_language_fkey FOREIGN KEY (id_report, language)
        REFERENCES public.report (id_report, language) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT label_fkey FOREIGN KEY (label, seq_number)
        REFERENCES public.annotation_label (label, seq_number) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION,
    CONSTRAINT username_fkey FOREIGN KEY (username,ns_id)
        REFERENCES public."user" (username,ns_id) MATCH SIMPLE
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

