import psycopg2
import re
import json
from MedTAG_sket_dock_App.models import *
import os
import numpy
import hashlib
from django.db import transaction
from django.db import connection
from collections import defaultdict
# from MedTAG_sket_dock_App. import *
# from MedTAG_sket_dock_App.utentity_linkingils_CERT_1 import *
from MedTAG_sket_dock_App.utils import *
import time
# from utils import *
# start_time = time.time()
# print('start!')
import owlready2
import argparse
import warnings
from MedTAG_sket_dock_App.sket.sket.sket import SKET

def get_range_labels_usecase(usecase):
    labs = AnnotationLabel.objects.filter(name=usecase)
    seqs = []
    for lab in labs:
        seqs.append(lab.seq_number)
    print(seqs)
    seqs.sort()
    print(seqs)

    return seqs


def run_sket_pipe(use_case,report_id,field):
    # set SKET
    try:
        sket = SKET(use_case, 'en', 'en_core_sci_sm', True, None, None, False, 0)


        dataset = {
                    'text': field,
                    'gender': None,
                    'age': None,
                    'id': report_id
        }

        # use SKET pipeline to extract concepts, labels, and graphs from dataset
        sket.med_pipeline(dataset, 'en', use_case, 0.9, True, True, False)
        return True
    except Exception as e:
        print(e)
        return False


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

def create_auto_gt(usecase,fields):

    """This method automatically creates the groundtruths"""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    mode = NameSpace.objects.get(ns_id='Robot')
    ag = User.objects.get(username='Robot_user',ns_id=mode)

    use = ''
    if usecase == 'Colon':
        use = 'colon'
    elif usecase == 'Uterine cervix':
        use = 'cervix'
    elif usecase == 'Lung':
        use = 'lung'
    if use != '':
        print(use)

    with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as use_outfile:
        json_to_ret = json.load(use_outfile)
        json_to_ret['extract_fields'][usecase] = fields
        with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'w') as out:
            json.dump(json_to_ret, out)

    with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as outfile:
        data = json.load(outfile)
        array_key_to_extract = data['extract_fields'][usecase]

    # Select reports of usecase without automatic gt associated
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT g.username FROM report AS r INNER JOIN ground_truth_log_file as g ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND g.ns_id = %s",
                    [usecase, 'Robot'])
                users = cursor.fetchall()
                cursor.execute(
                    "SELECT id_report,language,report_json FROM report WHERE name=%s AND (id_report,language) NOT IN (SELECT id_report,language FROM ground_truth_log_file WHERE username=%s)",
                    [usecase,'Robot_user'])
                reports = cursor.fetchall()

                new_users = []
                for user in users:
                    if user[0] not in new_users:
                        new_users.append(user[0])

                if len(reports) == 0:
                    # in questo caso l'utente decide di riannotare tutto, non ci sono report mancanti!!
                    # ELIMINO GT PREGRESSE
                    cursor.execute("DELETE FROM contains WHERE (id_report,language) IN (SELECT r.id_report,r.language FROM report AS r INNER JOIN contains as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND c.username IN %s)",[usecase,'Robot',tuple(new_users)])
                    cursor.execute("DELETE FROM annotate WHERE (id_report,language) IN (SELECT r.id_report,r.language FROM report AS r INNER JOIN annotate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND c.username IN %s)",[usecase,'Robot',tuple(new_users)])
                    cursor.execute("DELETE FROM associate WHERE (id_report,language) IN (SELECT r.id_report,r.language FROM report AS r INNER JOIN associate as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND c.username IN %s)",[usecase,'Robot',tuple(new_users)])
                    cursor.execute("DELETE FROM linked WHERE (id_report,language) IN (SELECT r.id_report,r.language FROM report AS r INNER JOIN linked as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND c.username IN %s)",[usecase,'Robot',tuple(new_users)])
                    cursor.execute("DELETE FROM ground_truth_log_file WHERE (id_report,language) IN (SELECT r.id_report,r.language FROM report AS r INNER JOIN ground_truth_log_file as c ON r.id_report = c.id_report AND r.language = c.language WHERE r.name = %s AND ns_id=%s AND c.username IN %s)",[usecase,'Robot',tuple(new_users)])

                    cursor.execute(
                        "SELECT id_report,language,report_json FROM report WHERE name=%s",
                        [usecase])
                    reports = cursor.fetchall()
                # reports = Report.objects.filter(name=usecase)
                # current_date = Now()
                for rep in reports[0:1]:
                    # print(rep)
                    report = Report.objects.get(id_report=rep[0], language=rep[1])
                    labels_created = False
                    concepts_created = False
                    mentions_created = False
                    linked_created = False
                    print(rep[2])
                    print(type(rep[2]))
                    # report_string = json.dumps(rep.report_json)
                    report_string = rep[2]
                    report_json = json.loads(rep[2])
                    print(report_string)
                    mentions = []
                    concepts = {'Diagnosis':[],'Test':[],'Anatomical Location':[],'Procedure':[]}
                    linked_data = []
                    for elem in array_key_to_extract:
                        print(elem)
                        ret = run_sket_pipe(use,rep[0],report_json[elem])
                        print(ret)
                        output_concepts_dir = os.path.join(workpath, './sket/outputs/concepts/raw/' + use + '/')
                        output_labels_dir = os.path.join(workpath, './sket/outputs/labels/raw/' + use + '/')
                        files_conc = os.listdir(output_concepts_dir)  # add path to each file
                        files_conc = [os.path.join(output_concepts_dir, f) for f in files_conc]

                        files_labels = os.listdir(output_labels_dir)  # add path to each file
                        files_labels = [os.path.join(output_concepts_dir, f) for f in files_labels]

                        files_conc.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                        files_labels.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                        out_file_conc = files_conc[0]
                        out_file_lab = files_labels[0]
                        if ret:
                            with open(out_file_conc,'r') as f:
                                data = json.load(f)
                                asso = data[rep[0]]
                                for element in asso:
                                    mentions = element[0]
                                    concept = element[1]
                                    url = concept[0]
                                    name = concept[1]
                                    area = concept[2]
                            with open(out_file_lab,'r') as f:
                                data = json.load(f)
                                asso = data[rep[0]]
                                for label in asso.keys():
                                    if asso[label] == 1:
                                        final_label = map_labels(label)
                                for element in asso:
                                    mentions = element[0]
                                    concept = element[1]
                                    url = concept[0]
                                    name = concept[1]
                                    area = concept[2]

                    #     mentions = mentions + ment
                    #     for key in concepts.keys():
                    #         concepts[key] = concepts[key] + con[key]
                    #     linked_data = linked_data + link
                    #
                    #     print(linked_data)
                    #     for tup in link:
                    #         print(tup)
                    #         mention = tup[0]
                    #         concept = tup[1]
                    #         concept_url = concept[0]
                    #         concept_name = concept[1]
                    #         concept_area = concept[2]
                    #
                    #         report_field = elem
                    #         concept_row = Concept.objects.get(concept_url=concept_url)
                    #         semantic_area = SemanticArea.objects.get(name=concept_area)
                    #
                    #         if (report_json.get(report_field) is not None and report_json.get(report_field) != ""):
                    #             element = report_json[report_field]
                    #
                    #             element_1 = json.dumps(element)
                    #             if element_1.startswith('"') and element_1.endswith('"'):
                    #                 element_1 = element_1.replace('"', '')
                    #
                    #             before_element = report_string.split(report_field)[0]
                    #             after_element = report_string.split(report_field)[1]
                    #             until_element_value = len(before_element) + len(report_field) + len(
                    #                 after_element.split(str(element_1))[0])
                    #             start_element = until_element_value + 1
                    #             end_element = start_element + len(str(element_1)) - 1
                    #             print(mention)
                    #             mention_1 = inverse_sanitizers(use,report_string,start_element,end_element,mention)
                    #             print(mention_1)
                    #             before_mention_element = str(element_1).split(mention_1)[0]
                    #             start_mention_element = until_element_value + len(before_mention_element) + 1
                    #             end_mention_element = start_mention_element + len(str(mention_1)) - 1
                    #             print(elem)
                    #             print(mention_1)
                    #             print(start_mention_element)
                    #             print(end_mention_element)
                    #             if not Mention.objects.filter(mention_text=mention_1, start=int(start_mention_element),
                    #                                           stop=int(end_mention_element), id_report=report,
                    #                                           language=rep[1]).exists():
                    #                 Mention.objects.create(mention_text=mention_1, start=int(start_mention_element),
                    #                                        stop=int(end_mention_element), id_report=report,
                    #                                        language=rep[1])
                    #
                    #             cur_mention = Mention.objects.get(mention_text=mention_1,
                    #                                               start=int(start_mention_element),
                    #                                               stop=int(end_mention_element), id_report=report,
                    #                                               language=rep[1])
                    #
                    #             if not Annotate.objects.filter(id_report=report, language=report.language,
                    #                                            start=cur_mention, stop=cur_mention.stop, username=ag,
                    #                                            ns_id=mode).exists():
                    #                 Annotate.objects.create(id_report=report, language=report.language,
                    #                                         start=cur_mention,
                    #                                         stop=cur_mention.stop, insertion_time=Now(), username=ag,
                    #                                         ns_id=mode)
                    #                 mentions_created = True
                    #                 # se ad esempio all'inizio sono stati automaticamente annotati 100 reports e poi ne vengono inseriti altri 50, può essere che quei 50 non abbiano auto gt. Questo significa che bisogna aggiornare il db copiando le gt anche per quegli utenti che avevano già almeno una gt copiata per quello usecase.
                    #                 for username in new_users:
                    #                     if username != 'Robot_user':
                    #                         user = User.objects.get(username=username, ns_id='Robot')
                    #                         Annotate.objects.create(id_report=report, language=report.language,
                    #                                                 start=cur_mention,
                    #                                                 stop=cur_mention.stop, insertion_time=Now(),
                    #                                                 username=user,
                    #                                                 ns_id=mode)
                    #
                    #             if not Linked.objects.filter(id_report=report, language=report.language,
                    #                                          start=cur_mention, stop=cur_mention.stop,
                    #                                          concept_url=concept_row, name=semantic_area, username=ag,
                    #                                          ns_id=mode).exists():
                    #                 Linked.objects.create(id_report=report, language=report.language, start=cur_mention,
                    #                                       stop=cur_mention.stop, insertion_time=Now(),
                    #                                       concept_url=concept_row, name=semantic_area, username=ag,
                    #                                       ns_id=mode)
                    #                 linked_created = True
                    #                 for username in new_users:
                    #                     if username != 'Robot_user':
                    #                         user = User.objects.get(username=username, ns_id='Robot')
                    #                         Linked.objects.create(id_report=report, language=report.language,
                    #                                               start=cur_mention,
                    #                                               stop=cur_mention.stop, insertion_time=Now(),
                    #                                               concept_url=concept_row, name=semantic_area,
                    #                                               username=user,
                    #                                               ns_id=mode)
                    #
                    #             if not Contains.objects.filter(id_report=report, language=report.language,
                    #                                            concept_url=concept_row, name=semantic_area, username=ag,
                    #                                            ns_id=mode).exists():
                    #                 Contains.objects.create(id_report=report, language=report.language,
                    #                                         concept_url=concept_row, name=semantic_area,
                    #                                         insertion_time=Now(), username=ag, ns_id=mode)
                    #                 for username in new_users:
                    #                     if username != 'Robot_user':
                    #                         user = User.objects.get(username=username, ns_id='Robot')
                    #                         Contains.objects.create(id_report=report, language=report.language,
                    #                                                 concept_url=concept_row, name=semantic_area,
                    #                                                 insertion_time=Now(), username=user, ns_id=mode)
                    #
                    #                 concepts_created = True
                    # # process labels
                    # con = {rep[0]:concepts}
                    # labels = []
                    # # labels = convert_concepts2labels(con)
                    # labels_list = labels[rep[0]]
                    # labels_list_new = [*labels_list]
                    # range_seq = get_range_labels_usecase(usecase)
                    # for k in labels_list_new:
                    #     ind = labels_list_new.index(k)
                    #     min = range_seq[0]
                    #     new_ind = min + ind
                    #     if labels_list[k] == 1:
                    #         print(usecase)
                    #         print(new_ind)
                    #         lab = AnnotationLabel.objects.get(seq_number=new_ind,name = usecase)
                    #         if (not Associate.objects.filter(id_report=report,language=rep[1],label=lab,seq_number=lab.seq_number,username = ag, ns_id = mode).exists()):
                    #             Associate.objects.create(insertion_time = Now(), username = ag, ns_id=mode,language=report.language, id_report = report, seq_number = lab.seq_number,label = lab)
                    #             labels_created = True
                    #             for username in new_users:
                    #                 if username != 'Robot_user':
                    #                     user = User.objects.get(username=username, ns_id='Robot')
                    #                     Associate.objects.create(insertion_time = Now(), username = user, ns_id=mode,language=report.language, id_report = report, seq_number = lab.seq_number,label = lab)
                    #
                    #
                    #
                    # if labels_created:
                    #     if not GroundTruthLogFile.objects.filter(gt_type = 'labels',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                    #         GroundTruthLogFile.objects.filter(gt_type='labels', username=ag, ns_id=mode, id_report=report,
                    #                                           language=rep[1]).delete()
                    #     ser_gt = serialize_gt('labels', usecase, 'Robot_user', rep[0], rep[1], mode)
                    #     GroundTruthLogFile.objects.create(username=ag, gt_type='labels', gt_json=ser_gt, id_report=report,
                    #                                       language=rep[1], insertion_time=Now(),ns_id=mode)
                    #     for user in new_users:
                    #         if user != 'Robot_user':
                    #             user = User.objects.get(username=user,ns_id=mode)
                    #             ser_us_gt = serialize_gt('labels', usecase, user.username, rep[0], rep[1], mode)
                    #             GroundTruthLogFile.objects.create(username=user, gt_type='labels', gt_json=ser_us_gt,
                    #                                               id_report=report,ns_id=mode,
                    #                                               language=rep[1], insertion_time=Now())
                    #
                    # if mentions_created:
                    #     if not GroundTruthLogFile.objects.filter(gt_type = 'mentions',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                    #         GroundTruthLogFile.objects.filter(gt_type='mentions', username=ag, ns_id=mode, id_report=report,
                    #                                           language=rep[1]).delete()
                    #     ser_gt = serialize_gt('mentions', usecase, 'Robot_user', rep[0], rep[1], mode)
                    #     GroundTruthLogFile.objects.create(username=ag, gt_type='mentions', gt_json=ser_gt, id_report=report,
                    #                                       ns_id=mode,language=rep[1], insertion_time=Now())
                    #     for user in new_users:
                    #         if user != 'Robot_user':
                    #             user = User.objects.get(username=user,ns_id=mode)
                    #             ser_us_gt = serialize_gt('mentions', usecase, user.username, rep[0], rep[1], mode)
                    #             GroundTruthLogFile.objects.create(username=user, gt_type='mentions', gt_json=ser_us_gt,
                    #                                               id_report=report,ns_id=mode,
                    #                                               language=rep[1], insertion_time=Now())
                    #
                    # if concepts_created:
                    #     if not GroundTruthLogFile.objects.filter(gt_type = 'concepts',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                    #         GroundTruthLogFile.objects.filter(gt_type='concepts', username=ag, ns_id=mode, id_report=report,
                    #                                           language=rep[1]).delete()
                    #     ser_gt = serialize_gt('concepts', usecase, 'Robot_user', rep[0], rep[1], mode)
                    #     GroundTruthLogFile.objects.create(username=ag, gt_type='concepts', gt_json=ser_gt,ns_id=mode, id_report=report,
                    #                                       language=rep[1], insertion_time=Now())
                    #     for user in new_users:
                    #         if user != 'Robot_user':
                    #             user = User.objects.get(username=user,ns_id=mode)
                    #             ser_us_gt = serialize_gt('concepts', usecase, user.username, rep[0], rep[1], mode)
                    #             GroundTruthLogFile.objects.create(username=user, gt_type='concepts', gt_json=ser_us_gt,
                    #                                               id_report=report,ns_id=mode,
                    #                                               language=rep[1], insertion_time=Now())
                    #
                    #
                    # if linked_created:
                    #     if not GroundTruthLogFile.objects.filter(gt_type = 'concept-mention',username=ag,ns_id=mode,id_report = report,language=rep[1]).exists():
                    #         GroundTruthLogFile.objects.filter(gt_type='concept-mention', username=ag, ns_id=mode, id_report=report,
                    #                                           language=rep[1]).delete()
                    #     ser_gt = serialize_gt('concept-mention', usecase, 'Robot_user', rep[0], rep[1], mode)
                    #     GroundTruthLogFile.objects.create(username=ag, gt_type='concept-mention', gt_json=ser_gt, id_report=report,
                    #                                       language=rep[1], ns_id=mode,insertion_time=Now())
                    #     for user in new_users:
                    #         if user != 'Robot_user':
                    #             user = User.objects.get(username=user,ns_id=mode)
                    #             ser_us_gt = serialize_gt('concept-mention', usecase, user.username, rep[0], rep[1], mode)
                    #             GroundTruthLogFile.objects.create(username=user, gt_type='concept-mention', gt_json=ser_us_gt,
                    #                                               id_report=report,ns_id=mode,
                    #                                               language=rep[1], insertion_time=Now())
        return True,''

    except Exception as error:
        print(error)
        print('ROLLBACK')

        return False,error

def inverse_sanitizers(use_case,rep_string,start,end,mention):
    mention_new = mention
    if 'octopus' in rep_string[start-1:end+1] and 'polyp' in mention:
        mention_new = mention.replace('octopus', 'polyp')
    if use_case == 'colon':
        if 'blind' in rep_string[start - 1:end + 1] and 'cecum' in mention:
            mention_new = mention.replace('cecum', 'blind')
        if 'cecal' in rep_string[start - 1:end + 1] and 'cecum' in mention:
            mention_new = mention.replace('cecum', 'cecal')
        if 'rectal' in rep_string[start - 1:end + 1] and 'rectum' in mention:
            mention_new = mention.replace('rectum', 'rectal')
        if 'proximal colon' in rep_string[start - 1:end + 1] and 'right colon' in mention:
            mention_new = mention.replace('right colon', 'proximal colon')
    return mention_new
# def copy_data_auto(usecase):
#     try:
#
#         connection = psycopg2.connect(dbname="ground_truth_3", user="postgres", password="postgres", host="localhost",
#                                       port="5432")
#         cursor = connection.cursor()
#         concepts = Contains.objects.filter()
#
#
#     except Exception as error:
#         print(error)
#
#     else:
#         return True