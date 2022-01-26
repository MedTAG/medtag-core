import traceback
from MedTAG_sket_dock_App.utils_configuration_and_update import *
import shutil
from MedTAG_sket_dock_App.sket.sket.sket import SKET
from MedTAG_sket_dock_App.sket.sket.utils.utils import *
from MedTAG_sket_dock import sket_pipe

def run_sket_pipe(dataset,use_case):

    """This method runs the sket pipeline given a use case a report id and the fields"""
    # sket = SKET(use_case, 'en', 'en_core_sci_sm', True, None, None, False, 0)
    concepts = sket_pipe.med_pipeline(dataset, 'en', use_case, 0.9, False, True, False)
    return concepts


def map_labels(usecase,label):

    """This method returns the entire name of a label"""

    if usecase == 'colon':
        if label == 'cancer':
            return "Cancer"
        if label == 'hgd':
            return "Adenomatous polyp - high grade dysplasia"
        if label == 'lgd':
            return "Adenomatous polyp - low grade dysplasia"
        if label == 'hyperplastic':
            return "Hyperplastic polyp"
        if label == 'ni':
            return "Non-informative"

    elif usecase == 'cervix':
        if label == 'cancer_scc_inv':
            return "Cancer - squamous cell carcinoma invasive"
        if label == 'cancer_scc_insitu':
            return "Cancer - squamous cell carcinoma in situ"
        if label == 'cancer_adeno_inv':
            return "Cancer - adenocarcinoma invasive"
        if label == 'cancer_adeno_insitu':
            return "Cancer - adenocarcinoma in situ"
        if label == 'hgd':
            return "High grade dysplasia"
        if label == 'lgd':
            return "Low grade dysplasia"
        if label == 'hpv':
            return "HPV infection present"
        if label == 'koilocytes':
            return "Koilocytes"
        if label == 'glands_norm':
            return "Normal glands"
        if label == 'squamous_norm':
            return "Normal squamous"

    if usecase == 'lung':
        if label == 'cancer_scc':
            return "Cancer - small cell cancer"
        if label == 'cancer_nscc_adeno':
            return "Cancer - non-small cell cancer, adenocarcinoma"
        if label == 'cancer_nscc_squamous':
            return "Cancer - non-small cell cancer, squamous cell carcinoma"
        if label == 'cancer_nscc_large':
            return "Cancer - non-small cell cancer, large cell carcinoma"
        if label == 'no_cancer':
            return "No cancer"


# def aux_start_end(report_field,mention,use,report):
#
#     """This method returns the start and end char of the mention found by sket."""
#
#     # report_json = Report.objects.get(id_report=report, language='english')
#     languages = ['English','english']
#     report_json = report.report_json
#     report_string = json.dumps(report_json)
#     if (report_json.get(report_field) is not None and report_json.get(report_field) != ""):
#         element = report_json[report_field]
#         element_1 = json.dumps(element)
#         if element_1.startswith('"') and element_1.endswith('"'):
#             element_1 = element_1.replace('"','')
#
#         before_element = report_string.split(report_field)[0]
#         after_element = report_string.split(report_field)[1]
#         until_element_value = len(before_element) + len(report_field) + len(after_element.split(str(element_1))[0])
#         start_element = until_element_value + 1
#         end_element = start_element + len(str(element_1)) - 1
#         mention_1 = inverse_sanitizers(use, report_string, start_element, end_element, mention)
#         before_mention_element = str(element_1).split(mention_1)[0]
#         start_mention_element = until_element_value + len(before_mention_element) + 1
#         end_mention_element = start_mention_element + len(str(mention_1)) - 1
#
#         mention_3 = mention_1
#         element_2 = re.sub("[^0-9a-zA-Z]"," ",element_1) # mi serve per non far tirare l'eccezione a regex
#         mention_2 = re.sub("[^0-9a-zA-Z]", " ", mention_1)
#         if element_1.count(mention_1) > 0:
#             starts = [m.start() for m in re.finditer(mention_2, element_2)]
#             no_collision = True
#             for start in starts:
#                 mention_3 = mention_1
#                 # mention reprocessing: example: (mild in this case re throws an exception: it want (mild)
#                 int_last_char = start + len(mention_1) -1
#                 int_next_of_last = int_last_char+1
#                 while int_next_of_last <= len(element_1)-1 and element_1[int_next_of_last] != ' ':
#                     last_next_char = element_1[int_next_of_last]
#                     mention_3 = mention_3 + last_next_char
#                     # mention_3 = mention_1 + last_next_char
#                     int_next_of_last += 1
#
#                 rob_ns = NameSpace.objects.get(ns_id='Robot')
#                 user_rob = User.objects.get(username='Robot_user', ns_id=rob_ns)
#                 mentions_annos = Annotate.objects.filter(username=user_rob, ns_id=rob_ns, id_report=report,
#                                                          language=report.language)
#
#                 start_ment = int(start_element) + int(start)
#                 stop_ment = int(start_ment) + len(mention_3) - 1  # nella mention devo incontrare il primo spazio se no è troncata e può dare problemi
#                 start_mention_element = start_ment
#                 end_mention_element = stop_ment
#
#                 if len(starts) > 1:
#                     for annot in mentions_annos:
#                         mention = Mention.objects.get(start=annot.start_id,stop = annot.stop, id_report = report, language = annot.language)
#                         stop = mention.stop
#                         if (int(start_ment) >= int(mention.start) and int(start_ment) <= int(stop)) or (int(stop_ment) >= int(mention.start) and int(stop_ment) <= int(stop)):
#                             no_collision = False
#                         else:
#                             no_collision = True
#                             break
#                 if no_collision:
#                     break
#
#         return start_mention_element,end_mention_element,mention_3

def aux_start_end(report_field,mention,use,report):

    """This method returns the start and end char of the mention found by sket."""

    # report_json = Report.objects.get(id_report=report, language='english')
    languages = ['English','english']
    report_json = report.report_json
    report_string = json.dumps(report_json)
    if (report_json.get(report_field) is not None and report_json.get(report_field) != ""):
        element = report_json[report_field]
        element_1 = json.dumps(element)
        if element_1.startswith('"') and element_1.endswith('"'):
            # element_1 = element_1.replace('"','')
            element_1 = element_1[1:-1]
        print(report_string)
        before_element = report_string.split(report_field)[0]
        after_element = report_string.split(report_field)[1]
        until_element_value = len(before_element) + len(report_field) + len(after_element.split(str(element_1))[0])
        # start_element = until_element_value + 1
        start_element = until_element_value
        end_element = start_element + len(str(element_1)) - 1
        print(report_string[start_element:end_element])
        mention_1 = inverse_sanitizers(use, report_string, start_element, end_element, mention)
        # before_mention_element = str(element_1).split(mention_1)[0]
        # start_mention_element = until_element_value + len(before_mention_element) + 1
        # end_mention_element = start_mention_element + len(str(mention_1)) - 1

        rob_ns = NameSpace.objects.get(ns_id='Robot')
        user_rob = User.objects.get(username='Robot_user', ns_id=rob_ns)
        mentions_annos = Annotate.objects.filter(username=user_rob, ns_id=rob_ns, id_report=report,
                                                 language=report.language)
        split_su_elemento = element_1.split(' ')
        mention_split = mention_1.split(' ')
        print(split_su_elemento)
        no_collision = True
        indices = [i for i, e in enumerate(split_su_elemento) if mention_split[0] in e]
        for index in indices:
            print(split_su_elemento[index])
            start = start_element
            for ii in range(0,index):
                print(split_su_elemento[ii],str(len(split_su_elemento[ii])))
                start = start + len(split_su_elemento[ii]) + 1
            # print(start)
            # end = start + len(split_su_elemento[index]) - 1
            # print(report_string[start:end])
            count_ind = index
            current_len = 0
            found = True
            # print(len(split_su_elemento))
            for i in range(len(mention_split)):
                if count_ind < len(split_su_elemento):
                    if mention_split[i] in split_su_elemento[count_ind]:
                        # print(split_su_elemento[count_ind])
                        current_len = current_len + len(split_su_elemento[count_ind]) + 1
                        end = start + current_len - 1
                        print(report_string[end])
                        count_ind = count_ind + 1
                        # print(element_1[start:end])

                    else:
                        found = False

                else:
                    found = False
                    break

            if found:
                # for annot in mention_list:

                for annot in mentions_annos:
                    mention = Mention.objects.get(start=annot.start_id, stop=annot.stop, id_report=report,
                                                  language=annot.language)
                    stop = mention.stop
                    if (int(start) >= int(mention.start) and int(start) <= int(stop)) or (
                            int(end) >= int(mention.start) and int(end) <= int(stop)):
                        no_collision = False
                    else:
                        no_collision = True
                        break
                    # if (int(start) >= int(annot['start']) and int(start) <= int(annot['stop'])) or (
                    #         int(end) >= int(annot['start']) and int(end) <= int(annot['stop'])):
                    #     no_collision = False
                    # else:
                    #     no_collision = True

                print(mention_1)
                print(report_string[start:end])
                print(report_string[start:end])
                if no_collision:
                    return start, end, report_string[start-1:end+1]
    return None,None,None



def create_concepts_all_dataset(use,rep,data_1,report_key):

    """This method creates a json object needed to automatically find the labels."""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    id = rep[0]
    concepts_to_ret = {}
    concepts_to_ret[id] = {}
    concepts_to_ret[id]['Diagnosis'] = []
    concepts_to_ret[id]['Procedure'] = []
    concepts_to_ret[id]['Test'] = []
    concepts_to_ret[id]['Anatomical Location'] = []
    array_key_to_extract = []
    if report_key == 'reports':
        with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as outfile:
            data = json.load(outfile)
            # print('DATA',data)
            array_key_to_extract = data['extract_fields'][use]
    elif report_key == 'pubmed':
        array_key_to_extract = ['abstract','title']
    for elem in array_key_to_extract:
        for el in data_1[rep[0]+'_'+elem]:
            concept_ar = []
            concept = el[1]
            concept_ar.append(concept[0])
            concept_ar.append(concept[1])
            area = concept[2]
            concepts_to_ret[id][area].append(concept_ar)

    return concepts_to_ret


def create_json_to_submit(reports,fields_to_extract):

    """This method creates json reports passed to sket"""

    json_to_submit = {}
    json_to_submit['reports'] = []
    for rep in reports:
        report_json = json.loads(rep[2])
        for field in fields_to_extract:
            json_rep = {}
            json_rep['age'] = None
            json_rep['gender'] = None
            json_rep['id'] = rep[0]+'_'+str(field)
            json_rep['text'] = report_json[field]
            if json_rep['text'] is None:
                json_rep['text'] = ''
            json_to_submit['reports'].append(json_rep)
    return json_to_submit


def create_auto_gt_1(usecase,fields,report_key,batch):

    """This method automatically creates the groundtruths"""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    mode = NameSpace.objects.get(ns_id='Robot')
    ag = User.objects.get(username='Robot_user',ns_id=mode)
    use = ''
    languages = ['english','English']
    # print(usecase)
    usecase_low = usecase.lower()
    if usecase_low == 'colon':
        use = 'colon'
    elif usecase_low == 'uterine cervix':
        use = 'cervix'
    elif usecase_low == 'lung':
        use = 'lung'
    update_all = True

    if fields == []:
        update_all = False
    array_key_to_extract = []
    if report_key == 'reports':
        with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as outfile:
            data = json.load(outfile)
            array_key_to_extract = data['extract_fields'][usecase]
    elif report_key == 'pubmed':
        array_key_to_extract = ['title','abstract']

    # Select reports of usecase without automatic gt associated
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                if update_all == True:
                    configure_concepts(cursor, [usecase],'robot')

                ns_human = NameSpace.objects.get(ns_id='Human')
                users = User.objects.filter(ns_id=ns_human)
                new_users = []
                for user in users:
                    if user.username not in ['Robot_user']:
                        new_users.append(user.username)

                if report_key == 'reports':
                    if batch == 'all' or batch is None:
                        cursor.execute(
                            "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute != %s AND language in %s AND (id_report,language) NOT IN (SELECT id_report,language FROM ground_truth_log_file WHERE username=%s)",
                            [usecase,'PUBMED',tuple(languages),'Robot_user'])
                    else:
                        cursor.execute(
                            "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute != %s AND batch = %s AND language in %s AND (id_report,language) NOT IN (SELECT id_report,language FROM ground_truth_log_file WHERE username=%s)",
                            [usecase, 'PUBMED',batch,tuple(languages) ,'Robot_user'])
                    reports = cursor.fetchall()

                elif report_key == 'pubmed':
                    if batch == 'all' or batch is None:
                        cursor.execute(
                            "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute = %s AND language in %s AND (id_report,language) NOT IN (SELECT id_report,language FROM ground_truth_log_file WHERE username=%s)",
                            [usecase,'PUBMED',tuple(languages),'Robot_user'])
                    else:
                        cursor.execute(
                            "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute = %s and batch = %s AND language in %s AND (id_report,language) NOT IN (SELECT id_report,language FROM ground_truth_log_file WHERE username=%s)",
                            [usecase,'PUBMED',batch,tuple(languages),'Robot_user'])
                    reports = cursor.fetchall()

                if len(reports) == 0 or update_all:
                    # in questo caso l'utente decide di riannotare tutto, non ci sono report mancanti!!
                    # ELIMINO GT PREGRESSE
                    if batch == 'all' or batch is None:
                        if report_key == 'reports':
                            cursor.execute(
                                "DELETE FROM contains WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN contains as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM annotate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN annotate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM associate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN associate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM linked WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN linked as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM ground_truth_log_file WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN ground_truth_log_file as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s)",
                                [usecase, 'Robot', 'PUBMED'])
                        elif report_key == 'pubmed':
                            cursor.execute(
                                "DELETE FROM contains WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN contains as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM annotate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN annotate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM associate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN associate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM linked WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN linked as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s)",
                                [usecase, 'Robot', 'PUBMED'])
                            cursor.execute(
                                "DELETE FROM ground_truth_log_file WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN ground_truth_log_file as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s)",
                                [usecase, 'Robot', 'PUBMED'])
                    else:
                        if report_key == 'reports':
                            cursor.execute("DELETE FROM contains WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN contains as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s and batch = %s)",[usecase,'Robot','PUBMED',batch])
                            cursor.execute("DELETE FROM annotate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN annotate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s and batch = %s)",[usecase,'Robot','PUBMED',batch])
                            cursor.execute("DELETE FROM associate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN associate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s and batch = %s)",[usecase,'Robot','PUBMED',batch])
                            cursor.execute("DELETE FROM linked WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN linked as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s and batch = %s)",[usecase,'Robot','PUBMED',batch])
                            cursor.execute("DELETE FROM ground_truth_log_file WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN ground_truth_log_file as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute != %s and batch = %s)",[usecase,'Robot','PUBMED',batch])
                        elif report_key == 'pubmed':
                            cursor.execute(
                                "DELETE FROM contains WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN contains as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s and batch = %s)",
                                [usecase, 'Robot','PUBMED',batch])
                            cursor.execute(
                                "DELETE FROM annotate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN annotate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s and batch = %s)",
                                [usecase, 'Robot','PUBMED',batch])
                            cursor.execute(
                                "DELETE FROM associate WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN associate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s and batch = %s)",
                                [usecase, 'Robot','PUBMED',batch])
                            cursor.execute(
                                "DELETE FROM linked WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN linked as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s and batch = %s)",
                                [usecase, 'Robot','PUBMED',batch])
                            cursor.execute(
                                "DELETE FROM ground_truth_log_file WHERE (id_report,language,ns_id) IN (SELECT r.id_report,r.language,c.ns_id FROM report AS r INNER JOIN ground_truth_log_file as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND r.institute = %s and batch = %s)",
                                [usecase, 'Robot','PUBMED',batch])

                    if report_key == 'pubmed':
                        if batch == 'all' or batch is None:
                            cursor.execute(
                                "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute = %s AND language in %s",
                                [usecase, 'PUBMED',tuple(languages)])
                        else:
                            cursor.execute(
                                "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute = %s and batch = %s AND language in %s",
                                [usecase,'PUBMED',batch,tuple(languages)])
                        reports = cursor.fetchall()
                    elif report_key == 'reports':
                        if batch == 'all' or batch is None:
                            cursor.execute(
                                "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute != %s AND language in %s",
                                [usecase, 'PUBMED',tuple(languages)])
                        else:
                            cursor.execute(
                                "SELECT id_report,language,report_json FROM report WHERE name=%s AND institute != %s and batch = %s AND language in %s",
                                [usecase, 'PUBMED',batch,tuple(languages)])
                        reports = cursor.fetchall()
                # sket = SKET(use, 'en', 'en_core_sci_sm', True, None, None, False, 0)
                json_to_submit = create_json_to_submit(reports,array_key_to_extract)
                # print(json_to_submit)
                concepts_annotated = run_sket_pipe(json_to_submit, use)
                # print('concepts_annotated',concepts_annotated)
                for rep in reports:
                    # print(reports.index(rep))
                    report = Report.objects.get(id_report=rep[0], language=rep[1])
                    labels_created = False
                    concepts_created = False
                    mentions_created = False
                    linked_created = False
                    report_string = rep[2]
                    for elemento in array_key_to_extract:
                        if elemento in json.loads(rep[2]).keys():

                            data = concepts_annotated
                            report_field = elemento
                            asso = data[rep[0] + '_' + elemento]
                            asso = sorted(asso, key=lambda x: len(x[0]),reverse=True)

                            for element in asso:
                                mention_raw = element[0]
                                concept = element[1]
                                concept_url = concept[0]
                                concept_area = concept[2]
                                if concept_url == 'SevereColonDysplasia':
                                    concept_url = 'https://w3id.org/examode/ontology/SevereColonDysplasia'
                                elif concept_url == 'uterusNOS':
                                    concept_url = 'https://w3id.org/examode/ontology/UterusNOS'
                                concept_row = Concept.objects.filter(concept_url=concept_url)
                                if concept_row.exists():
                                    concept_row = concept_row.first()
                                    semantic_area = SemanticArea.objects.get(name=concept_area)
                                    start_mention_element,end_mention_element,mention = aux_start_end(report_field,mention_raw,use,report)
                                    if start_mention_element is not None and end_mention_element is not None and mention is not None:
                                        if not Mention.objects.filter(mention_text=mention,start=int(start_mention_element),
                                                                      stop=int(end_mention_element), id_report=report,language=rep[1]).exists():

                                            Mention.objects.create(mention_text=mention, start=int(start_mention_element),
                                                                   stop=int(end_mention_element), id_report=report,
                                                                   language=rep[1])

                                        cur_mention = Mention.objects.get(mention_text=mention,
                                                                          start=int(start_mention_element),
                                                                          stop=int(end_mention_element), id_report=report,
                                                                          language=rep[1])
                                        if not Annotate.objects.filter(id_report=report, language=report.language,
                                                                       start=cur_mention, stop=cur_mention.stop,
                                                                       username=ag,
                                                                       ns_id=mode).exists():
                                            Annotate.objects.create(id_report=report, language=report.language,
                                                                    start=cur_mention,
                                                                    stop=cur_mention.stop, insertion_time=Now(),
                                                                    username=ag,
                                                                    ns_id=mode)
                                            mentions_created = True
                                            # se ad esempio all'inizio sono stati automaticamente annotati 100 reports e poi ne vengono inseriti altri 50, può essere che quei 50 non abbiano auto gt. Questo significa che bisogna aggiornare il db copiando le gt anche per quegli utenti che avevano già almeno una gt copiata per quello usecase.
                                            for username in new_users:
                                                if username != 'Robot_user':
                                                    user = User.objects.get(username=username, ns_id='Robot')
                                                    last_anno = Annotate.objects.get(id_report=report, language=report.language,
                                                                            start=cur_mention,username=ag, ns_id=mode,
                                                                            stop=cur_mention.stop)
                                                    Annotate.objects.create(id_report=report, language=report.language,
                                                                            start=cur_mention,
                                                                            stop=cur_mention.stop, insertion_time=last_anno.insertion_time,
                                                                            username=user,
                                                                            ns_id=mode)


                                        if not Linked.objects.filter(id_report=report, language=report.language,
                                                                     start=cur_mention, stop=cur_mention.stop,
                                                                     concept_url=concept_row, name=semantic_area,
                                                                     username=ag,
                                                                     ns_id=mode).exists():
                                            Linked.objects.create(id_report=report, language=report.language,
                                                                  start=cur_mention,
                                                                  stop=cur_mention.stop, insertion_time=Now(),
                                                                  concept_url=concept_row, name=semantic_area, username=ag,
                                                                  ns_id=mode)
                                            linked_created = True
                                            for username in new_users:
                                                if username != 'Robot_user':
                                                    user = User.objects.get(username=username, ns_id='Robot')
                                                    last_linked = Linked.objects.get(id_report=report, language=report.language,
                                                                          start=cur_mention,username=ag, ns_id=mode,
                                                                          stop=cur_mention.stop,concept_url=concept_row, name=semantic_area)
                                                    Linked.objects.create(id_report=report, language=report.language,
                                                                          start=cur_mention,
                                                                          stop=cur_mention.stop, insertion_time=last_linked.insertion_time,
                                                                          concept_url=concept_row, name=semantic_area,
                                                                          username=user,
                                                                          ns_id=mode)

                                        if not Contains.objects.filter(id_report=report, language=report.language,
                                                                       concept_url=concept_row, name=semantic_area,
                                                                       username=ag,
                                                                       ns_id=mode).exists():
                                            Contains.objects.create(id_report=report, language=report.language,
                                                                    concept_url=concept_row, name=semantic_area,
                                                                    insertion_time=Now(), username=ag, ns_id=mode)
                                            for username in new_users:
                                                if username != 'Robot_user':
                                                    user = User.objects.get(username=username, ns_id='Robot')
                                                    last_contains = Contains.objects.get(username=ag, ns_id=mode,id_report=report, language=report.language,
                                                                            concept_url=concept_row, name=semantic_area)
                                                    Contains.objects.create(id_report=report, language=report.language,
                                                                            concept_url=concept_row, name=semantic_area,
                                                                            insertion_time=last_contains.insertion_time, username=user, ns_id=mode)

                                            concepts_created = True

                    concepts_to_ret = create_concepts_all_dataset(usecase, rep,concepts_annotated,report_key)
                    if use == 'colon':
                        labels_fin = colon_concepts2labels(concepts_to_ret)
                    elif use == 'cervix':
                        labels_fin = cervix_concepts2labels(concepts_to_ret)
                    elif use == 'lung':
                        labels_fin = lung_concepts2labels(concepts_to_ret)

                    labels = labels_fin[rep[0]]
                    labels_keys = labels.keys()
                    for label in labels_keys:
                        if labels[label] == 1:
                            final_label = map_labels(use,label)
                            lab_arr = ['Automatic','Manual and Automatic']
                            labb = AnnotationLabel.objects.get(label = final_label,annotation_mode__in=lab_arr,name=usecase)
                            seq = labb.seq_number
                            lab = AnnotationLabel.objects.get(seq_number=seq, name=usecase)
                            if (not Associate.objects.filter(id_report=report, language=rep[1], label=lab,
                                                             seq_number=lab.seq_number, username=ag,
                                                             ns_id=mode).exists()):
                                Associate.objects.create(insertion_time=Now(), username=ag, ns_id=mode,
                                                         language=report.language, id_report=report,
                                                         seq_number=lab.seq_number, label=lab)
                                labels_created = True
                                for username in new_users:
                                    if username != 'Robot_user':
                                        user = User.objects.get(username=username, ns_id='Robot')
                                        last_asso = Associate.objects.get(username=ag, ns_id=mode,language=report.language,
                                                                 id_report=report, seq_number=lab.seq_number,label=lab)
                                        Associate.objects.create(insertion_time=last_asso.insertion_time, username=user,
                                                                 ns_id=mode, language=report.language,
                                                                 id_report=report, seq_number=lab.seq_number,
                                                                 label=lab)

                    if labels_created:
                        if GroundTruthLogFile.objects.filter(gt_type = 'labels',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                            GroundTruthLogFile.objects.filter(gt_type='labels', username=ag, ns_id=mode, id_report=report,
                                                              language=rep[1]).delete()
                        ser_gt = serialize_gt('labels', usecase, 'Robot_user', rep[0], rep[1], mode)
                        GroundTruthLogFile.objects.create(username=ag, gt_type='labels', gt_json=ser_gt, id_report=report,
                                                          language=rep[1], insertion_time=Now(),ns_id=mode)
                        # for user in new_users:
                        #     if user != 'Robot_user':
                        #         user = User.objects.get(username=user,ns_id=mode)
                        #         ser_us_gt = serialize_gt('labels', usecase, user.username, rep[0], rep[1], mode)
                        #         last_gt = GroundTruthLogFile.objects.get(username=ag, gt_type='labels', gt_json=ser_gt, id_report=report,
                        #                                   language=rep[1],ns_id=mode)
                        #         GroundTruthLogFile.objects.create(username=user, gt_type='labels', gt_json=ser_us_gt,
                        #                                           id_report=report,ns_id=mode,
                        #                                           language=rep[1], insertion_time=last_gt.insertion_time)

                    if mentions_created:
                        if GroundTruthLogFile.objects.filter(gt_type = 'mentions',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                            GroundTruthLogFile.objects.filter(gt_type='mentions', username=ag, ns_id=mode, id_report=report,
                                                              language=rep[1]).delete()
                        ser_gt = serialize_gt('mentions', usecase, 'Robot_user', rep[0], rep[1], mode)
                        GroundTruthLogFile.objects.create(username=ag, gt_type='mentions', gt_json=ser_gt, id_report=report,
                                                          ns_id=mode,language=rep[1], insertion_time=Now())
                        # for user in new_users:
                        #     if user != 'Robot_user':
                        #         user = User.objects.get(username=user,ns_id=mode)
                        #         ser_us_gt = serialize_gt('mentions', usecase, user.username, rep[0], rep[1], mode)
                        #         last_gt = GroundTruthLogFile.objects.get(username=ag, gt_type='mentions',
                        #                                                     gt_json=ser_gt, id_report=report,
                        #                                                     language=rep[1], ns_id=mode)
                        #         GroundTruthLogFile.objects.create(username=user, gt_type='mentions', gt_json=ser_us_gt,
                        #                                           id_report=report,ns_id=mode,
                        #                                           language=rep[1], insertion_time=last_gt.insertion_time)

                    if concepts_created:
                        if GroundTruthLogFile.objects.filter(gt_type = 'concepts',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                            GroundTruthLogFile.objects.filter(gt_type='concepts', username=ag, ns_id=mode, id_report=report,
                                                              language=rep[1]).delete()
                        ser_gt = serialize_gt('concepts', usecase, 'Robot_user', rep[0], rep[1], mode)
                        GroundTruthLogFile.objects.create(username=ag, gt_type='concepts', gt_json=ser_gt,ns_id=mode, id_report=report,
                                                          language=rep[1], insertion_time=Now())
                        # for user in new_users:
                        #     if user != 'Robot_user':
                        #         user = User.objects.get(username=user,ns_id=mode)
                        #         ser_us_gt = serialize_gt('concepts', usecase, user.username, rep[0], rep[1], mode)
                        #         last_gt = GroundTruthLogFile.objects.get(username=ag, gt_type='concepts',
                        #                                                     gt_json=ser_gt, id_report=report,
                        #                                                     language=rep[1], ns_id=mode)
                        #         GroundTruthLogFile.objects.create(username=user, gt_type='concepts', gt_json=ser_us_gt,
                        #                                           id_report=report,ns_id=mode,
                        #                                           language=rep[1], insertion_time=last_gt.insertion_time)

                    if linked_created:
                        if GroundTruthLogFile.objects.filter(gt_type = 'concept-mention',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                            GroundTruthLogFile.objects.filter(gt_type='concept-mention', username=ag, ns_id=mode, id_report=report,
                                                              language=rep[1]).delete()
                        ser_gt = serialize_gt('concept-mention', usecase, 'Robot_user', rep[0], rep[1], mode)
                        GroundTruthLogFile.objects.create(username=ag, gt_type='concept-mention', gt_json=ser_gt, id_report=report,
                                                          language=rep[1], ns_id=mode,insertion_time=Now())
                        # for user in new_users:
                        #     if user != 'Robot_user':
                        #         user = User.objects.get(username=user,ns_id=mode)
                        #         ser_us_gt = serialize_gt('concept-mention', usecase, user.username, rep[0], rep[1], mode)
                        #         last_gt = GroundTruthLogFile.objects.get(username=ag, gt_type='concept-mention',
                        #                                                     gt_json=ser_gt, id_report=report,
                        #                                                     language=rep[1], ns_id=mode)
                        #         GroundTruthLogFile.objects.create(username=user, gt_type='concept-mention', gt_json=ser_us_gt,
                        #                                           id_report=report,ns_id=mode,
                        #                                           language=rep[1], insertion_time=last_gt.insertion_time)
        return True,''

    except Exception as error:
        print(error)
        print(traceback.format_exc())
        print('ROLLBACK')
        return False,error


def inverse_sanitizers(use_case,rep_string,start,end,record):

    """Sket applies a sanification of records when it comes to find mentions: in order to provide the user with mentions in his own
    text then we apply an inverse sanification"""

    if record:
        if use_case == 'colon':
            if 'octopus' in rep_string[start - 1:end + 1] and 'polyp' in record:
                record = record.replace('polyp','octopus')
            if 'hairy' in rep_string[start - 1:end + 1] and 'villous' in record:
                record = record.replace('villous','hairy')
            if 'villous adenoma-tubule' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace('tubulo-villous adenoma','villous adenoma-tubule')
            if 'villous adenomas-tubule' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace('tubulo-villous adenoma','villous adenomas-tubule')
            if 'villous adenomas tubule' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace('tubulo-villous adenoma','villous adenomas tubule')
            if 'tubule adenoma-villous' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace('tubulo-villous adenoma','tubule adenoma-villous')
            if 'tubular adenoma-villous' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace('tubulo-villous adenoma','tubular adenoma-villous')
            if 'villous adenoma tubule-' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma ' in record:
                record = record.replace('tubulo-villous adenoma ','villous adenoma tubule-')
            if 'villous adenoma tubule' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace('tubulo-villous adenoma','villous adenoma tubule')
            if 'tubulovilloso adenoma' in rep_string[start - 1:end + 1] and 'tubulo-villous adenoma' in record:
                record = record.replace( 'tubulo-villous adenoma','tubulovilloso adenoma')
            if 'blind' in rep_string[start - 1:end + 1] and 'caecum' in record:
                record = record.replace('caecum','blind')
            if 'cecal' in rep_string[start - 1:end + 1] and 'caecum' in record:
                record = record.replace('caecum','cecal')
            if 'rectal' in rep_string[start - 1:end + 1] and 'rectum' in record:
                record = record.replace('rectum','rectal')
            if 'sigma' in rep_string[start - 1:end + 1] and 'sigmoid' in record:
                record = record.replace( 'sigmoid','sigma')
            if 'hyperplasia' in rep_string[start - 1:end + 1] and 'hyperplastic' in record:
                record = record.replace('hyperplastic','hyperplasia')  # MarianMT translates 'iperplastico' as 'hyperplasia' instead of 'hyperplastic'
            if 'proximal colon' in rep_string[start - 1:end + 1] and 'right colon' in record:
                record = record.replace('right colon','proximal colon')
        if use_case == 'cervix':
            if 'octopus' in rep_string[start - 1:end + 1] and 'polyp' in record:
                record = record.replace('polyp','octopus')
            if 'his cassock' in rep_string[start - 1:end + 1] and 'lamina propria' in record:
                record = record.replace( 'lamina propria','his cassock')
            if 'tunica propria' in rep_string[start - 1:end + 1] and 'lamina propria' in record:
                record = record.replace('lamina propria','tunica propria')
            if 'l-sil' in rep_string[start - 1:end + 1] and 'lsil' in record:
                record = record.replace('lsil','l-sil')
            if 'h-sil' in rep_string[start - 1:end + 1] and 'hsil' in record:
                record = record.replace('hsil','h-sil')
            if 'cin ii / iii' in rep_string[start - 1:end + 1] and 'cin23' in record:
                record = record.replace('cin23','cin ii / iii')
            if 'cin iii' in rep_string[start - 1:end + 1] and 'cin3' in record:
                record = record.replace('cin3','cin iii')
            if 'cin ii' in rep_string[start - 1:end + 1] and 'cin2' in record:
                record = record.replace('cin2','cin ii')
            if 'cin i' in rep_string[start - 1:end + 1] and 'cin1' in record:
                record = record.replace('cin1','cin i')
            if 'cin-iii' in rep_string[start - 1:end + 1] and 'cin3' in record:
                record = record.replace('cin3','cin-iii')
            if 'cin-ii' in rep_string[start - 1:end + 1] and 'cin2' in record:
                record = record.replace('cin2','cin-ii')
            if 'cin-i' in rep_string[start - 1:end + 1] and 'cin1' in record:
                record = record.replace('cin1','cin-i')
            if 'cin1-2' in rep_string[start - 1:end + 1] and 'cin1 cin2' in record:
                record = record.replace('cin1 cin2','cin1-2')
            if 'cin2-3' in rep_string[start - 1:end + 1] and 'cin2 cin3' in record:
                record = record.replace('cin2 cin3','cin2-3')
            if 'cin-1' in rep_string[start - 1:end + 1] and 'cin1' in record:
                record = record.replace('cin1','cin-1')
            if 'cin-2' in rep_string[start - 1:end + 1] and 'cin2' in record:
                record = record.replace('cin2','cin-2')
            if 'cin-3' in rep_string[start - 1:end + 1] and 'cin3' in record:
                record = record.replace('cin3', 'cin-3')
            if 'cin 2 / 3' in rep_string[start - 1:end + 1] and 'cin23' in record:
                record = record.replace('cin23','cin 2 / 3')
            if 'cin 2/3' in rep_string[start - 1:end + 1] and 'cin23' in record:
                record = record.replace('cin23','cin 2/3')
            if 'cin 1-2' in rep_string[start - 1:end + 1] and 'cin1 cin2' in record:
                record = record.replace('cin1 cin2','cin 1-2')
            if 'cin 2-3' in rep_string[start - 1:end + 1] and 'cin2 cin3' in record:
                record = record.replace('cin2 cin3','cin 2-3')
            if 'cin 1' in rep_string[start - 1:end + 1] and 'cin1' in record:
                record = record.replace('cin1','cin 1')
            if 'cin 2' in rep_string[start - 1:end + 1] and 'cin2' in record:
                record = record.replace('cin2','cin 2')
            if 'cin 3' in rep_string[start - 1:end + 1] and 'cin3' in record:
                record = record.replace('cin3','cin 3')
            if 'ii-iii cin' in rep_string[start - 1:end + 1] and 'cin2 cin3' in record:
                record = record.replace('cin2 cin3','ii-iii cin')
            if 'i-ii cin' in rep_string[start - 1:end + 1] and 'cin1 cin2' in record:
                record = record.replace('cin1 cin2','i-ii cin')
            if 'iii cin' in rep_string[start - 1:end + 1] and 'cin3' in record:
                record = record.replace('cin3','iii cin')
            if 'ii cin' in rep_string[start - 1:end + 1] and 'cin2' in record:
                record = record.replace('cin2','ii cin')
            if 'i cin' in rep_string[start - 1:end + 1] and 'cin1' in record:
                record = record.replace('cin1','i cin')
            if 'port biopsy' in rep_string[start - 1:end + 1] and 'portio biopsy' in record:
                record = record.replace('portio biopsy','port biopsy')
    return record

