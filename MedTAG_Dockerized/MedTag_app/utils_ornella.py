import psycopg2
import re
import json
from MedTag_app.models import *
#from groundtruth_app.utils import *
from django.db import transaction
import os
import numpy
import hashlib
from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)
#
#
# def nan_to_null(f):
#     if f is numpy.NaN:
#         return psycopg2.extensions.AsIs('NULL')
#     else:
#         return psycopg2.extensions.Float(f)
#
#
# psycopg2.extensions.register_adapter(float, nan_to_null)

# LABELS FUNCTIONS
def get_labels(usecase):
    labels1 = AnnotationLabel.objects.filter(name=usecase).values('label','seq_number')
    labels = []
    for e in labels1:
        labels.append((e['label'], e['seq_number']))
    # print(labels)
    return labels


def update_annotation_labels(labels_to_save,usecase,user,report1,language):
    lab_saved = []
    json_response = {'message':'labels updated!'}

    for label in labels_to_save:
        # print(label)
        label1 = AnnotationLabel.objects.get(name=usecase, label=label['label'], seq_number=label['seq_number'])
        if label1 is None:
            json_response = {
                'error': 'An error occurred accessing the database, looking for the correct annotation label.'}
            return json_response

        if not Associate.objects.filter(username = user,seq_number=label1.seq_number, label=label1,
                                         id_report=report1,language = language).exists():
            label = Associate.objects.create(username=user, seq_number=label1.seq_number, label=label1,
                                             id_report=report1,language = language, insertion_time=Now())
            # print('salvato', label)
        else:
            json_response = {'message': 'Some labels were already insert in the database. This should not be possible'}
            # print('this label was already inserted')

    return json_response

def delete_all_annotation(to_del,user, report1,language,type):
    a = True
    json_response = {'message':'OK,deletion done.'}
    if len(to_del) > 0:
            ass = Associate.objects.filter(username=user, id_report=report1,language = language)
            ass.delete()
            # print('Labels deleted with success')
            obj = GroundTruthLogFile.objects.filter(username=user, id_report=report1, gt_type=type,language = language)
            obj.delete()
            # print('GT deleted with success')

    else:
        json_response = {'message': 'Nothing to delete.'}

    return json_response

def clean_mentions(user,report1,language):
    mentions = Mention.objects.filter(id_report=report1, language=language)
    for mention in mentions:
        ann = Annotate.objects.filter(start=mention.start, stop=mention.stop, id_report=report1,
                                      language=language)
        link = Linked.objects.filter(start=mention.start, stop=mention.stop,
                                     id_report=report1, language=language)




        # print(ann.count())
        # print(link.count())
        if(ann.count() == 0 and link.count() == 0):
            mention.delete()
    # print('Mentions deleted with success')
    json_response={'message':'mention deleted'}
    return json_response
# MENTION FUNCTIONS
def delete_all_mentions(user,report1,language,type,usecase):

    json_response = {'message':'OK,deletion done.'}
    # if len(to_del) > 0:
    ass = Annotate.objects.filter(username=user, id_report=report1,language = language).values('start','stop')
    # print(len(ass))
    rem_contains = False

    for el in ass:

        mention_el = Mention.objects.get(start = el['start'],stop = el['stop'], id_report = report1,language = language)
# controllo se altri utenti hanno individuato quella mention. Se sì rimuovo solo da annotate. Se no, rimuovo anche da mention
        #riga = Annotate.objects.filter(start=mention_el.start,stop=mention_el.stop, id_report=report1,language = language)

        toDel = Annotate.objects.filter(username=user, start=mention_el.start, stop=mention_el.stop,
                                        id_report=report1,language = language)
        if(toDel.exists()):
            toDel.delete()

        toDel_Linked = Linked.objects.filter(username=user,start=mention_el.start, stop=mention_el.stop,
                                        id_report=report1,language = language)
        if toDel_Linked.exists():
            concept_obj = Concept.objects.get(concept_url = toDel_Linked.first().concept_url_id)
            area_obj = SemanticArea.objects.get(name = toDel_Linked.first().name_id)
            contains_obj = Contains.objects.filter(username = user,id_report=report1,language = language,concept_url = concept_obj,
                                               name = area_obj)
            toDel_Linked.delete()

            if contains_obj.exists():
                contains_obj.delete()
                rem_contains = True
        # print(toDel)

        if(toDel.count() > 1 and toDel_Linked.count() > 1):
            json_response = {'error': 'FATAL ERROR DATABASE'}
            return json_response
        else:
            ann = Annotate.objects.filter(start=mention_el.start,stop=mention_el.stop, id_report=report1,language = language)
            link = Linked.objects.filter(start=mention_el.start, stop=mention_el.stop,
                                        id_report=report1,language = language)
            # print(ann.count())
            # print(link.count())
            # if(ann.count() == 0 and link.count() == 0):
            #     mention_el.delete()
    # print('Mentions deleted with success')

    if rem_contains == True:
        obj2 = GroundTruthLogFile.objects.filter(username=user, id_report=report1,language = language, gt_type='concepts')
        if obj2.exists():
            obj2.delete()
            if(Contains.objects.filter(username = user, id_report = report1,language = language).exists()):
                jsonDict = serialize_gt('concepts', usecase, user.username, report1.id_report, language)
                groundtruth = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                                gt_json=jsonDict,
                                                                gt_type='concepts', insertion_time=Now())

    obj = GroundTruthLogFile.objects.filter(username=user, id_report=report1,language = language, gt_type=type)
    obj1 = GroundTruthLogFile.objects.filter(username=user, id_report=report1,language = language, gt_type='concept-mention')
    if obj.exists() or obj1.exists():
        if obj.exists():
            obj.delete()
            # print('GT mention deleted with success')
        if obj1.exists():
            obj1.delete()
            # print('GT concept-mention deleted with success')

    else:
         print('nothing to delete')

    return json_response

def update_mentions(mentions,report1,language,user,usecase):
        json_response = {'message':'Mentions and Ground truth saved'}
        # print(mentions)
        var_link = False
        var_conc = False
        user_annot = Annotate.objects.filter(username = user, language = language, id_report=report1)
        for single_ann in user_annot:
            mention_cur = Mention.objects.get(start = int(single_ann.start_id),stop = int(single_ann.stop),id_report = report1,language = language)
            # print(mention_cur)
            # print(mentions)
            #La mention c'era nella lista precedente ma non nella nuova, è stata rimossa la singola mention
            ment_deleted = True
            for mention in mentions:
                # print(type(mention))
                # print((mention['start']))
                # print(single_ann.start_id)
                #mention = json.loads(mention)
                if single_ann.start_id == int(mention['start']) and single_ann.stop == int(mention['stop']):
                    ment_deleted = False

            if ment_deleted:
                annotation = Annotate.objects.filter(username = user,start = mention_cur,stop = mention_cur.stop, language = language, id_report = report1)
                if annotation.exists():
                    annotation.delete()
                link = Linked.objects.filter(username = user,start = mention_cur,stop = mention_cur.stop, language = language, id_report = report1)
                for elem in link:
                    conc = Concept.objects.get(concept_url = elem.concept_url_id)
                    area = SemanticArea.objects.get(name = elem.name_id)
                    conc_obj = Contains.objects.filter(username = user, language = language, id_report=report1,concept_url = conc,
                                                       name = area)
                    # total_conc = Linked.objects.filter(username = user,language = language, id_report=report1,concept_url = conc,
                    #                                    name = area)
                    #if conc_obj.exists() and total_conc.count() == 1:

                    if conc_obj.exists():
                        conc_obj.delete()
                        var_conc = True

                if link.exists():
                    link.delete()
                    var_link = True

        if var_link:
            obj1 = GroundTruthLogFile.objects.filter(username=user,id_report=report1,language = language, gt_type='concept-mention')
            if obj1.exists():
                obj1.delete()
                if Linked.objects.filter(username = user, language = language, id_report = report1).exists():
                    jsonDict = serialize_gt('concept-mention', usecase, user.username, report1.id_report, language)
                    c = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                          gt_json=jsonDict, gt_type='concept-mention',
                                                          insertion_time=Now())

        if var_conc:
            obj1 = GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                     gt_type='concepts')
            if obj1.exists():
                obj1.delete()
                if Contains.objects.filter(username = user, language = language, id_report = report1).exists():
                    jsonDict = serialize_gt('concepts', usecase, user.username, report1.id_report, language)
                    c = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                          gt_json=jsonDict, gt_type='concepts',
                                                          insertion_time=Now())

        for mention in mentions:
            json_val = {}
            # print(mention)
            #La mention è del tutto nuova
            #La mention è invariata
            #mention = json.loads(mentions[i])

            start_char = int(mention['start'])
            end_char = int(mention['stop'])
            mention_text = mention['mention_text']
            if not Mention.objects.filter(start=start_char, stop=end_char,id_report=report1,language = language).exists():
                obj_ment = Mention.objects.create(language = language,start=start_char, stop=end_char, mention_text=mention_text, id_report=report1)
                # print('created: ',obj_ment)

            obj = Mention.objects.get(start=start_char, stop=end_char,id_report=report1, language=language)
            if not Annotate.objects.filter(username=user,language = language, id_report=report1,start=obj, stop=obj.stop).exists() :
                b = Annotate.objects.create(username=user,language = language, id_report=report1,start=obj, stop=obj.stop, insertion_time=Now())
                # print('saved ', b)
            else:
                json_response = {'message':'You tried to save the same element twice. This is not allowed. We saved only once.'}
                # print('Some annotations previously existed! (why?) ERROR OF THE USER')


        return json_response

def check_mentions_for_linking(mentions, report1,language,user,usecase):
    json_response = {'message': 'Mentions and Ground truth saved'}
    # print(mentions)
    for i in range(len(mentions)):
        json_val = {}
        #mention = json.loads(mentions[i])
        mention = mentions[i]
        start_char = int(mention['start'])
        end_char = int(mention['stop'])
        mention_text = mention['mention_text']
        mention_el = Mention.objects.get(start= start_char,stop=end_char,id_report = report1,language = language)
        toDel_Linked = Linked.objects.filter(start=mention_el.start, stop=mention_el.stop,
                                             id_report=report1, language=language)
        toDel_anno = Annotate.objects.filter(start=mention_el.start, stop=mention_el.stop,
                                             id_report=report1, language=language)

        if((not toDel_anno.exists()) and toDel_anno.count() ==1 and toDel_Linked.exists() and toDel_Linked.count() == 1):
            toDel_Linked.delete()
            mention_el.delete()

            type = 'concept-mention'
            if GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                 gt_type=type).exists():
                GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                  gt_type=type).delete()

                jsonDict = serialize_gt(type, usecase, user.username, report1.id_report, language)
                groundtruth = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                            gt_json=jsonDict,
                                                            gt_type=type, insertion_time=Now())
                # print('salvo gt per association!')
                # print(groundtruth)

        else:
            json_response = {'message':'nothing to do with associations'}


    return json_response

# LINK FUNCTIONS
def delete_all_associations(user, report1,language,type,usecase):
        json_response = {'message':'OK,deletion done.'}
        ass = Linked.objects.filter(username=user, id_report=report1,language = language)
        modifyconc = False
        for association in ass:
            concept = Concept.objects.get(concept_url = association.concept_url_id)
            semarea = SemanticArea.objects.get(name=association.name_id)
            concepts_user = Contains.objects.filter(username = user, id_report = report1,language = language, concept_url = concept,
                                                    name=semarea)
            for con in concepts_user:
                if con.concept_url == association.concept_url and con.name == association.name:
                    con.delete()
                    modifyconc = True

        if modifyconc:
            if GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                 gt_type='concepts').exists():
                GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                  gt_type='concepts').delete()
                if Contains.objects.filter(username = user, id_report = report1, language = language).exists():
                    jsonDict = serialize_gt(type, usecase, user.username, report1.id_report, language)
                    groundtruth = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                                    gt_json=jsonDict, gt_type='concepts', insertion_time=Now())


        ass.delete()
        # print('Labels deleted with success')
        obj = GroundTruthLogFile.objects.filter(username=user, id_report=report1, language = language,gt_type=type)
        obj.delete()
        # print('GT deleted with success')
        return json_response

def update_associations(concepts,user,report1,language,usecase):

    json_response = {'message':'Associations and Ground Truth saved.'}

    modify_con = False

    user_link = Linked.objects.filter(username=user, language=language, id_report=report1)
    for single_link in user_link:
        mention_cur = Mention.objects.get(start=single_link.start_id, stop=single_link.stop, id_report=report1,
                                          language=language)
        sem_area = SemanticArea.objects.get(name=single_link.name_id)
        con = Concept.objects.get(concept_url=single_link.concept_url_id)
        concetto = Contains.objects.filter(username=user, language=language, id_report=report1,name = sem_area,concept_url=con)
        # La mention c'era nella lista precedente ma non nella nuova, è stata rimossa la singola mention
        ass_deleted = True
        # total_conc = Linked.objects.filter(username=user, language=language, id_report=report1, concept_url=con,
        #                                    name=sem_area)
        for concept in concepts:
            mention_con = Mention.objects.get(start=int(concept['start']), stop=int(concept['stop']), id_report=report1,
                                          language=language)
            sem_area_con = SemanticArea.objects.get(name=concept['semantic_area'])
            con_con = Concept.objects.get(concept_url=concept['concept_url'])

            if mention_con.start == mention_cur.start and mention_con.stop == mention_cur.stop and con.concept_url == con_con.concept_url and sem_area_con.name == sem_area.name:
                ass_deleted = False

        if ass_deleted:
            if concetto.exists():
                concetto.delete()
                modify_con = True

            single_link.delete()




    for concept1 in (concepts):
        #concept = json.loads(concept1)
        concept = concept1
        area = concept['semantic_area']
        concept_url = concept['concept_url']
        start_char = concept['start']
        end_char = concept['stop']


        obj = Mention.objects.get(start=start_char, stop=end_char, id_report=report1,language = language)
        # print(obj)

        sem = SemanticArea.objects.get(name=area)
        concept_2 = Concept.objects.get(concept_url=concept_url)
        con = Contains.objects.filter(username = user,id_report = report1,language = language, name = sem,concept_url = concept_2)
        if not con.exists():
            modify_con = True
            Contains.objects.create(username = user,id_report = report1,language = language, name = sem, concept_url = concept_2,insertion_time=Now())

        if not Linked.objects.filter(username=user, id_report=report1, language = language, name=sem, concept_url=concept_2, start=obj, stop=obj.stop).exists():
            linkInsert = Linked.objects.create(username=user, id_report=report1,language = obj.language, insertion_time=Now(), name=sem,
                                concept_url=concept_2, start=obj, stop=obj.stop)
            # print('salvato')
            # print(linkInsert)
        else:
            json_response = {'message':'You tried to save the same element twice. This is not allowed. We saved it once'}
            # print('the linked entry already exists!')

    if modify_con:
        if GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                             gt_type='concepts').exists():
            GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                              gt_type='concepts').delete()

        jsonDict = serialize_gt('concepts', usecase, user.username, report1.id_report, language)
        groundtruth = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                        gt_json=jsonDict,
                                                        gt_type='concepts', insertion_time=Now())
        # print('ok concept updated')

    return json_response

# CONTAINS
def get_list_concepts(semantic_area):
    concepts = BelongTo.objects.filter(name=semantic_area)
    conc = []
    for el in concepts:
        conc.append({'concept_name':el.concept_url.name, 'concept_url':el.concept_url.concept_url, 'semantic_area':el.name.name})
    return conc

from django.db import connection
def get_concepts_by_usecase_area(usecase,semantic_area):
    with connection.cursor() as cursor:
        cursor.execute("SELECT u.name,c.concept_url,c.name, b.name FROM concept AS c INNER JOIN concept_has_uc AS u ON c.concept_url = u.concept_url INNER JOIN belong_to AS b ON b.concept_url = c.concept_url WHERE u.name = %s AND b.name = %s", [str(usecase),str(semantic_area)])
        rows = cursor.fetchall()
        conc = []
        for el in rows:
            name = el[2]
            if '\n' in el[2]:
                name = el[2].replace('\n','')
            conc.append({'concept_name': name, 'concept_url': el[1],
                         'semantic_area': el[3]})
        return conc

    #return rows
## END


# FUNCTIONS NEEDED
def serialize_gt(gt_type,use_case,username,id_report,language):
    user = User.objects.get(username = username)
    report1 = Report.objects.get(id_report = id_report,language = language)
    jsonDict = {}
    json_rep = report1.report_json
    # jsonDict['report_id_not_hashed'] = json_rep['report_id']
    jsonErr = {'error': 'Errors in the creation of the ground_truth!'}
    jsonDict['username'] = username
    jsonDict['language'] = language
    jsonDict['id_report'] = id_report
    jsonDict['institute'] = report1.institute
    jsonDict['use_case'] = use_case
    jsonDict['gt_type'] = gt_type
    if gt_type == 'concept-mention':
        couples = Linked.objects.filter(username=user, id_report=report1.id_report,language = language).values('start','stop','concept_url', 'name')

        jsonDict['couples'] = []


        for el in couples:
            json_val = {}
            json_val['start'] = el['start']
            json_val['stop'] = el['stop']
            concept = Concept.objects.get(concept_url = el['concept_url'])
            mention = Mention.objects.get(id_report = report1,language = language,start = el['start'],stop=el['stop'])
            mention_textual = mention.mention_text
            mention_textual = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_textual)
            if language == 'Italian':
                mention_words = mention_textual.split(' ')
                text = []
                for word in mention_words:
                    if "'" in word:
                        word = word.split("'")[1]
                        text.append(word)
                    else:
                        text.append(word)
                mention_textual = ' '.join(text)
            json_val['mention_text'] = mention_textual

            json_val['semantic_area'] = el['name']
            json_val['concept_url'] = el['concept_url']
            json_val['concept_name'] = concept.name
            jsonDict['couples'].append(json_val)

        json_object = json.dumps(jsonDict)

        return jsonDict

    elif gt_type == 'concepts':
        concepts1 = Contains.objects.filter(username=user, id_report=report1,language = language).values('concept_url', 'name')
        concepts = []

        concept = {}

        areas = SemanticArea.objects.all().values('name')
        for el in areas:
            concept[el['name']] = []
        for el in concepts1:
            co = Concept.objects.get(concept_url=el['concept_url'])

            #concepts.append((el['concept_url'],co.name))

            name = el['name']
            concept[name].append((el['concept_url'],co.name))
        jsonDict['concepts'] = concept

        json_object = json.dumps(jsonDict)
        return jsonDict



    elif gt_type == 'labels':
        lab1 = Associate.objects.filter(username=user, id_report=report1,language = language).values('label', 'seq_number')
        lab = []
        jsonDict['labels'] = []
        for el in lab1:
            # print(el['label'])
            lab.append((el['label'], el['seq_number']))

            jsonVal = {}
            jsonVal['seq_number'] = el['seq_number']
            jsonVal['label'] = el['label'].replace('\n','')
            jsonDict['labels'].append(jsonVal)
        json_object = json.dumps(jsonDict)
        return jsonDict

    elif gt_type =='mentions':
        ment = Annotate.objects.filter(username = user, id_report = report1.id_report,language = language).values('start','stop')
        mentions = []
        jsonDict['mentions'] = []

        for el in ment:

            mention_text = Mention.objects.get(start = int(el['start']),stop = int(el['stop']),id_report = report1,language = language)
            # print(mention_text.mention_text)
            jsonVal = {}
            jsonVal['start'] = el['start']
            jsonVal['stop'] = el['stop']
            mention_textual = mention_text.mention_text
            #mention_textual = mention_textual.replace([\#!$%\^&\*;:{}=`~()],'')
            mention_textual = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_textual)
            if language == 'Italian':
                mention_words = mention_textual.split(' ')
                text = []
                for word in mention_words:
                    if "'" in word:
                        word = word.split("'")[1]
                        text.append(word)
                    else:
                        text.append(word)
                mention_textual = ' '.join(text)
            jsonVal['mention_text'] = mention_textual
            jsonDict['mentions'].append(jsonVal)
        json_object = json.dumps(jsonDict)

        return jsonDict
    else:
        json_object = json.dumps(jsonErr)

        return json_object

def get_report(usecase,language,institute):
    reports = Report.objects.filter(name = usecase,language = language,institute = institute).values('id_report','report_json')
    objects = []
    for report in reports:
        objects.append((report['id_report'], report['report_json']))
    return objects

def get_report_finale(usecase,language):
    reports = Report.objects.filter(name = usecase, language = language).values('id_report','report_json')
    objects = []
    for report in reports:
        objects.append((report['id_report'], report['report_json']))
    return objects


def get_last_groundtruth(username,use_case = None,language = None, institute = None):
    user = User.objects.get(username = username)
    if use_case is not None and language is not None and institute is not None:
        if GroundTruthLogFile.objects.filter(username=user).exists():
            gt = GroundTruthLogFile.objects.filter(username=user,language = language).order_by('-insertion_time')
            ## print('count_gt',gt.count())
            # for groundtruth in gt:
            #     print(groundtruth.insertion_time)
            for groundtruth in gt:
            #     print(groundtruth)

                gt_json = groundtruth.gt_json
                if(gt_json['institute']==institute and gt_json['use_case'] == use_case and gt_json['language'] == language):
                    json_response = gt_json
                    #print(gt_json)
                    return json_response
                #else: return None
        else: return None


    elif GroundTruthLogFile.objects.filter(username = user).exists():
        gt = GroundTruthLogFile.objects.filter(username = user).order_by('-insertion_time')
        ground_truth = gt.first()
        json_response = ground_truth.gt_json
        return (json_response)



def get_distinct():
    jsonDict = {}
    language = Report.objects.all().distinct('language')
    languages = []
    for lang in language:
        languages.append(lang.language)
    jsonDict['language'] = languages

    institute = Report.objects.all().distinct('institute')
    institutes = []
    for inst in institute:
        institutes.append(inst.institute)
    jsonDict['institute'] = institutes

    usecase = Report.objects.all().distinct('name')
    usecases = []
    for uc in usecase:
        usecases.append(uc.name_id)
    jsonDict['usecase'] = usecases
    return jsonDict


import pandas as pd
def check_file(type_req,reports,labels,concepts,jsonDisp,jsonAnn,username,password):
    message = 'ok'
    json_resp = {}
    json_keys = []
    usecases_list = []
    json_resp['general_message'] = ''
    json_resp['username_message'] = ''
    json_resp['report_message'] = ''
    json_resp['concept_message'] = ''
    json_resp['label_message'] = ''
    json_resp['fields_message'] = ''
    json_resp['keys'] = json_keys

    if len(concepts) == 0 and len(labels) == 0 and len(jsonAnn) == 0:
        json_resp['general_message'] = 'ERROR - You must provide at least one file between labels and concepts or at least one field to annotate'

    try:

            try:
                connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres",
                                              host="db",
                                              port="5432")
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM public.user WHERE username = %s',(str(username),))
                ans = cursor.fetchall()
                if len(ans) > 0:
                    json_resp['username_message'] = 'USRNAME - The username you selected is already taken. Choose another one.'

                if(username == ''):
                    json_resp['username_message'] = 'USRNAME - Please provide a username.'
                if(password == ''):
                    json_resp['username_message'] = 'PASSWORD - Please provide a password.'
                if password == '' and username == '':
                    json_resp['username_message'] = 'USRNAME - Please provide a username and a password.'

            except (Exception, psycopg2.Error) as e:
                print(e)
                json_resp['username_message'] = 'An error occurred handling the username and the password. Please, insert them again.'
                return json_resp

            else:
                if json_resp['username_message'] == '':
                    json_resp['username_message'] = 'Ok'

            fields = []
            all_fields = []
            fields_to_ann = []
            jsondisp = ''.join(jsonDisp)
            jsonann = ''.join(jsonAnn)
            jsondisp = jsondisp.split(',')
            jsonann = jsonann.split(',')
            # print(jsondisp)
            # print(jsonann)
            # print(jsonall)

            for el in jsondisp:
                fields.append(el)
            for el in jsonann:
                if len(el) > 0:
                    fields_to_ann.append(el)
            if len(reports) == 0:
                json_resp['report_message'] = 'REPORTS FILES - You must provide at least one file before checking'

            for i in range(len(reports)):
                if not reports[i].name.endswith('csv'):
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - The file must be .csv'

                try:
                    df = pd.read_csv(reports[i])
                except:
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - An error occurred during parsing the csv. Check if it is well formed.'
                    return json_resp
                # print(df)
                cols = list(df.columns)
                # print(cols)
                list_db_col = ['id_report', 'institute', 'usecase', 'language']

                if 'usecase' in df:
                    list_usecases_report = df.usecase.unique()
                    for el in list_usecases_report:
                        if el not in usecases_list:
                            usecases_list.append(el)
                for el in list_db_col:
                    if el not in cols:
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                            i].name + ' - The column: ' + el + ' is missing, please add a value.'

                list_not_db_col = []
                for el in cols:
                    if el not in list_db_col:
                        list_not_db_col.append(el)

                if df.shape[0] == 0:
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                        i].name + ' -  You must provide at least a report.'
                else:
                    count_nan = 0
                    for ind in range(df.shape[0]):
                        for el in list_not_db_col:
                            if df.loc[ind, el] is None:
                                count_nan = count_nan + 1
                        if count_nan == len(list_not_db_col):
                            json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(ind) + ' has the columns ' + ' ,'.join(
                                list_not_db_col) + ' empty. Provide a value for at least one of these columns. Or delete this report from the csv file.'
                    count = 0
                    for el in list_not_db_col:
                        if el not in fields and el not in fields_to_ann:
                            count = count +1
                    if count == len(list_not_db_col):
                        json_resp['fields_message'] = 'REPORTS FIELDS TO ANNOTATE - WARNING provide at least one field to display and/or annotate between:\n' + ','.join(list_not_db_col)

                    for ind in range(df.shape[0]):
                        for el in list_db_col:
                            if df.loc[ind,el] is None:
                                json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                                    i].name + ' -  You must provide at least a value for column: '+el+ ' in the row: '+str(ind) +' .'
                    # found = False
                    # for ind in range(df.shape[0]):
                    #     for el in list_not_db_col:
                    #         if df.loc[ind, el] is not None and (el in fields_to_ann or el in fields):
                    #             found = True
                    #             break
                    #     if found == False and json_resp['report_message'] == '':
                    #         json_resp['report_message'] = 'REPORTS FILE - WARNING' + reports[i].name + ' -  The report at row ' + str(ind) + ' has the columns ' + ' ,'.join(
                    #             list_not_db_col) + ' empty. Provide a value for at least one of these columns. Or delete this report from the csv file.'

            if json_resp['report_message'] == '':
                json_resp['report_message'] = 'Ok'


            if(len(concepts) > 0):
                for i in range(len(concepts)):
                    if not concepts[i].name.endswith('csv'):
                        json_resp['concept_message'] = 'CONCEPTS FILE - '+ concepts[i].name + ' - The file must be .csv'

                    try:
                        df = pd.read_csv(concepts[i])
                    except:
                        json_resp['concept_message']='CONCEPTS FILE - '+ concepts[i].name + ' - An error occurred during parsing the csv. Check if it is well formed.'
                    #print(df)
                    cols = list(df.columns)
                    #print(cols)
                    esco = False
                    list_db_col = ['concept_url', 'concept_name','usecase','area']
                    for el in cols:
                        if el.replace(' ','') not in list_db_col:
                            if el == 'usecase':
                                esco = True
                            json_resp['concept_message'] = 'CONCEPTS FILE - '+ concepts[i].name + ' - The column ' + el + ' is not allowed.'


                    if esco == False:
                        for el in df.usecase.unique():
                            if el not in usecases_list:
                                if json_resp['concept_message'] == '':
                                    json_resp['concept_message'] = 'WARNING CONCEPTS FILE - '+ concepts[i].name + ' - The usecase ' + el + ' has not any report associated. It\'ok but you can not use them until you have inserted a report with that usecase.'

                        if df.shape[0] == 0:
                            json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                                i].name + ' - You must provide at least a concept.'

                        else:
                            for ind in range(df.shape[0]):
                                for el in df:
                                    if df.loc[ind,el] is None:
                                        json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[
                                            i].name + ' - The column ' + el + ' is empty in the row: '+str(ind)+ ' .'

                if json_resp['concept_message'] == '':
                    json_resp['concept_message'] = 'Ok'


            # if len(labels) == 0:
            #     json_resp['label_message'] = 'LABELS FILES - You must provide at least one file before checking'
            if(len(labels) > 0):
                for i in range(len(labels)):
                    if not labels[i].name.endswith('csv'):
                        json_resp['label_message'] = 'LABELS FILE - '+ labels[i].name + ' - The file must be .csv'
                    try:
                        df = pd.read_csv(labels[i])
                    except:
                        json_resp['label_message'] = 'LABELS FILE - '+ labels[i].name + ' - An error occurred during parsing the csv. Check if is well formed.'
                    # print(df)
                    cols = list(df.columns)
                    list_db_col = ['label', 'usecase']
                    esco = False
                    for el in cols:
                        if el.replace(' ','') not in list_db_col:
                            if el == 'usecase':
                                esco = True
                            json_resp['label_message'] = 'LABELS FILE - '+ labels[i].name + ' - The columns: ' + el + ' is not allowed.'


                    if esco == False:
                        for el in df.usecase.unique():
                            if el not in usecases_list:
                                if json_resp['label_message'] == '':
                                    json_resp['label_message'] = 'WARNING LABELS FILE - '+ labels[i].name + ' - The usecase ' + el + ' has not any report associated. It\'s ok but you can not use them until you have inserted a report with that usecase.'

                        if df.shape[0] == 0:
                            json_resp['label_message'] = 'LABELS FILE - ' + labels[
                                i].name + ' - You must provide at least a label.'
                        else:

                            for ind in range(df.shape[0]):
                                for el in df:
                                    if df.loc[ind, el] is None:
                                        json_resp['labels_message'] = 'LABELS FILE - ' + labels[
                                            i].name + ' - The column ' + el + ' is empty in the row: ' + str(ind) + ' .'
                if json_resp['label_message'] == '':
                    json_resp['label_message'] = 'Ok'

            if len(jsonAnn) == 0 and len(jsonDisp) == 0:
                json_resp['fields_message'] = 'REPORT FIELDS TO DISPLAY AND ANNOTATE - Please provide at least one field to be displayed and/or at least one field to be annotated.'

            if len(jsonAnn) == 0:
                if json_resp['fields_message'] == '':
                    json_resp['fields_message'] = 'WARNING REPORT FIELDS TO ANNOTATE - ok but with such a configuration you will not be able to perform mention annotation and linking. Please, select also at least a field to annotate if you want to find some mentions and link them.'

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

def configure_data(reports,labels,areas,usecase,concepts,jsondisp,jsonann,jsonall,username,password):

    filename =''
    error_location = ''
    connection = ''
    usecases = []
    sem_areas = []
    out_use = ''
    out_sem = ''
    report_usecases = []
    out_rep = []
    created_file = False

    try:


        connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres", host="db",
                                port="5432")
        cursor = connection.cursor()
        try:
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            path = os.path.join(workpath, './data/')
            for filename in os.listdir(path):
                if filename != 'fields0.json' and filename.endswith('json'):
                    os.remove(filename)

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

            # query = ("SELECT * FROM use_case;")
            # cursor.execute(query)
            # ans = cursor.fetchall()
            # print(ans)
            if username is not None and password is not None:
                cursor.execute("INSERT INTO public.user (username,password,profile) VALUES(%s,%s,%s);",(str(username),hashlib.md5(str(password).encode()).hexdigest(),'Admin'))

            # print(type(jsondisp))
            # print(type(jsonann))
            #print(jsondisp)
            #print(jsonann)
            fields = []
            all_fields = []
            fields_to_ann = []
            jsonall = ''.join(jsonall)
            jsondisp = ''.join(jsondisp)
            jsonann = ''.join(jsonann)
            jsonall = jsonall.split(',')
            jsondisp = jsondisp.split(',')
            jsonann = jsonann.split(',')
            #print(jsondisp)
            #print(jsonann)
            #print(jsonall)
            for el in jsonall:
                all_fields.append(el)
            for el in jsondisp:
                fields.append(el)
            for el in jsonann:
                if len(el) > 0:
                    fields_to_ann.append(el)

            error_location = 'Reports'
            for report in reports:
                df_report = pd.read_csv(report)
                #print(df_report)
                usecases = df_report.usecase.unique()

                for el in usecases:
                    if el not in report_usecases:
                        report_usecases.append(el)
                    cursor.execute('SELECT * FROM use_case WHERE name = %s',(str(el),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute('INSERT INTO use_case VALUES(%s)',(str(el),))

                list_col_mandatory = ['id_report', 'institute', 'usecase', 'language']
                list_col_not_mandatory = []
                for col in df_report:
                    if col not in list_col_mandatory:
                        list_col_not_mandatory.append(col)

                count_rows = df_report.shape[0]
                for i in range(count_rows):
                    # id_report = df_report.loc[i, df_report.columns[0]]
                    # cursor.execute("INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);", (df_report.loc[i, df_report.columns[0]],df_report.loc[i, df_report.columns[1]],df_report.loc[i, df_report.columns[2]],df_report.loc[i, df_report.columns[3]],df_report.loc[i, df_report.columns[4]]))

                    id_report = str(df_report.loc[i, 'id_report'])
                    # report_json = df_report.loc[i, 'report_json']
                    institute = str(df_report.loc[i, 'institute'])
                    language = str(df_report.loc[i, 'language'])
                    name = str(df_report.loc[i, 'usecase'])
                    list_col_mandatory = ['id_report','institute','usecase','language']
                    report_json = {}
                    found = False
                    for col in list_col_not_mandatory:
                        # if col in jsondisp or col in jsonann:
                            if df_report.loc[i,col] is not None:
                                found = True
                                break
                    if found == False:
                        raise Exception
                    else:
                        for col in list_col_not_mandatory:
                            if df_report.loc[i,col] is not None:
                                col1 = col.replace(' ','_')
                                report_json[col1] = str(df_report.loc[i,col])

                    # if name not in report_usecases:
                    #     report_usecases.append(name)
                    (type(report_json))
                    report_json = json.dumps(report_json)
                    # if name not in usecases:
                    #     out_use = name
                    #     raise Exception

                    cursor.execute("SELECT * FROM report WHERE id_report = %s AND language = %s;",
                                   (str(id_report), str(language)))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute(
                            "INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);",
                            (str(id_report), report_json, str(institute), str(language), str(name)))


            # Popolate the labels table
            if len(labels) > 0:
                error_location = 'Labels'

                for label_file in labels:
                    df_labels = pd.read_csv(label_file)
                    count_lab_rows = df_labels.shape[0]
                    for i in range(count_lab_rows):
                        # cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);", (df_labels.loc[i, df_labels.columns[0]],df_labels.loc[i, df_labels.columns[1]],df_labels.loc[i, df_labels.columns[2]]))
                        label = str(df_labels.loc[i, 'label'])
                        name = str(df_labels.loc[i,'usecase'])
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name),))

                        cursor.execute('SELECT * FROM annotation_label')
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            seq_number = 1
                        else:
                            cursor.execute('SELECT seq_number FROM annotation_label ORDER BY seq_number DESC;')
                            ans = cursor.fetchall()
                            print(ans[0][0])

                            seq_number = int(ans[0][0]) + 1

                        name = str(df_labels.loc[i, 'usecase'])

                        # if name not in usecases:
                        #     out_use = name
                        #     raise Exception


                        cursor.execute("SELECT * FROM annotation_label WHERE seq_number = %s AND name = %s AND label = %s;", (seq_number,str(name),str(label)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);",
                                       (str(label), int(seq_number), str(name)))



                        # if name not in report_usecases:
                        #     out_rep.append(label_file.name)
                        #     out_rep.append(name)

                    # if name not in usecases:
                    #     out_use = name
                    #     raise Exception



                        # out_rep.append(label_file.name)
                        # out_rep.append(name)
            # Popolate the concepts table

            error_location = 'Concepts'

            for concept_file in concepts:
                df_concept = pd.read_csv(concept_file)
                #print(df_concept)
                count_conc_rows = df_concept.shape[0]

                list_uc_concept = df_concept.usecase.unique()
                list_area_concept = df_concept.area.unique()
                for name in list_uc_concept:
                    cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name),))

                for el in list_area_concept:
                    cursor.execute('SELECT * FROM semantic_area WHERE name = %s',(str(el),))
                    if len(cursor.fetchall()) == 0:
                        cursor.execute('INSERT INTO semantic_area VALUES (%s)',(str(el),))

                for i in range(count_conc_rows):
                    #print(df_concept.loc[i, df_concept.columns[2]])

                    df_concept = df_concept.where(pd.notnull(df_concept), None)
                    concept_url = str(df_concept.loc[i, 'concept_url'])
                    concept_name = str(df_concept.loc[i, 'concept_name'])
                    usecase = str(df_concept.loc[i, 'usecase'])
                    semantic_area = str(df_concept.loc[i, 'area'])

                    # if usecase not in report_usecases:
                    #     out_use = usecase
                    #     raise Exception
                    # if usecase not in report_usecases:
                    #     out_use = usecase
                    #     raise Exception
                        # out_rep.append(concept_file.name)
                        # out_rep.append(usecase)

                    # if semantic_area not in sem_areas:
                    #     out_sem = semantic_area
                    #     raise Exception

                    cursor.execute("SELECT * FROM concept WHERE concept_url = %s;", (str(concept_url),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute("INSERT INTO concept (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(concept_name)))

                    cursor.execute("SELECT * FROM concept_has_uc WHERE concept_url = %s AND name=%s;",
                                   (str(concept_url), str(usecase)))
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
            # for el in report_usecases:
            #     str_name_disp = el + '_fields'
            #     str_name_anno = el + '_fields_to_ann'
            #     disp_usecase = []
            #     ann_usecase = []
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            version = get_version()

            version_new = int(version) + 1
            filename = 'fields' + str(version_new)
            with open(os.path.join(workpath, './data/'+filename+'.json'), 'w') as outfile:
                json.dump(data, outfile)
                created_file = True



        except psycopg2.IntegrityError:
            connection.rollback()
            print('rolledback')
            if created_file == True:
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                # path = os.path.join(workpath, './data/fields_configured.json')
                if filename != '' and filename != 'fields0':
                    path = os.path.join(workpath, './data/'+filename+'.json')
                    os.remove(path)
            json_resp = {'error': 'an error occurred in the file: ' + error_location + '.'}
            return json_resp
        else:
            connection.commit()
            outfile.close()
            if len(out_rep) > 0:
                json_resp = {'warning': 'In the file '+ out_rep[0] + ' the usecase ' + out_rep[1] + ' has 0 reports associated, this means that the information included in the ' + out_rep[0] +' file will not be used until you upload some reports with that usecase.'}
            else:
                json_resp = {'message':'Ok'}
            return json_resp

    except (Exception,psycopg2.Error) as e:
        print(e)
        # print('rolledback')

        # if out_use != '':
        #     json_resp = {'error': 'an error occurred in the file: ' + error_location + '. The usecase '+ out_use +' is not included in usecase file. Please add it.'}
        #     return json_resp
        # elif out_sem != '':
        #     json_resp = {'error': 'an error occurred in the file: ' + error_location + '. The semantic area '+ out_sem +' is not included in semantic area file. Please add it.'}
        #     return json_resp
        json_resp = {'error': 'an error occurred in the file: ' + error_location + '.'}
        return json_resp

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

def update_db_util(type1,reports,labels,concepts,areas,usecase,jsondisp,jsonann,jsondispup,jsonannup):
    filename = ''
    error_location = ''
    connection = ''
    usecases = []
    sem_areas = []
    out_use = ''
    out_sem = ''
    # report_usecases = []
    out_rep = []
    version_new = ''
    try:
        connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres", host="db",
                                      port="5432")
        cursor = connection.cursor()
        try:
            # cursor.execute('SELECT DISTINCT name FROM report')
            # ans = cursor.fetchall()
            # for el in ans:
            #     report_usecases.append(el)

            if (jsonannup != '') or jsondispup != '':
                # print(jsondispup)
                # print(jsonannup)
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
                jsondispup = jsondispup.split(',')
                jsonannup = jsonannup.split(',')
                # print(jsondisp)
                # print(jsonannup)

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

                data['fields'] = fields
                data['fields_to_ann'] = fields_to_ann
                data['all_fields'] = all_fields
                version = get_version()

                version_new = int(version) + 1
                filename = 'fields' + str(version_new)
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                with open(os.path.join(workpath, './data/' + filename + '.json'), 'w') as outfile:
                    json.dump(data, outfile)

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
            if len(reports) > 0:
                error_location = 'Reports'
                for report in reports:
                    df_report = pd.read_csv(report)
                    print(df_report)
                    report_use = df_report.usecase.unique()
                    for el in report_use:
                        if el not in usecases:
                            out_use = el
                            cursor.execute("INSERT INTO use_case VALUES (%s)",(str(el),))

                    count_rows = df_report.shape[0]
                    list_col_mandatory = ['id_report', 'institute', 'usecase', 'language']
                    list_col_not_mandatory = []
                    for col in df_report:
                        if col not in list_col_mandatory:
                            list_col_not_mandatory.append(col)

                    for i in range(count_rows):
                        # id_report = df_report.loc[i, df_report.columns[0]]
                        # cursor.execute("INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);", (df_report.loc[i, df_report.columns[0]],df_report.loc[i, df_report.columns[1]],df_report.loc[i, df_report.columns[2]],df_report.loc[i, df_report.columns[3]],df_report.loc[i, df_report.columns[4]]))

                        id_report = str(df_report.loc[i, 'id_report'])
                        # report_json = df_report.loc[i, 'report_json']
                        institute = str(df_report.loc[i, 'institute'])
                        language = str(df_report.loc[i, 'language'])
                        name = str(df_report.loc[i, 'usecase'])
                        report_json = {}
                        found = False
                        for col in list_col_not_mandatory:
                            # col = col.replace(' ', '_')
                            if col in fields or col in fields_to_ann:
                                if df_report.loc[i, col] is not None:
                                    found = True
                                    break
                        if found == False:
                            raise Exception
                        else:
                            for col in list_col_not_mandatory:

                                if df_report.loc[i, col] is not None:

                                        col1 = col.replace(' ', '_')
                                        report_json[col1] = str(df_report.loc[i, col])

                        # if name not in report_usecases:
                        #     report_usecases.append(name)
                        print(type(report_json))
                        report_json = json.dumps(report_json)
                        # if name not in usecases:
                        #     out_use = name
                        #     raise Exception

                        cursor.execute("SELECT * FROM report WHERE id_report = %s AND language = %s;",
                                       (str(id_report), str(language)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute(
                                "INSERT INTO report (id_report,report_json,institute,language,name) VALUES (%s,%s,%s,%s,%s);",
                                (str(id_report), report_json, str(institute), str(language), str(name)))

            # Popolate the labels table
            if len(labels) > 0:
                error_location = 'Labels'

                for label_file in labels:
                    df_labels = pd.read_csv(label_file)
                    count_lab_rows = df_labels.shape[0]
                    for i in range(count_lab_rows):
                        # cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);", (df_labels.loc[i, df_labels.columns[0]],df_labels.loc[i, df_labels.columns[1]],df_labels.loc[i, df_labels.columns[2]]))
                        label = str(df_labels.loc[i, 'label'])
                        name = str(df_labels.loc[i,'usecase'])
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%S)', (str(name),))

                        cursor.execute('SELECT * FROM annotation_label')
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            seq_number = 1
                        else:
                            cursor.execute('SELECT seq_number FROM annotation_label ORDER BY seq_number DESC;')
                            ans = cursor.fetchall()
                            print(ans[0][0])

                            seq_number = int(ans[0][0]) + 1

                        name = df_labels.loc[i, 'usecase']

                        # if name not in usecases:
                        #     out_use = name
                        #     raise Exception


                        cursor.execute("SELECT * FROM annotation_label WHERE seq_number = %s AND name = %s AND label = %s;", (seq_number,str(name),str(label)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);",
                                       (str(label), int(seq_number), str(name)))



                        # if name not in report_usecases:
                        #     out_rep.append(label_file.name)
                        #     out_rep.append(name)

            # Popolate the concepts table
            if len(concepts) > 0:

                error_location = 'Concepts'
                for concept_file in concepts:
                    df_concept = pd.read_csv(concept_file)
                    print(df_concept)
                    count_conc_rows = df_concept.shape[0]

                    list_uc_concept = df_concept.usecase.unique()
                    list_area_concept = df_concept.area.unique()
                    # for el in list_uc_concept:
                    #     if el not in usecases:
                    #         raise Exception
                    for name in list_uc_concept:
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%S)', (str(name),))
                    for el in list_area_concept:
                        cursor.execute('SELECT * FROM semantic_area WHERE name = %s', (str(el),))
                        if len(cursor.fetchall()) == 0:
                            cursor.execute('INSERT INTO semantic_area VALUES (%s)', (str(el),))


                    for i in range(count_conc_rows):
                        print(df_concept.loc[i, df_concept.columns[2]])

                        df_concept = df_concept.where(pd.notnull(df_concept), None)
                        concept_url = df_concept.loc[i, 'concept_url']
                        concept_name = df_concept.loc[i, 'concept_name']
                        usecase = df_concept.loc[i, 'usecase']
                        semantic_area = df_concept.loc[i, 'area']

                        # if usecase not in usecases:
                        #     out_use = usecase
                        #     raise Exception

                        # if usecase not in report_usecases:
                        #     out_rep.append(concept_file.name)
                        #     out_rep.append(usecase)

                        # if semantic_area not in sem_areas:
                        #     print(semantic_area)
                        #     cursor.execute("SELECT * FROM semantic_area WHERE name = %s",(semantic_area,))
                        #     ans = cursor.fetchall()
                        #     print(ans)
                        #     if len(ans) == 0:
                        #         cursor.execute("INSERT INTO semantic_area VALUES (%s)", (semantic_area,))

                        #print(df_concept)
                        cursor.execute("SELECT * FROM concept WHERE concept_url = %s;", (str(concept_url),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO concept (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(concept_name)))

                        cursor.execute("SELECT * FROM concept_has_uc WHERE concept_url = %s AND name=%s;", (str(concept_url),str(usecase)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO concept_has_uc (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(usecase)))

                        cursor.execute("SELECT * FROM belong_to WHERE concept_url = %s AND name=%s;", (str(concept_url),str(semantic_area)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO belong_to (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(semantic_area)))
            # print(jsonann)



            if ((jsonann is not None) and (jsonann != '')) or ((jsondisp is not None) and jsondisp != ''):
                data = {}
                # print(type(jsondisp))
                # print(type(jsonann))
                print(jsondisp)
                print(jsonann)
                fields = []
                fields_to_ann = []
                version = get_version()
                if int(version) != 0:
                    json_resp = get_fields_from_json()
                    all_fields = json_resp['all_fields']
                    #fields = json_resp['fields']
                    fields_to_ann = json_resp['fields_to_ann']
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
                for el in jsonann:
                    if len(el) > 0:
                        if el not in fields_to_ann:
                            fields_to_ann.append(el)

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


        except psycopg2.IntegrityError as e:
            print(e)
            connection.rollback()
            print('rolledback')
            if type1 == 'json_fields' and created_file == True:
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                # path = os.path.join(workpath, './data/fields_configured.json')
                if filename != '' and filename != 'fields0':
                    path = os.path.join(workpath, './data/'+filename+'.json')
                    os.remove(path)

            # if out_use != '':
            #     json_resp = {
            #         'error': 'an error occurred in the file: ' + error_location + '. The usecase ' + out_use + ' is not included in usecase file. Please add it.'}
            #     return json_resp
            # elif out_sem != '':
            #     json_resp = {
            #         'error': 'an error occurred in the file: ' + error_location + '. The semantic area ' + out_sem + ' is not included in semantic area file. Please add it.'}
            #     return json_resp


            json_resp = {'error': 'an error occurred in the file: ' + error_location + '. Maybe the ids of the new reports are duplicated.'}
            return json_resp
        else:
            connection.commit()
            if (jsonann is not None) and (jsonann != ''):
                outfile.close()

            json_resp = {'message': 'Ok'}

            return json_resp

    except (Exception, psycopg2.Error) as e:
        print(e)
        # print('rolledback')
        json_resp = {'error': 'an error occurred in the file: ' + error_location + '. Maybe the ids of the new reports are duplicated.'}
        return json_resp

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()


# def get_json_keys(reports):
#     json_keys = []
#     for i in range(len(reports)):
#         df = pd.read_csv(reports[i], quotechar='"', skipinitialspace=True)
#         print(df)
#         cols = list(df.columns)
#         print(cols)
#
#         json_col = df['report_json'].tolist()
#         for el in json_col:
#                 el = json.loads(el)
#                 for key in el.keys():
#                     if key not in json_keys:
#                         json_keys.append(key)
#
#     return json_keys


def get_keys_csv(reports):
    keys = []
    for report in reports:
        df = pd.read_csv(report)
        col_list = ['id_report','language','institute','usecase']
        for col in df:
            if col not in col_list and col not in keys:
                keys.append(col.replace(' ','_'))
    return keys

def get_keys_csv_update(reports):
    keys = get_keys_csv(reports)
    keys_to_ret = []
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, './data/')
    search_dir = path
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x),reverse=True)
    json_file = open(files[0], 'r')
    data = json.load(json_file)
    all = data['all_fields']
    for el in keys:
        if el not in all:
            keys_to_ret.append(el)

    return keys_to_ret


def get_fields_from_json():
    json_resp = {}
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, './data/')
    search_dir = path
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x),reverse=True)
    json_file = open(files[0], 'r')

    # path = os.path.join(workpath, './data/fields_updated.json')
    # path1 = os.path.join(workpath, './data/fields_configured.json')
    # if os.path.isfile(path1):
    #     json_file =  open(os.path.join(workpath, './data/fields_updated.json'), 'r')
    # elif os.path.isfile(path):
    #     json_file =  open(os.path.join(workpath, './data/fields_configured.json'), 'r')
    # else:
    #     json_file =  open(os.path.join(workpath, './data/fields0.json'), 'r')
    data = json.load(json_file)
    json_resp['fields'] = data['fields']
    json_resp['fields_to_ann'] = data['fields_to_ann']
    json_resp['all_fields'] = data['all_fields']
    return json_resp

def get_fields_from_json_usecase(usecase):
    json_resp = {}
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, './data/')
    search_dir = path
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x),reverse=True)
    json_file = open(files[0], 'r')

    data = json.load(json_file)
    json_resp['fields'] = data['fields']
    json_resp['fields_to_ann'] = data['fields_to_ann']
    json_resp['all_fields'] = data['all_fields']
    reports = Report.objects.filter(name=usecase)
    for report in reports:
        rep = (report.report_json)
        for key in rep.keys():
            if key in json_resp['fields']:
                if key not in json_resp['fields']:
                    json_resp['fields'].append(key)
            if key in json_resp['fields_to_ann']:
                if key not in json_resp['fields_to_ann']:
                    json_resp['fields_to_ann'].append(key)

    # print(json_resp)
    return json_resp

def check_for_update(type_req,reports,labels,concepts,areas,usecase,jsonDisp,jsonAnn,jsonDispUp,jsonAnnUp):
    usecases = []
    sem_areas = []
    json_keys = []
    keys = get_fields_from_json()
    disp = keys['fields']
    ann = keys['fields_to_ann']
    all = keys['all_fields']
    # print(jsonDispUp)
    # print(jsonAnnUp)
    if(jsonDispUp is not None and jsonAnnUp is not None):
        jsonDispUp = ''.join(jsonDispUp)
        jsonAnnUp = ''.join(jsonAnnUp)
        jsonDispUp = jsonDispUp.split(',')
        jsonAnnUp = jsonAnnUp.split(',')
        # print(jsonDispUp)
        # print(jsonAnnUp)


    try:
        connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres", host="db",
                                port="5432")
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
        message = 'ok'
        json_rep = ''
        json_keys = []


        if len(concepts) > 0:

            message = 'ok'
            for i in range(len(concepts)):
                if not concepts[i].name.endswith('csv'):
                    message = 'CONCEPTS FILE - The file must be .csv'
                    return json_keys,message

                df = pd.read_csv(concepts[i])
                # print(df)
                distinct_concept_usecase = []
                esco = False
                if 'usecase' in df:
                    distinct_concept_usecase = df['usecase'].unique()
                else:
                    esco = True

                if esco == False:
                    for el in distinct_concept_usecase:

                        if el not in distinct_uc_report:
                            message = 'CONCEPTS FILE - WARNING: The file contains the concepts for the usecase ' + el + ' which has 0 reports associated.'


                cols = list(df.columns)
                # print(cols)
                list_db_col = ['concept_url', 'concept_name','usecase','area']
                for el in cols:
                    if el.replace(' ','') not in list_db_col:
                        message = 'CONCEPTS FILE - The columns: ' + el + 'is not allowed.'
                        return json_keys,message

                if df.shape[0] == 0:
                    message = 'CONCEPTS FILE - You must provide at least a concept.'
                    return json_keys,message
                else:
                    for ind in range(df.shape[0]):
                        for el in df:
                            if df.loc[ind,el] is None:
                                message = 'CONCEPTS FILE - You must provide a value for the field: ' + el + ' at the row ' + str(ind)
                                return json_keys, message
            return json_keys,message


        elif len(labels) > 0:

            message = 'ok'
            for i in range(len(labels)):
                if not labels[i].name.endswith('csv'):
                    message = 'LABELS FILE - The file must be .csv'
                    return json_keys,message

                df = pd.read_csv(labels[i])
                # print(df)
                if 'usecase' in df:
                    distinct_label_usecase = df['usecase'].unique()
                    for el in distinct_label_usecase:
                        # if el not in usecases:
                        #     message = 'LABELS FILE - The usecase ' + el + ' is not included in the usecases.'
                        #     return json_keys,message

                        if el not in distinct_uc_report:
                            if message == 'ok':
                                message = 'LABELS FILE - WARNING: The file contains the labels for '+ el+' which has 0 reports associated. You can not annotate them until you add the reports for that usecase.'

                cols = list(df.columns)
                list_db_col = ['label', 'usecase']
                for el in cols:
                    if el.replace(' ','') not in list_db_col:
                        message = 'LABELS FILE - The columns: ' + el + 'is not allowed.'
                        return json_keys,message


                if df.shape[0] == 0:
                    message = 'LABELS FILE - You must provide at least a label.'
                    return json_keys,message
                else:
                    for ind in range(df.shape[0]):
                        for el in df:
                            if df.loc[ind,el] is None:
                                message = 'LABELS FILE - You must provide a value for the field: ' + el + ' at the row ' + str(ind)
                                return json_keys, message
            return json_keys, message


        elif len(reports) > 0:
            message = 'ok'
            for i in range(len(reports)):
                if not reports[i].name.endswith('csv'):
                    message = 'REPORTS FILE - '+ reports[i].name + ' - The file must be .csv'
                    return json_keys,message

                df = pd.read_csv(reports[i])
                distinct_rep_usecase = df['usecase'].unique()


                # print(df)
                cols = list(df.columns)

                # print(cols)
                list_db_col = ['id_report','institute','usecase','language']
                list_not_db_col = []
                for el in cols:
                    if el not in list_db_col:
                        list_not_db_col.append(el)

                count = 0
                if (jsonDispUp is not None and jsonAnnUp is not None):
                    if (len(disp) > 0 or len(ann) > 0):
                        for el in list_not_db_col:
                            if(el not in disp and el not in ann) and (el not in jsonDispUp and el not in jsonAnnUp):
                                count = count + 1

                if count == len(list_not_db_col):
                    message='REPORT FIELDS: Please, provide at least one field to display. Be careful that if you do not provide one field to annotate you will not be able to perform mention annotation and linking.'
                    return json_keys, message
                if (jsonAnnUp) is not None:
                    if jsonAnnUp[0] == '':
                        print('MESSAGGIO')
                        message='REPORT FIELDS - WARNING: Please, provide at least one field to annotate. If you do not provide them you will not be able to perform mention annotation and linking. '



                for el in list_db_col:
                    if el not in cols:
                        message = 'REPORTS FILE - '+ reports[i].name + ' - The columns: ' + el + ' must be inserted.'
                        return json_keys,message




                if df.shape[0] == 0:
                    message = 'REPORTS FILE - ' + reports[i].name + ' -  You must provide at least a report.'
                    return json_keys,message
                else:
                    for ind in range(df.shape[0]):
                        found = False
                        for el in list_db_col:
                            if df.loc[ind,el] is None:
                                message = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(
                                    ind) + ' has the column ' + el + ' empty. Provide a value for this column.'
                                return json_keys, message
                        for el in list_not_db_col:
                            if df.loc[ind, el] is not None:
                                found = True
                                break
                        if found == False:
                            message = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(ind) + ' has the columns ' + ' ,'.join(list_not_db_col) + ' empty. Provide a value for at least one of these columns. Or delete this report from the csv file.'
                            return json_keys, message

        if(type_req == 'json_fields' and len(jsonAnn) == 0):
            message = 'REPORT FIELDS TO ANNOTATE - ok, but with such a configuration you will not be able to perform mention annotation and linking. Please, select also at least a field to annotate if you want to find some mentions and link them'
            return json_keys,message


        if type_req == 'labels' and len(labels) == 0:
            message = 'LABELS TO ANNOTATE - Please insert a labels file.'
            return json_keys,message

        if type_req == 'concepts' and len(concepts) == 0:
            message = 'CONCEPTS TO ANNOTATE - Please insert a concepts file.'
            return json_keys,message

        if type_req == 'reports' and len(reports) == 0:
            message = 'REPORTS TO ANNOTATE - Please insert a reports file.'
            return json_keys,message

        return json_keys,message

    except (Exception,psycopg2.Error) as e:
        print(e)
        message='An error occurred in ' + type_req + ' file(s). Please check if it is similar to the example we provided.'
        return json_keys,message

    finally:
        cursor.close()
        connection.close()

def get_version():
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, 'data')
    search_dir = path
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    name = (os.path.splitext(files[0])[0])
    version = name.split('fields')[1]
    return version

def create_json_to_download(username,use = None,inst = None,lang = None, action = None,all = None):
    json_resp = {}
    json_resp['ground_truth'] = []
    if all == 'all':
        gt = GroundTruthLogFile.objects.filter(username=username)
        for el in gt:
            gt_json = el.gt_json
            json_resp['ground_truth'].append(gt_json)

    elif use is None and lang is None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                if gt_json['gt_type'] == action:
                    json_resp['ground_truth'].append(gt_json)


    elif use is not None and lang is not None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['institute'] == inst and gt_json['use_case'] == use and gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is not None and lang is not None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['use_case'] == use and gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is not None and lang is None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['institute'] == inst and gt_json['use_case'] == use and gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)


    elif use is None and lang is not None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['institute'] == inst and gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is not None and lang is None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['use_case'] == use and gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is None and lang is None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['institute'] == inst and gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is None and lang is not None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                if (gt_json['gt_type'] == action):
                    json_resp['ground_truth'].append(gt_json)

    return (json_resp)

import csv
def create_csv_to_download(username,use,inst,lang,action):
    row_list = []
    if action == 'labels':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'label'])
    elif action == 'mentions':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'start','stop','mention_text'])
    elif action == 'concept-mention':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'start', 'stop', 'mention_text','concept_url','concept_name','area'])
    elif action == 'concepts':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'concept_url','concept_name','area'])


    if use is None and lang is None and inst is None and action is not None:

        if action == 'labels':

            asso = Associate.objects.filter(username = username)
            for el in asso:
                print(el.id_report)
                print(el.language)
                report = Report.objects.get(id_report = el.id_report_id, language = el.language)

                row = [username,report.id_report,report.language,report.institute,report.name_id,el.label_id]
                row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username = username)
            for el in anno:
                report = Report.objects.get(id_report = el.id_report_id, language = el.language)
                mention = Mention.objects.get(start = el.start_id,stop = el.stop,id_report=report,language = report.language)
                row = [username,report.id_report,report.language,report.institute,report.name_id,mention.start,mention.stop,mention.mention_text]
                row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username = username)
            for el in cont:
                report = Report.objects.get(id_report = el.id_report_id, language = el.language)
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                row = [username,report.id_report,report.language,report.institute,report.name_id,concept.concept_url,concept.name,el.name_id]
                row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username = username)
            for el in cont:
                report = Report.objects.get(id_report = el.id_report_id, language = el.language)
                mention = Mention.objects.get(start = el.start_id,stop = el.stop,id_report=report,language = report.language)
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                row = [username,report.id_report,report.language,report.institute,report.name_id,mention.start,mention.stop,mention.mention_text,concept.concept_url,concept.name,el.name_id]
                row_list.append(row)






    elif use is not None and lang is not None and inst is not None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id, name = use, language=lang, institute = inst)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name = use, language=lang, institute=inst)
                    row = [username, report.id_report, lang, inst, use, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id,name=use, language=lang, institute=inst)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                               id_report=report, language=lang)
                if report.exists():
                    report = Report.objects.get(id_report=anno.id_report,name=use,language=lang, institute = inst)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                     id_report=report, language=lang)

                    row = [username, report.id_report, lang,inst,use, mention.start, mention.stop, mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id,name=use, language=lang, institute=inst)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=use, language=lang, institute=inst)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, lang, inst, use, concept.concept_url,
                       concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, name=use, language=lang, institute=inst)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                               id_report=report, language=lang)

                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=use, language=lang, institute=inst)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                      id_report=report, language=lang)
                    row = [username, report.id_report, lang, inst, use, mention.start,
                       mention.stop, mention.mention_text, concept.concept_url, concept.name,el.name_id]
                    row_list.append(row)

    elif use is not None and lang is not None and inst is None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id,name = use, language=lang)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name = use,language=lang)
                    row = [username, report.id_report, lang, report.institute, use, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id, name=use, language=lang)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                                  id_report=report, language=lang)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=use, language=lang)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=lang)

                    row = [username, report.id_report, lang, report.institute, use, mention.start, mention.stop,
                           mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, name=use, language=lang, institute=inst)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=use, language=lang, institute=inst)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, lang, report.institute, use, concept.concept_url,
                           concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, name=use, language=lang)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                                   id_report=report, language=lang)

                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=use, language=lang)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=lang)
                    row = [username, report.id_report, report.language, report.institute, report.name_id, mention.start,
                           mention.stop, mention.mention_text, concept.concept_url, concept.name,el.name_id]
                    row_list.append(row)

    elif use is not None and lang is None and inst is not None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id, language = el.language, name=use, institute = inst)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id,language = el.language, name=use, institute = inst)
                    row = [username, report.id_report, report.language, report.institute, use, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id, language = el.language, name=use, institute = inst)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                                  id_report=report, language=el.language)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use,
                                                   institute=inst)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=report.language)

                    row = [username, report.id_report, report.language, report.institute, use, mention.start, mention.stop,
                           mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, language = el.language, name=use, institute = inst)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use,
                                                   institute=inst)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, report.language, inst, use, concept.concept_url,
                           concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, language = el.language, name=use, institute = inst)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                                   id_report=report, language = el.language)

                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use,
                                                   institute=inst)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language = report.language)
                    row = [username, report.id_report, report.language, inst, use, mention.start,
                           mention.stop, mention.mention_text, concept.concept_url, concept.name,el.name_id]
                    row_list.append(row)


    elif use is None and lang is not None and inst is not None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id, language=lang, institute=inst)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=lang, institute=inst)
                    row = [username, report.id_report, lang, inst, report.name_id, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id, language=lang, institute=inst)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                                  id_report=report, language=lang)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=lang, institute=inst)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=lang)

                    row = [username, report.id_report, lang, inst, report.name_id, mention.start, mention.stop,
                           mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, language=lang, institute=inst, name = el.name_id)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=lang, institute=inst, name=el.name_id)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, lang, inst, report.name_id, concept.concept_url,
                           concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, language=lang, institute=inst, name = el.name_id)
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                                   id_report=report, language=lang)

                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=lang, institute=inst, name=el.name_id)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=lang)
                    row = [username, report.id_report, lang, inst, report.name_id, mention.start,
                           mention.stop, mention.mention_text, concept.concept_url, concept.name,el.name_id]
                    row_list.append(row)

    elif use is not None and lang is None and inst is None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language, name=use)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use)
                    row = [username, report.id_report, report.language, report.institute, use, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language, name=use)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                                  id_report=report, language=el.language)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=report.language)

                    row = [username, report.id_report, report.language, report.institute, use, mention.start, mention.stop,
                           mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language, name=use)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, report.language, report.institute, use, concept.concept_url,
                           concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language, name=use)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                                   id_report=report, language=el.language)

                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=use)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=report.language)
                    row = [username, report.id_report, report.language, report.institute, use, mention.start,
                           mention.stop, mention.mention_text, concept.concept_url, concept.name,el.name_id]
                    row_list.append(row)
    elif use is None and lang is None and inst is not None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language,name = el.name_id)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=el.name_id)
                    row = [username, report.id_report, report.language, inst, report.name_id, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language,name = el.name_id)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                                  id_report=report, language=el.language)
                if report.exists() :
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=el.name_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=el.language)

                    row = [username, report.id_report, report.language, inst, report.name_id, mention.start, mention.stop,
                           mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language,name = el.name_id)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=el.name_id)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, report.language, inst, report.name_id, concept.concept_url,
                           concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id,language = el.language,name = el.name_id)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                                   id_report=report, language=el.language)

                if report.exists()  and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, language=el.language, name=el.name_id)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=report.language)
                    row = [username, report.id_report, report.language, inst, report.name_id, mention.start,
                           mention.stop, mention.mention_text, concept.concept_url, concept.name,el.name_id]
                    row_list.append(row)

    elif use is None and lang is not None and inst is None and action is not None:
        if action == 'labels':

            asso = Associate.objects.filter(username=username)
            for el in asso:
                report = Report.objects.filter(id_report=el.id_report_id, name=el.name_id, language=lang)
                if report.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=el.name_id, language=lang)
                    row = [username, report.id_report, report.language, report.institute, report.name_id, el.label_id]
                    row_list.append(row)

        elif action == 'mentions':
            anno = Annotate.objects.filter(username=username)
            for el in anno:
                report = Report.objects.filter(id_report=el.id_report_id, name=el.name_id, language=lang)
                # mention = Mention.objects.filter(start=el.start_id, stop=el.stop,
                #                                  id_report=report, language=lang)
                if report.exists():
                    report = Report.objects.get(id_report=anno.id_report, name=use, language=lang, institute=inst)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=lang)

                    row = [username, report.id_report, report.language, report.institute, report.name_id, mention.start, mention.stop,
                           mention.mention_text]
                    row_list.append(row)

        elif action == 'concepts':
            cont = Contains.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, name=el.name_id, language=lang)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=el.name_id, language=lang)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    row = [username, report.id_report, report.language, report.institute, report.name_id, concept.concept_url,
                           concept.name,el.name_id]
                    row_list.append(row)

        elif action == 'concept-mention':
            cont = Linked.objects.filter(username=username)
            for el in cont:
                report = Report.objects.filter(id_report=el.id_report_id, name=el.name_id, language=lang)
                concept = Concept.objects.filter(concept_url=el.concept_url_id)
                # mention = Mention.objects.mention(start=el.start_id, stop=el.stop,
                #                                   id_report=report, language=lang)

                if report.exists() and concept.exists():
                    report = Report.objects.get(id_report=el.id_report_id, name=el.name_id, language=lang)
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop,
                                                  id_report=report, language=lang)
                    row = [username, report.id_report, report.language, report.institute, report.name_id, mention.start,
                           mention.stop, mention.mention_text, concept.concept_url, concept.name, el.name_id]
                    row_list.append(row)

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, './static/temp/')
    with open(path +'temp.csv', 'w', newline='') as file:
        try:
            writer = csv.writer(file)
            writer.writerows(row_list)

            return True
        except Exception as e:
            print(e)
            return False
