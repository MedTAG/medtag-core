import psycopg2
import re
import json
from MedTAG_sket_dock_App.models import *
import os
import numpy
import hashlib
from django.db import connection
import pandas as pd
from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)
from django.db.models import Count
from django.db import transaction
import datetime

def get_user_gt(username,mode,report1,language,action):

    """This method is needed to satisfy GET requests for each task: when this method is called for a specific task,
    report,language the user's annotation is returned."""

    try:
        username = User.objects.get(username=username,ns_id=mode)
        if action == 'labels':
            labels = Associate.objects.filter(username=username, ns_id=mode, id_report=report1, language=language).values(
                'seq_number', 'label')
            json_dict = {}
            json_dict['labels'] = []

            if len(labels) > 0:
                for el in labels:
                    json_val = {}
                    json_val['label'] = (el['label'])
                    json_val['seq_number'] = (el['seq_number'])
                    json_dict['labels'].append(json_val)

            json_dict['labels'] = sorted(json_dict['labels'], key=lambda json: json['seq_number'])
            # print(json_dict['labels'])
            return json_dict

        elif action == 'mentions':
            a = Annotate.objects.filter(username=username, ns_id=mode, id_report=report1, language=language).values(
                'start','stop')
            json_dict = {}
            json_dict['mentions'] = []
            for el in a:
                mention_text = Mention.objects.get(start=int(el['start']), stop=int(el['stop']), id_report=report1,
                                                   language=language)
                json_val = {}
                json_val['start'] = (el['start'])
                json_val['stop'] = (el['stop'])
                json_val['mention_text'] = mention_text.mention_text
                json_dict['mentions'].append(json_val)
            return json_dict

        elif action == 'concept-mention':
            associations = Linked.objects.filter(username=username, ns_id=mode, language=language,
                                                 id_report=report1.id_report).values('name', 'start', 'stop', 'concept_url')
            json_dict = {}
            json_dict['associations'] = []
            for el in associations:
                mention_text = Mention.objects.get(start=int(el['start']), stop=int(el['stop']), id_report=report1,
                                                   language=language)
                json_val = {}
                concept_name = Concept.objects.get(concept_url=el['concept_url'])
                json_val['start'] = (el['start'])
                json_val['stop'] = (el['stop'])
                json_val['mention_text'] = mention_text.mention_text
                json_val['semantic_area'] = el['name']
                json_val['concept_name'] = concept_name.name.replace('\n', '')  # Rimuovo il replace
                json_val['concept_url'] = el['concept_url']
                json_dict['associations'].append(json_val)
            return json_dict

        elif action == 'concepts':
            json_dict = get_contains_records(report=report1, language=language, ns_id=mode, user=username)

            return json_dict

    except Exception as e:
        print(e)

def check_concept_report_existance(report, concept, user, ns_id,semantic_area,language):

    """This method checks whether the user already annotated a concept for a specific report,language,semantic area."""

    check = False
    report = Report.objects.get(id_report=report,language = language)
    user = User.objects.get(username=user,ns_id=ns_id)
    concept = Concept.objects.get(concept_url=concept)
    semantic_area = SemanticArea.objects.get(name=semantic_area)
    rows = Contains.objects.filter(id_report = report, language = language,username = user, ns_id=ns_id,concept_url = concept, name = semantic_area)

    if len(rows) > 0:
        print("[ rows >0 ] for (report, concept) : (" + str(report) + ", "+concept.concept_url+")")
        check = True
    else:
        print("[ 0 rows ] for (report, concept) : (" + str(report) + ", "+concept.concept_url+")")

    return check


def populate_contains_table(report, concept, user, ns_id,semantic_area,language):

    """This method creates an entry in contains table for a specific user,concept,semantic area, report, language."""

    connection = False
    status = False

    report = Report.objects.get(id_report = report,language = language)
    user = User.objects.get(username = user,ns_id=ns_id)
    concept = Concept.objects.get(concept_url = concept)
    semantic_area = SemanticArea.objects.get(name = semantic_area)
    Contains.objects.create(id_report = report, ns_id=ns_id,username = user,language = language,concept_url = concept, name = semantic_area, insertion_time = Now())

    status = "Ok"
    return status


def get_contains_records(report=None, language = None, concepts=None,ns_id=None, user=None, semantic_area=None):

    """This method returns the list of records in contains table for a specific user, language, report semantic area."""

    records = []
    reports_dict = {}

    if report is not None and concepts is not None and user is not None and semantic_area is not None:
        for concept in concepts:
            for record in Contains.objects.filter(id_report=report, language = language, concept_url=concept, username=user,ns_id=ns_id, name=semantic_area):
                records.append(record)
    elif report is not None and user is not None and semantic_area is not None:
            for record in Contains.objects.filter(id_report=report,language = language, username=user,ns_id=ns_id, name=semantic_area):
                records.append(record)
    elif report is not None and user is not None:
            for record in Contains.objects.filter(id_report=report,language = language,ns_id=ns_id, username=user):
                records.append(record)


    response_dict = {}
    reports = {}
    sem_areas = SemanticArea.objects.all()
    for el in sem_areas:
        reports[el.name] = []
    if (len(records) > 0):

        for index, record in enumerate(records):
            # print(record)

            concept = record.concept_url
            semantic_area = record.name
            concept_mod = Concept.objects.get(concept_url=concept.concept_url)
            # report_dict = {"timestamp": str(record.insertion_time), "concept_url": str(concept.concept_url),
            #                "report_id": str(report.id_report),"concept_name":str(concept_mod.name),
            #                "user": str(user.username), "semantic_area": str(semantic_area.name)}

            report_dict = {"concept_url": str(concept.concept_url),
                           "concept_name": str(concept_mod.name),
                           "semantic_area": str(semantic_area.name)}
            reports[semantic_area.name].append(report_dict)


    reports_dict = {"concepts": reports}


    # print(records)
    # print(reports_dict)
    return reports


def delete_contains_record(report=None, language = None,concept=None,ns_id=None, user=None, semantic_area=None):

    """This method deletes one or more records from the table contains."""

    response_dict = {"Error": "Invalid parameters"}

    if report is not None and concept is not None and user is not None and semantic_area is not None:
        if Contains.objects.filter(id_report=report, ns_id=ns_id,concept_url=concept,language = language, username=user, name=semantic_area).delete():
            response_dict = {"Success":"(Report: %s, Concept: %s, User: %s, Semantic area: %s) deleted successfully" % (report, concept, user, semantic_area)}
        else:
            error_json = {"Error": "(Report: %s, Concept: %s, User: %s, Semantic area: %s) not deleted" % (report, concept, user, semantic_area)}
            response_dict = error_json
    elif report is not None and language is not None and user is not None:
        if Contains.objects.filter(id_report=report, language = language,ns_id=ns_id,username=user).delete():
            response_dict = {"Success": "(Report: %s, User: %s) All related records deleted successfully" % (report, user)}
            obj = GroundTruthLogFile.objects.filter(id_report=report,ns_id=ns_id,language = language,username=user,gt_type='concepts')
            if obj.exists():
                obj.delete()
        else:
            error_json = {"Error": "(Report: %s, User: %s) related records NOT deleted successfully" % (report, user)}
            response_dict = error_json

    return response_dict

# LABELS FUNCTIONS
def get_labels(usecase):

    """This method returns the list of labels for a specific use case"""

    labels1 = AnnotationLabel.objects.filter(name=usecase).values('label','seq_number')
    labels = []
    for e in labels1:
        labels.append((e['label'], e['seq_number']))
    # print(labels)
    return labels

def update_annotation_labels(labels_to_save,usecase,user,report1,language,mode):

    """This method updates the associate table: given the list of labels to insert it inserts them in the db."""

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
                                         id_report=report1,language = language,ns_id=mode).exists():
            Associate.objects.create(username=user, seq_number=label1.seq_number, label=label1,
                                             id_report=report1,language = language, insertion_time=Now(),ns_id=mode)
            # print('salvato', label)
        else:
            json_response = {'message': 'Some labels were already insert in the database. This should not be possible'}
            # print('this label was already inserted')

    return json_response

def delete_all_annotation(to_del,user, report1,language,type,mode):

    """This method deletes all the labels from the associate table."""

    a = True
    json_response = {'message':'OK,deletion done.'}
    if len(to_del) > 0:
        ass = Associate.objects.filter(username=user,ns_id=mode, id_report=report1,language = language)
        ass.delete()
        # print('Labels deleted with success')
        obj = GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, gt_type=type,language = language)
        obj.delete()
        # print('GT deleted with success')

    else:
        json_response = {'message': 'Nothing to delete.'}

    return json_response

def clean_mentions(user,report1,language):

    """This method deletes the mentions which have nor linked records nor annotate records associated."""

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
def delete_all_mentions(user,report1,language,type,usecase,mode):

    """This method deletes all the mentions annotated by a user for a specific report. This method also deletes
    linked records associated to that mention. The ground truth are updated in the ground truth log file table"""

    json_response = {'message':'OK,deletion done.'}
    # if len(to_del) > 0:
    ass = Annotate.objects.filter(username=user,ns_id=mode, id_report=report1,language = language).values('start','stop')
    # print(len(ass))
    rem_contains = False

    for el in ass:

        mention_el = Mention.objects.get(start = el['start'],stop = el['stop'], id_report = report1,language = language)
# controllo se altri utenti hanno individuato quella mention. Se sì rimuovo solo da annotate. Se no, rimuovo anche da mention

        toDel = Annotate.objects.filter(username=user,ns_id=mode, start=mention_el.start, stop=mention_el.stop,
                                        id_report=report1,language = language)
        if(toDel.exists()):
            toDel.delete()

        toDel_Linked = Linked.objects.filter(username=user,ns_id=mode,start=mention_el.start, stop=mention_el.stop,
                                        id_report=report1,language = language)
        if toDel_Linked.exists():
            concept_obj = Concept.objects.get(concept_url = toDel_Linked.first().concept_url_id)
            area_obj = SemanticArea.objects.get(name = toDel_Linked.first().name_id)
            contains_obj = Contains.objects.filter(username = user,ns_id=mode,id_report=report1,language = language,concept_url = concept_obj,
                                               name = area_obj)
            toDel_Linked.delete()

            if contains_obj.exists():
                contains_obj.delete()
                rem_contains = True
        # print(toDel)

        if(toDel.count() > 1 and toDel_Linked.count() > 1):
            json_response = {'error': 'FATAL ERROR DATABASE'}
            return json_response

    if rem_contains == True:
        obj2 = GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1,language = language, gt_type='concepts')
        if obj2.exists():
            obj2.delete()
            # In this case the ground truth is created again because it may happen that some concepts were added without
            # any associations with a mention
            if(Contains.objects.filter(username = user,ns_id=mode, id_report = report1,language = language).exists()):
                jsonDict = serialize_gt('concepts', usecase, user.username, report1.id_report, language,mode)
                GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                                gt_json=jsonDict,ns_id=mode,
                                                                gt_type='concepts', insertion_time=Now())

    obj = GroundTruthLogFile.objects.filter(username=user, id_report=report1,ns_id=mode,language = language, gt_type=type)
    obj1 = GroundTruthLogFile.objects.filter(username=user, id_report=report1,ns_id=mode,language = language, gt_type='concept-mention')
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

def update_mentions(mentions,report1,language,user,usecase,mode):
        json_response = {'message':'Mentions and Ground truth saved'}
        # print(mentions)
        var_link = False
        var_conc = False
        user_annot = Annotate.objects.filter(username = user,ns_id=mode, language = language, id_report=report1)
        for single_ann in user_annot:
            mention_cur = Mention.objects.get(start = int(single_ann.start_id),stop = int(single_ann.stop),id_report = report1,language = language)
            # print(mention_cur)
            # print(mentions)
            #La mention c'era nella lista precedente ma non nella nuova, è stata rimossa la singola mention
            ment_deleted = True
            for mention in mentions:

                if single_ann.start_id == int(mention['start']) and single_ann.stop == int(mention['stop']):
                    Annotate.objects.filter(username=user, ns_id=mode, start=mention_cur,
                                                         stop=mention_cur.stop, language=language, id_report=report1).delete()
                    Annotate.objects.create(username=user, ns_id=mode, start=mention_cur,
                                                         stop=mention_cur.stop, language=language, id_report=report1,insertion_time=Now())
                    ment_deleted = False



            if ment_deleted:
                annotation = Annotate.objects.filter(username = user,ns_id=mode,start = mention_cur,stop = mention_cur.stop, language = language, id_report = report1)

                if annotation.exists():
                    annotation.delete()
                link = Linked.objects.filter(username = user,ns_id=mode,start = mention_cur,stop = mention_cur.stop, language = language, id_report = report1)
                for elem in link:
                    conc = Concept.objects.get(concept_url = elem.concept_url_id)
                    area = SemanticArea.objects.get(name = elem.name_id)
                    conc_obj = Contains.objects.filter(username = user,ns_id=mode, language = language, id_report=report1,concept_url = conc,
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
            obj1 = GroundTruthLogFile.objects.filter(username=user,ns_id=mode,id_report=report1,language = language, gt_type='concept-mention')
            if obj1.exists():
                obj1.delete()
                if Linked.objects.filter(username = user,ns_id=mode, language = language, id_report = report1).exists():
                    jsonDict = serialize_gt('concept-mention', usecase, user.username, report1.id_report, language,mode)
                    c = GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language=language,
                                                          gt_json=jsonDict, gt_type='concept-mention',
                                                          insertion_time=Now())

        if var_conc:
            obj1 = GroundTruthLogFile.objects.filter(username=user, ns_id=mode,id_report=report1, language=language,
                                                     gt_type='concepts')
            if obj1.exists():
                obj1.delete()
                if Contains.objects.filter(username = user,ns_id=mode, language = language, id_report = report1).exists():
                    jsonDict = serialize_gt('concepts', usecase, user.username, report1.id_report, language,mode)
                    c = GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language=language,
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
            if not Annotate.objects.filter(username=user,ns_id=mode,language = language, id_report=report1,start=obj, stop=obj.stop).exists() :
                b = Annotate.objects.create(username=user,ns_id=mode,language = language, id_report=report1,start=obj, stop=obj.stop, insertion_time=Now())
                # print('saved ', b)
            else:
                json_response = {'message':'You tried to save the same element twice. This is not allowed. We saved only once.'}
                # print('Some annotations previously existed! (why?) ERROR OF THE USER')


        return json_response

def check_mentions_for_linking(mentions, report1,language,user,usecase,mode):
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
            if GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language=language,
                                                 gt_type=type).exists():
                GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language=language,
                                                  gt_type=type).delete()

                jsonDict = serialize_gt(type, usecase, user.username, report1.id_report, language,mode)
                GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language=language,
                                                            gt_json=jsonDict,
                                                            gt_type=type, insertion_time=Now())
                # print('salvo gt per association!')
                # print(groundtruth)

        else:
            json_response = {'message':'nothing to do with associations'}


    return json_response

# LINK FUNCTIONS
def delete_all_associations(user, report1,language,type,usecase,mode):

    """This method deletes all associations made by a user for a specific report and language."""

    json_response = {'message':'OK,deletion done.'}
    ass = Linked.objects.filter(username=user, id_report=report1,language = language)
    modifyconc = False
    for association in ass:
        concept = Concept.objects.get(concept_url = association.concept_url_id)
        semarea = SemanticArea.objects.get(name=association.name_id)
        concepts_user = Contains.objects.filter(username = user,ns_id=mode, id_report = report1,language = language, concept_url = concept,
                                                name=semarea)
        for con in concepts_user:
            if con.concept_url == association.concept_url and con.name == association.name:
                con.delete()
                modifyconc = True

    if modifyconc:
        if GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language=language,
                                             gt_type='concepts').exists():
            GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language=language,
                                              gt_type='concepts').delete()
            if Contains.objects.filter(username = user,ns_id=mode, id_report = report1, language = language).exists():
                jsonDict = serialize_gt(type, usecase, user.username, report1.id_report, language,mode)
                GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language=language,
                                                                gt_json=jsonDict, gt_type='concepts', insertion_time=Now())


    ass.delete()
    # print('Labels deleted with success')
    obj = GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language = language,gt_type=type)
    obj.delete()
    # print('GT deleted with success')
    return json_response


def update_associations(concepts,user,report1,language,usecase,mode):

    """This method updates the records in tables: linked, contains. In particular when a concept is linked also the
    contains table is updates"""

    json_response = {'message':'Associations and Ground Truth saved.'}

    modify_con = False
    user_link = Linked.objects.filter(username=user, ns_id=mode,language=language, id_report=report1)
    for single_link in user_link:
        mention_cur = Mention.objects.get(start=single_link.start_id, stop=single_link.stop, id_report=report1,
                                          language=language)
        sem_area = SemanticArea.objects.get(name=single_link.name_id)
        con = Concept.objects.get(concept_url=single_link.concept_url_id)
        concetto = Contains.objects.filter(username=user,ns_id=mode, language=language, id_report=report1,name = sem_area,concept_url=con)
        # La mention c'era nella lista precedente ma non nella nuova, è stata rimossa la singola mention
        ass_deleted = True
        a = Linked.objects.filter(concept_url = con,name=sem_area,start = mention_cur,username=user,ns_id = mode,id_report = report1,language = report1.language)
        if a.exists():
            a.delete()
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

        #single_link.delete()




    for concept1 in (concepts):
        #concept = json.loads(concept1)
        concept = concept1
        area = concept['semantic_area']
        concept_url = concept['concept_url']
        start_char = concept['start']
        end_char = concept['stop']
        obj = Mention.objects.get(start=start_char, stop=end_char, id_report=report1,language = language)
        sem = SemanticArea.objects.get(name=area)
        concept_2 = Concept.objects.get(concept_url=concept_url)
        con = Contains.objects.filter(username = user,ns_id=mode,id_report = report1,language = language, name = sem,concept_url = concept_2)
        if not con.exists():
            modify_con = True
            Contains.objects.create(username = user,ns_id=mode,id_report = report1,language = language, name = sem, concept_url = concept_2,insertion_time=Now())
        if not Linked.objects.filter(username=user,ns_id=mode, id_report=report1, language = language, name=sem, concept_url=concept_2, start=obj, stop=obj.stop).exists():
             Linked.objects.create(username=user,ns_id=mode, id_report=report1,language = obj.language, insertion_time=Now(), name=sem,
                                concept_url=concept_2, start=obj, stop=obj.stop)
             # print(len(user_link))
        else:
            json_response = {'message':'You tried to save the same element twice. This is not allowed. We saved it once'}

    if modify_con:
        if GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language=language,
                                             gt_type='concepts').exists():
            GroundTruthLogFile.objects.filter(username=user,ns_id=mode, id_report=report1, language=language,
                                              gt_type='concepts').delete()

        jsonDict = serialize_gt('concepts', usecase, user.username, report1.id_report, language,mode)
        GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language=language,
                                                        gt_json=jsonDict,
                                                        gt_type='concepts', insertion_time=Now())
        # print('ok concept updated')
    # print(len(user_link))
    return json_response

# CONTAINS
def get_list_concepts(semantic_area):

    """This method returns the list of concepts related to a semantic area"""

    concepts = BelongTo.objects.filter(name=semantic_area)
    conc = []
    for el in concepts:
        conc.append({'concept_name':el.concept_url.name, 'concept_url':el.concept_url.concept_url, 'semantic_area':el.name.name})
    return conc


def get_concepts_by_usecase_area(usecase,semantic_area,desc):

    """This method returns a list of concepts given a use case and a semantic area"""

    with connection.cursor() as cursor:
        cursor.execute("SELECT u.name,c.concept_url,c.name, b.name FROM concept AS c INNER JOIN concept_has_uc AS u ON c.concept_url = u.concept_url INNER JOIN belong_to AS b ON b.concept_url = c.concept_url WHERE u.name = %s AND b.name = %s AND c.json_concept = %s", [str(usecase),str(semantic_area),desc])
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
def serialize_gt(gt_type,use_case,username,id_report,language,mode):

    """This method serializes a ground truth: it takes the user's labels/mentions/concepts/associations and
    put them into a json object which will be included in ground truth log file table."""

    user = User.objects.get(username = username,ns_id=mode)
    report1 = Report.objects.get(id_report = id_report,language = language)
    data = get_fields_from_json()
    json_keys_to_display = data['fields']
    json_keys_to_ann = data['fields_to_ann']
    if mode.ns_id == 'Robot':
        workpath = os.path.dirname(
            os.path.abspath(__file__))  # Returns the Path your .py file is in
        with open(os.path.join(workpath,
                               './automatic_annotation/auto_fields/auto_fields.json')) as out:
            data = json.load(out)
            json_keys_to_ann = data['extract_fields'][report1.name.name]
    json_keys = json_keys_to_display + json_keys_to_ann

    rep = report_get_start_end(json_keys,json_keys_to_ann, id_report, language)

    jsonDict = {}
    json_rep = report1.report_json
    # jsonDict['report_id_not_hashed'] = json_rep['report_id']
    jsonErr = {'error': 'Errors in the creation of the ground_truth!'}
    jsonDict['username'] = username
    if mode.ns_id == 'Human':
        jsonDict['mode'] = 'Manual'
    else:
        jsonDict['mode'] = 'Automatic'
    jsonDict['language'] = language
    jsonDict['id_report'] = id_report
    jsonDict['institute'] = report1.institute
    jsonDict['use_case'] = use_case
    # if gt_type == 'concept-mention':
    #     jsonDict['gt_type'] = 'linking'
    # else:
    jsonDict['gt_type'] = gt_type
    if gt_type == 'concept-mention':
        couples = Linked.objects.filter(username=user, ns_id=mode,id_report=report1.id_report,language = language).values('start','stop','concept_url', 'name')

        jsonDict['concept-mention_associations'] = []


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
            # for k in rep['rep_string'].keys():
            #     if int(rep['rep_string'][k]['start']) <= int(el['start']) and int(rep['rep_string'][k]['end']) >= int(
            #             el['stop']):
            #         json_val['report_field'] = k
            #         break
            json_val['semantic_area'] = el['name']
            json_val['concept_url'] = el['concept_url']
            json_val['concept_name'] = concept.name
            jsonDict['concept-mention_associations'].append(json_val)

        json_object = json.dumps(jsonDict)

        return jsonDict

    elif gt_type == 'concepts':
        concepts1 = Contains.objects.filter(username=user,ns_id=mode, id_report=report1,language = language).values('concept_url', 'name')
        concepts = []

        concept = {}

        areas = SemanticArea.objects.all().values('name')
        for el in areas:
            concept[el['name']] = []
        for el in concepts1:
            co = Concept.objects.get(concept_url=el['concept_url'])

            #concepts.append((el['concept_url'],co.name))

            name = el['name']
            concept[name].append({'concept_url':el['concept_url'],'concept_name':co.name})
        jsonDict['concepts'] = concept

        json_object = json.dumps(jsonDict)
        return jsonDict



    elif gt_type == 'labels':
        lab1 = Associate.objects.filter(username=user,ns_id=mode, id_report=report1,language = language).values('label', 'seq_number')
        lab = []
        jsonDict['labels'] = []
        for el in lab1:
            # print(el['label'])
            lab.append((el['label'], el['seq_number']))

            jsonVal = {}
            # jsonVal['seq_number'] = el['seq_number']
            jsonVal['label'] = el['label'].replace('\n','')
            jsonDict['labels'].append(jsonVal)
        json_object = json.dumps(jsonDict)
        return jsonDict

    elif gt_type =='mentions':
        ment = Annotate.objects.filter(username = user,ns_id=mode, id_report = report1.id_report,language = language).values('start','stop')
        mentions = []
        jsonDict['mentions'] = []

        for el in ment:

            mention_text = Mention.objects.get(start = int(el['start']),stop = int(el['stop']),id_report = report1,language = language)
            # print(mention_text.mention_text)
            jsonVal = {}
            # for k in rep['rep_string'].keys():
            #     if int(rep['rep_string'][k]['start'])<=int(el['start']) and int(rep['rep_string'][k]['end'])>=int(el['stop']):
            #         jsonVal['report_field'] = k
            #         break
            jsonVal['start'] = el['start']
            jsonVal['stop'] = el['stop']
            mention_textual = mention_text.mention_text
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

    """This method returns an array of tuples: each tuple contains the id and the json object of each report
    belonging to a specific usecase,language and institute."""

    reports = Report.objects.filter(name = usecase,language = language,institute = institute).values('id_report','report_json')
    objects = []
    for report in reports:
        objects.append((report['id_report'], report['report_json']))
    return objects


def get_last_groundtruth(username,use_case = None,language = None, institute = None,mode=None):

    """This method returns the last made by a specific user according to a use case,language,institute and mode."""

    user = User.objects.get(username = username,ns_id=mode)
    if use_case is not None and language is not None and institute is not None and mode is not None:
        if GroundTruthLogFile.objects.filter(username=user,ns_id=mode).exists():
            gt = GroundTruthLogFile.objects.filter(username=user,ns_id=mode,language = language).order_by('-insertion_time')
            if mode.ns_id == 'Human':
                for groundtruth in gt:
                    gt_json = (groundtruth.gt_json)
                    if(gt_json['institute']==institute and gt_json['use_case'] == use_case and gt_json['language'] == language):
                        json_response = gt_json
                        #print(gt_json)
                        return json_response
            elif mode.ns_id == 'Robot':
                for groundtruth in gt:
                    user_rob = User.objects.get(username='Robot_user')
                    g_rob = GroundTruthLogFile.objects.get(id_report = groundtruth.id_report,language = groundtruth.language,ns_id=mode,username=user_rob,gt_type=groundtruth.gt_type)
                    gt_json = groundtruth.gt_json
                    if(gt_json['institute']==institute and gt_json['use_case'] == use_case and gt_json['language'] == language and groundtruth.insertion_time != g_rob.insertion_time):
                        json_response = gt_json
                        return json_response
                return None
        else: return None

    elif GroundTruthLogFile.objects.filter(username = user).exists():
        gt = GroundTruthLogFile.objects.filter(username = user).order_by('-insertion_time')
        ground_truth = gt.first()
        json_response = ground_truth.gt_json
        return json_response


def get_distinct():

    """This method returns a json object containing three lists of distinct elements: the institutes,the use cases and
    the languages."""

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


def get_array_per_usecase(user,mode1):

    """This method returns the stats for each use case related to a specific user"""

    array_tot = {}
    array_tot_percent = {}
    mode = NameSpace.objects.get(ns_id=mode1)
    # types = GroundTruthLogFile.objects.order_by().values('gt_type').distinct()
    types = ['labels','mentions','concepts','concept-mention']
    usecase = Report.objects.all().distinct('name')

    if mode1 == 'Human':
        array_stats = {}
        array_stats_percent = {}
        # usecase = Report.objects.all().distinct('name')
        usecases = []
        for uc in usecase:
            usecases.append(uc.name_id)

        # Subdivided for each usecase
        for usecase in usecases:
            # print(usecase)
            array_stats = {}
            array_stats_percent = {}

            use_obj = UseCase.objects.get(name=usecase)
            count_per_usecase = Report.objects.filter(name=use_obj).exclude(institute = 'PUBMED')
            array_stats['all_reports'] = count_per_usecase.count()
            array_stats_percent['all_reports'] = 100

            count_tot = 0
            if count_per_usecase.count() > 0:
                with connection.cursor() as cursor:
                    for type in types:
                        cursor.execute(
                            "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND username = %s AND gt_type = %s AND ns_id = %s AND institute != %s;",
                            [str(usecase), str(user.username), type, mode1,'PUBMED'])
                        count = cursor.fetchone()
                        count_gt = count[0]
                        count_tot += count_gt
                        # name = usecase + '_' + type
                        array_stats[type] = count_gt
                        # array_stats_percent[type] = round(((count_gt * 100) / count_per_usecase.count()), 2)
                        array_stats_percent[type] = int((count_gt * 100) / count_per_usecase.count())

            array_tot[usecase] = array_stats
            array_tot_percent[usecase] = array_stats_percent
    # else:
    #     array_tot_percent['all_gt'] = 0
    #     array_tot['all_gt'] = 0

    elif mode1 == 'Robot':
        array_stats = {}
        array_stats_percent = {}
        with connection.cursor() as cursor:
            user_rob = User.objects.get(username = 'Robot_user')
            """all_rep are all the reports such that have an automatic gt created."""

            # cursor.execute("SELECT DISTINCT(r.name) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND g.language = r.language WHERE g.username =%s AND g.ns_id=%s AND institute != %s",['Robot_user','Robot','PUBMED'])
            # uses = cursor.fetchall()
            # usecases = []
            usecases = []
            for uc in usecase:
                usecases.append(uc.name_id)
            # for el in usecase:
            #     if el[0] not in usecases:
            #         usecases.append(el[0])

            for usecase in usecases:
                # print(usecase)
                array_stats = {}
                array_stats_percent = {}

                count_tot = 0
                cursor.execute(
                    "SELECT COUNT(DISTINCT(r.id_report,r.language)) FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND username = %s AND ns_id = %s AND institute != %s;",
                    [str(usecase), 'Robot_user', mode1,'PUBMED'])
                count = cursor.fetchone()
                count_rep = count[0]
                array_stats['all_reports'] = count_rep  # all reports auto annotated for a usecase
                array_stats_percent['all_reports'] = 100  # all reports auto annotated for a usecase
                if count_rep > 0:
                    for type in types:
                        cursor.execute(
                            "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS gt ON r.id_report = gt.id_report AND r.language = gt.language INNER JOIN ground_truth_log_file AS gtt ON gtt.id_report = gt.id_report AND gtt.language = gt.language AND gtt.gt_type = gt.gt_type WHERE gtt.username=%s AND gt.username=%s AND r.name = %s AND gt.ns_id=%s AND gt.gt_type = %s AND gtt.insertion_time < gt.insertion_time AND institute != %s;",
                            ['Robot_user', str(user.username), usecase, mode1, type,'PUBMED'])
                        gt_count = cursor.fetchone()[0]
                        count_tot += gt_count
                        array_stats[type] = gt_count
                        array_stats_percent[type] = int((gt_count * 100) / count_rep)

                array_tot[usecase] = array_stats
                array_tot_percent[usecase] = array_stats_percent


    to_ret = {}
    to_ret['original'] = array_tot
    to_ret['percent'] = array_tot_percent
    # print(to_ret)
    return to_ret

def get_array_per_usecase_PUBMED(user,mode1):

    """This method returns the stats for each use case related to a specific user"""

    array_tot = {}
    array_tot_percent = {}
    mode = NameSpace.objects.get(ns_id=mode1)
    usecase = Report.objects.all().distinct('name')
    # types = GroundTruthLogFile.objects.order_by().values('gt_type').distinct()
    types = ['labels','mentions','concepts','concept-mention']
    if mode1 == 'Human':


        # Subdivided for each usecase
        # usecase = Report.objects.filter(institute = 'PUBMED').distinct('name')
        usecases = []
        for uc in usecase:
            usecases.append(uc.name_id)

        for usecase in usecases:
            # print(usecase)
            array_stats = {}
            array_stats_percent = {}
            us = UseCase.objects.get(name=usecase)
            all_rep = Report.objects.filter(name=us,institute = 'PUBMED')
            array_stats['all_reports'] = all_rep.count()
            array_stats_percent['all_reports'] = 100
            if all_rep.count() > 0:
                count_tot = 0
                with connection.cursor() as cursor:
                    for type in types:
                        cursor.execute(
                            "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND username = %s AND gt_type = %s AND ns_id = %s AND institute = %s;",
                            [str(usecase), str(user.username), type, mode1,'PUBMED'])
                        count = cursor.fetchone()
                        count_gt = count[0]
                        count_tot += count_gt
                        array_stats[type] = count_gt
                        array_stats_percent[type] = int((count_gt * 100) / all_rep.count())

            array_tot[usecase] = array_stats
            array_tot_percent[usecase] = array_stats_percent
        # else:
        #     array_tot_percent['all_gt'] = 0
        #     array_tot['all_gt'] = 0

    elif mode1 == 'Robot':
        array_stats = {}
        array_stats_percent = {}
        with connection.cursor() as cursor:
            usecases = []
            for uc in usecase:
                usecases.append(uc.name_id)
            # cursor.execute(
            #     "SELECT r.name FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND g.language = r.language WHERE g.username =%s AND g.ns_id=%s AND institute != %s",
            #     ['Robot_user', 'Robot', 'PUBMED'])
            # uses = cursor.fetchall()
            # usecases = []
            # for el in uses:
            #     if el[0] not in usecases:
            #         usecases.append(el[0])

            for usecase in usecases:
                # print(usecase)
                array_stats = {}
                array_stats_percent = {}
                count_tot = 0
                cursor.execute(
                    "SELECT COUNT(DISTINCT(r.id_report,r.language)) FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND username = %s AND ns_id = %s AND institute = %s;",
                    [str(usecase), 'Robot_user', mode1,'PUBMED'])
                count = cursor.fetchone()
                count_rep = count[0]
                array_stats['all_reports'] = count_rep  # all reports auto annotated for a usecase
                array_stats_percent['all_reports'] = 100  # all reports auto annotated for a usecase
                if count_rep > 0 :
                    for type in types:
                        cursor.execute(
                            "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS gt ON r.id_report = gt.id_report AND r.language = gt.language INNER JOIN ground_truth_log_file AS gtt ON gtt.id_report = gt.id_report AND gtt.language = gt.language AND gtt.gt_type = gt.gt_type WHERE gtt.username=%s AND gt.username=%s AND r.name = %s AND gt.ns_id=%s AND gt.gt_type = %s AND gtt.insertion_time < gt.insertion_time AND institute = %s;",
                            ['Robot_user', str(user.username), usecase, mode1, type,'PUBMED'])
                        gt_count = cursor.fetchone()[0]
                        count_tot += gt_count
                        array_stats[type] = gt_count
                        array_stats_percent[type] = int((gt_count * 100) / count_rep)

                array_tot[usecase] = array_stats
                array_tot_percent[usecase] = array_stats_percent




    to_ret = {}
    to_ret['original'] = array_tot
    to_ret['percent'] = array_tot_percent
    # print(to_ret)
    return to_ret


# user_rob = User.objects.get(username = 'Robot_user')
# """all_rep are all the reports such that have an automatic gt created."""
# reps = Report.objects.filter(institute = 'PUBMED')
# all_rep = GroundTruthLogFile.objects.filter(id_report__in=reps,username = user_rob,ns_id = mode).distinct('id_report','language')
# print(all_rep.count())
# array_stats['all_reports'] = all_rep.count()
# array_stats_percent['all_reports'] = 100
# cursor.execute(
#     "SELECT COUNT(*) FROM ground_truth_log_file AS gt INNER JOIN ground_truth_log_file AS gtt ON gtt.id_report = gt.id_report AND gtt.language = gt.language AND gtt.gt_type = gt.gt_type WHERE gtt.username=%s AND gt.username=%s AND gt.ns_id=%s AND gtt.insertion_time > gt.insertion_time AND institute = %s;",
#     ['Robot_user', str(user.username), mode1,'PUBMED'])
# gt_count = cursor.fetchone()[0]
# array_stats['all_gt'] = gt_count
# if all_rep.count()>0:
#     array_stats_percent['all_gt'] = round(((gt_count * 100) / all_rep.count()), 2)
#     for type in types:
#         cursor.execute(
#             "SELECT COUNT(*) FROM ground_truth_log_file AS gt INNER JOIN ground_truth_log_file AS gtt ON gtt.id_report = gt.id_report AND gtt.language = gt.language AND gtt.gt_type = gt.gt_type WHERE gtt.username=%s AND gt.username=%s AND gt.ns_id=%s AND gt.gt_type = %s AND gtt.insertion_time < gt.insertion_time AND institute = %s;",
#             ['Robot_user', str(user.username), mode1, type,'PUBMED'])
#         gt_count = cursor.fetchone()[0]
#         array_stats[type] = gt_count
#         array_stats_percent[type] = round(((gt_count * 100) / all_rep.count()), 2)
#
#     workpath = os.path.dirname(os.path.abspath(__file__))
#     with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as out:
#         data = json.load(out)
#         fields = data['extract_fields']
#         keys = fields.keys()
#         usecases = []
#         for key in keys:
#             if len(fields[key]) > 0 and key not in usecases:
#                 usecases.append(key)
#
#     array_tot['all_stats'] = array_stats
#     array_tot_percent['all_stats'] = array_stats_percent


def get_labels_exa_count():

    """This method returns the number of labels automatically inserted those needed in automatic annotations"""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    with open(os.path.join(workpath, 'automatic_annotation/db_examode_data/examode_db_population.json'),
              'r') as outfile:
        data = json.load(outfile)
        usecases = data['labels'].keys()
        count = 0
        for el in usecases:
            count += len(data['labels'][el])
        return count



def get_presence_exa_concepts():

    """This method returns a list with the usecases which do not belong to EXAMODE"""

    usecases = UseCase.objects.all()
    arr_to_ret = []
    for el in usecases:
        if el.name.lower() in ['colon', 'lung', 'uterine cervix']:
            use_concept = True
            if not ConceptHasUc.objects.filter(name=el).exists():
                if el.name not in arr_to_ret:
                    arr_to_ret.append(el.name)
            else:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT c.json_concept FROM concept AS c INNER JOIN concept_has_uc AS u ON c.concept_url = u.concept_url INNER JOIN belong_to AS b ON b.concept_url = c.concept_url WHERE u.name = %s",
                        [str(el.name)])
                    rows = cursor.fetchall()
                    for row in rows:
                        json_obj = json.loads(row[0])
                        if 'EXAMODE' in json_obj['provenance']:
                            use_concept = False
                            break
                if use_concept:
                    if el.name not in arr_to_ret:
                        arr_to_ret.append(el.name)
    return arr_to_ret

def get_presence_exa_labels():

    """This method returns a list with the usecases which do not belong to EXAMODE"""

    usecases = UseCase.objects.all()
    arr_to_ret = []
    for el in usecases:
        if el.name.lower() in ['colon', 'lung', 'uterine cervix']:
            if not AnnotationLabel.objects.filter(name=el,seq_number__gt=20).exists():
                if el.name not in arr_to_ret:
                    arr_to_ret.append(el.name)
            # else:
            #     labels = AnnotationLabel.objects.filter(name=el,seq_number__lte = 20)
            #     for label in labels:
            #         label_str = label.label
            #         if not AnnotationLabel.objects.filter(label = label_str,seq_number__gt=20,name = el).exists() :
            #             if el.name not in arr_to_ret:
            #                 arr_to_ret.append(el.name)
            #                 break
    return arr_to_ret


def get_keys_and_uses_csv(reports,type_selected = None):

    """This method returns the distinct keys contained in reports files and a list of usecases (those where automatic
    annotation can be applied)"""

    keys = []
    final_uses = []
    for report in reports:
        try:
            if not report.name.endswith('csv'):
                return keys
            df = pd.read_csv(report)
            df = df.where(pd.notnull(df), None)
            df = df.reset_index(drop=True)
        except Exception as e:
            print(e)
            return keys
        else:
            # if type_selected == 'reports':
            col_list = ['id_report','language','institute','usecase','ID']
            for col in df:
                if col not in col_list and col not in keys:
                    keys.append(col.replace(' ','_'))

            uses = df.usecase.unique()
            if 'Colon' in uses:
                if 'colon' not in final_uses:
                    final_uses.append('colon')
            if 'Uterine cervix' in uses:
                if 'uterine cervix' not in final_uses:
                    final_uses.append('uterine cervix')
            if 'Lung' in uses:
                if 'lung' not in final_uses:
                    final_uses.append('lung')
            if 'colon' in uses:
                if 'colon' not in final_uses:
                    final_uses.append('colon')
            if 'uterine cervix' in uses:
                if 'uterine cervix' not in final_uses:
                    final_uses.append('uterine cervix')
            if 'lung' in uses:
                if 'lung' not in final_uses:
                    final_uses.append('lung')


    return keys,final_uses


# function used when it is needed to update fields. In this case they are taken from the json file.
def get_keys_csv_update(reports):

    """This method returns the list of keys never seen in the reports inserted to update the db and the usecases whose
    examode concepts have not been loaded yet"""

    keys,uses = get_keys_and_uses_csv(reports)
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

    return keys_to_ret,uses


def get_fields_from_json():

    """This method returns respectively the fields to display, to annotate and all the fields (together with those to
    hide"""

    json_resp = {}
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, './data/')
    search_dir = path
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x),reverse=True)

    if User.objects.filter(profile='Admin').exists() == False:
        json_file = open(files[-1], 'r')
        for filename in os.listdir(path):
            if filename != 'fields0.json' and filename.endswith('json'):
                os.remove(filename)
    else:
        json_file = open(files[0], 'r')

    data = json.load(json_file)

    json_resp['fields'] = data['fields']
    json_resp['fields_to_ann'] = data['fields_to_ann']
    json_resp['all_fields'] = data['all_fields']

    # ADDED 06092021
    # json_resp['fields'].extend(['volume','authors','journal','year'])
    # json_resp['fields_to_ann'].extend(['abstract','title'])
    # json_resp['all_fields'].extend(['volume','authors','journal','year','abstract','title'])
    # json_resp['fields'] = list(set(json_resp['fields']))
    # json_resp['all_fields'] = list(set(json_resp['all_fields']))
    # json_resp['fields_to_ann'] = list(set(json_resp['fields_to_ann']))
    return json_resp


def get_fields_from_json_configuration(usecase,institute,language):

    """This method returns the list fields to display, annotate and all the fields given a specific configuration"""

    json_resp1 = get_fields_from_json()
    json_resp = {}
    json_resp['fields'] = []
    json_resp['fields_to_ann'] = []
    json_resp['all_fields'] = []
    reports = Report.objects.filter(name=usecase,institute = institute, language = language)
    for report in reports:
        rep = (report.report_json)
        for key in rep.keys():
            if key in json_resp1['fields']:
                if key not in json_resp['fields']:
                    json_resp['fields'].append(key)
                    json_resp['all_fields'].append(key)
            elif key in json_resp1['fields_to_ann']:
                if key not in json_resp['fields_to_ann']:
                    json_resp['fields_to_ann'].append(key)
                    json_resp['all_fields'].append(key)
            elif key in json_resp1['all_fields']:
                if key not in json_resp['all_fields']:
                    json_resp['all_fields'].append(key)

    return json_resp


def get_version():

    """This method returns the version of the fields file where the fields to display and annotate are stored"""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, 'data')
    search_dir = path
    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]  # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    name = (os.path.splitext(files[0])[0])
    version = name.split('fields')[1]
    # print(version)
    return version


def report_get_start_end(json_keys,json_keys_to_ann,report,language):

    """This method returns a json object: for each key of the json report it is returned the key's textual value of
    the field, the start char in the json report considered as string and the stop one."""

    json_dict = {}
    count_words = 0

    json_dict['rep_string'] = {}
    report_json = Report.objects.get(id_report=report, language=language)
    report_json = report_json.report_json

    # print(report_json)
    # convert to string

    report_string = json.dumps(report_json)
    # print(report_string)
    try:
        for key in json_keys:
            # print(report_json[key])
            if (report_json.get(key) is not None and report_json.get(key) != ""):
                element = report_json[key]

                element_1 = json.dumps(element)
                if element_1.startswith('"') and element_1.endswith('"'):
                    element_1 = element_1.replace('"', '')

                before_element = report_string.split(key)[0]
                after_element = report_string.split(key)[1]
                until_element_value = len(before_element) + len(key) + len(after_element.split(str(element_1))[0])
                start_element = until_element_value + 1
                end_element = start_element + len(str(element_1)) - 1
                element = {'text': element, 'start': start_element, 'end': end_element}
                json_dict['rep_string'][key] = element

        # print(json_keys_to_ann)
        for key in json_dict['rep_string'].keys():
            if key in json_keys_to_ann:
                element = json_dict['rep_string'][key]
                # print(element)
                text = str(element['text'])
                count = text.split(' ')
                count_words = count_words + len(count)

        # print(count_words)

    except Exception as error:
        print(error)
        pass
    json_dict['final_count'] = count_words
    # print(count_words)
    return json_dict


# update anche dopo configurazione!!!
def get_fields_extractable(configuration_status):

    """This method creates or updates the file where the fields used to automatically extract concepts are stored."""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    keys_to_filter = ['institute','id_report','language','usecase',
                      'abstract','title','volume','year','journal','authors']
    with open(os.path.join(workpath, './automatic_annotation/db_examode_data/examode_db_population.json'), 'r') as f:
        data = json.load(f)
        arr_extract = list(data['labels'].keys())
    f.close()
    usecases = UseCase.objects.all()
    json_to_ret = {}
    if configuration_status == 'configure':

        json_to_ret['total_fields'] = {}
        json_to_ret['extract_fields'] = {}

        for el in usecases:
            if el.name.lower() in arr_extract:
                json_to_ret['total_fields'][el.name.lower()] = []
                json_to_ret['extract_fields'][el.name.lower()] = []
                new_chiavi = []
                reports_use = Report.objects.filter(name=el)
                for report in reports_use:
                    json_rep = report.report_json
                    chiavi = json_rep.keys()
                    for k in chiavi:
                        if k not in keys_to_filter and k not in new_chiavi:
                            new_chiavi.append(k)
                json_to_ret['total_fields'][el.name.lower()] = new_chiavi

    elif configuration_status == 'update':
        with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as use_outfile:
            json_to_ret = json.load(use_outfile)  # LISTA CAMPI PER ESTRAZIONE
        for el in usecases:
            el = el.name
            if el in arr_extract:
                if el not in json_to_ret['total_fields'].keys() and el not in json_to_ret['extract_fields'].keys():
                    json_to_ret['total_fields'][el] = []
                    json_to_ret['extract_fields'][el] = []
                reports_use = Report.objects.filter(name=el)
                for report in reports_use:
                    json_rep = report.report_json
                    chiavi = json_rep.keys()
                    for k in chiavi:
                        if k not in json_to_ret['total_fields'][el] and k not in keys_to_filter:
                            json_to_ret['total_fields'][el].append(k)

    with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'w') as use_outfile:
        json.dump(json_to_ret,use_outfile)
    use_outfile.close()




def check_user_agent_gt_presence(username,usecase):

    """This method returns the number of reports which have been automatically annotated by the robot user for a
     specific use case and the corresponding """

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND g.language = r.language WHERE r.name = %s AND g.ns_id = %s AND g.username = %s;",
            [str(usecase),'Robot', username])
        groundTruths = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND g.language = r.language WHERE r.name = %s AND g.ns_id = %s AND g.username = %s;",
            [str(usecase),'Robot', 'Robot_user'])
        groundTruths1 = cursor.fetchone()[0]

    return groundTruths,groundTruths1


def copy_rows(use_case,agent_name,user):

    """This method copies the annotations performed by the robot: the automatic annotations are copied and they can be
    considered as done by the user whose name space is Robot. The user can modify them and check the auto annotations."""

    mode = NameSpace.objects.get(ns_id='Robot')
    username = User.objects.get(username=user, ns_id=mode)
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT g.username,g.id_report,g.language,g.label,g.seq_number,g.insertion_time FROM report AS r INNER JOIN associate AS g ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND g.username = %s;",
                    [str(use_case), str(agent_name)])
                rows_asso = cursor.fetchall()
                for row in rows_asso:
                    report = Report.objects.get(id_report=row[1], language=row[2])
                    label = AnnotationLabel.objects.get(seq_number=row[4], label=row[3])
                    Associate.objects.create(username=username, ns_id=mode, insertion_time=row[5], label=label,
                                             seq_number=row[4],
                                             id_report=report, language=row[2])

                cursor.execute(
                    "SELECT g.insertion_time,g.gt_json,g.id_report,g.language FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND g.username = %s AND gt_type = %s;",
                    [str(use_case), str(agent_name), 'labels'])
                rows_gt_lab = cursor.fetchall()
                for row in rows_gt_lab:
                    report = Report.objects.get(id_report=row[2],language = row[3])
                    GroundTruthLogFile.objects.create(username=username, ns_id=mode, insertion_time=row[0],
                                                      id_report=report,language=report.language, gt_json=json.loads(row[1]), gt_type='labels')



                cursor.execute(
                    "SELECT g.username,g.id_report,g.language,g.start,g.stop,g.insertion_time FROM report AS r INNER JOIN annotate AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND g.username = %s;",
                    [str(use_case), str(agent_name)])
                rows = cursor.fetchall()
                for row in rows:
                    report = Report.objects.get(id_report=row[1], language=row[2])
                    mention = Mention.objects.get(start=row[3], stop=row[4], id_report=report, language=report.language)
                    Annotate.objects.create(username=username, ns_id=mode, insertion_time=row[5], start=mention,
                                            stop=mention.stop,
                                            id_report=report,
                                            language=row[2])

                cursor.execute(
                    "SELECT g.insertion_time,g.gt_json,g.id_report,g.language FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND g.username = %s AND gt_type = %s;",
                    [str(use_case), str(agent_name), 'mentions'])
                rows_gt_lab = cursor.fetchall()
                for row in rows_gt_lab:
                    report = Report.objects.get(id_report=row[2],language = row[3])

                    GroundTruthLogFile.objects.create(username=username, ns_id=mode, insertion_time=row[0],
                                                      id_report=report, language=report.language, gt_json=json.loads(row[1]),
                                                      gt_type='mentions')

                cursor.execute(
                    "SELECT g.username,g.id_report,g.language,g.concept_url,g.name,g.insertion_time FROM report AS r INNER JOIN contains AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND g.username = %s;",
                    [str(use_case), str(agent_name)])
                rows = cursor.fetchall()
                for row in rows:
                    report = Report.objects.get(id_report=row[1], language=row[2])
                    concept = Concept.objects.get(concept_url=row[3])
                    sem = SemanticArea.objects.get(name=row[4])
                    Contains.objects.create(username=username, ns_id=mode, insertion_time=row[5], concept_url=concept,
                                            name=sem,
                                            id_report=report,
                                            language=row[2])

                cursor.execute(
                    "SELECT g.insertion_time,g.gt_json,g.id_report,g.language FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND g.username = %s AND gt_type = %s;",
                    [str(use_case), str(agent_name), 'concepts'])
                rows_gt_lab = cursor.fetchall()
                for row in rows_gt_lab:
                    report = Report.objects.get(id_report=row[2],language = row[3])

                    GroundTruthLogFile.objects.create(username=username, ns_id=mode, insertion_time=row[0],
                                                      id_report=report, language=report.language, gt_json=json.loads(row[1]),
                                                      gt_type='concepts')

                cursor.execute(
                    "SELECT g.username,g.id_report,g.language,g.concept_url,g.name,g.start,g.stop,g.insertion_time FROM report AS r INNER JOIN linked AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND username = %s;",
                    [str(use_case), str(agent_name)])
                rows = cursor.fetchall()
                for row in rows:
                    report = Report.objects.get(id_report=row[1], language=row[2])
                    concept = Concept.objects.get(concept_url=row[3])
                    sem = SemanticArea.objects.get(name=row[4])

                    mention = Mention.objects.get(start=row[5], stop=row[6], id_report=report, language=report.language)
                    Linked.objects.create(username=username, ns_id=mode, insertion_time=row[7], name=sem,
                                          start=mention, stop=mention.stop, concept_url=concept, id_report=report,
                                          language=row[2])

                cursor.execute(
                    "SELECT g.insertion_time,g.gt_json,g.id_report,g.language FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND r.language = g.language WHERE  r.name = %s AND g.username = %s AND gt_type = %s;",
                    [str(use_case), str(agent_name), 'concept-mention'])
                rows_gt_lab = cursor.fetchall()
                for row in rows_gt_lab:
                    gt_json = row[1]
                    # print(type(gt_json))
                    gt_json = json.loads(gt_json)
                    # print(type(gt_json))
                    report = Report.objects.get(id_report=row[2],language = row[3])
                    GroundTruthLogFile.objects.create(username=username, ns_id=mode, insertion_time=row[0],
                                                      id_report=report, language=report.language, gt_json=json.loads(row[1]),
                                                      gt_type='concept-mention')
            return True
    except Exception as e:
        print(e)
        return False


def get_annotations_count(id_report,language):

    """Given a report and its language and an annotation mode, this method returns:
    - the number of annotations for each task
    - the number of annotations for each label/mention/association/concept
    - whether the robot annotated that label/mention/association/concept"""

    report = Report.objects.get(id_report=id_report, language=language)
    # usecase = UseCase.objects.get(name=report.name)
    json_dict = {}
    mode_human = NameSpace.objects.get(ns_id='Human')
    mode_robot = NameSpace.objects.get(ns_id='Robot')
    user_robot = User.objects.get(username = 'Robot_user', ns_id=mode_robot)


    # HUMAN
    json_dict['Human'] = {}
    json_dict['Human']['labels'] = {}
    json_dict['Human']['mentions'] = {}
    json_dict['Human']['concepts'] = {}
    json_dict['Human']['linking'] = {}

    json_dict['Human']['labels']['users_list'] = []
    labels_human_users = GroundTruthLogFile.objects.filter(id_report = report,language = language,ns_id = mode_human,gt_type='labels').values('username')
    for user in labels_human_users:
        if user['username'] not in ['Robot_user']:
            json_dict['Human']['labels']['users_list'].append(user['username'])

    json_dict['Human']['mentions']['users_list'] = []
    mentions_human_users = GroundTruthLogFile.objects.filter(id_report = report,language = language,ns_id = mode_human,gt_type='mentions').values('username')
    for user in mentions_human_users:
        if user['username'] not in ['Robot_user']:
            json_dict['Human']['mentions']['users_list'].append(user['username'])

    json_dict['Human']['concepts']['users_list'] = []
    concepts_human_users = GroundTruthLogFile.objects.filter(id_report = report,language = language,ns_id = mode_human,gt_type='concepts').values('username')
    for user in concepts_human_users:
        if user['username'] not in ['Robot_user']:
            json_dict['Human']['concepts']['users_list'].append(user['username'])

    json_dict['Human']['linking']['users_list'] = []
    linking_human_users = GroundTruthLogFile.objects.filter(id_report = report,language = language,ns_id = mode_human,gt_type='concept-mention').values('username')
    for user in linking_human_users:
        if user['username'] not in ['Robot_user']:
            json_dict['Human']['linking']['users_list'].append(user['username'])

    json_dict['Human']['labels']['labels_list'] = []
    json_dict['Human']['mentions']['mentions_list'] = []
    json_dict['Human']['concepts']['concepts_list'] = []
    json_dict['Human']['linking']['linking_list'] = []

    gt_labels = GroundTruthLogFile.objects.filter(ns_id=mode_human,id_report=report,language = language,gt_type='labels').count()
    gt_mentions = GroundTruthLogFile.objects.filter(ns_id=mode_human,id_report=report,language = language,gt_type='mentions').count()
    gt_concepts = GroundTruthLogFile.objects.filter(ns_id=mode_human,id_report=report,language = language,gt_type='concepts').count()
    gt_linking = GroundTruthLogFile.objects.filter(ns_id=mode_human,id_report=report,language = language,gt_type='concept-mention').count()

    json_dict['Human']['mentions']['count'] = gt_mentions
    json_dict['Human']['concepts']['count'] = gt_concepts
    json_dict['Human']['linking']['count'] = gt_linking
    json_dict['Human']['labels']['count'] = gt_labels

    users_black_list = ['Robot_users']
    # LABELS HUMAN
    labels_list = AnnotationLabel.objects.filter(name=report.name)
    for label in labels_list:
        json_val = {}
        annotations = Associate.objects.filter(label=label,seq_number=label.seq_number,id_report = report,language=language,ns_id=mode_human)
        if annotations.exists() and annotations.count() > 0:
            json_val['label'] = label.label
            json_val['count'] = annotations.count()
            json_val['users_list'] = []
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list and us['username'] not in json_val['users_list']:
                    json_val['users_list'].append(us['username'])
            json_dict['Human']['labels']['labels_list'].append(json_val)

    # MENTIONS HUMAN
    rep_mentions = Mention.objects.filter(id_report = report,language = language)
    for mention in rep_mentions:
        json_val = {}
        annotations = Annotate.objects.filter(id_report=report, language=language, ns_id=mode_human, start=mention,stop=mention.stop)
        if annotations.exists() and annotations.count() > 0:
            json_val['start'] = mention.start
            json_val['stop'] = mention.stop
            json_val['mention'] = mention.mention_text
            json_val['count'] = annotations.count()
            json_val['users_list'] = []
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list and us['username'] not in json_val['users_list']:
                    json_val['users_list'].append(us['username'])
            json_dict['Human']['mentions']['mentions_list'].append(json_val)

    # CONCEPTS HUMAN
    rep_concepts = Contains.objects.filter(id_report = report, language = language,ns_id=mode_human)
    for c in rep_concepts:
        json_val = {}
        concept = Concept.objects.get(concept_url=c.concept_url_id)
        area = SemanticArea.objects.get(name=c.name_id)
        annotations = Contains.objects.filter(id_report=report, language=language, ns_id=mode_human, concept_url = concept,name=area)
        if annotations.exists() and annotations.count() > 0:
            json_val['concept_url'] = concept.concept_url
            json_val['concept_name'] = concept.name
            json_val['area'] = area.name
            json_val['count'] = annotations.count()
            json_val['users_list'] = []
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list and us['username'] not in json_val['users_list']:
                    json_val['users_list'].append(us['username'])
            json_dict['Human']['concepts']['concepts_list'].append(json_val)

    # LINKS HUMAN
    rep_links = Linked.objects.filter(id_report=report, language=language, ns_id=mode_human)
    for c in rep_links:
        json_val = {}
        mention = Mention.objects.get(start = c.start_id,stop = c.stop,id_report = report,language = language)
        concept = Concept.objects.get(concept_url=c.concept_url_id)
        area = SemanticArea.objects.get(name=c.name_id)
        annotations = Linked.objects.filter(id_report=report, language=language, ns_id=mode_human,
                                              concept_url=concept, name=area,start = mention,stop = mention.stop)
        if annotations.exists() and annotations.count() > 0:
            json_val['mention'] = mention.mention_text
            json_val['start'] = mention.start
            json_val['stop'] = mention.stop
            json_val['concept_url'] = concept.concept_url
            json_val['concept_name'] = concept.name
            json_val['area'] = area.name
            json_val['count'] = annotations.count()
            json_val['users_list'] = []
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list and us['username'] not in json_val['users_list']:
                    json_val['users_list'].append(us['username'])
            json_dict['Human']['linking']['linking_list'].append(json_val)

    # ROBOT
    json_dict['Robot'] = {}
    json_dict['Robot']['labels'] = {}
    json_dict['Robot']['mentions'] = {}
    json_dict['Robot']['concepts'] = {}
    json_dict['Robot']['linking'] = {}
    json_dict['Robot']['labels']['labels_list'] = []
    json_dict['Robot']['mentions']['mentions_list'] = []
    json_dict['Robot']['concepts']['concepts_list'] = []
    json_dict['Robot']['linking']['linking_list'] = []

    json_dict['Robot']['labels']['users_list'] = []
    cursor = connection.cursor()
    cursor.execute("select distinct(g.username) from ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id where gg.username = %s and gg.ns_id = %s and g.username != %s and g.gt_type = %s and gg.insertion_time != g.insertion_time AND g.id_report = %s AND g.language = %s",['Robot_user','Robot','Robot_user','labels',str(id_report),str(language)])
    ans = cursor.fetchall()
    for el in ans:
        json_dict['Robot']['labels']['users_list'].append(el[0])

    json_dict['Robot']['mentions']['users_list'] = []
    cursor.execute(
        "select distinct(g.username) from ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id where gg.username = %s and gg.ns_id = %s and g.username != %s and g.gt_type = %s and gg.insertion_time != g.insertion_time AND g.id_report = %s AND g.language = %s",
        ['Robot_user', 'Robot', 'Robot_user', 'mentions',str(id_report),str(language)])
    ans = cursor.fetchall()
    for el in ans:
        json_dict['Robot']['mentions']['users_list'].append(el[0])


    json_dict['Robot']['concepts']['users_list'] = []
    cursor.execute(
        "select distinct(g.username) from ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id where gg.username = %s and gg.ns_id = %s and g.username != %s and g.gt_type = %s and gg.insertion_time != g.insertion_time AND g.id_report = %s AND g.language = %s",
        ['Robot_user', 'Robot', 'Robot_user', 'concepts',str(id_report),str(language)])
    ans = cursor.fetchall()
    for el in ans:
        json_dict['Robot']['concepts']['users_list'].append(el[0])

    json_dict['Robot']['linking']['users_list'] = []
    cursor.execute(
        "select distinct(g.username) from ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id where gg.username = %s and gg.ns_id = %s and g.username != %s and g.gt_type = %s and gg.insertion_time != g.insertion_time AND g.id_report = %s AND g.language = %s",
        ['Robot_user', 'Robot', 'Robot_user', 'concept-mention',str(id_report),str(language)])
    ans = cursor.fetchall()
    for el in ans:
        json_dict['Robot']['linking']['users_list'].append(el[0])

    json_dict['Robot']['labels']['users_list'].append('Robot_user')
    json_dict['Robot']['mentions']['users_list'].append('Robot_user')
    json_dict['Robot']['concepts']['users_list'].append('Robot_user')
    json_dict['Robot']['linking']['users_list'].append('Robot_user')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM ground_truth_log_file AS g INNER JOIN ground_truth_log_file AS gg ON g.id_report = gg.id_report AND g.language = gg.language AND g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id  WHERE gg.username = %s AND g.gt_type = %s AND  g.insertion_time != gg.insertion_time AND g.ns_id=%s AND g.id_report = %s and g.language = %s",['Robot_user','labels','Robot',str(id_report),str(language)])
    gt_labels = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ground_truth_log_file AS g INNER JOIN ground_truth_log_file AS gg ON g.id_report = gg.id_report AND g.language = gg.language AND g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id  WHERE gg.username = %s AND g.gt_type = %s AND  g.insertion_time != gg.insertion_time AND g.ns_id=%s AND g.id_report = %s and g.language = %s",['Robot_user','mentions','Robot',str(id_report),str(language)])
    gt_mentions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ground_truth_log_file AS g INNER JOIN ground_truth_log_file AS gg ON g.id_report = gg.id_report AND g.language = gg.language AND g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id  WHERE gg.username = %s AND g.gt_type = %s AND g.insertion_time != gg.insertion_time AND g.ns_id=%s AND g.id_report = %s and g.language = %s",['Robot_user','concepts','Robot',str(id_report),str(language)])
    gt_concepts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ground_truth_log_file AS g INNER JOIN ground_truth_log_file AS gg ON g.id_report = gg.id_report AND g.language = gg.language AND g.gt_type = gg.gt_type AND g.ns_id = gg.ns_id WHERE gg.username = %s AND g.gt_type = %s AND g.insertion_time != gg.insertion_time AND g.ns_id=%s AND g.id_report = %s and g.language = %s",['Robot_user','concept-mention','Robot',str(id_report),str(language)])
    gt_linking = cursor.fetchone()[0]


    # +1 for robot anno
    json_dict['Robot']['mentions']['count'] = gt_mentions +1
    json_dict['Robot']['concepts']['count'] = gt_concepts+1
    json_dict['Robot']['linking']['count'] = gt_linking+1
    json_dict['Robot']['labels']['count'] = gt_labels+1

    users_black_list = []
    # LABELS ROBOT
    labels_list = AnnotationLabel.objects.filter(name=report.name)
    for label in labels_list:
        json_val = {}
        json_val['users_list'] = []
        ins_time = '0001-01-01 00:00:00.000000+00'
        robot_anno = Associate.objects.filter(label = label,seq_number = label.seq_number,id_report = report,language = language, ns_id=mode_robot,username=user_robot)
        if robot_anno.exists() and robot_anno.count() == 1:
            robot_ann = robot_anno.first()
            ins_time = robot_ann.insertion_time
            json_val['users_list'].append('Robot_user')

        annotations = Associate.objects.filter(label=label, seq_number=label.seq_number, id_report=report,
                                               language=language, ns_id=mode_robot).exclude(insertion_time = ins_time)

        if annotations.exists() and annotations.count() > 0:
            json_val['count'] = annotations.count()
            json_val['label'] = label.label
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list:
                    json_val['users_list'].append(us['username'])
            json_dict['Robot']['labels']['labels_list'].append(json_val)

        elif 'Robot_user' in json_val['users_list']:
            json_val['label'] = label.label
            json_val['count'] = 0
            json_dict['Robot']['labels']['labels_list'].append(json_val)

    # MENTIONS ROBOT
    rep_mentions = Mention.objects.filter(id_report=report, language=language)
    for mention in rep_mentions:
        json_val = {}
        json_val['users_list'] = []
        ins_time = '0001-01-01 00:00:00.000000+00'
        robot_anno = Annotate.objects.filter(id_report=report, language=language, ns_id=mode_robot,start = mention,stop = mention.stop,
                                              username=user_robot)
        if robot_anno.exists() and robot_anno.count() == 1:
            robot_ann = robot_anno.first()
            ins_time = robot_ann.insertion_time
            json_val['users_list'].append('Robot_user')

        annotations = Annotate.objects.filter(id_report=report, language=language, ns_id=mode_robot, start=mention,
                                              stop=mention.stop).exclude(insertion_time = ins_time)
        if annotations.exists() and annotations.count() > 0:

            json_val['mention'] = mention.mention_text
            json_val['start'] = mention.start
            json_val['stop'] = mention.stop

            json_val['count'] = annotations.count()

            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list:
                    json_val['users_list'].append(us['username'])
            json_dict['Robot']['mentions']['mentions_list'].append(json_val)

        elif 'Robot_user' in json_val['users_list']:

            json_val['mention'] = mention.mention_text
            json_val['start'] = mention.start
            json_val['stop'] = mention.stop

            json_val['count'] = 0
            json_dict['Robot']['mentions']['mentions_list'].append(json_val)

    # CONCEPTS ROBOT
    rep_concepts = Contains.objects.filter(id_report=report, language=language, ns_id=mode_robot).distinct('concept_url','name')
    for c in rep_concepts:
        # print(c.concept_url)
        json_val = {}
        json_val['users_list'] = []
        ins_time = '0001-01-01 00:00:00.000000+00'
        concept = c.concept_url
        area = c.name
        robot_anno = Contains.objects.filter(id_report=report, language=language, ns_id=mode_robot,concept_url=c.concept_url,name=area,
                                             username=user_robot)
        if robot_anno.exists() and robot_anno.count() == 1:
            robot_ann = robot_anno.first()
            ins_time = robot_ann.insertion_time
            json_val['users_list'].append('Robot_user')

        annotations = Contains.objects.filter(id_report=report, language=language, ns_id=mode_robot,
                                              concept_url=concept, name=area).exclude(insertion_time = ins_time)
        if annotations.exists() and annotations.count() > 0:

            json_val['concept_url'] = concept.concept_url
            json_val['concept_name'] = concept.name
            json_val['area'] = area.name

            json_val['count'] = annotations.count()
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list:
                    json_val['users_list'].append(us['username'])
            json_dict['Robot']['concepts']['concepts_list'].append(json_val)

        elif 'Robot_user' in json_val['users_list']:

            json_val['concept_url'] = concept.concept_url
            json_val['concept_name'] = concept.name
            json_val['area'] = area.name

            json_val['count'] = 0
            json_dict['Robot']['concepts']['concepts_list'].append(json_val)

    # LINKS ROBOT
    rep_links = Linked.objects.filter(id_report=report, language=language, ns_id=mode_robot).distinct('concept_url','start','name')
    for c in rep_links:
        json_val = {}
        ins_time = '0001-01-01 00:00:00.000000+00'
        json_val['users_list'] = []
        concept = c.concept_url
        mention = Mention.objects.get(start = c.start_id,stop=c.stop,id_report = report,language = language)
        area = c.name
        robot_anno = Linked.objects.filter(id_report=report, language=language, ns_id=mode_robot, concept_url=concept,
                                             name=area,start = mention,stop = mention.stop,
                                             username=user_robot)
        if robot_anno.exists() and robot_anno.count() == 1:
            robot_ann = robot_anno.first()
            ins_time = robot_ann.insertion_time
            json_val['users_list'].append('Robot_user')

        annotations = Linked.objects.filter(id_report=report, language=language, ns_id=mode_robot,
                                            concept_url=concept, name=area, start=mention, stop=mention.stop).exclude(insertion_time=ins_time)

        if annotations.exists() and annotations.count() > 0:
            json_val['mention'] = mention.mention_text
            json_val['start'] = mention.start
            json_val['stop'] = mention.stop
            json_val['concept_url'] = concept.concept_url
            json_val['concept_name'] = concept.name
            json_val['area'] = area.name
            json_val['count'] = annotations.count()
            users = annotations.values('username')
            for us in users:
                if us['username'] not in users_black_list:
                    json_val['users_list'].append(us['username'])
            json_dict['Robot']['linking']['linking_list'].append(json_val)

        elif 'Robot_user' in json_val['users_list']:
            json_val['mention'] = mention.mention_text
            json_val['start'] = mention.start
            json_val['stop'] = mention.stop
            json_val['concept_url'] = concept.concept_url
            json_val['concept_name'] = concept.name
            json_val['area'] = area.name

            json_val['count'] = 0
            json_dict['Robot']['linking']['linking_list'].append(json_val)

    usecase = report.name_id
    json_dict['Human_Robot'] = {}
    if check_exa_lab_conc_only(usecase):
        json_dict['Human_Robot']['labels'] = {}
        json_dict['Human_Robot']['mentions'] = {}
        json_dict['Human_Robot']['concepts'] = {}
        json_dict['Human_Robot']['linking'] = {}
        json_dict['Human_Robot']['labels']['labels_list'] = []
        json_dict['Human_Robot']['mentions']['mentions_list'] = []
        json_dict['Human_Robot']['concepts']['concepts_list'] = []
        json_dict['Human_Robot']['linking']['linking_list'] = []
        # json_dict['Human_Robot']['labels']['count'] = json_dict['Human']['labels']['count'] + json_dict['Robot']['labels']['count']
        json_dict['Human_Robot']['labels']['users_list'] = list(set(json_dict['Human']['labels']['users_list'] + json_dict['Robot']['labels']['users_list']))
        json_dict['Human_Robot']['labels']['count'] = len(json_dict['Human_Robot']['labels']['users_list'])
        # json_dict['Human_Robot']['mentions']['count'] = json_dict['Human']['mentions']['count'] + json_dict['Robot']['mentions']['count']
        json_dict['Human_Robot']['mentions']['users_list'] = list(set(json_dict['Human']['mentions']['users_list'] + json_dict['Robot']['mentions']['users_list']))
        json_dict['Human_Robot']['mentions']['count'] = len(json_dict['Human_Robot']['mentions']['users_list'])
        # json_dict['Human_Robot']['concepts']['count'] = json_dict['Human']['concepts']['count'] + json_dict['Robot']['concepts']['count']
        json_dict['Human_Robot']['concepts']['users_list'] = list(set(json_dict['Human']['concepts']['users_list'] + json_dict['Robot']['concepts']['users_list']))
        json_dict['Human_Robot']['concepts']['count'] = len(json_dict['Human_Robot']['concepts']['users_list'])
        # json_dict['Human_Robot']['linking']['count'] = json_dict['Human']['linking']['count'] + json_dict['Robot']['linking']['count']
        json_dict['Human_Robot']['linking']['users_list'] = list(set(json_dict['Human']['linking']['users_list'] + json_dict['Robot']['linking']['users_list']))
        json_dict['Human_Robot']['linking']['count'] = len(json_dict['Human_Robot']['linking']['users_list'])
        workpath = os.path.dirname(
            os.path.abspath(__file__))
        labels = []# Returns the Path your .py file is in
        with open(os.path.join(workpath, 'automatic_annotation/db_examode_data/examode_db_population.json'),
                  'r') as outfile:
            data = json.load(outfile)
            labels = data['labels'][usecase]
        for label in labels:
            json_val = {}
            users_list = []
            json_val['robot_users'] = []
            json_val['human_users'] = []
            json_val['users_list'] = []
            for lab_entry in json_dict['Robot']['labels']['labels_list']:
                if lab_entry['label'] == label:
                    json_val['label'] = label
                    json_val['robot_users'] = lab_entry['users_list']
                    for name in lab_entry['users_list']:
                        if name not in users_list:
                            users_list.append(name)
            for lab_entry in json_dict['Human']['labels']['labels_list']:
                if lab_entry['label'] == label:
                    json_val['label'] = label
                    json_val['human_users'] = lab_entry['users_list']

                    for name in lab_entry['users_list']:
                        if name not in users_list:
                            users_list.append(name)
            if len(users_list) > 0:
                # print('USERS',users_list)
                json_val['count'] = len(users_list)
                json_val['users_list'] = users_list

                json_dict['Human_Robot']['labels']['labels_list'].append(json_val)

        mentions_list = []
        for lab_entry in json_dict['Robot']['mentions']['mentions_list']:
            print('human',lab_entry)
            if {'start':lab_entry['start'],'stop':lab_entry['stop'],'mention':lab_entry['mention']} not in mentions_list:
                mentions_list.append({'start':lab_entry['start'],'stop':lab_entry['stop'],'mention':lab_entry['mention']})

        for lab_entry in json_dict['Human']['mentions']['mentions_list']:
            print('robot',lab_entry)

            if {'start': lab_entry['start'], 'stop': lab_entry['stop'],'mention': lab_entry['mention']} not in mentions_list:
                mentions_list.append({'start': lab_entry['start'], 'stop': lab_entry['stop'], 'mention': lab_entry['mention']})

        for entry in mentions_list:
            # print(mentions_list)
            # print(len(mentions_list))
            json_val = {}
            users_list = []
            json_val['robot_users'] = []
            json_val['human_users'] = []
            json_val['users_list'] = []
            for lab_entry in json_dict['Human']['mentions']['mentions_list']:
                if entry['start'] == lab_entry['start'] and entry['stop'] == lab_entry['stop'] and entry['mention'] == lab_entry['mention']:
                    json_val['human_users'] = lab_entry['users_list']
                    for user in lab_entry['users_list']:
                        if user not in users_list:
                            users_list.append(user)
            for lab_entry in json_dict['Robot']['mentions']['mentions_list']:
                if entry['start'] == lab_entry['start'] and entry['stop'] == lab_entry['stop'] and entry['mention'] == lab_entry['mention']:
                    json_val['robot_users'] = lab_entry['users_list']
                    for user in lab_entry['users_list']:
                        if user not in users_list:
                            users_list.append(user)
            json_val['count'] = len(users_list)
            json_val['users_list'] = (users_list)
            # print(json_val['users_list'])
            if len(users_list) > 0:
                json_val['start'] = entry['start']
                json_val['stop'] = entry['stop']
                json_val['mention'] = entry['mention']
                # print(json_val)
                json_dict['Human_Robot']['mentions']['mentions_list'].append(json_val)
        # print(json_dict['Human_Robot']['mentions']['mentions_list'])

        concepts_list = []
        for lab_entry in json_dict['Robot']['concepts']['concepts_list']:
            cur_entry = {'concept_url': lab_entry['concept_url'], 'concept_name': lab_entry['concept_name'],
                         'area': lab_entry['area']}
            if cur_entry not in concepts_list:
                concepts_list.append(
                    cur_entry)

        for lab_entry in json_dict['Human']['concepts']['concepts_list']:
            cur_entry = {'concept_url': lab_entry['concept_url'], 'concept_name': lab_entry['concept_name'],
                         'area': lab_entry['area']}
            if cur_entry not in concepts_list:
                concepts_list.append(
                    cur_entry)

        users_list = []
        for entry in concepts_list:
            json_val = {}
            users_list = []
            json_val['robot_users'] = []
            json_val['human_users'] = []
            json_val['users_list'] = []
            for lab_entry in json_dict['Human']['concepts']['concepts_list']:
                if entry['concept_url'] == lab_entry['concept_url'] and entry['concept_name'] == lab_entry[
                    'concept_name'] and entry[
                    'area'] == lab_entry['area']:
                    json_val['human_users'] = lab_entry['users_list']
                    for user in lab_entry['users_list']:
                        if user not in users_list:
                            users_list.append(user)
            for lab_entry in json_dict['Robot']['concepts']['concepts_list']:
                if entry['concept_url'] == lab_entry['concept_url'] and entry['concept_name'] == lab_entry[
                    'concept_name'] and entry[
                    'area'] == lab_entry['area']:
                    json_val['robot_users'] = lab_entry['users_list']
                    for user in lab_entry['users_list']:
                        if user not in users_list:
                            users_list.append(user)
            json_val['count'] = len(users_list)
            json_val['users_list'] = (users_list)
            if len(users_list) > 0:
                json_val['concept_url'] = entry['concept_url']
                json_val['concept_name'] = entry['concept_name']
                json_val['area'] = entry['area']
                json_dict['Human_Robot']['concepts']['concepts_list'].append(json_val)


        associations_list = []
        for lab_entry in json_dict['Robot']['linking']['linking_list']:
            cur_entry = {'concept_url': lab_entry['concept_url'], 'concept_name': lab_entry['concept_name'],
                         'area': lab_entry['area'],'mention':lab_entry['mention'],'start':lab_entry['start'],'stop':lab_entry['stop']}
            if cur_entry not in associations_list:
                associations_list.append(
                    cur_entry)

        for lab_entry in json_dict['Human']['linking']['linking_list']:
            cur_entry = {'concept_url': lab_entry['concept_url'], 'concept_name': lab_entry['concept_name'],
                         'area': lab_entry['area'], 'mention': lab_entry['mention'], 'start': lab_entry['start'],
                         'stop': lab_entry['stop']}
            if cur_entry not in associations_list:
                associations_list.append(
                    cur_entry)

        users_list = []
        for entry in associations_list:
            json_val = {}
            users_list = []
            json_val['robot_users'] = []
            json_val['human_users'] = []
            json_val['users_list'] = []
            for lab_entry in json_dict['Human']['linking']['linking_list']:
                if entry['concept_url'] == lab_entry['concept_url'] and entry['concept_name'] == lab_entry[
                    'concept_name'] and entry[
                    'area'] == lab_entry['area'] and entry['mention'] == lab_entry['mention'] and entry['start'] == lab_entry['start'] and lab_entry['stop'] == entry['stop']:
                    json_val['human_users'] = lab_entry['users_list']
                    for user in lab_entry['users_list']:
                        if user not in users_list:
                            users_list.append(user)
            for lab_entry in json_dict['Robot']['linking']['linking_list']:
                if entry['concept_url'] == lab_entry['concept_url'] and entry['concept_name'] == lab_entry[
                    'concept_name'] and entry[
                    'area'] == lab_entry['area'] and entry['mention'] == lab_entry['mention'] and entry['start'] == \
                        lab_entry['start'] and lab_entry['stop'] == entry['stop']:
                    json_val['robot_users'] = lab_entry['users_list']
                    for user in lab_entry['users_list']:
                        if user not in users_list:
                            users_list.append(user)
            json_val['count'] = len(users_list)
            if len(users_list) > 0:
                json_val['concept_url'] = entry['concept_url']
                json_val['concept_name'] = entry['concept_name']
                json_val['area'] = entry['area']
                json_val['start'] = entry['start']
                json_val['stop'] = entry['stop']
                json_val['mention'] = entry['mention']
                json_val['users_list'] = (users_list)
                json_dict['Human_Robot']['linking']['linking_list'].append(json_val)


    # print('DICT ',json_dict)
    return json_dict


def check_exa_lab_conc_only(usecase):
    """This method returns whether the concepts and the labels for a use case are only those of examode"""
    cursor = connection.cursor()
    bool = [True,True]
    cursor.execute("SELECT json_concept FROM concept AS c INNER JOIN concept_has_uc AS ch ON c.concept_url = ch.concept_url WHERE ch.name=%s",[str(usecase)])
    ans = cursor.fetchall()
    for el in ans:
        data = json.loads(el[0])
        if data['provenance'] != 'EXAMODE':
            bool[1] = False

    cursor.execute("SELECT label FROM annotation_label WHERE seq_number > %s and name=%s",[20,str(usecase)])
    ans = cursor.fetchall()
    workpath = os.path.dirname(
        os.path.abspath(__file__))  # Returns the Path your .py file is in
    with open(os.path.join(workpath, 'automatic_annotation/db_examode_data/examode_db_population.json'),
              'r') as outfile:
        data = json.load(outfile)
        # print(usecase)
        labels = data['labels'][usecase]
    if len(ans) != len(labels): # the number of labels is different! not the same labels were inserted
        bool[0] = False

    for el in ans:
        if el[0] not in labels:
            bool[0] = False

    return bool


def generate_majority_vote_arr(id_report,language,action,ns_id):

    """This method generates the ground truth corresponding to majority vote strategy. Each annotations includes:
        labels/concepts/mentions/associations which received more than the 50% of consensus. For each task (or action)
        this method returns: the number of annotations for each label/mention/concept/annotation,the total of annotations
        for that task and report and the annotation."""

    if ns_id is not None:
        ns_id = NameSpace.objects.get(ns_id=ns_id)
    report = Report.objects.get(id_report=id_report, language=language)
    if ns_id is not None:
        gt_count = GroundTruthLogFile.objects.filter(id_report=report, language=language, gt_type=action,
                                                     ns_id=ns_id).count()
    else:
        gt_count = GroundTruthLogFile.objects.filter(id_report=report, language=language,
                                                     gt_type=action).distinct('id_report', 'language', 'gt_type',
                                                                                  'username').count()
    gt_count = gt_count/2
    asso = []
    cursor = connection.cursor()

    annotators = []
    annotators_ns = []
    if action == 'labels':
        cursor.execute("SELECT label,seq_number,COUNT(label) FROM associate WHERE id_report=%s AND language=%s GROUP BY (label,seq_number,id_report,language) HAVING COUNT(start)>=%s",[report.id_report,language,gt_count])
        asso = cursor.fetchall()
        # asso = Associate.objects.values('label','seq_number').annotate(total=Count('label')).filter(total__gte = gt_count,id_report = report,language = language)
        for el in asso:
            lab = AnnotationLabel.objects.get(label=el[0], seq_number=el[1])
            annotators.append(el[2])

        if ns_id is not None:
            cursor.execute(
                "SELECT label,seq_number,COUNT(label) FROM associate WHERE id_report=%s AND language=%s AND ns_id=%s GROUP BY (label,seq_number,id_report,language) HAVING COUNT(start)>=%s",
                [report.id_report, language,ns_id, gt_count])
            asso = cursor.fetchall()
            # asso = Associate.objects.values('label','seq_number').annotate(total=Count('label')).filter(total__gte = gt_count,id_report = report,language = language,ns_id = ns_id)
            for el in asso:
                annotators.append(el[2])

    elif action == 'mentions':
        cursor.execute("SELECT start,stop,COUNT(start) FROM annotate WHERE id_report=%s AND language=%s GROUP BY (start,stop,id_report,language) HAVING COUNT(start)>=%s",[report.id_report,language,gt_count])
        asso = cursor.fetchall()

        if ns_id is not None:
            cursor.execute(
                "SELECT start,stop,COUNT(start) FROM annotate WHERE id_report=%s AND language=%s AND ns_id=%s GROUP BY (start,stop,id_report,language) HAVING COUNT(start)>=%s",
                [report.id_report, language,ns_id.ns_id, gt_count])
            asso = cursor.fetchall()
        for el in asso:
            annotators.append(el[2])
    elif action == 'concepts':

        cursor.execute("SELECT concept_url,name,COUNT(concept_url) FROM contains WHERE id_report=%s AND language=%s GROUP BY (id_report,language,concept_url,name) HAVING COUNT(concept_url)>=%s ",[report.id_report, language, gt_count])
        asso = cursor.fetchall()

        if ns_id is not None:
            cursor.execute(
                "SELECT concept_url,name,COUNT(concept_url) FROM contains WHERE id_report=%s AND language=%s AND ns_id=%s GROUP BY (id_report,language,concept_url,name) HAVING COUNT(concept_url)>=%s ",
                [report.id_report, language,ns_id.ns_id, gt_count])
            asso = cursor.fetchall()
        for el in asso:
            annotators.append(el[2])


    elif action == 'concept-mention':
        # asso = Linked.objects.values('concept_url', 'name','start','stop').annotate(total=Count('*')).filter(total__gte=gt_count,
        #                                                                                              id_report=report,
        #                                                                                             language=language)
        cursor.execute("SELECT concept_url,name,start,stop,COUNT(*) FROM linked WHERE id_report=%s AND language=%s GROUP BY (id_report,language,start,stop,name,concept_url) HAVING COUNT(*)>=%s",[report.id_report,language,gt_count])
        asso = cursor.fetchall()

        if ns_id is not None:
            cursor.execute(
                "SELECT concept_url,name,start,stop,COUNT(*) FROM linked WHERE id_report=%s AND language=%s AND ns_id=%s GROUP BY (id_report,language,start,stop,name,concept_url) HAVING COUNT(*)>=%s",
                [report.id_report, language,ns_id.ns_id, gt_count])
            asso = cursor.fetchall()
        for el in asso:

            annotators.append(el[4])

    return asso,gt_count*2,annotators


# def generate_json_majority_gt(json_resp,id_report,language,action,ns_id=None):
#
#     """This method creates the majority vote ground truth in json format"""
#
#     report = Report.objects.get(id_report=id_report,language = language)
#     asso,gt_count,annotators = generate_majority_vote_arr(id_report,language,action,ns_id)
#
#     data = get_fields_from_json()
#     json_keys_to_display = data['fields']
#     json_keys_to_ann = data['fields_to_ann']
#     if ns_id == 'Robot':
#         workpath = os.path.dirname(
#             os.path.abspath(__file__))  # Returns the Path your .py file is in
#         with open(os.path.join(workpath,
#                                './automatic_annotation/auto_fields/auto_fields.json')) as out:
#             data = json.load(out)
#             json_keys_to_ann = data['extract_fields'][report.name.name]
#     json_keys = json_keys_to_display + json_keys_to_ann
#
#     rep = report_get_start_end(json_keys, json_keys_to_ann, report, language)
#     annotators = list(annotators)
#     c = 0
#     if action == 'labels':
#         json_resp['labels'] = []
#         json_val = {}
#         for el in asso:
#             json_val['label'] = el['label']
#             json_val['seq_number'] = el['seq_number']
#             json_val['label_annotators'] = annotators[c]
#             c += 1
#             json_val['total_report_labels_annotators'] = gt_count
#             json_resp['labels'].append(json_val)
#
#     if action == 'mentions':
#         json_resp['mentions'] = []
#
#         for index,el in enumerate(asso):
#             json_val = {}
#             json_val['start'] = el[0]
#             json_val['stop'] = el[1]
#             mention = Mention.objects.get(id_report=report, language=language, start=el[0], stop=el[1])
#             mention_textual = mention.mention_text
#             mention_textual = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_textual)
#             json_val['mention_text'] = mention_textual
#             json_val['mentions_annotators'] =  annotators[index]
#             c+=1
#             json_val['total_report_mentions_annotators'] = gt_count
#             json_resp['mentions'].append(json_val)
#
#     if action == 'concepts':
#         json_resp['concepts'] = []
#         concept = {}
#         areas = []
#         for el in asso:
#             areas.append(el[1])
#         for el in areas:
#             concept[el] = []
#         for index,el in enumerate(asso):
#
#                 co = Concept.objects.get(concept_url=el[0])
#
#                 # concepts.append((el['concept_url'],co.name))
#
#                 name = el[1]
#                 concept[name].append({'concept_url':el[0],'concept_name': co.name, 'concept_annotators': annotators[index],
#                                    'total_report_concepts_annotators':gt_count })
#
#         json_resp['concepts'] = concept
#
#     if action == 'concept-mention':
#         json_resp['concept-mention_associations'] = []
#         for index,el in enumerate(asso):
#             json_val = {}
#             json_val['start'] = el[2]
#             json_val['stop'] = el[3]
#             concept = Concept.objects.get(concept_url=el[0])
#             mention = Mention.objects.get(id_report=report, language=language, start=el[2], stop=el[3])
#             mention_textual = mention.mention_text
#             mention_textual = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_textual)
#
#             json_val['mention_text'] = mention_textual
#
#             json_val['semantic_area'] = el[1]
#             json_val['concept_url'] = el[0]
#             json_val['concept_name'] = concept.name
#             json_val['link_annotators'] =  annotators[index]
#             c+=1
#             json_val['total_linking_annotators'] = gt_count
#             json_resp['concept-mention_associations'].append(json_val)
#
#     return json_resp


# def generate_csv_majority_gt(chosen_users,report_list,action,ns_id=None):
#
#     """This method creates the majority vote ground truth in csv format"""
#
#     report = Report.objects.get(id_report=id_report, language=language)
#     asso,gt_count,annotators = generate_majority_vote_arr(id_report, language, action, ns_id)
#
#     row_list = []
#     for c, el in enumerate(asso):
#         row = []
#         row.append('MAJORITY VOTE')
#         row.append('MAJORITY ALGORITHM')
#         row.append(report.id_report)
#         row.append(report.language)
#         row.append(report.institute)
#         row.append(report.name_id)
#         if action == 'labels':
#             row.append(el['label'])
#
#         elif action == 'mentions':
#             row.append(el['start'])
#             row.append(el['stop'])
#             mention = Mention.objects.get(id_report=report, language=language, start=el['start'], stop=el['stop'])
#             mention_textual = mention.mention_text
#             mention_textual = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_textual)
#             row.append(mention_textual)
#
#         elif action == 'concepts':
#             row.append(el['concept_url'])
#             concept = Concept.objects.get(concept_url = el['concept_url'])
#             row.append(concept.name)
#             row.append(el['name'])
#
#         elif action == 'concept-mention':
#             concept = Concept.objects.get(concept_url = el['concept_url'])
#             mention = Mention.objects.get(id_report=report, language=language, start=el['start'], stop=el['stop'])
#             row.append(el['start'])
#             row.append(el['stop'])
#             mention_textual = mention.mention_text
#             mention_textual = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_textual)
#             row.append(mention_textual)
#             row.append(concept.name)
#             row.append(el['concept_url'])
#             row.append(el['name'])
#
#         row.append(annotators[c])
#         row.append(gt_count)
#
#         row_list.append(row)
#
#     return row_list


def restore_robot_annotation(report,action,user):

    """This method restores the robot annotation of a report for a specific action. This action is needed when the usert
    wants to delete an automatic ground truth. In this case the robot's annotation is restored."""

    try:
        with transaction.atomic():
            mode = NameSpace.objects.get(ns_id = 'Robot')
            robot = User.objects.get(ns_id=mode, username='Robot_user')
            gt_to_del = GroundTruthLogFile.objects.filter(gt_type = action,username=user,ns_id=mode,id_report = report,language = report.language)
            gt_robot = GroundTruthLogFile.objects.get(gt_type = action,ns_id=mode,username=robot,id_report = report,language = report.language)

            gt_to_del.delete()
            GroundTruthLogFile.objects.create(ns_id=mode,username=user,gt_type = action,gt_json = gt_robot.gt_json,insertion_time = gt_robot.insertion_time,id_report = report,language = report.language)

            if action == 'labels':
                to_del_user = Associate.objects.filter(username=user,ns_id = mode,id_report = report,language = report.language)
                robot_annos = Associate.objects.filter(username=robot,ns_id = mode,id_report = report,language = report.language)
                to_del_user.delete()
                for el in robot_annos:
                    label = AnnotationLabel.objects.get(label = el.label_id,seq_number = el.seq_number)
                    Associate.objects.create(label = label,seq_number = el.seq_number,insertion_time = el.insertion_time,username=user,ns_id = mode,id_report = report,language = report.language)

            if action == 'mentions':
                to_del_user = Annotate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                       language=report.language)
                robot_annos = Annotate.objects.filter(username=robot, ns_id=mode, id_report=report,
                                                       language=report.language)
                to_del_user.delete()
                for el in robot_annos:
                    mention = Mention.objects.get(id_report = report,language = report.language, start = el.start_id, stop = el.stop)
                    Annotate.objects.create(
                                             insertion_time=el.insertion_time, username=user, ns_id=mode,
                                             id_report=report,start = mention, stop = mention.stop, language=report.language)

                    robot_links = Linked.objects.filter(username=robot, ns_id=mode,
                                             id_report=report,start = mention, stop = mention.stop, language=report.language)
                    for link in robot_links:
                        if not Linked.objects.filter(id_report = report,language = report.language,username=user,ns_id=mode,start=mention,stop = mention.stop,name = link.name,concept_url =link.concept_url).exists():
                            Linked.objects.create(id_report = report,language = report.language,username=user,ns_id=mode,insertion_time=link.insertion_time,start=mention,stop = mention.stop,name = link.name,concept_url =link.concept_url)
                        if not Contains.objects.filter(id_report = report,language = report.language,username=user,ns_id=mode,name=link.name,concept_url = link.concept_url).exists():
                            Contains.objects.create(id_report = report,language = report.language,username=user,ns_id=mode,insertion_time=link.insertion_time,name=link.name,concept_url = link.concept_url)

                gt_link_robot = GroundTruthLogFile.objects.get(gt_type='concept-mention',id_report = report,language = report.language,username=robot,ns_id=mode)
                gt_conc_robot = GroundTruthLogFile.objects.get(gt_type='concepts',id_report = report,language = report.language,username=robot,ns_id=mode)
                GroundTruthLogFile.objects.filter(gt_type='concept-mention', id_report=report, language=report.language,
                                               username=user, ns_id=mode).delete()
                GroundTruthLogFile.objects.filter(gt_type='concepts', id_report=report, language=report.language,
                                               username=user, ns_id=mode).delete()
                json_serial1 = serialize_gt('concepts',report.name_id,user.username,report.id_report,report.language,mode)
                json_serial2 = serialize_gt('concept-mention',report.name_id,user.username,report.id_report,report.language,mode)
                GroundTruthLogFile.objects.create(gt_type='concept-mention', id_report=report, language=report.language,
                                               username=user, ns_id=mode,insertion_time = gt_link_robot.insertion_time,gt_json=json_serial2)
                GroundTruthLogFile.objects.create(gt_type='concepts', id_report=report, language=report.language,
                                               username=user, ns_id=mode,insertion_time = gt_conc_robot.insertion_time,gt_json = json_serial1)


            if action == 'concepts':
                    to_del_user = Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                           language=report.language)
                    robot_annos = Contains.objects.filter(username=robot, ns_id=mode, id_report=report,
                                                           language=report.language)
                    to_del_user.delete()
                    for el in robot_annos:
                        concept = Concept.objects.get(concept_url = el.concept_url_id)
                        area = SemanticArea.objects.get(name = el.name_id)
                        Contains.objects.create(
                                                 insertion_time=el.insertion_time, username=user, ns_id=mode,
                                                 id_report=report,concept_url = concept, name = area, language=report.language)
            if action == 'concept-mention':
                    to_del_user = Linked.objects.filter(username=user, ns_id=mode, id_report=report,
                                                           language=report.language)
                    robot_annos = Linked.objects.filter(username=robot, ns_id=mode, id_report=report,
                                                           language=report.language)
                    to_del_user.delete()
                    for el in robot_annos:
                        mention = Mention.objects.get(id_report=report, language=report.language, start=el.start_id,
                                                      stop=el.stop)
                        concept = Concept.objects.get(concept_url = el.concept_url_id)
                        area = SemanticArea.objects.get(name = el.name_id)
                        Linked.objects.create(start = mention, stop = mention.stop,
                                                 insertion_time=el.insertion_time, username=user, ns_id=mode,
                                                 id_report=report,concept_url = concept, name = area, language=report.language)

                        robot_concept_anno = Contains.objects.get(id_report = report,language=report.language, name=area,concept_url = concept,username=robot,ns_id=mode)
                        if not Contains.objects.filter(username=user, ns_id=mode,concept_url = concept,name=area,
                                                            id_report=report,
                                                            language=report.language).exists():
                            Contains.objects.create(username=user, ns_id=mode, concept_url=concept, name=area,
                                                    id_report=report, insertion_time=robot_concept_anno.insertion_time,
                                                    language=report.language)

                    gt_conc_robot = GroundTruthLogFile.objects.get(gt_type='concepts', id_report=report,
                                                                   language=report.language, username=robot, ns_id=mode)

                    GroundTruthLogFile.objects.filter(gt_type='concepts', id_report=report, language=report.language,
                                                      username=user, ns_id=mode).delete()
                    json_serial1 = serialize_gt('concepts', report.name_id, user.username, report.id_report,
                                                report.language, mode)
                    GroundTruthLogFile.objects.create(gt_type='concepts', id_report=report, language=report.language,
                                                      username=user, ns_id=mode,
                                                      insertion_time=gt_conc_robot.insertion_time,
                                                      gt_json=json_serial1)


    except Exception as e:
        print(e)
        json_response = {'error': 'an error occurred'}
        return (json_response)
    else:
        json_response = {'message': 'Robot mode, Robot GT restored.'}
        return (json_response)


def create_majority_vote_linking(report,language):

    """This method creates a ground-truth based on majority vote for linking task"""

    count_gt_tot = GroundTruthLogFile.objects.filter(gt_type='concept-mention', id_report=report,
                                                     language=language).count()
    cursor = connection.cursor()
    cursor.execute('SELECT start,stop,concept_url,name,COUNT(*) FROM linked WHERE id_report = %s AND language = %s GROUP BY (start,stop,concept_url,name)  HAVING COUNT(*) > %s ',[str(report.id_report),str(language),count_gt_tot])
    res = cursor.fetchall()
    return res


def create_majority_vote_mentions(report,language):

    """This method creates a ground-truth based on majority vote for mentions identification task"""

    count_gt_tot = GroundTruthLogFile.objects.filter(gt_type='mentions', id_report=report,
                                                     language=language).count()
    cursor = connection.cursor()
    cursor.execute('SELECT start,stop,COUNT(*) FROM annotate WHERE id_report = %s AND language = %s GROUP BY (start,stop) HAVING COUNT(*) > %s ',[str(report.id_report),str(language),count_gt_tot])
    res = cursor.fetchall()
    return res


def create_majority_vote_concepts(report,language):

    """This method creates a ground-truth based on majority vote for concepts identification task"""

    count_gt_tot = GroundTruthLogFile.objects.filter(gt_type='concepts', id_report=report,
                                                     language=language).count()
    cursor = connection.cursor()
    cursor.execute('SELECT concept_url,name,COUNT(*) FROM contains WHERE id_report = %s AND language = %s GROUP BY (concept_url,name) HAVING COUNT(*) > %s ',[str(report.id_report),str(language),count_gt_tot])
    res = cursor.fetchall()
    return res


def create_majority_vote_labels(report,language):

    """This method creates a ground-truth based on majority vote for labels identification task"""

    count_gt_tot = GroundTruthLogFile.objects.filter(gt_type='labels', id_report=report,
                                                     language=language).count()
    cursor = connection.cursor()
    cursor.execute('SELECT label,seq_number,COUNT(*) FROM associate WHERE id_report = %s AND language = %s GROUP BY (label,seq_number) HAVING COUNT(*) > %s ',[str(report.id_report),str(language),count_gt_tot])
    res = cursor.fetchall()
    return res


def update_majority_vote_GT_linking(report,language,anno_mode):

    """This method updates the current ground truth based on majority vote for linking task"""

    mode = NameSpace.objects.get(ns_id=anno_mode)
    IAA_user = User.objects.get(username='IAA',ns_id=mode)

    report = Report.objects.get(id_report = report,language = language)
    cursor = connection.cursor()
    #delete current annotation and create a new one
    try:
        with transaction.atomic():
            Linked.objects.filter(username=IAA_user,ns_id=mode,id_report = report,language = language).delete()
            GroundTruthLogFile.objects.filter(gt_type='concept-mention',username=IAA_user,ns_id=mode,id_report = report,
                                              language = language).delete()

            #Get the number of ground-truth for the report "report", language "language" and action "concept-mention"
            res = create_majority_vote_linking(report, language)
            if len(res) > 0:
                for row in res:
                    cursor.execute(
                        'INSERT INTO linked (username,ns_id,start,stop,concept_url,name,id_report,language,insertion_time) '
                        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',['IAA','Robot',row[0],row[1],row[2],row[3],report.id_report,language,Now()])

            gt_json = serialize_gt('concept-mention',report.name_id,'IAA',report.id_report,language,mode)
            GroundTruthLogFile.objects.create(username=IAA_user,gt_json=gt_json,insertion_time=Now(),ns_id=mode,
                                              language = language,id_report = report,gt_type='concept-mention')

    except Exception as error:
        print(error)
        return error


def update_majority_vote_GT_mentions(report,language,anno_mode):

    """This method updates the current ground truth based on majority vote for mentions identification task"""

    mode = NameSpace.objects.get(ns_id=anno_mode)
    IAA_user = User.objects.get(username='IAA',ns_id=mode)

    report = Report.objects.get(id_report = report,language = language)
    cursor = connection.cursor()
    #delete current annotation and create a new one
    try:
        with transaction.atomic():
            Annotate.objects.filter(username=IAA_user,ns_id=mode,id_report = report,language = language).delete()
            GroundTruthLogFile.objects.filter(gt_type='mentions',username=IAA_user,ns_id=mode,id_report = report,
                                              language = language).delete()

            #Get the number of ground-truth for the report "report", language "language" and action "concept-mention"
            res = create_majority_vote_linking(report, language)
            if len(res) > 0:
                for row in res:
                    cursor.execute(
                        'INSERT INTO annotate (username,ns_id,start,stop,id_report,language,insertion_time) '
                        'VALUES (%s,%s,%s,%s,%s,%s,%s)',['IAA','Robot',row[0],row[1],report.id_report,language,Now()])

            gt_json = serialize_gt('mentions',report.name_id,'IAA',report.id_report,language,mode)
            GroundTruthLogFile.objects.create(username=IAA_user,gt_json=gt_json,insertion_time=Now(),ns_id=mode,
                                              language = language,id_report = report,gt_type='mentions')

    except Exception as error:
        print(error)
        return error


def update_majority_vote_GT_concepts(report,language,anno_mode):

    """This method updates the current ground truth based on majority vote for concepts identification task"""

    mode = NameSpace.objects.get(ns_id=anno_mode)
    IAA_user = User.objects.get(username='IAA',ns_id=mode)

    report = Report.objects.get(id_report = report,language = language)
    cursor = connection.cursor()
    #delete current annotation and create a new one
    try:
        with transaction.atomic():
            Contains.objects.filter(username=IAA_user,ns_id=mode,id_report = report,language = language).delete()
            GroundTruthLogFile.objects.filter(gt_type='concepts',username=IAA_user,ns_id=mode,id_report = report,
                                              language = language).delete()

            #Get the number of ground-truth for the report "report", language "language" and action "concept-mention"
            res = create_majority_vote_linking(report, language)
            if len(res) > 0:
                for row in res:
                    cursor.execute(
                        'INSERT INTO contains (username,ns_id,concept_url,name,id_report,language,insertion_time) '
                        'VALUES (%s,%s,%s,%s,%s,%s,%s)',['IAA','Robot',row[0],row[1],report.id_report,language,Now()])

            gt_json = serialize_gt('concepts',report.name_id,'IAA',report.id_report,language,mode)
            GroundTruthLogFile.objects.create(username=IAA_user,gt_json=gt_json,insertion_time=Now(),ns_id=mode,
                                              language = language,id_report = report,gt_type='concepts')

    except Exception as error:
        print(error)
        return error

def update_majority_vote_GT_labels(report,language,anno_mode):

    """This method updates the current ground truth based on majority vote for labels identification task"""

    mode = NameSpace.objects.get(ns_id=anno_mode)
    IAA_user = User.objects.get(username='IAA',ns_id=mode)

    report = Report.objects.get(id_report = report,language = language)
    cursor = connection.cursor()
    #delete current annotation and create a new one
    try:
        with transaction.atomic():
            Associate.objects.filter(username=IAA_user,ns_id=mode,id_report = report,language = language).delete()
            GroundTruthLogFile.objects.filter(gt_type='labels',username=IAA_user,ns_id=mode,id_report = report,
                                              language = language).delete()

            #Get the number of ground-truth for the report "report", language "language" and action "concept-mention"
            res = create_majority_vote_linking(report, language)
            if len(res) > 0:
                for row in res:
                    cursor.execute(
                        'INSERT INTO associate (username,ns_id,concept_url,name,id_report,language,insertion_time) '
                        'VALUES (%s,%s,%s,%s,%s,%s,%s)',['IAA','Robot',row[0],row[1],report.id_report,language,Now()])

            gt_json = serialize_gt('labels',report.name_id,'IAA',report.id_report,language,mode)
            GroundTruthLogFile.objects.create(username=IAA_user,gt_json=gt_json,insertion_time=Now(),ns_id=mode,
                                              language = language,id_report = report,gt_type='labels')

    except Exception as error:
        print(error)
        return error


def create_majority_vote_gt(action,users,mode,report):
    ns_human = NameSpace.objects.filter(ns_id='Human')
    ns_robot = NameSpace.objects.filter(ns_id='Robot')
    majority_gt = {}
    majority_gt['human'] = []
    majority_gt['robot'] = []
    majority_gt['both'] = []
    try:
        if action == 'labels':
            labels = AnnotationLabel.objects.filter(name=report.name)
            if mode == 'Human':
                for lab in labels:
                    assos_human = Associate.objects.filter(username__in=users, ns_id=ns_human, label=lab, seq_number__gt=20,id_report = report, language = report.language)
                    json_val = {}
                    json_val['users_list'] = []
                    for ass in assos_human:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['count'] = assos_human.count()
                    json_val['label'] = lab.label_id
                    json_val['total_gt'] = GroundTruthLogFile.objects.filter(gt_type='labels', ns_id=ns_human,
                                                                                          username__in=users, id_report=report,
                                                                                          language=report.language)
                    majority_gt['human'].append(json_val)
            if mode == 'Robot':
                for lab in labels:
                    assos_human = Associate.objects.filter(username__in=users, ns_id=ns_human, label=lab,
                                                           seq_number__lte=20, id_report=report,
                                                           language=report.language)


                    json_val = {}
                    json_val['users_list'] = []
                    for ass in assos_human:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['count'] = assos_human.count()
                    json_val['label'] = lab.label_id
                    json_val['total_gt'] = GroundTruthLogFile.objects.filter(gt_type='labels',
                                                                                          ns_id=ns_robot,
                                                                                          username__in=users,
                                                                                          id_report=report,
                                                                                          language=report.language)
                    majority_gt['robot'].append(json_val)
            if mode == 'both':
                for lab in labels:
                    found = False
                    json_val = {}
                    json_val['users_list'] = []
                    total_gt = GroundTruthLogFile.objects.filter(gt_type='labels',username__in=users,id_report = report,language = report.language)
                    for j_val in majority_gt['human']:
                        for js_val in majority_gt['robot']:
                            if lab.label == j_val['label'] == js_val['label']:
                                found = True
                                json_val['count'] =  int(j_val['count']) + int(js_val['count'])
                                json_val['label'] = j_val['label']
                                json_val['total_gt'] = total_gt.count()
                                json_val['users_list'] = list(set(js_val['users_list'] + j_val['users_list']))
                                majority_gt['both'].append(json_val)
                            if found:
                                break
                        if found:
                            break

        elif action == 'mentions':
            if mode == 'Human':
                mentions = Annotate.objects.filter(username__in=users,ns_id=ns_human,id_report = report, language = report.language).distinct('start')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='mentions',ns_id=ns_human,id_report = report,language = report.language)
                for el in mentions:
                    json_val = {}
                    mention = Mention.objects.get(start=el.start,stop=el.stop,id_report = report, language = report.language)
                    anno = Annotate.objects.filter(username__in = users,id_report = report,language = report.language,start = mention,stop=mention.stop,ns_id=ns_human)
                    json_val['count'] = anno.count()
                    json_val['total_gt'] = total_gt.count()
                    json_val['mention'] = mention.mention_text
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    json_val['users_list'] = []

                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)

                    majority_gt['human'].append(json_val)

            if mode == 'Robot':
                mentions = Annotate.objects.filter(username__in=users, id_report=report,
                                                   language=report.language).distinct('start')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='mentions', ns_id=ns_robot, id_report=report,username__in=users,
                                                             language=report.language)
                for el in mentions:
                    json_val = {}
                    mention = Mention.objects.get(start=el.start, stop=el.stop, id_report=report, language=report.language)
                    anno = Annotate.objects.filter(username__in=users, id_report=report, language=report.language,
                                                                start=mention, stop=mention.stop, ns_id=ns_robot)
                    json_val['count'] = anno.count()
                    json_val['users_list'] = []

                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)

                    json_val['total_gt'] = total_gt.count()
                    json_val['mention'] = mention.mention_text
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    majority_gt['robot'].append(json_val)

            if mode == 'both':
                mentions = Annotate.objects.filter(username__in=users, ns_id=ns_robot, id_report=report,
                                                   language=report.language).distinct('start')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='mentions', ns_id=ns_robot, id_report=report,
                                                             language=report.language)
                for el in mentions:
                    json_val = {}
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop, id_report=report, language=report.language)
                    anno = Annotate.objects.filter(username__in=users, id_report=report, language=report.language,
                                                   start=mention, stop=mention.stop)
                    json_val['count'] = anno.count()
                    json_val['users_list'] = []

                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['total_gt'] = total_gt.count()
                    json_val['mention'] = mention.mention_text
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    majority_gt['both'].append(json_val)

        elif action == 'concepts':
            if mode == 'Human':
                concepts = Contains.objects.filter(username__in=users, ns_id=ns_human, id_report=report,
                                                   language=report.language).distinct('concept_url','name')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='concepts', ns_id=ns_human, id_report=report,
                                                             language=report.language)
                for el in concepts:
                    json_val = {}
                    json_val['users_list'] = []
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    anno = Contains.objects.filter(username__in=users, id_report=report,
                                            language=report.language, concept_url=concept, name=area,
                                            ns_id=ns_human)
                    json_val['count'] = anno.count()
                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)

                    json_val['total_gt'] = total_gt.count()
                    json_val['concept_url'] = concept.concept_url
                    json_val['area'] = area.name
                    json_val['concept_name'] = concept.name
                    majority_gt['human'].append(json_val)

            if mode == 'Robot':
                concepts = Contains.objects.filter(username__in=users, ns_id=ns_robot, id_report=report,
                                                   language=report.language).distinct('concept_url', 'name')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='concepts', ns_id=ns_robot, id_report=report,
                                                             language=report.language)
                for el in concepts:
                    json_val = {}
                    json_val['users_list'] = []
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    anno = Contains.objects.filter(username__in=users, id_report=report,
                                                   language=report.language, concept_url=concept, name=area,
                                                   ns_id=ns_robot)
                    json_val['count'] = anno.count()
                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['total_gt'] = total_gt.count()
                    json_val['concept_url'] = concept.concept_url
                    json_val['area'] = area.name
                    json_val['concept_name'] = concept.name
                    majority_gt['robot'].append(json_val)

            if mode == 'both':
                concepts = Contains.objects.filter(username__in=users, id_report=report,
                                                   language=report.language).distinct('concept_url', 'name')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='concepts', id_report=report,
                                                             language=report.language)
                for el in concepts:
                    json_val = {}
                    json_val['users_list'] = []
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    anno = Contains.objects.filter(username__in=users, id_report=report,
                                                   language=report.language, concept_url=concept, name=area
                                                   )
                    json_val['count'] = anno.count()
                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)

                    json_val['total_gt'] = total_gt.count()
                    json_val['concept_url'] = concept.concept_url
                    json_val['area'] = area.name
                    json_val['concept_name'] = concept.name
                    majority_gt['both'].append(json_val)

        elif action == 'concept-mention':
            if mode == 'Human':
                concepts = Linked.objects.filter(username__in=users, ns_id=ns_human, id_report=report,
                                                   language=report.language).distinct('concept_url','name','start')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='concept-mention', ns_id=ns_human, id_report=report,
                                                             language=report.language)
                for el in concepts:
                    json_val = {}
                    json_val['users_list'] = []
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    mention = Mention.objects.filter(start=el.start_id,stop=el.stop,id_report = report,language = report.language)
                    anno = Linked.objects.filter(username__in=users, id_report=report, start=mention,
                                          language=report.language, concept_url=concept, name=area,
                                          ns_id=ns_human)
                    json_val['count'] = anno.count()
                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['total_gt'] = total_gt.count()
                    json_val['concept_url'] = concept.concept_url
                    json_val['area'] = area.name
                    json_val['concept_name'] = concept.name
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    json_val['mention'] = mention.mention_text
                    majority_gt['human'].append(json_val)

            if mode == 'Robot':
                concepts = Linked.objects.filter(username__in=users, ns_id=ns_robot, id_report=report,
                                                 language=report.language).distinct('concept_url', 'name', 'start')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='concept-mention', ns_id=ns_robot, id_report=report,
                                                             language=report.language)
                for el in concepts:
                    json_val = {}
                    json_val['users_list'] = []
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    mention = Mention.objects.filter(start=el.start_id, stop=el.stop, id_report=report,
                                                     language=report.language)
                    anno = Linked.objects.filter(username__in=users, id_report=report, start=mention,
                                                 language=report.language, concept_url=concept, name=area,
                                                 ns_id=ns_robot)
                    json_val['count'] = anno.count()
                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['total_gt'] = total_gt.count()
                    json_val['concept_url'] = concept.concept_url
                    json_val['area'] = area.name
                    json_val['concept_name'] = concept.name
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    json_val['mention'] = mention.mention_text
                    majority_gt['robot'].append(json_val)

            if mode == 'both':
                concepts = Linked.objects.filter(username__in=users, id_report=report,
                                                 language=report.language).distinct('concept_url', 'name', 'start')
                total_gt = GroundTruthLogFile.objects.filter(gt_type='concept-mention', id_report=report,
                                                             language=report.language)
                for el in concepts:
                    json_val = {}
                    json_val['users_list'] = []
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    mention = Mention.objects.filter(start=el.start_id, stop=el.stop, id_report=report,
                                                     language=report.language)
                    anno = Linked.objects.filter(username__in=users, id_report=report, start=mention,
                                                 language=report.language, concept_url=concept, name=area
                                                 )
                    json_val['count'] = anno.count()
                    for ass in anno:
                        if ass.username_id not in json_val['users_list']:
                            json_val['users_list'].append(ass.username_id)
                    json_val['total_gt'] = total_gt.count()
                    json_val['concept_url'] = concept.concept_url
                    json_val['area'] = area.name
                    json_val['concept_name'] = concept.name
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    json_val['mention'] = mention.mention_text
                    majority_gt['both'].append(json_val)
        return majority_gt
    except Exception as e:
        print(e)
        json_resp = {'error':e}
        return json_resp







