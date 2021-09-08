from MedTAG_sket_dock_App.utils import *
from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)
from collections import defaultdict
from MedTAG_sket_dock_App.utils_pubmed import *
import os.path
import owlready2

"""This .py file includes the methods needed to configure MedTAG and update its configuration"""

def process_ontology(workpath, disease):
    ontology_path = os.path.join(workpath, 'sket/sket/ont_proc/ontology/examode.owl')
    ontology = owlready2.get_ontology(ontology_path).load()
    sparql = "PREFIX exa: <https://w3id.org/examode/ontology/> " \
             "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> " \
             "select ?iri ?iri_label ?semantic_area_label where { " \
             "?iri rdfs:label ?iri_label ; exa:AssociatedDisease ?disease . " \
             "filter (langMatches( lang(?iri_label), 'en')). " \
             "?disease rdfs:label '" + disease + "'@en . " \
                                                 "OPTIONAL {?iri exa:hasSemanticArea ?semantic_area . " \
                                                 "?semantic_area rdfs:label ?semantic_area_label . " \
                                                 "filter (langMatches( lang(?semantic_area_label), 'en')).} " \
                                                 "} " \
                                                 "limit 1000"
    # get ontology graph as in rdflib
    ontology_graph = ontology.world.as_rdflib_graph()
    # issue sparql query
    r = ontology_graph.query(query_object=sparql)
    ontology_dict = defaultdict(list)
    for e in r:
        ontology_dict['iri'].append(e[0].toPython() if e[0] else None)
        ontology_dict['label'].append(e[1].toPython() if e[1] else None)
        ontology_dict['semantic_area_label'].append(e[2].toPython() if e[2] else None)
    # print(pd.DataFrame(ontology_dict))
    return r


def configure_concepts(cursor,load_concepts,author):

    """This method configures concepts when a NEW CONFIGURATION is performed"""

    for usecase in load_concepts:
        disease = ''
        description = {'provenance':'EXAMODE','insertion_author':author}
        desc = json.dumps(description)
        if usecase.lower() == 'colon':
            disease = 'colon carcinoma'
        elif usecase.lower() == 'uterine cervix':
            disease = 'cervical cancer'
        elif usecase.lower() == 'lung':
            disease = 'lung cancer'
        if disease != '':
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            r = process_ontology(workpath,disease)
            # convert query output to DataFrame
            belong_to = []
            concept_has_uc = []
            conc = []
            with transaction.atomic():
                for e in r:
                    if (e[0] is not None and e[1] is not None and e[2] is not None):
                        concept = e[0].toPython()
                        # print(concept)
                        if concept == 'SevereColonDysplasia':
                            concept = 'https://w3id.org/examode/ontology/SevereColonDysplasia'
                        elif concept == 'uterusNOS':
                            concept = 'https://w3id.org/examode/ontology/UterusNOS'

                        cursor.execute("SELECT * FROM semantic_area WHERE name = %s",[e[2].toPython()])
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO semantic_area VALUES(%s)",[e[2].toPython()])

                        belong_to.append((concept, e[2].toPython()))
                        concept_has_uc.append((concept, usecase))
                        conc.append((concept, e[1].toPython(), None))
                        cursor.execute('SELECT * FROM concept WHERE concept_url = %s',(concept,))
                        ans = cursor.fetchall()
                        # print(ans)
                        if len(ans) == 0:
                            query = ("INSERT INTO concept (concept_url, json_concept, name) VALUES(%s,%s,%s);")
                            values = (concept, desc, e[1].toPython())
                            cursor.execute(query, values)
                        else:
                            for row in ans:
                                j_c = json.loads(row[2])
                                if author == 'admin':
                                    if j_c['insertion_author'] != 'admin' or j_c['provenance'] != 'EXAMODE':
                                        j_c['insertion_author'] = 'admin'
                                        j_c['provenance'] = 'EXAMODE'
                                        j_c = json.dumps(j_c)
                                        cursor.execute("UPDATE concept SET json_concept = %s WHERE concept_url = %s",
                                                       [j_c, e[0].toPython()])

                                elif author == 'robot':
                                    if j_c['provenance'] != 'EXAMODE':
                                        j_c['provenance'] = 'EXAMODE'
                                        j_c = json.dumps(j_c)
                                        cursor.execute("UPDATE concept SET json_concept = %s WHERE concept_url = %s",[j_c,e[0].toPython()])

                        cursor.execute('SELECT * FROM belong_to WHERE concept_url = %s AND name=%s',[concept,e[2].toPython()])
                        if len(cursor.fetchall()) == 0:
                            query1 = ("INSERT INTO belong_to (name, concept_url) VALUES(%s,%s);")
                            values1 = (e[2].toPython(), concept)
                            cursor.execute(query1, values1)
                        cursor.execute('SELECT * FROM concept_has_uc WHERE concept_url = %s AND name=%s',[concept,usecase.lower()])
                        if len(cursor.fetchall()) == 0:
                            query2 = ("INSERT INTO concept_has_uc (concept_url,name) VALUES(%s,%s);")
                            values2 = (concept, usecase.lower())
                            cursor.execute(query2, values2)


def configure_labels(cursor,load_labels):

    """This method configures labels when a NEW CONFIGURATION is performed"""

    with transaction.atomic():
        workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
        with open(os.path.join(workpath, 'automatic_annotation/db_examode_data/examode_db_population.json'),
                  'r') as outfile:
            data = json.load(outfile)
            usecases = data['labels'].keys()
            areas = data['semantic area']
            ar_tup = []
            for el in areas:
                ar_tup.append((el,))
            cursor.executemany("INSERT INTO semantic_area VALUES (%s)", ar_tup)
            ar_tup = []
            ar_tup_label = []
            seq = 0
            # print(usecases)
            cursor.execute('SELECT * FROM use_case')
            ans = cursor.fetchall()
            # print(ans)
            for el in usecases:
                ar_tup.append(el.lower())
                for label in data['labels'][el]:
                    seq = seq + 1
                    ar_tup_label.append((label, seq, el.lower(),))
            for el in ar_tup:
                cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(el).lower(),))
                ans = cursor.fetchall()
                if len(ans) == 0:
                    cursor.execute('INSERT INTO use_case VALUES(%s)', (str(el).lower(),))
            cursor.execute("SELECT * FROM use_case")
            ans = cursor.fetchall()
            # print(ans)
            cursor.executemany("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s)", ar_tup_label)

            if load_labels is not None:
                if len(load_labels) > 0: #TODO risolvere questo problema: ora li ricopio due volte ma va gestito
                    labs = []
                    for el in load_labels:
                        for label in data['labels'][el.lower()]:
                            seq = seq + 1
                            labs.append((label, seq, el.lower(),))


                    cursor.executemany("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s)",
                                       labs)


def configure_update_labels(cursor,load_labels):

    """This method configures labels when a an existing configuration is updated"""

    with transaction.atomic():
        workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
        with open(os.path.join(workpath, 'automatic_annotation/db_examode_data/examode_db_population.json'),
                  'r') as outfile:
            data = json.load(outfile)
            cursor.execute("SELECT MAX(seq_number) FROM annotation_label")
            seq = cursor.fetchone()[0]
            if len(load_labels) > 0:
                labs = []
                for el in load_labels:
                    for label in data['labels'][el]:
                        seq = seq + 1
                        labs.append((label, seq, el.lower(),))

                cursor.executemany("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s)",
                                   labs)


# def configure_update_concepts(cursor,load_concepts):
#
#     """This method configures concepts when a an existing configuration is updated"""
#
#     for usecase in load_concepts:
#         disease = ''
#         description = {'provenance':'EXAMODE','insertion_author':'admin'}
#         desc = json.dumps(description)
#         if usecase.lower() == 'colon':
#             disease = 'colon carcinoma'
#         elif usecase.lower() == 'uterine cervix':
#             disease = 'cervical cancer'
#         elif usecase.lower() == 'lung':
#             disease = 'lung cancer'
#         if disease != '':
#             workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
#             r = process_ontology(workpath,disease)
#             # convert query output to DataFrame
#             belong_to = []
#             concept_has_uc = []
#             conc = []
#             description = {'provenance': 'EXAMODE', 'insertion_author': 'admin'}
#             desc = json.dumps(description)
#             with transaction.atomic():
#                 for e in r:
#                     if(e[0] is not None and e[1] is not None and e[2] is not None and e[3] is not None):
#                         belong_to.append((e[0].toPython(),e[3].toPython()))
#                         concept_has_uc.append((e[0].toPython(),usecase))
#                         conc.append((e[0].toPython(),e[1].toPython(),None))
#                         cursor.execute("SELECT json_concept FROM concept WHERE concept_url = %s",[e[0].toPython()])
#                         ans = cursor.fetchall()
#                         if len(ans) == 0:
#                             query = ("INSERT INTO concept (concept_url,json_concept, name) VALUES(%s,%s,%s);")
#                             values = (e[0].toPython(), desc,e[1].toPython())
#                             cursor.execute(query, values)
#                         else:
#                             for row in ans:
#                                 j_c = json.loads(row[0])
#                                 j_c['insertion_author'] = 'admin'
#                                 j_c['provenance'] = 'EXAMODE'
#                                 j_c = json.dumps(j_c)
#                                 cursor.execute("UPDATE concept SET json_concept = %s WHERE concept_url = %s",[j_c,e[0].toPython()])
#
#                         cursor.execute("SELECT * FROM belong_to WHERE concept_url = %s AND name = %s", [e[0].toPython(),e[3].toPython()])
#                         ans = cursor.fetchall()
#                         if len(ans) == 0:
#                             query1 = ("INSERT INTO belong_to (name, concept_url) VALUES(%s,%s);")
#                             values1 = (e[3].toPython(), e[0].toPython())
#                             cursor.execute(query1, values1)
#
#                         cursor.execute("SELECT * FROM concept_has_uc WHERE concept_url = %s AND name = %s",
#                                     [e[0].toPython(),usecase])
#                         ans = cursor.fetchall()
#                         if len(ans) == 0:
#                             query2 = ("INSERT INTO concept_has_uc (concept_url,name) VALUES(%s,%s);")
#                             values2 = (e[0].toPython(), usecase)
#                             cursor.execute(query2, values2)


def check_file(reports,pubmedfiles, labels, concepts, jsonDisp, jsonAnn, username, password,load_concepts,load_labels):

    """This method checks whether the inserted files complies with the requirements"""

    message = 'ok'
    json_resp = {}
    json_keys = []
    usecases_list = []
    json_resp['general_message'] = ''
    json_resp['username_message'] = ''
    json_resp['report_message'] = ''
    json_resp['pubmed_message'] = ''
    json_resp['concept_message'] = ''
    json_resp['label_message'] = ''
    json_resp['fields_message'] = ''
    json_resp['keys'] = json_keys

    # Error if the user has not inserted enough files
    if len(concepts) == 0 and load_concepts is None and load_labels is None and len(labels) == 0 and len(jsonAnn) == 0 and len(reports) > 0:
        json_resp[
            'general_message'] = 'ERROR - You must provide at least one file between labels and concepts or at least one field to annotate.'
    elif len(reports) == 0 and len(pubmedfiles) == 0:
        json_resp['general_message'] = 'ERROR - You must provide a file with one or more reports or one or more pubmed files.'
    elif len(pubmedfiles) > 0 and len(concepts) == 0 and load_concepts is None and load_labels is None and len(labels) == 0 and len(jsonAnn) == 0:
        json_resp['general_message'] = 'PUBMED - only mentions allowed.'

    try:

        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM public.user WHERE username = %s', (str(username),))
            ans = cursor.fetchall()
            # Error on username and password: duplicated username or missing
            if len(ans) > 0:
                json_resp['username_message'] = 'USERNAME - The username you selected is already taken. Choose another one.'
            if (username == ''):
                json_resp['username_message'] = 'USERNAME - Please, provide a username.'
            # if (email == ''):
            #     json_resp['username_message'] = 'EMAIL - Please, provide a valid email address.'
            if password == '' and username == '':
                json_resp['username_message'] = 'USERNAME - Please, provide a username and a password.'

        except (Exception, psycopg2.Error) as e:
            print(e)
            json_resp[
                'username_message'] = 'An error occurred handling the username and the password. Please, insert them again.'
            pass

        else:
            if json_resp['username_message'] == '':
                json_resp['username_message'] = 'Ok'

        # This is necessary to collect the fields to annotate and display
        fields = []
        fields_to_ann = []
        jsondisp = ''.join(jsonDisp)
        jsonann = ''.join(jsonAnn)
        jsondisp = jsondisp.split(',')
        jsonann = jsonann.split(',')

        for el in jsondisp:
            fields.append(el)
        for el in jsonann:
            if len(el) > 0:
                fields_to_ann.append(el)

        # Error if 0 report files are added
        if len(reports) == 0 and len(pubmedfiles) == 0:
            json_resp['report_message'] = 'REPORTS FILES - You must provide at least one file containing reports or at least one file containing PubMED IDs before checking'
            json_resp['pubmed_message'] = 'PUBMED FILES - You must provide at least one file containing reports or at least one file containing PubMED IDs before checking'

        for i in range(len(pubmedfiles)):

            # Error if the file is not csv
            if not pubmedfiles[i].name.endswith('csv'):
                json_resp['pubmed_message'] = 'PUBMED FILE - ' + pubmedfiles[i].name + ' - The file must be .csv'
                break

            try:
                df = pd.read_csv(pubmedfiles[i])
                df = df.where(pd.notnull(df), None)
                df = df.reset_index(drop=True)  # Useful if the csv includes only commas
            except Exception as e:
                print(e)
                json_resp['pubmed_message'] = 'PUBMED FILE - ' + pubmedfiles[
                    i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. Check if it contains as many columns as they are declared in the header.'
                pass

            else:
                # check if colunns are allowed and without duplicates
                cols = list(df.columns)
                list_db_col = ['ID', 'usecase']

                missing = False
                for el in list_db_col:
                    if el not in cols:
                        json_resp['pubmed_message'] = 'PUBMED FILE - ' + pubmedfiles[
                            i].name + ' - The column: ' + el + ' is missing, please add it.'
                        missing = True
                        break
                if missing:
                    break

                for column in cols:
                    null_val = df[df[column].isnull()].index.tolist()
                    if len(null_val) > 0:
                        json_resp['pubmed_message'] = 'PUBMED FILE - ' + pubmedfiles[
                            i].name + ' - You did not inserted the '+column +' for rows: '+null_val.split(', ')

                if 'usecase' in cols:
                    df['usecase']=df['usecase'].str.lower()


                # usecases_list = df.usecase.unique()
                for el in df.usecase.unique():
                    if el not in usecases_list:
                        usecases_list.append(el)

                # Check if the csv is empty with 0 rows
                if df.shape[0] == 0:
                    json_resp['pubmed_message'] = 'PUBMED FILE - ' + pubmedfiles[
                        i].name + ' -  You must provide at least a report.'
                    break
                else:
                    # check if columns id_report and language have no duplicates
                    df_dup = df[df.duplicated(subset=['ID', 'usecase'], keep=False)]
                    # print(df_dup.loc[:, 'id_report'])
                    if df_dup.shape[0] > 0:
                        json_resp['pubmed_message'] = 'WARNING PUBMED FILE - ' + pubmedfiles[
                            i].name + ' - The rows: ' + str(
                            df_dup.index.to_list()) + ' are duplicated. The duplicates are ignored.'

        if len(pubmedfiles)>0:
            if json_resp['pubmed_message'] == '':
                json_resp['pubmed_message'] = 'Ok'
                

        for i in range(len(reports)):

            # Error if the file is not csv
            if not reports[i].name.endswith('csv'):
                json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - The file must be .csv'
                break

            try:
                df = pd.read_csv(reports[i])
                df = df.where(pd.notnull(df), None)
                df = df.reset_index(drop=True)  # Useful if the csv includes only commas
            except Exception as e:
                print(e)
                json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                    i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. Check if it contains as many columns as they are declared in the header.'
                pass

            else:
                # check if colunns are allowed and without duplicates
                cols = list(df.columns)
                list_db_col = ['id_report', 'institute', 'usecase', 'language']
                list_not_db_col = []

                missing = False
                for el in list_db_col:
                    if el not in cols:
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                            i].name + ' - The column: ' + el + ' is missing, please add it.'
                        missing = True
                        break
                if missing:
                    break


                for el in cols:
                    if el not in list_db_col:
                        list_not_db_col.append(el)

                if 'usecase' in cols:
                    df['usecase'] = df['usecase'].str.lower()
                if 'institute' in cols:
                    df['institute'] = df['institute'].str.lower()

                for el in df.institute.unique():
                    if el.lower() == 'pubmed':
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                            i].name + ' - calling an institute "PUBMED" is forbidden, please, change the name'

                for el in df.id_report:
                    if el.lower().startswith('pubmed_'):
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                            i].name + ' - reports\' ids can not start with "PUBMED_", please, change the name'
                # usecases_list = df.usecase.unique()
                for el in df.usecase.unique():
                    if el not in usecases_list:
                        usecases_list.append(el)

                # if 0 optional columns are added
                if len(list_not_db_col) == 0:
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - You must provide at least one column other than institute, usecase, language, id_report'
                    break

                # Check if the csv is empty with 0 rows
                if df.shape[0] == 0:
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                        i].name + ' -  You must provide at least a report.'
                    break
                else:
                    # check if columns id_report and language have no duplicates
                    df_dup = df[df.duplicated(subset=['id_report', 'language'], keep=False)]
                    # print(df_dup.loc[:, 'id_report'])
                    if df_dup.shape[0] > 0:
                        json_resp['report_message'] = 'WARNING REPORTS FILE - ' + reports[
                            i].name + ' - The rows: ' + str(
                            df_dup.index.to_list()) + ' are duplicated. The duplicates are ignored.'

                # Check if the optional rows are empty for one or more reports.
                exit = False
                for ind in range(df.shape[0]):

                    count_both = 0

                    not_none_cols = []
                    isnone = True
                    for el in list_not_db_col:
                        if df.loc[ind, el] is not None:
                            isnone = False
                            not_none_cols.append(el)

                    for el in not_none_cols:
                        if el not in jsonann and el not in jsondisp:
                            count_both = count_both + 1

                    if count_both == len(not_none_cols):
                        json_resp['fields_message'] = 'WARNING REPORT FIELDS TO DISPLAY AND ANNOTATE - ' + reports[
                            i].name + ' -  With this configuration the report at the row: ' + str(
                            ind) + ' would not be displayed since the columns to display are all empty for that report.'

                    if isnone:
                        exit = True
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                            i].name + ' -  The report at row ' + str(ind) + ' has the columns: ' + ', '.join(
                            list_not_db_col) + ' empty. Provide a value for at least one of these columns.'
                        break
                if exit == True:
                    break

                # check if there are None in mandatory columns
                el = ''
                if None in df['usecase'].tolist():
                    el = 'usecase'
                elif None in df['institute'].tolist():
                    el = 'institute'
                elif None in df['language'].tolist():
                    el = 'language'
                elif None in df['id_report'].tolist():
                    el = 'id_report'
                if el != '':
                    lista = df[el].tolist()
                    ind = lista.index(None)
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                        i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                    break
        if len(reports)>0:
            if json_resp['report_message'] == '':
                json_resp['report_message'] = 'Ok'

        if (len(concepts) > 0):
            for i in range(len(concepts)):
                # Check if it is a csv
                if not concepts[i].name.endswith('csv'):
                    json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[i].name + ' - The file must be .csv'

                try:
                    df = pd.read_csv(concepts[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True)
                except Exception as e:
                    json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                        i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. '
                    pass
                # print(df)
                else:

                    cols = list(df.columns)
                    columns_wrong = False
                    list_db_col = ['concept_url', 'concept_name', 'usecase', 'area']
                    if 'usecase' in cols:
                        df['usecase'] = df['usecase'].str.lower()

                    # Check if all the mandatory cols are present
                    for el in list_db_col:
                        if el not in cols:
                            columns_wrong = True
                            json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                                i].name + ' - The column ' + el + ' is not present. The only columns allowed are: concept_utl, concept_name, usecase, area'
                            break
                    if columns_wrong == True:
                        break



                    # header length must be the same, no extra columns
                    if len(list_db_col) != len(cols):
                        json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                            i].name + ' - The columns allowed are: concept_url, concept_name, usecase, area. If you inserted more (less) columns please, remove (add) them.'
                        break

                    # Check if the df has no rows
                    if df.shape[0] == 0:
                        json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                            i].name + ' - You must provide at least a concept.'
                        break
                    else:
                        # check if column concept_url has no duplicates
                        df_dup = df[df.duplicated(subset=['concept_url', 'usecase', 'area'], keep=False)]
                        if df_dup.shape[0] > 0:
                            json_resp['concept_message'] = 'WARNING CONCEPTS FILE - ' + concepts[
                                i].name + ' - The rows: ' + str(
                                df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'

                        # Check if there are None in mandatory cols
                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['concept_url'].tolist():
                            el = 'concept_url'
                        elif None in df['concept_name'].tolist():
                            el = 'concept_name'
                        elif None in df['area'].tolist():
                            el = 'area'
                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                                i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + ' .'
                            break

                        # warning if there are new use cases
                        for el in df.usecase.unique():
                            if el not in usecases_list and el is not None:
                                json_resp['concept_message'] = 'WARNING CONCEPTS FILE - ' + concepts[
                                    i].name + ' - The usecase ' + el + ' has not any report associated. It\'ok but you can not use the concepts until you have inserted a report with that use case.'

            if json_resp['concept_message'] == '':
                json_resp['concept_message'] = 'Ok'

        if (len(labels) > 0):
            for i in range(len(labels)):
                if not labels[i].name.endswith('csv'):
                    json_resp['label_message'] = 'LABELS FILE - ' + labels[i].name + ' - The file must be .csv'
                try:
                    df = pd.read_csv(labels[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True)

                except Exception as e:
                    json_resp['label_message'] = 'LABELS FILE - ' + labels[
                        i].name + ' - An error occurred while parsing the csv. Check if is well formatted.'
                    pass
                # print(df)
                else:

                    cols = list(df.columns)
                    list_db_col = ['label', 'usecase']
                    if 'usecase' in cols:
                        df['usecase'] = df['usecase'].str.lower()

                    esco = False
                    for el in list_db_col:
                        if el not in cols:
                            esco = True
                            json_resp['label_message'] = 'LABELS FILE - ' + labels[
                                i].name + ' - The columns: ' + el + ' is not present. The columns allowed are: labels, usecase.'

                    if esco == True:
                        break

                    if len(cols) != len(list_db_col):
                        json_resp['label_message'] = 'LABELS FILE - ' + labels[
                            i].name + ' - The columns allowed are: label, usecase. If you inserted more (less) columns please, remove (add) them.'
                        break

                    if df.shape[0] == 0:
                        json_resp['label_message'] = 'LABELS FILE - ' + labels[
                            i].name + ' - You must provide at least a row.'
                        break
                    else:
                        # check if columns annotation_label and name have no duplicates
                        df_dup = df[df.duplicated(subset=['label', 'usecase'], keep=False)]
                        if df_dup.shape[0] > 0:
                            json_resp['label_message'] = 'WARNING LABELS FILE - ' + labels[
                                i].name + ' - The rows: ' + str(
                                df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'

                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['label'].tolist():
                            el = 'label'
                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            json_resp['label_message'] = 'LABELS FILE - ' + labels[
                                i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + ' .'
                            break

                        for el in df.usecase.unique():
                            if el not in usecases_list:
                                json_resp['label_message'] = 'WARNING LABELS FILE - ' + labels[
                                    i].name + ' - The use case ' + el + ' has not any report associated. It\'s ok, but you need some reports associated to that use case if you want to use the labels.'

            if json_resp['label_message'] == '':
                json_resp['label_message'] = 'Ok'

        if len(jsonAnn) == 0 and len(jsonDisp) == 0 and len(reports)>0:
            json_resp[
                'fields_message'] = 'REPORT FIELDS TO DISPLAY AND ANNOTATE - Please provide at least one field to be displayed and/or at least one field to be annotated.'

        elif len(jsonAnn) == 0  and len(reports)>0:
            if json_resp['fields_message'] == '':
                json_resp[
                    'fields_message'] = 'WARNING REPORT FIELDS TO ANNOTATE - ok but with this configuration you will not be able to perform mention annotation and linking. Please, select also at least a field to annotate if you want to find some mentions and link them.'

        if len(reports) > 0:
            if json_resp['fields_message'] == '':
                json_resp['fields_message'] = 'Ok'

    except Exception as e:
        print(e)
        json_resp['general_message'] = 'An error occurred. Please check if it is similar to the example we provided.'

        return json_resp

    else:
        if json_resp['general_message'] == '':
            json_resp['general_message'] = 'Ok'
        return json_resp

import time
def configure_data(pubmedfiles,reports, labels, concepts, jsondisp, jsonann, jsonall, username, password, load_concepts,load_labels):

    """This method is run after having checked the files inserted by the user"""

    filename = ''
    error_location = 'database'
    report_usecases = []
    created_file = False

    try:
        with transaction.atomic():
            cursor = connection.cursor()

            cursor.execute("DELETE FROM annotate;")
            cursor.execute("DELETE FROM linked;")
            cursor.execute("DELETE FROM associate;")
            cursor.execute("DELETE FROM contains;")
            cursor.execute("DELETE FROM mention;")
            cursor.execute("DELETE FROM belong_to;")
            cursor.execute("DELETE FROM concept_has_uc;")
            cursor.execute("DELETE FROM annotation_label;")
            cursor.execute("DELETE FROM concept;")
            cursor.execute("DELETE FROM ground_truth_log_file;")
            cursor.execute("DELETE FROM report;")
            cursor.execute("DELETE FROM use_case;")
            cursor.execute("DELETE FROM semantic_area;")
            # connection.commit()

            cursor.execute("DELETE FROM public.user WHERE username = 'Test'")
            if username is not None and password is not None:
                cursor.execute("INSERT INTO public.user (username,password,profile,ns_id) VALUES(%s,%s,%s,%s);",
                               (str(username), hashlib.md5(str(password).encode()).hexdigest(), 'Admin', 'Human'))
                cursor.execute("INSERT INTO public.user (username,password,profile,ns_id) VALUES(%s,%s,%s,%s);",
                               (str(username), hashlib.md5(str(password).encode()).hexdigest(), 'Admin', 'Robot'))

            fields = []
            all_fields = []
            fields_to_ann = []

            jsonall = ''.join(jsonall)
            jsondisp = ''.join(jsondisp)
            jsonann = ''.join(jsonann)

            jsonall = jsonall.split(',')
            jsondisp = jsondisp.split(',')
            jsonann = jsonann.split(',')
            if load_labels is not None:
                load_labels = ''.join(load_labels)
                load_labels = load_labels.split(',')
            if load_concepts is not None:
                load_concepts = ''.join(load_concepts)

                load_concepts = load_concepts.split(',')

            for el in jsonall:
                all_fields.append(el)
            for el in jsondisp:
                fields.append(el)
            for el in jsonann:
                if len(el) > 0:
                    fields_to_ann.append(el)

            error_location = 'Pubmed'
            for pubfile in pubmedfiles:
                df_pubmed = pd.read_csv(pubfile)
                df_pubmed = df_pubmed.where(pd.notnull(df_pubmed), None)
                df_pubmed = df_pubmed.reset_index(drop=True)
                # print(df_report)

                df_pubmed['pubmed'] = df_pubmed['usecase'].str.lower()

                usecases = df_pubmed.usecase.unique()
                for el in usecases:
                    if el not in report_usecases:
                        report_usecases.append(el.lower())
                    cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(el).lower(),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute('INSERT INTO use_case VALUES(%s)', (str(el).lower(),))

                list_col_mandatory = ['ID', 'usecase']
                count_rows = df_pubmed.shape[0]
                i = 0
                var = True

                # print(count_rows)
                while var:
                    st = time.time()
                    for count in range(3):
                        count = count + 1
                        id_report_original = str(df_pubmed.loc[i, 'ID'])
                        id_report = 'PUBMED_' + str(id_report_original)
                        name = str(df_pubmed.loc[i, 'usecase'])
                        report_json = insert_articles_of_PUBMED(id_report_original)
                        if 'error' in report_json.keys():
                            return report_json
                        report_json = json.dumps(report_json)
                        # Duplicates are not inserted
                        cursor.execute("SELECT * FROM report WHERE id_report = %s AND language = %s;",
                                       (str(id_report), 'English'))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute(
                                "INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);",
                                (str(id_report), report_json, 'PUBMED', 'English', str(name).lower()))

                        i = i + 1
                        # print(count)
                        # print(i)

                        if count_rows == i:
                            var = False
                            break

                    try:
                        time.sleep(1 - (time.time() - st))
                    except Exception as e:
                        print(e)
                        pass


            error_location = 'Reports'
            for report in reports:
                df_report = pd.read_csv(report)
                df_report = df_report.where(pd.notnull(df_report), None)
                df_report = df_report.reset_index(drop=True)
                # print(df_report)
                df_report['usecase'] = df_report['usecase'].str.lower()
                df_report['institute'] = df_report['institute'].str.lower()

                usecases = df_report.usecase.unique()
                for el in usecases:

                    if el not in report_usecases:
                        report_usecases.append(el)
                    cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(el).lower(),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute('INSERT INTO use_case VALUES(%s)', (str(el).lower(),))

                list_col_mandatory = ['id_report', 'institute', 'usecase', 'language']
                list_col_not_mandatory = []
                for col in df_report:
                    if col not in list_col_mandatory:
                        list_col_not_mandatory.append(col)

                # 30062021
                # df_report_filtered = df_report.loc[df_report['usecase'].lower() == 'Colon']
                #
                count_rows = df_report.shape[0]
                for i in range(count_rows):
                    id_report = str(df_report.loc[i, 'id_report'])
                    # id_report = rep_count_id
                    # rep_count_id +=1
                    institute = str(df_report.loc[i, 'institute'])

                    language = str(df_report.loc[i, 'language'])
                    name = str(df_report.loc[i, 'usecase'])
                    report_json = {}

                    # Check if all the not mandatory cols have at least one value != None
                    found = False
                    for col in list_col_not_mandatory:
                        if df_report.loc[i, col] is not None:
                            # col1 = col.replace(' ','_')
                            # report_json[col1] = str(df_report.loc[i,col])
                            col1 = col.replace(' ', '_')
                            testo = str(df_report.loc[i, col])
                            filtered_characters = list(s for s in testo if s.isprintable())
                            testo = ''.join(filtered_characters)
                            report_json[col1] = testo

                    report_json = json.dumps(report_json)
                    # Duplicates are not inserted
                    cursor.execute("SELECT * FROM report WHERE id_report = %s AND language = %s;",
                                   (str(id_report), str(language)))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute(
                            "INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);",
                            (str(id_report), report_json, str(institute), str(language), str(name.lower())))

            # Popolate the labels table
            # print(load_labels)
            # if load_labels != '' and load_labels != [] and load_labels is not None:
            configure_labels(cursor,load_labels)
            if len(labels) > 0:
                error_location = 'Labels'
                for label_file in labels:
                    df_labels = pd.read_csv(label_file)
                    df_labels = df_labels.where(pd.notnull(df_labels), None)
                    df_labels = df_labels.reset_index(drop=True)
                    df_labels['usecase'] = df_labels['usecase'].str.lower()
                    count_lab_rows = df_labels.shape[0]
                    for i in range(count_lab_rows):
                        # cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);", (df_labels.loc[i, df_labels.columns[0]],df_labels.loc[i, df_labels.columns[1]],df_labels.loc[i, df_labels.columns[2]]))
                        label = str(df_labels.loc[i, 'label'])
                        name = str(df_labels.loc[i, 'usecase'])
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name).lower(),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name).lower(),))

                        cursor.execute('SELECT * FROM annotation_label')
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            seq_number = 1
                        else:
                            cursor.execute('SELECT seq_number FROM annotation_label ORDER BY seq_number DESC;')
                            ans = cursor.fetchall()
                            # print(ans[0][0])

                            seq_number = int(ans[0][0]) + 1

                        count = get_labels_exa_count()
                        cursor.execute("SELECT * FROM annotation_label WHERE seq_number > %s AND name = %s AND label = %s;",
                                       (int(count), str(name), str(label).lower()))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);",
                                           (str(label), int(seq_number), str(name).lower()))

            # Popolate the concepts table
            error_location = 'Concepts'
            if load_concepts is not None and load_concepts != '' and load_concepts !=[] and len(concepts) == 0:
                configure_concepts(cursor,load_concepts,'admin')
            for concept_file in concepts:
                df_concept = pd.read_csv(concept_file)
                df_concept = df_concept.where(pd.notnull(df_concept), None)
                df_concept = df_concept.reset_index(drop=True)
                df_concept['usecase'] = df_concept['usecase'].str.lower()

                # print(df_concept)
                count_conc_rows = df_concept.shape[0]
                list_uc_concept = df_concept.usecase.unique()
                list_area_concept = df_concept.area.unique()

                for name in list_uc_concept:
                    cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name).lower(),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name).lower(),))

                for el in list_area_concept:
                    cursor.execute('SELECT * FROM semantic_area WHERE name = %s', (str(el),))
                    if len(cursor.fetchall()) == 0:
                        cursor.execute('INSERT INTO semantic_area VALUES (%s)', (str(el),))

                for i in range(count_conc_rows):
                    df_concept = df_concept.where(pd.notnull(df_concept), None)
                    concept_url = str(df_concept.loc[i, 'concept_url'])
                    concept_name = str(df_concept.loc[i, 'concept_name'])
                    usecase = str(df_concept.loc[i, 'usecase'])
                    semantic_area = str(df_concept.loc[i, 'area'])

                    cursor.execute("SELECT concept_url,json_concept FROM concept WHERE concept_url = %s;",
                                   (str(concept_url),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        json_concept = json.dumps({'provenance': 'admin', 'insertion_author': 'admin'})
                        cursor.execute("INSERT INTO concept (concept_url,name,json_concept) VALUES (%s,%s,%s);",
                                       (str(concept_url), str(concept_name), json_concept))

                    # se c'è già significa che è stato inserito automaticamente quindi. tolgo robot e metto e admin come author così so quale prendere
                    else:
                        for el in ans:
                            # print(el)
                            desc = el[1]
                            desc = json.loads(desc)
                            if desc['insertion_author'] != 'admin':
                                desc['insertion_author'] = 'admin'
                                desc = json.dumps(desc)
                                cursor.execute('UPDATE concept SET json_concept = %s WHERE concept_url = %s', [desc, el[0]])

                    cursor.execute("SELECT * FROM concept_has_uc WHERE concept_url = %s AND name = %s;",
                                   (str(concept_url), str(usecase).lower()))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute("INSERT INTO concept_has_uc (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(usecase)))

                    cursor.execute("SELECT * FROM belong_to WHERE concept_url = %s AND name=%s;",
                                   (str(concept_url), str(semantic_area)))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute("INSERT INTO belong_to (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(semantic_area)))

            data = {}
            data['fields'] = fields
            data['fields_to_ann'] = fields_to_ann
            data['all_fields'] = all_fields
            version = get_version()
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            version_new = int(version) + 1
            filename = 'fields' + str(version_new)
            created_file = False
            with open(os.path.join(workpath, './data/' + filename + '.json'), 'w') as outfile:
                json.dump(data, outfile)
                created_file = True

    except (Exception, psycopg2.Error) as e:
        print(e)
        print('rollback')
        # connection.rollback()
        if created_file == True:
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            if filename != '' and filename != 'fields0':
                path = os.path.join(workpath, './data/' + filename + '.json')
                os.remove(path)
        json_resp = {'error': 'an error occurred in: ' + error_location + '.'}
        return json_resp
    else:
        # connection.commit()
        if created_file == True:

            for filen in os.listdir(os.path.join(workpath, './data')):
                if filen.endswith('json'):
                    print(filen)
                    if filen != '' and filen != 'fields0.json' and filen != filename+'.json':
                        path = os.path.join(workpath, './data/' + filen )
                        os.remove(path)
        outfile.close()
        json_resp = {'message': 'Ok'}
        return json_resp

#-------------------UPDATE----------------------------


def check_for_update(type_req,pubmedfiles, reports, labels, concepts, areas, usecase, jsonDisp, jsonAnn, jsonDispUp, jsonAnnUp,load_concepts,load_labels):

    """This method checks the files inserted by the user to update the db"""

    usecases = []
    sem_areas = []
    json_keys = []
    keys = get_fields_from_json()
    ann = keys['fields_to_ann']
    disp = keys['fields']

    if (jsonDispUp is not None and jsonAnnUp is not None):
        jsonDispUp = ''.join(jsonDispUp)
        jsonAnnUp = ''.join(jsonAnnUp)
        jsonDispUp = jsonDispUp.split(',')
        jsonAnnUp = jsonAnnUp.split(',')

    try:

        cursor = connection.cursor()
        distinct_uc_report = []
        cursor.execute("SELECT * FROM use_case")
        ans = cursor.fetchall()
        for el in ans:
            if el[0] not in usecases:
                usecases.append(el[0])

        cursor.execute("SELECT * FROM semantic_area")
        ans = cursor.fetchall()
        for el in ans:
            if el[0] not in sem_areas:
                sem_areas.append(el[0])

        cursor.execute("SELECT DISTINCT name FROM report")
        ans = cursor.fetchall()
        for el in ans:
            distinct_uc_report.append(el[0])
        message = ''

        if len(concepts) > 0:

            message = ''
            for i in range(len(concepts)):
                if not concepts[i].name.endswith('csv'):
                    message = 'CONCEPTS FILE - ' + concepts[i].name + ' - The file must be .csv'
                    return message

                try:
                    df = pd.read_csv(concepts[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True)

                except Exception as e:
                    message = 'CONCEPTS FILE - ' + concepts[
                        i].name + ' - An error occurred while parsing the csv. Check if it is well formatted.'
                    return message
                else:
                    list_db_col = ['concept_url', 'concept_name', 'usecase', 'area']
                    cols = list(df.columns)

                    for el in list_db_col:
                        if el not in cols:
                            message = 'CONCEPTS FILE - ' + concepts[
                                i].name + ' - The columns: ' + el + ' is missing. Please, add it.'
                            return message

                    if 'usecase' in cols:
                        df['usecase'] = df['usecase'].str.lower()

                    if len(list_db_col) != len(cols):
                        message = 'CONCEPTS FILE - ' + concepts[
                            i].name + ' - The columns allowed are: concept_url, concept_name, usecase, area. If you inserted more (less) columns please, remove (add) them.'
                        return message

                    if df.shape[0] == 0:
                        message = 'CONCEPTS FILE - ' + concepts[i].name + ' - You must provide at least a concept.'
                        return message
                    else:
                        # duplicates in file
                        df_dup = df[df.duplicated(subset=['concept_url', 'usecase', 'area'], keep=False)]
                        if df_dup.shape[0] > 0:
                            message = 'WARNING CONCEPTS FILE - ' + concepts[i].name + ' - The rows: ' + str(
                                df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'

                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['concept_url'].tolist():
                            el = 'concept_url'
                        elif None in df['concept_name'].tolist():
                            el = 'concept_name'
                        elif None in df['area'].tolist():
                            el = 'area'
                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            message = 'CONCEPTS FILE - ' + concepts[
                                i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                            return message

                        distinct_concept_usecase = df['usecase'].unique()
                        for el in distinct_concept_usecase:
                            el = el.lower()
                            if el in ['colon','uterine cervix','lung']:
                                bool_arr = check_exa_lab_conc_only(str(el))
                                if bool_arr[1] == True:
                                    message = ' WARNING CONCEPTS FILE - ' + concepts[
                                        i].name + ' - You are using EXAMODE concepts for the use case '+str(el) + '. Uploading new concepts will remove the existing ones together with all the annotatiions. The action is irreversible.'

                            if el not in distinct_uc_report:
                                message = 'WARNING CONCEPTS FILE - ' + concepts[
                                    i].name + ' - The file contains the concepts for the use case ' + el + ' which has 0 reports associated.'

                        # Check for duplicates in db
                        for ind in range(df.shape[0]):
                            cursor.execute('SELECT COUNT(*) FROM concept WHERE concept_url = %s',
                                           [str(df.loc[ind, 'concept_url'])])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING CONCEPTS FILE - ' + concepts[i].name + ' - The concept: ' + str(
                                    df.loc[
                                        ind, 'concept_url']) + ' is already present in the database. It will be ignored.'

                return message


        elif len(labels) > 0:

            message = ''
            for i in range(len(labels)):
                if not labels[i].name.endswith('csv'):
                    message = 'LABELS FILE - ' + labels[i].name + ' - The file must be .csv'
                    return message

                try:
                    df = pd.read_csv(labels[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True)

                except Exception as e:
                    message = 'LABELS FILE - ' + labels[
                        i].name + ' - An error occurred while parsing the csv. Check if is well formatted.'
                    return message
                else:
                    cols = list(df.columns)
                    list_db_col = ['label', 'usecase']
                    if 'usecase' in cols:
                        df['usecase'] = df['usecase'].str.lower()
                        # print(df)
                    for el in list_db_col:
                        if el not in cols:
                            message = 'LABELS FILE - ' + labels[
                                i].name + ' - The columns: ' + el + 'is missing. The columns allowed are: label, usecase.'
                            return message

                    if len(list_db_col) != len(cols):
                        message = 'LABELS FILE - ' + labels[
                            i].name + ' - The columns allowed are: label, usecase. If you inserted more (less) columns please, remove (add) them.'
                        return message

                    if df.shape[0] == 0:
                        message = 'LABELS FILE - You must provide at least a row.'
                        return message

                    else:

                        df_dup = df[df.duplicated(subset=['label', 'usecase'], keep=False)]
                        if df_dup.shape[0] > 0:
                            message = 'WARNING LABELS FILE - ' + labels[
                                i].name + ' - The rows: ' + str(
                                df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'

                        for ind in range(df.shape[0]):
                            cursor.execute('SELECT COUNT(*) FROM annotation_label WHERE label = %s AND name = %s AND seq_number > %s',
                                           [str(df.loc[ind, 'label']), str(df.loc[ind, 'usecase']),20])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING LABELS FILE - ' + labels[i].name + ' - The label: ' + str(
                                    df.loc[ind, 'label']) + ' for the use case: ' + str(
                                    df.loc[ind, 'usecase']) + ' is already present in the database. It will be ignored.'

                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['label'].tolist():
                            el = 'label'

                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            message = 'LABELS FILE - ' + labels[
                                i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + ' .'
                            return message

                        distinct_label_usecase = df['usecase'].unique()
                        for el in distinct_label_usecase:
                            if el in ['colon', 'uterine cervix', 'lung']:
                                bool_arr = check_exa_lab_conc_only(str(el))
                                if bool_arr[0] == True:
                                    message = ' WARNING LABELS FILE - ' + labels[
                                        i].name + ' - You are using EXAMODE labels for the use case ' + str(
                                        el) + '. Uploading new labels will remove the existing ones together with all the annotatiions. The action is irreversible.'

                            if el not in distinct_uc_report:
                                message = 'WARNING LABELS FILE - ' + labels[
                                    i].name + ' - The file contains the labels for ' + el + ' which has 0 reports associated.'

                return message

        elif len(pubmedfiles) > 0:
            message = ''
            for i in range(len(pubmedfiles)):
                if not pubmedfiles[i].name.endswith('csv'):
                    message = 'PUBMED FILE - ' + pubmedfiles[i].name + ' - The file must be .csv'
                    return message

                try:
                    df = pd.read_csv(pubmedfiles[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True)
                    # somma = df.notnull().sum(axis=1)
                    # somma_null = df.isnull().sum(axis=1)
                    # print(somma)
                    # print(somma_null)
                    # print(type(somma))
                except Exception as e:
                    message = 'PUBMED FILE - ' + reports[
                        i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. '
                    return message
                else:
                    cols = list(df.columns)
                    count = 0
                    if 'usecase' in cols:
                        df['usecase']=df['usecase'].str.lower()
                    # print(cols)
                    list_db_col = ['ID', 'usecase']
                    for el in list_db_col:
                        if el not in cols:
                            message = 'PUBMED FILE - ' + pubmedfiles[i].name + ' - The column: ' + str(
                                el) + ' must be present.'
                            return message

                    for el in cols:
                        if el not in list_db_col:
                            message = 'PUBMED FILE - ' + pubmedfiles[i].name + ' - The column: ' + str(
                                el) + ' is not allowed.'
                            return message


                    if df.shape[0] == 0:
                        message = 'PUBMED FILE - ' + pubmedfiles[i].name + ' -  You must provide at least a report.'
                        return message
                    else:
                        df_dup = df[df.duplicated(subset=['ID', 'usecase'], keep=False)]
                        if df_dup.shape[0] > 0:
                                message = 'WARNING PUBMED FILE - ' + pubmedfiles[i].name + ' - The rows: ' + str(
                                df_dup.index.to_list()) + ' are duplicated. The duplicates are ignored.'

                        for ind in range(df.shape[0]):
                            found = False
                            id_report = 'PUBMED_'+str(df.loc[ind, 'ID'])
                            cursor.execute('SELECT COUNT(*) FROM report WHERE id_report = %s AND language = %s',
                                           [str(id_report), 'English'])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING PUBMED FILE - ' + pubmedfiles[i].name + ' - The report: ' + str(
                                    id_report) + ' is already present in the database. It will be ignored.'

                            for el in list_db_col:
                                if df.loc[ind, el] is not None:
                                    found = True
                                    break

                            if found == False:
                                message = 'PUBMED FILE - ' + pubmedfiles[i].name + ' -  The report at row ' + str(
                                    ind) + ' has the columns: ' + ', '.join(
                                    list_db_col) + ' empty. Provide a value for at least one of these columns.'
                                return message


                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['ID'].tolist():
                            el = 'institute'

                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            message = 'PUBMED FILE - ' + pubmedfiles[
                                i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                            return message

        elif len(reports) > 0:
            message = ''
            for i in range(len(reports)):
                if not reports[i].name.endswith('csv'):
                    message = 'REPORTS FILE - ' + reports[i].name + ' - The file must be .csv'
                    return message

                try:
                    df = pd.read_csv(reports[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True)

                    # somma = df.notnull().sum(axis=1)
                    # somma_null = df.isnull().sum(axis=1)
                    # print(somma)
                    # print(somma_null)
                    # print(type(somma))
                except Exception as e:
                    message = 'REPORTS FILE - ' + reports[
                        i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. '
                    return message
                else:
                    cols = list(df.columns)
                    count = 0
                    if 'usecase' in cols:
                        df['usecase']=df['usecase'].str.lower()
                    if 'institute' in cols:
                        df['institute']=df['institute'].str.lower()

                    # print(cols)
                    list_db_col = ['id_report', 'institute', 'usecase', 'language']
                    for el in list_db_col:
                        if el not in cols:
                            message = 'REPORTS FILE - ' + reports[i].name + ' - The column: ' + str(
                                el) + ' must be present.'
                            return message

                    if 'usecase' in cols:
                        df['usecase']=df['usecase'].str.lower()
                    if 'institute' in cols:
                        df['institute']=df['institute'].str.lower()

                    list_not_db_col = []
                    for el in cols:
                        if el not in list_db_col:
                            list_not_db_col.append(el)

                    if (jsonDispUp is not None and jsonAnnUp is not None):
                        if (len(disp) > 0 or len(ann) > 0):
                            disp_intersect = list(set(disp) & set(list_not_db_col))
                            ann_intersect = list(set(ann) & set(list_not_db_col))
                            for el in list_not_db_col:
                                if (el not in disp and el not in ann) and (
                                        el not in jsonDispUp and el not in jsonAnnUp):
                                    count = count + 1
                            if count == len(list_not_db_col):
                                message = 'REPORT FIELDS - Please, provide at least one field to display in file: ' + \
                                          reports[
                                              i].name + '. Be careful that if you do not provide one field to annotate you will not be able to perform mention annotation and linking.'
                                return message
                            elif len(ann_intersect) == 0 and (jsonAnnUp[0]) == '':
                                message = 'WARNING REPORT FIELDS - file: ' + reports[
                                    i].name + ' Please, provide at least one field to annotate if you want to find mentions and perform linking.'

                    if len(list_not_db_col) == 0:
                        message = 'REPORTS FILE - ' + reports[
                            i].name + ' - You must provide at least one column other than institute, usecase, language, id_report'
                        return message

                    if df.shape[0] == 0:
                        message = 'REPORTS FILE - ' + reports[i].name + ' -  You must provide at least a report.'
                        return message
                    else:
                        df_dup = df[df.duplicated(subset=['id_report', 'language'], keep=False)]
                        if df_dup.shape[0] > 0:
                            message = 'WARNING REPORTS FILE - ' + reports[i].name + ' - The rows: ' + str(
                                df_dup.index.to_list()) + ' are duplicated. The duplicates are ignored.'

                        for ind in range(df.shape[0]):
                            found = False
                            cursor.execute('SELECT COUNT(*) FROM report WHERE id_report = %s AND language = %s',
                                           [str(df.loc[ind, 'id_report']), str(df.loc[ind, 'language'])])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING REPORT FILE - ' + reports[i].name + ' - The report: ' + str(
                                    df.loc[ind, 'id_report']) + ' for the language: ' + str(df.loc[
                                                                                                ind, 'language']) + ' is already present in the database. It will be ignored.'

                            for el in list_db_col:
                                if df.loc[ind, el] is not None:
                                    found = True
                                    break

                            if found == False:
                                message = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(
                                    ind) + ' has the columns: ' + ', '.join(
                                    list_db_col) + ' empty. Provide a value for at least one of these columns.'
                                return message

                            found = False
                            count_both = 0
                            not_none_cols = []

                            for el in list_not_db_col:
                                if df.loc[ind, el] is not None:
                                    found = True
                                    not_none_cols.append(el)

                            if found == False:
                                message = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(
                                    ind) + ' has the columns: ' + ', '.join(
                                    list_not_db_col) + ' empty. Provide a value for at least one of these columns, or delete this report from the csv file.'
                                return message

                            for el in not_none_cols:
                                if jsonAnnUp is not None and jsonDispUp is not None:
                                    if el not in disp and el not in jsonDispUp and el not in ann and el not in jsonAnnUp:
                                        count_both = count_both + 1

                                else:
                                    if el not in disp and el not in ann:
                                        count_both = count_both + 1

                            if count_both == len(not_none_cols):
                                message = 'WARNING REPORT FIELDS TO DISPLAY AND ANNOTATE - ' + reports[
                                    i].name + ' -  With the current configuration the report at the row: ' + str(
                                    ind) + ' would not be displayed since the columns to display are all empty for that report.'

                        for el in df.institute.unique():
                            if el.lower() == 'pubmed':
                                message = 'REPORTS FILE - ' + reports[
                                    i].name + ' - calling an institute "PUBMED" is forbidden, please, change the name'

                        for el in df.id_report:
                            if el.lower().startswith('pubmed_'):
                                message = 'REPORTS FILE - ' + reports[
                                    i].name + ' - reports\' ids can not start with "PUBMED_", please, change the name'
                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['institute'].tolist():
                            el = 'institute'
                        elif None in df['language'].tolist():
                            el = 'language'
                        elif None in df['id_report'].tolist():
                            el = 'id_report'
                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            message = 'REPORTS FILE - ' + reports[
                                i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                            return message

        if jsonAnn is not None and jsonDisp is not None:
            if (type_req == 'json_fields' and len(jsonAnn) == 0) and len(jsonDisp) == 0 and len(ann) == 0:
                message = 'REPORT FIELDS TO ANNOTATE - You must provide at least one field to display and/or one field to display and annotate.'
                return message

            elif (type_req == 'json_fields' and len(jsonAnn) == 0):
                message = 'WARNING REPORT FIELDS TO ANNOTATE - ok, but with this configuration you will not be able to perform mention annotation and linking. Please, select also at least a field to annotate if you want to find some mentions and link them'
                return message
        # if jsonAnnUp is not None and jsonDispUp is not None:
        #     if type_req == 'reports' and len(jsonAnnUp) == 0 and len(jsonDispUp) == 0:
        #         message = 'REPORT FIELDS - You must provide at least one field to display and/or one field to display and annotate.'
        #         return message

        if type_req == 'labels' and len(labels) == 0 and (load_labels) is None:
            message = 'LABELS - Please insert a labels file.'
            return message

        if type_req == 'concepts' and len(concepts) == 0 and (load_concepts) is None:
            message = 'CONCEPTS - Please insert a concepts file.'
            return message

        if type_req == 'reports' and len(reports) == 0:
            message = 'REPORTS - Please insert a reports file.'
            return message
        if type_req == 'pubmed' and len(pubmedfiles) == 0:
            message = 'PUBMED - Please insert a reports file.'
            return message

        return message

    except (Exception, psycopg2.Error) as e:
        print(e)
        message = 'An error occurred in ' + type_req + ' file(s). Please check if it is similar to the example we provided.'
        return message


def update_db_util(reports,pubmedfiles,labels,concepts,jsondisp,jsonann,jsondispup,jsonannup,jsonall,load_concepts,load_labels):

    """This method is run after having checked the files inserted for the update. It updates the db."""


    filename = ''
    error_location = 'database'
    usecases = []
    sem_areas = []
    created_file = False
    cursor = connection.cursor()
    try:
        with transaction.atomic():
            if load_concepts is not None:
                load_concepts = ''.join(load_concepts)
                load_concepts = load_concepts.split(',')
                load_concepts = list(set(load_concepts))
                configure_concepts(cursor,load_concepts,'admin')

            if load_labels is not None:
                    load_labels = ''.join(load_labels)
                    load_labels = load_labels.split(',')
                    load_labels = list(set(load_labels))
                    configure_update_labels(cursor,load_labels)

            if (jsonannup != '') or jsondispup != '' or jsonall != '':

                data = {}
                all_fields = []
                fields = []
                fields_to_ann = []
                version = get_version()
                if int(version) != 0:
                    json_resp = get_fields_from_json()
                    all_fields = json_resp['all_fields']
                    fields = json_resp['fields']
                    fields_to_ann = json_resp['fields_to_ann']

                jsondispup = ''.join(jsondispup)
                jsonannup = ''.join(jsonannup)
                jsonall = ''.join(jsonall)
                jsondispup = jsondispup.split(',')
                jsonannup = jsonannup.split(',')
                jsonall = jsonall.split(',')

                for el in jsondispup:
                    if len(el) > 0:
                        if el not in all_fields:
                            all_fields.append(el)
                        if el not in fields:
                            fields.append(el)

                for el in jsonannup:
                    if len(el) > 0:
                        if el not in fields_to_ann:
                            fields_to_ann.append(el)
                        if el not in all_fields:
                            all_fields.append(el)

                for el in jsonall:
                    if el not in all_fields and el:
                        all_fields.append(el)

                # added 06092021
                # fields.extend(['volume','journal','year','authors'])
                # fields_to_ann.extend(['abstract','title'])
                # all_fields.extend(['volume','journal','year','authors','abstract','title'])
                # data['fields'] = list(set(fields))
                # data['fields_to_ann'] = list(set(fields_to_ann))
                # data['all_fields'] = list(set(all_fields))

                data['fields'] = fields
                data['fields_to_ann'] = fields_to_ann
                data['all_fields'] = all_fields
                version = get_version()
                version_new = int(version) + 1
                filename = 'fields' + str(version_new)
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                with open(os.path.join(workpath, './data/' + filename + '.json'), 'w') as outfile:
                    json.dump(data, outfile)
                    created_file = True

            all_fields = []
            fields = []
            fields_to_ann = []
            version = get_version()
            if int(version) != 0:
                json_resp = get_fields_from_json()
                all_fields = json_resp['all_fields']
                fields = json_resp['fields']
                fields_to_ann = json_resp['fields_to_ann']

            cursor.execute('SELECT * FROM use_case')
            ans = cursor.fetchall()
            for el in ans:
                if el[0] not in usecases:
                    usecases.append(el[0])


            cursor.execute('SELECT * FROM semantic_area')
            ans = cursor.fetchall()
            for el in ans:
                sem_areas.append(el[0])
            # Popolate the report table
            if len(pubmedfiles) > 0:
                rep_count_id = 1
                error_location = 'Pubmed'
                for pubmed in pubmedfiles:
                    df_pubmed = pd.read_csv(pubmed)
                    df_pubmed = df_pubmed.where(pd.notnull(df_pubmed), None)
                    df_pubmed = df_pubmed.reset_index(drop=True)
                    df_pubmed['usecase']=df_pubmed['usecase'].str.lower()
                    # print(df_report)
                    report_use = df_pubmed.usecase.unique()
                    for el in report_use:
                        if el not in usecases:
                            cursor.execute("INSERT INTO use_case VALUES (%s)",(str(el).lower(),))

                    count_rows = df_pubmed.shape[0]
                    list_col_mandatory = ['ID', 'usecase']


                    i = 0
                    var = True
                    # print(count_rows)
                    while var:
                        st = time.time()
                        for count in range(3):
                            count = count + 1
                            id_report_original = str(df_pubmed.loc[i, 'ID'])
                            id_report = 'PUBMED_' + str(id_report_original)
                            name = str(df_pubmed.loc[i, 'usecase'])
                            report_json = insert_articles_of_PUBMED(id_report_original)
                            if 'error' in report_json.keys():
                                return report_json
                            report_json = json.dumps(report_json)
                            # Duplicates are not inserted
                            cursor.execute("SELECT * FROM report WHERE id_report = %s AND language = %s;",
                                           (str(id_report), 'English'))
                            ans = cursor.fetchall()
                            if len(ans) == 0:
                                cursor.execute(
                                    "INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);",
                                    (str(id_report), report_json, 'PUBMED', 'English', str(name).lower()))

                            i = i + 1
                            # print(count)
                            # print(i)

                            if count_rows == i:
                                var = False
                                break



                        try:
                            time.sleep(1 - (time.time() - st))
                        except Exception as e:
                            print(e)
                            pass



            if len(reports) > 0:
                rep_count_id = 1
                error_location = 'Reports'
                for report in reports:
                    df_report = pd.read_csv(report)
                    df_report = df_report.where(pd.notnull(df_report), None)
                    df_report = df_report.reset_index(drop=True)
                    df_report['usecase']=df_report['usecase'].str.lower()
                    df_report['institute']=df_report['institute'].str.lower()
                    # print(df_report)
                    report_use = df_report.usecase.unique()
                    for el in report_use:
                        if el not in usecases:
                            cursor.execute("INSERT INTO use_case VALUES (%s)",(str(el).lower(),))

                    count_rows = df_report.shape[0]
                    list_col_mandatory = ['id_report', 'institute', 'usecase', 'language']
                    list_col_not_mandatory = []
                    for col in df_report:
                        if col not in list_col_mandatory:
                            list_col_not_mandatory.append(col)

                    for i in range(count_rows):
                        id_report = str(df_report.loc[i, 'id_report'])
                        # id_report = rep_count_id
                        # rep_count_id += 1
                        institute = str(df_report.loc[i, 'institute'])
                        language = str(df_report.loc[i, 'language'])
                        name = str(df_report.loc[i, 'usecase'])
                        report_json = {}
                        found = False
                        for col in list_col_not_mandatory:

                                if df_report.loc[i, col] is not None:
                                    col1 = col.replace(' ', '_')
                                    testo = str(df_report.loc[i, col])
                                    filtered_characters = list(s for s in testo if s.isprintable())
                                    testo = ''.join(filtered_characters)
                                    report_json[col1] = testo

                        report_json = json.dumps(report_json)
                        cursor.execute("SELECT * FROM report WHERE id_report = %s AND language = %s;",
                                       (str(id_report), str(language)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute(
                                "INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);",
                                (str(id_report), report_json, str(institute), str(language), str(name).lower()))

            # Popolate the labels table
            if len(labels) > 0:
                error_location = 'Labels'

                for label_file in labels:
                    df_labels = pd.read_csv(label_file)
                    df_labels = df_labels.where(pd.notnull(df_labels), None)
                    df_labels = df_labels.reset_index(drop=True)
                    df_labels['usecase']=df_labels['usecase'].str.lower()

                    distinct_label_usecase = df_labels['usecase'].unique()
                    for el in distinct_label_usecase:
                        if el in ['colon', 'uterine cervix', 'lung']:
                            bool_arr = check_exa_lab_conc_only(str(el))
                            if bool_arr[0] == True:
                                usecase = UseCase.objects.get(name = str(el))
                                cursor.execute("DELETE FROM associate WHERE ns_id = %s AND seq_number > %s AND id_report IN (SELECT id_report FROM report WHERE name = %s)",['Human',20,str(el)])
                                AnnotationLabel.objects.filter(name = usecase, seq_number__gt = 20).delete()
                                cursor = connection.cursor()
                                cursor.execute("DELETE FROM ground_truth_log_file WHERE ns_id = %s AND gt_type = %s AND id_report IN (SELECT id_report FROM report WHERE name = %s)",['Human','labels',str(el)])

                    count_lab_rows = df_labels.shape[0]
                    for i in range(count_lab_rows):
                        label = str(df_labels.loc[i, 'label'])
                        name = str(df_labels.loc[i,'usecase'])
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name).lower(),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name).lower(),))

                        cursor.execute('SELECT * FROM annotation_label')
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            seq_number = 1
                        else:
                            cursor.execute('SELECT seq_number FROM annotation_label ORDER BY seq_number DESC;')
                            ans = cursor.fetchall()
                            # print(ans[0][0])

                            seq_number = int(ans[0][0]) + 1


                        cursor.execute("SELECT * FROM annotation_label WHERE name = %s AND label = %s AND seq_number > %s;", (str(name),str(label),20))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);",
                                       (str(label), int(seq_number), str(name).lower()))


            # Popolate the concepts table
            if len(concepts) > 0:
                error_location = 'Concepts'
                if len(load_concepts) > 0:
                    usecases = get_presence_exa_concepts()
                    # in questo caso l'utente ha scelto nell'update di usare i concetti di examode
                    description = {'provenance':'EXAMODE','insertion_author':'admin'}
                    description = json.dumps(description)
                    cursor.execute("UPDATE concept SET json_concept = %s WHERE concept_url IN (SELECT concept_url "
                                   "FROM concept AS c INNER JOIN concept_has_uc AS chu ON "
                                   "chu.concept_utl = c.concept_utl WHERE chu.name IN %s)",
                                   [description,tuple(usecases)])


                for concept_file in concepts:
                    df_concept = pd.read_csv(concept_file)
                    df_concept = df_concept.where(pd.notnull(df_concept), None)
                    df_concept = df_concept.reset_index(drop=True)
                    count_conc_rows = df_concept.shape[0]
                    df_concept['usecase']=df_concept['usecase'].str.lower()

                    list_uc_concept = df_concept.usecase.unique()
                    list_area_concept = df_concept.area.unique()

                    for name in list_uc_concept:
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name).lower(),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name).lower(),))
                    for el in list_area_concept:
                        cursor.execute('SELECT * FROM semantic_area WHERE name = %s', (str(el),))
                        if len(cursor.fetchall()) == 0:
                            cursor.execute('INSERT INTO semantic_area VALUES (%s)', (str(el),))

                    distinct_concet_usecase = df_concept['usecase'].unique()
                    for el in distinct_concet_usecase:
                        if el in ['colon', 'uterine cervix', 'lung']:
                            bool_arr = check_exa_lab_conc_only(str(el))
                            if bool_arr[1] == True:
                                cursor = connection.cursor()

                                cursor.execute(
                                    "DELETE FROM contains WHERE ns_id = %s AND id_report IN (SELECT id_report FROM report WHERE name = %s)",
                                    [ 'Human',str(el)])
                                cursor.execute(
                                    "DELETE FROM linked WHERE ns_id = %s AND id_report IN (SELECT id_report FROM report WHERE name = %s)",
                                    [ 'Human',str(el)])
                                cursor.execute(
                                    "DELETE FROM concept WHERE concept_url IN (SELECT concept_url FROM concept_has_uc WHERE name = %s)",
                                    [ str(el)])

                                cursor.execute(
                                    "DELETE FROM ground_truth_log_file WHERE ns_id = %s AND gt_type = %s AND id_report IN (SELECT id_report FROM report WHERE name = %s)",
                                    ['Human','concepts', str(el)])

                    for i in range(count_conc_rows):

                        concept_url = str(df_concept.loc[i, 'concept_url'])
                        concept_name = str(df_concept.loc[i, 'concept_name'])
                        usecase = str(df_concept.loc[i, 'usecase'])
                        semantic_area = str(df_concept.loc[i, 'area'])

                        cursor.execute("SELECT concept_url,name,json_concept FROM concept WHERE concept_url = %s;", (str(concept_url),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO concept (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(concept_name)))
                        else:
                            for el in ans:
                                desc = el[2]
                                desc = json.loads(desc)
                                if desc['insertion_author'] != 'admin' and desc['provenance'] == 'EXAMODE':
                                    desc['insertion_author'] = 'admin'
                                    desc = json.dumps(desc)
                                    cursor.execute('UPDATE concept SET json_concept = %s WHERE concept_url = %s',
                                                   [desc, el[0]])



                        cursor.execute("SELECT * FROM concept_has_uc WHERE concept_url = %s AND name=%s;", (str(concept_url),str(usecase)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO concept_has_uc (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(usecase).lower()))

                        cursor.execute("SELECT * FROM belong_to WHERE concept_url = %s AND name = %s;", (str(concept_url),str(semantic_area)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO belong_to (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(semantic_area)))

            if ((jsonann is not None) and (jsonann != '')) or ((jsondisp is not None) and jsondisp != ''):
                data = {}
                fields = []
                fields_to_ann = []
                version = get_version()
                if int(version) != 0:
                    json_resp1 = get_fields_from_json()
                    all_fields = json_resp1['all_fields']
                    fields_to_ann = json_resp1['fields_to_ann']
                jsondisp = ''.join(jsondisp)
                jsonann = ''.join(jsonann)
                jsondisp = jsondisp.split(',')
                jsonann = jsonann.split(',')
                # print(jsondisp)
                # print(jsonann)
                for el in jsondisp:
                    if len(el) > 0:
                        if el not in fields:
                            fields.append(el)
                        if el not in all_fields:
                            all_fields.append(el)
                for el in jsonann:
                    if len(el) > 0:
                        if el not in fields_to_ann:
                            fields_to_ann.append(el)
                        if el not in all_fields:
                            all_fields.append(el)


                version = get_version()
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                version_new = int(version) + 1
                filename = 'fields' + str(version_new)
                with open(os.path.join(workpath, './data/' + filename + '.json'), 'w') as outfile:
                    json.dump(data, outfile)
                    created_file = True

    except (Exception,psycopg2.IntegrityError) as e:
        print(e)
        # connection.rollback()
        print('rolledback')

        if created_file == True:
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            if filename != '' and filename != 'fields0':
                path = os.path.join(workpath, './data/'+filename+'.json')
                os.remove(path)

        json_resp = {'error': 'an error occurred in: ' + error_location + '. The configuration failed.'}
        return json_resp
    else:
        # connection.commit()
        if created_file == True:

            for filen in os.listdir(os.path.join(workpath, './data')):
                if filen.endswith('json'):
                    print(filen)
                    if filen != '' and filen != 'fields0.json' and filen != filename + '.json':
                        path = os.path.join(workpath, './data/' + filen)
                        os.remove(path)
        if ((jsonann is not None) and (jsonann != '')) or ((jsondisp is not None) and jsondisp != ''):
            outfile.close()

        json_resp = {'message': 'Ok'}

        return json_resp




