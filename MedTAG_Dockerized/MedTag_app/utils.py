import psycopg2
import re
import json
from MedTag_app.models import *
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




def check_concept_report_existance(report, concept, user, semantic_area,language):
        check = False

        report = Report.objects.get(id_report=report,language = language)
        user = User.objects.get(username=user)
        concept = Concept.objects.get(concept_url=concept)
        semantic_area = SemanticArea.objects.get(name=semantic_area)
        rows = Contains.objects.filter(id_report = report, language = language,username = user, concept_url = concept, name = semantic_area)

        if len(rows) > 0:
            print("[ rows >0 ] for (report, concept) : (" + str(report) + ", "+concept.concept_url+")")
            check = True
        else:
            print("[ 0 rows ] for (report, concept) : (" + str(report) + ", "+concept.concept_url+")")


        return check



def populate_contains_table(report, concept, user, semantic_area,language):
    connection = False
    status = False

    report = Report.objects.get(id_report = report,language = language)
    user = User.objects.get(username = user)
    concept = Concept.objects.get(concept_url = concept)
    semantic_area = SemanticArea.objects.get(name = semantic_area)
    Contains.objects.create(id_report = report, username = user,language = language,concept_url = concept, name = semantic_area, insertion_time = Now())

    status = "Ok"



    return status


def get_contains_records(report=None, language = None, concepts=None, user=None, semantic_area=None):
    """connection = False
    status = False

    try:
        connection = psycopg2.connect(user="ims",
                                      password="grace.period",
                                      host="localhost",
                                      port="5432",
                                      database="groundtruthdb")

        cursor = connection.cursor()

        query = "SELECT * FROM public.contains WHERE 1=1"

        query_params = []

        records = []

        if report is not None:
            query += " AND contains.id_report=%s"
            query_params.append(report)
        if concept is not None:
            query += " AND contains.concept_url=%s"
            query_params.append(concept)
        if user is not None:
            query += " AND contains.username=%s"
            query_params.append(user)
        if semantic_area is not None:
            query += " AND contains.name=%s"
            query_params.append(semantic_area)

        print(tuple(query_params))
        print(query)


        cursor.execute(query, tuple(query_params))

        records = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Error in get_contains_records()", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()"""
    records = []
    reports_dict = {}

    if report is not None and concepts is not None and user is not None and semantic_area is not None:
        for concept in concepts:
            for record in Contains.objects.filter(id_report=report, language = language, concept_url=concept, username=user, name=semantic_area):
                records.append(record)
    elif report is not None and user is not None and semantic_area is not None:
            for record in Contains.objects.filter(id_report=report,language = language, username=user, name=semantic_area):
                records.append(record)
    elif report is not None and user is not None:
            for record in Contains.objects.filter(id_report=report,language = language, username=user):
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


def delete_contains_record(report=None, language = None,concept=None, user=None, semantic_area=None):
    response_dict = error_json = {"Error": "Invalid parameters"}

    if report is not None and concept is not None and user is not None and semantic_area is not None:
        if Contains.objects.filter(id_report=report, concept_url=concept,language = language, username=user, name=semantic_area).delete():
            response_dict = {"Success":"(Report: %s, Concept: %s, User: %s, Semantic area: %s) deleted successfully" % (report, concept, user, semantic_area)}
        else:
            error_json = {"Error": "(Report: %s, Concept: %s, User: %s, Semantic area: %s) not deleted" % (report, concept, user, semantic_area)}
            response_dict = error_json
    elif report is not None and language is not None and user is not None:
        if Contains.objects.filter(id_report=report, language = language,username=user).delete():
            response_dict = {"Success": "(Report: %s, User: %s) All related records deleted successfully" % (report, user)}
            obj = GroundTruthLogFile.objects.filter(id_report=report, language = language,username=user,gt_type='concepts')
            if obj.exists():
                obj.delete()
        else:
            error_json = {"Error": "(Report: %s, User: %s) related records NOT deleted successfully" % (report, user)}
            response_dict = error_json

    return (response_dict)

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
    # if gt_type == 'concept-mention':
    #     jsonDict['gt_type'] = 'linking'
    # else:
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

    # Error if the user has not inserted enough files
    if len(concepts) == 0 and len(labels) == 0 and len(jsonAnn) == 0 and len(reports) > 0:
        json_resp['general_message'] = 'ERROR - You must provide at least one file between labels and concepts or at least one field to annotate.'
    elif len(reports) == 0:
        json_resp['general_message'] = 'ERROR - You must provide a file with one or more reports.'

    try:

            try:
                connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres",
                                              host="db",
                                              port="5432")
                cursor = connection.cursor()
                cursor.execute('SELECT * FROM public.user WHERE username = %s',(str(username),))
                ans = cursor.fetchall()
                # Error on username and password: duplicated username or missing
                if len(ans) > 0:
                    json_resp['username_message'] = 'USERNAME - The username you selected is already taken. Choose another one.'

                if(username == ''):
                    json_resp['username_message'] = 'USERNAME - Please, provide a username.'
                if(password == ''):
                    json_resp['username_message'] = 'PASSWORD - Please, provide a password.'
                if password == '' and username == '':
                    json_resp['username_message'] = 'USERNAME - Please, provide a username and a password.'

            except (Exception, psycopg2.Error) as e:
                print(e)
                json_resp['username_message'] = 'An error occurred handling the username and the password. Please, insert them again.'
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
            if len(reports) == 0:
                json_resp['report_message'] = 'REPORTS FILES - You must provide at least one file before checking'

            for i in range(len(reports)):

                # Error if the file is not csv
                if not reports[i].name.endswith('csv'):
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - The file must be .csv'
                    break

                try:
                    df = pd.read_csv(reports[i])
                    df = df.where(pd.notnull(df), None)
                    df = df.reset_index(drop=True) #Useful if the csv includes only commas
                except Exception as e:
                    print(e)
                    json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. Check if it contains as many columns as they are declared in the header.'
                    pass

                else:
                    #check if colunns are allowed and without duplicates
                    cols = list(df.columns)
                    list_db_col = ['id_report', 'institute', 'usecase', 'language']
                    list_not_db_col = []

                    missing = False
                    for el in list_db_col:
                        if el not in cols:
                            json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - The column: ' + el + ' is missing, please add it.'
                            missing = True
                            break
                    if missing:
                        break

                    for el in cols:
                        if el not in list_db_col:
                            list_not_db_col.append(el)

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
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' -  You must provide at least a report.'
                        break
                    else:
                        # check if columns id_report and language have no duplicates
                        df_dup = df[df.duplicated(subset=['id_report', 'language'], keep=False)]
                        # print(df_dup.loc[:, 'id_report'])
                        if df_dup.shape[0] > 0:
                            json_resp['report_message'] = 'WARNING REPORTS FILE - ' + reports[i].name + ' - The rows: ' + str(
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
                                count_both = count_both +1

                        if count_both == len(not_none_cols):
                            json_resp['fields_message'] = 'WARNING REPORT FIELDS TO DISPLAY AND ANNOTATE - ' +reports[i].name+ ' -  With this configuration the report at the row: ' + str(ind) +' would not be displayed since the columns to display are all empty for that report.'

                        if isnone:
                            exit = True
                            json_resp['report_message'] = 'REPORTS FILE - ' + reports[
                                i].name + ' -  The report at row ' + str(ind) + ' has the columns: ' + ', '.join(
                                list_not_db_col) + ' empty. Provide a value for at least one of these columns.'
                            break

                    if exit == True:
                        break


                    # check if there are None in mandatory vcolumns
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
                        json_resp['report_message'] = 'REPORTS FILE - ' + reports[i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                        break


            if json_resp['report_message'] == '' :
                json_resp['report_message'] = 'Ok'


            if(len(concepts) > 0):
                for i in range(len(concepts)):
                    #Check if it is a csv
                    if not concepts[i].name.endswith('csv'):
                        json_resp['concept_message'] = 'CONCEPTS FILE - '+ concepts[i].name + ' - The file must be .csv'

                    try:
                        df = pd.read_csv(concepts[i])
                        df = df.where(pd.notnull(df), None)
                        df = df.reset_index(drop=True)
                    except Exception as e:
                        json_resp['concept_message']='CONCEPTS FILE - '+ concepts[i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. '
                        pass
                    #print(df)
                    else:

                        cols = list(df.columns)
                        columns_wrong = False
                        list_db_col = ['concept_url', 'concept_name','usecase','area']

                        # Check if all the mandatory cols are present
                        for el in list_db_col:
                            if el not in cols:
                                columns_wrong = True
                                json_resp['concept_message'] = 'CONCEPTS FILE - '+ concepts[i].name + ' - The column ' + el + ' is not present. The only columns allowed are: concept_utl, concept_name, usecase, area'
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
                            json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[i].name + ' - You must provide at least a concept.'
                            break
                        else:
                            # check if column concept_url has no duplicates
                            df_dup = df[df.duplicated(subset=['concept_url','usecase','area'], keep=False)]
                            if df_dup.shape[0] > 0:
                                    json_resp['concept_message'] = 'WARNING CONCEPTS FILE - ' + concepts[i].name + ' - The rows: ' + str(
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
                                json_resp['concept_message'] = 'CONCEPTS FILE - ' + concepts[i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + ' .'
                                break

                            # warning if there are new use cases
                            for el in df.usecase.unique():
                                if el not in usecases_list and el is not None:
                                    json_resp['concept_message'] = 'WARNING CONCEPTS FILE - ' + concepts[i].name + ' - The usecase ' + el + ' has not any report associated. It\'ok but you can not use the concepts until you have inserted a report with that use case.'

                if json_resp['concept_message'] == '':
                    json_resp['concept_message'] = 'Ok'


            if(len(labels) > 0):
                for i in range(len(labels)):
                    if not labels[i].name.endswith('csv'):
                        json_resp['label_message'] = 'LABELS FILE - '+ labels[i].name + ' - The file must be .csv'
                    try:
                        df = pd.read_csv(labels[i])
                        df = df.where(pd.notnull(df), None)
                        df = df.reset_index(drop=True)

                    except Exception as e:
                        json_resp['label_message'] = 'LABELS FILE - '+ labels[i].name + ' - An error occurred while parsing the csv. Check if is well formatted.'
                        pass
                    # print(df)
                    else:

                        cols = list(df.columns)
                        list_db_col = ['label', 'usecase']

                            
                        esco = False
                        for el in list_db_col:
                            if el not in cols:
                                esco = True
                                json_resp['label_message'] = 'LABELS FILE - '+ labels[i].name + ' - The columns: ' + el + ' is not present. The columns allowed are: labels, usecase.'

                        if esco == True:
                            break

                        if len(cols) != len(list_db_col):
                            json_resp['label_message'] = 'LABELS FILE - ' + labels[i].name + ' - The columns allowed are: label, usecase. If you inserted more (less) columns please, remove (add) them.'
                            break

                        if df.shape[0] == 0:
                            json_resp['label_message'] = 'LABELS FILE - ' + labels[
                                i].name + ' - You must provide at least a row.'
                            break
                        else:
                            # check if columns annotation_label and name have no duplicates
                            df_dup = df[df.duplicated(subset=['label', 'usecase'], keep=False)]
                            if df_dup.shape[0] > 0:
                                json_resp['label_message'] = 'WARNING LABELS FILE - ' + labels[i].name + ' - The rows: ' + str(df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'


                            el = ''
                            if None in df['usecase'].tolist():
                                el = 'usecase'
                            elif None in df['label'].tolist():
                                el = 'label'
                            if el != '':
                                lista = df[el].tolist()
                                ind = lista.index(None)
                                json_resp['label_message'] = 'LABELS FILE - ' + labels[i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + ' .'
                                break

                            for el in df.usecase.unique():
                                if el not in usecases_list:
                                    json_resp['label_message'] = 'WARNING LABELS FILE - ' + labels[i].name + ' - The use case ' + el + ' has not any report associated. It\'s ok, but you need some reports associated to that use case if you want to use the labels.'

                if json_resp['label_message'] == '':
                    json_resp['label_message'] = 'Ok'

            if len(jsonAnn) == 0 and len(jsonDisp) == 0:
                json_resp['fields_message'] = 'REPORT FIELDS TO DISPLAY AND ANNOTATE - Please provide at least one field to be displayed and/or at least one field to be annotated.'

            elif len(jsonAnn) == 0:
                if json_resp['fields_message'] == '':
                    json_resp['fields_message'] = 'WARNING REPORT FIELDS TO ANNOTATE - ok but with this configuration you will not be able to perform mention annotation and linking. Please, select also at least a field to annotate if you want to find some mentions and link them.'

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

def configure_data(reports,labels,concepts,jsondisp,jsonann,jsonall,username,password):

    filename =''
    error_location = 'database'
    connection = ''
    report_usecases = []
    created_file = False

    try:

        connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres", host="db",
                                port="5432")
        cursor = connection.cursor()
        try:
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


            if username is not None and password is not None:
                cursor.execute("INSERT INTO public.user (username,password,profile) VALUES(%s,%s,%s);",(str(username),hashlib.md5(str(password).encode()).hexdigest(),'Admin'))


            fields = []
            all_fields = []
            fields_to_ann = []
            jsonall = ''.join(jsonall)
            jsondisp = ''.join(jsondisp)
            jsonann = ''.join(jsonann)
            jsonall = jsonall.split(',')
            jsondisp = jsondisp.split(',')
            jsonann = jsonann.split(',')

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
                df_report = df_report.where(pd.notnull(df_report), None)
                df_report = df_report.reset_index(drop=True)
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
                    id_report = str(df_report.loc[i, 'id_report'])
                    institute = str(df_report.loc[i, 'institute'])
                    language = str(df_report.loc[i, 'language'])
                    name = str(df_report.loc[i, 'usecase'])
                    report_json = {}

                    #Check if all the not mandatory cols have at least one value != None
                    found = False
                    for col in list_col_not_mandatory:
                    #     if df_report.loc[i,col] is not None:
                    #         found = True
                    #         break
                    # if found == False:
                    #     raise Exception
                    # else:
                    #     for col in list_col_not_mandatory:
                            if df_report.loc[i,col] is not None:
                                col1 = col.replace(' ','_')
                                testo = str(df_report.loc[i,col])
                                filtered = list(s for s in testo if s.isprintable())
                                testo = ''.join(filtered)
                                report_json[col1] = str(testo)

                    report_json = json.dumps(report_json)
                    # Duplicates are not inserted
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
                    df_labels = df_labels.where(pd.notnull(df_labels), None)
                    df_labels = df_labels.reset_index(drop=True)

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


                        cursor.execute("SELECT * FROM annotation_label WHERE name = %s AND label = %s;", (str(name),str(label)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);",
                                       (str(label), int(seq_number), str(name)))

            # Popolate the concepts table
            error_location = 'Concepts'

            for concept_file in concepts:
                df_concept = pd.read_csv(concept_file)
                df_concept = df_concept.where(pd.notnull(df_concept), None)
                df_concept = df_concept.reset_index(drop=True)

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
                    df_concept = df_concept.where(pd.notnull(df_concept), None)
                    concept_url = str(df_concept.loc[i, 'concept_url'])
                    concept_name = str(df_concept.loc[i, 'concept_name'])
                    usecase = str(df_concept.loc[i, 'usecase'])
                    semantic_area = str(df_concept.loc[i, 'area'])

                    cursor.execute("SELECT * FROM concept WHERE concept_url = %s;", (str(concept_url),))
                    ans = cursor.fetchall()
                    if len(ans) == 0:
                        cursor.execute("INSERT INTO concept (concept_url,name) VALUES (%s,%s);",
                                       (str(concept_url), str(concept_name)))

                    cursor.execute("SELECT * FROM concept_has_uc WHERE concept_url = %s AND name = %s;",
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

            version = get_version()
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            version_new = int(version) + 1
            filename = 'fields' + str(version_new)
            created_file = False
            with open(os.path.join(workpath, './data/' + filename + '.json'), 'w') as outfile:
                json.dump(data, outfile)
                created_file = True

        except psycopg2.IntegrityError:
            connection.rollback()
            print('rolledback')
            if created_file == True:
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                if filename != '' and filename != 'fields0':
                    path = os.path.join(workpath, './data/'+filename+'.json')
                    os.remove(path)
            json_resp = {'error': 'an error occurred in: ' + error_location + '.'}
            return json_resp
        else:
            connection.commit()
            outfile.close()
            json_resp = {'message':'Ok'}
            return json_resp

    except (Exception,psycopg2.Error) as e:
        print(e)
        print('rollback')
        json_resp = {'error': 'an error occurred in: ' + error_location + '.'}
        return json_resp

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

def update_db_util(reports,labels,concepts,jsondisp,jsonann,jsondispup,jsonannup,jsonall):
    filename = ''
    error_location = 'database'
    connection = ''
    usecases = []
    sem_areas = []
    created_file = False

    try:
        connection = psycopg2.connect(dbname="ground_truth_db", user="postgres", password="postgres", host="db",
                                      port="5432")
        cursor = connection.cursor()
        try:
            if (jsonannup != '') or jsondispup != '' or jsonall != '':
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
                jsonall = ''.join(jsonall)
                jsondispup = jsondispup.split(',')
                jsonannup = jsonannup.split(',')
                jsonall = jsonall.split(',')
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

                for el in jsonall:
                    if el not in all_fields and el:
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
            if len(reports) > 0:
                error_location = 'Reports'
                for report in reports:
                    df_report = pd.read_csv(report)
                    df_report = df_report.where(pd.notnull(df_report), None)
                    df_report = df_report.reset_index(drop=True)

                    # print(df_report)
                    report_use = df_report.usecase.unique()
                    for el in report_use:
                        if el not in usecases:
                            cursor.execute("INSERT INTO use_case VALUES (%s)",(str(el),))

                    count_rows = df_report.shape[0]
                    list_col_mandatory = ['id_report', 'institute', 'usecase', 'language']
                    list_col_not_mandatory = []
                    for col in df_report:
                        if col not in list_col_mandatory:
                            list_col_not_mandatory.append(col)

                    for i in range(count_rows):
                        id_report = str(df_report.loc[i, 'id_report'])
                        institute = str(df_report.loc[i, 'institute'])
                        language = str(df_report.loc[i, 'language'])
                        name = str(df_report.loc[i, 'usecase'])
                        report_json = {}
                        found = False
                        for col in list_col_not_mandatory:
                            # if col in fields or col in fields_to_ann:
                        #         if df_report.loc[i, col] is not None:
                        #             found = True
                        #             break
                        # if found == False:
                        #     raise Exception
                        # else:
                        #     for col in list_col_not_mandatory:
                                if df_report.loc[i, col] is not None:
                                        col1 = col.replace(' ', '_')
                                        testo = str(df_report.loc[i, col])
                                        filtered = list(s for s in testo if s.isprintable())
                                        testo = ''.join(filtered)
                                        report_json[col1] = str(testo)

                        report_json = json.dumps(report_json)
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
                    df_labels = df_labels.where(pd.notnull(df_labels), None)
                    df_labels = df_labels.reset_index(drop=True)

                    count_lab_rows = df_labels.shape[0]
                    for i in range(count_lab_rows):
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


                        cursor.execute("SELECT * FROM annotation_label WHERE name = %s AND label = %s;", (str(name),str(label)))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute("INSERT INTO annotation_label (label,seq_number,name) VALUES (%s,%s,%s);",
                                       (str(label), int(seq_number), str(name)))


            # Popolate the concepts table
            if len(concepts) > 0:

                error_location = 'Concepts'
                for concept_file in concepts:
                    df_concept = pd.read_csv(concept_file)
                    df_concept = df_concept.where(pd.notnull(df_concept), None)
                    df_concept = df_concept.reset_index(drop=True)
                    count_conc_rows = df_concept.shape[0]

                    list_uc_concept = df_concept.usecase.unique()
                    list_area_concept = df_concept.area.unique()

                    for name in list_uc_concept:
                        cursor.execute('SELECT * FROM use_case WHERE name = %s', (str(name),))
                        ans = cursor.fetchall()
                        if len(ans) == 0:
                            cursor.execute('INSERT INTO use_case VALUES (%s)', (str(name),))
                    for el in list_area_concept:
                        cursor.execute('SELECT * FROM semantic_area WHERE name = %s', (str(el),))
                        if len(cursor.fetchall()) == 0:
                            cursor.execute('INSERT INTO semantic_area VALUES (%s)', (str(el),))


                    for i in range(count_conc_rows):

                        concept_url = str(df_concept.loc[i, 'concept_url'])
                        concept_name = str(df_concept.loc[i, 'concept_name'])
                        usecase = str(df_concept.loc[i, 'usecase'])
                        semantic_area = str(df_concept.loc[i, 'area'])

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
                    json_resp = get_fields_from_json()
                    all_fields = json_resp['all_fields']
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
                        if el not in all_fields:
                            all_fields.append(el)
                for el in jsonann:
                    if len(el) > 0:
                        if el not in fields_to_ann:
                            fields_to_ann.append(el)
                        if el not in all_fields:
                            all_fields.append(el)


                data['fields'] = fields
                data['fields_to_ann'] = fields_to_ann
                data['all_fields'] = all_fields
                version = get_version()
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                version_new = int(version) + 1
                filename = 'fields' + str(version_new)
                with open(os.path.join(workpath, './data/' + filename + '.json'), 'w') as outfile:
                    json.dump(data, outfile)
                    created_file = True


        except psycopg2.IntegrityError as e:
            print(e)
            connection.rollback()
            print('rolledback')

            if created_file == True:
                workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
                if filename != '' and filename != 'fields0':
                    path = os.path.join(workpath, './data/'+filename+'.json')
                    os.remove(path)

            json_resp = {'error': 'an error occurred in: ' + error_location + '. The configuration failed.'}
            return json_resp
        else:
            connection.commit()
            if ((jsonann is not None) and (jsonann != '')) or ((jsondisp is not None) and jsondisp != ''):
                outfile.close()

            json_resp = {'message': 'Ok'}

            return json_resp

    except (Exception, psycopg2.Error) as e:
        print(e)
        print('rolledback')
        json_resp = {'error': 'an error occurred in the file: ' + error_location + '. The configuration failed.'}
        return json_resp

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()


def get_keys_csv(reports):
    keys = []
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
            col_list = ['id_report','language','institute','usecase']
            for col in df:
                if col not in col_list and col not in keys:
                    keys.append(col.replace(' ','_'))
    return keys

# function used when it is needed to update fields. In this case they are taken from the json file.
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
    if User.objects.filter(profile = 'Admin').exists() == False:
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
    return json_resp

# def get_fields_from_json_configuration(usecase,institute,language):
#     json_resp1 = get_fields_from_json()
#     json_resp = {}
#     json_resp['fields'] = []
#     json_resp['fields_to_ann'] = []
#     reports = Report.objects.filter(name=usecase,institute = institute, language = language)
#     for report in reports:
#         rep = (report.report_json)
#         for key in rep.keys():
#             if key in json_resp1['fields']:
#                 if key not in json_resp['fields']:
#                     json_resp['fields'].append(key)
#             if key in json_resp1['fields_to_ann']:
#                 if key not in json_resp['fields_to_ann']:
#                     json_resp['fields_to_ann'].append(key)
#
#     # print(json_resp)
#     return json_resp

def check_for_update(type_req,reports,labels,concepts,areas,usecase,jsonDisp,jsonAnn,jsonDispUp,jsonAnnUp):
    usecases = []
    sem_areas = []
    json_keys = []
    keys = get_fields_from_json()
    ann = keys['fields_to_ann']
    disp = keys['fields']


    if(jsonDispUp is not None and jsonAnnUp is not None):
        jsonDispUp = ''.join(jsonDispUp)
        jsonAnnUp = ''.join(jsonAnnUp)
        jsonDispUp = jsonDispUp.split(',')
        jsonAnnUp = jsonAnnUp.split(',')

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
                    list_db_col = ['concept_url', 'concept_name','usecase','area']
                    cols = list(df.columns)


                    for el in list_db_col:
                        if el not in cols:
                            message = 'CONCEPTS FILE - ' + concepts[i].name + ' - The columns: ' + el + ' is missing. Please, add it.'
                            return message

                    if len(list_db_col) != len(cols):
                        message = 'CONCEPTS FILE - ' + concepts[i].name + ' - The columns allowed are: concept_url, concept_name, usecase, area. If you inserted more (less) columns please, remove (add) them.'
                        return message

                    if df.shape[0] == 0:
                        message = 'CONCEPTS FILE - ' + concepts[i].name + ' - You must provide at least a concept.'
                        return message
                    else:
                        #duplicates in file
                        df_dup = df[df.duplicated(subset=['concept_url','usecase','area'], keep=False)]
                        if df_dup.shape[0] > 0:
                            message = 'WARNING CONCEPTS FILE - ' + concepts[i].name + ' - The rows: ' + str(df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'

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
                            message = 'CONCEPTS FILE - ' + concepts[i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                            return message

                        distinct_concept_usecase = df['usecase'].unique()
                        for el in distinct_concept_usecase:
                            if el not in distinct_uc_report:
                                message = 'WARNING CONCEPTS FILE - ' + concepts[
                                    i].name + ' - The file contains the concepts for the use case ' + el + ' which has 0 reports associated.'

                        #Check for duplicates in db
                        for ind in range(df.shape[0]):
                            cursor.execute('SELECT COUNT(*) FROM concept WHERE concept_url = %s',[str(df.loc[ind,'concept_url'])])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING CONCEPTS FILE - ' + concepts[i].name + ' - The concept: ' + str(df.loc[ind,'concept_url']) + ' is already present in the database. It will be ignored.'

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
                    message = 'LABELS FILE - ' + labels[i].name + ' - An error occurred while parsing the csv. Check if is well formatted.'
                    return message
                else:
                    cols = list(df.columns)
                    list_db_col = ['label', 'usecase']


                    for el in list_db_col:
                        if el  not in cols:
                            message = 'LABELS FILE - ' + labels[i].name + ' - The columns: ' + el + ' is missing. The columns allowed are: label, usecase.'
                            return message

                    if len(list_db_col) != len(cols):
                        message = 'LABELS FILE - ' + labels[i].name + ' - The columns allowed are: label, usecase. If you inserted more (less) columns please, remove (add) them.'
                        return message

                    if df.shape[0] == 0:
                        message = 'LABELS FILE - You must provide at least a row.'
                        return message

                    else:

                        df_dup = df[df.duplicated(subset=['label','usecase'], keep=False)]
                        if df_dup.shape[0] > 0:
                            message = 'WARNING LABELS FILE - ' + labels[
                                i].name + ' - The rows: ' + str(df_dup.index.to_list()) + ' are duplicated. The duplicates will be ignored.'

                        for ind in range(df.shape[0]):
                            cursor.execute('SELECT COUNT(*) FROM annotation_label WHERE label = %s AND name = %s',
                                           [str(df.loc[ind, 'label']),str(df.loc[ind, 'usecase'])])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING LABELS FILE - ' + labels[i].name + ' - The label: ' + str(df.loc[ind, 'label']) + ' for the use case: '+ str(df.loc[ind,'usecase'])+' is already present in the database. It will be ignored.'

                        el = ''
                        if None in df['usecase'].tolist():
                            el = 'usecase'
                        elif None in df['label'].tolist():
                            el = 'label'

                        if el != '':
                            lista = df[el].tolist()
                            ind = lista.index(None)
                            message = 'LABELS FILE - ' + labels[i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + ' .'
                            return message

                        distinct_label_usecase = df['usecase'].unique()
                        for el in distinct_label_usecase:
                            if el not in distinct_uc_report:
                                message = 'WARNING LABELS FILE - ' + labels[
                                    i].name + ' - The file contains the labels for ' + el + ' which has 0 reports associated.'

                return  message


        elif len(reports) > 0:
            message = ''
            for i in range(len(reports)):
                if not reports[i].name.endswith('csv'):
                    message = 'REPORTS FILE - '+ reports[i].name + ' - The file must be .csv'
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
                    message = 'REPORTS FILE - ' + reports[i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. '
                    return  message
                else:
                    cols = list(df.columns)
                    count = 0



                    # print(cols)
                    list_db_col = ['id_report','institute','usecase','language']
                    for el in list_db_col:
                        if el not in cols:
                            message = 'REPORTS FILE - ' + reports[i].name + ' - The column: ' + str(el) + ' must be present.'
                            return message

                    list_not_db_col = []
                    for el in cols:
                        if el not in list_db_col:
                            list_not_db_col.append(el)

                    if (jsonDispUp is not None and jsonAnnUp is not None):
                        if (len(disp) > 0 or len(ann) > 0):
                            disp_intersect = list(set(disp) & set(list_not_db_col))
                            ann_intersect = list(set(ann) & set(list_not_db_col))
                            for el in list_not_db_col:
                                if(el not in disp and el not in ann) and (el not in jsonDispUp and el not in jsonAnnUp):
                                    count = count + 1
                            if count == len(list_not_db_col):
                                message = 'REPORT FIELDS - Please, provide at least one field to display in file: ' + reports[i].name + '. Be careful that if you do not provide one field to annotate you will not be able to perform mention annotation and linking.'
                                return message
                            elif len(ann_intersect) == 0 and (jsonAnnUp[0]) == '':
                                message = 'WARNING REPORT FIELDS - file: ' + reports[i].name + ' Please, provide at least one field to annotate if you want to find mentions and perform linking.'


                    if len(list_not_db_col) == 0:
                        message = 'REPORTS FILE - ' + reports[i].name + ' - You must provide at least one column other than institute, usecase, language, id_report'
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
                                           [str(df.loc[ind, 'id_report']),str(df.loc[ind, 'language'])])
                            num = cursor.fetchone()
                            if num[0] > 0:
                                message = 'WARNING REPORT FILE - ' + reports[i].name + ' - The report: ' + str(df.loc[ind, 'id_report']) + ' for the language: '+ str(df.loc[ind,'language'])+' is already present in the database. It will be ignored.'

                            for el in list_db_col:
                                if df.loc[ind, el] is not None:
                                    found = True
                                    break

                            if found == False:
                                message = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(ind) + ' has the columns: ' + ', '.join(list_db_col) + ' empty. Provide a value for at least one of these columns.'
                                return  message

                            found = False
                            count_both= 0
                            not_none_cols = []

                            for el in list_not_db_col:
                                if df.loc[ind, el] is not None:
                                    found = True
                                    not_none_cols.append(el)

                            if found == False:
                                message = 'REPORTS FILE - ' + reports[i].name + ' -  The report at row ' + str(ind) + ' has the columns: ' + ', '.join(list_not_db_col) + ' empty. Provide a value for at least one of these columns, or delete this report from the csv file.'
                                return  message


                            for el in not_none_cols:
                                if jsonAnnUp is not None and jsonDispUp is not None:
                                    if el not in disp and el not in jsonDispUp and el not in ann and el not in jsonAnnUp:
                                        count_both = count_both + 1

                                else:
                                    if el not in disp and el not in ann :
                                        count_both = count_both + 1

                            if count_both == len(not_none_cols):
                                message = 'WARNING REPORT FIELDS TO DISPLAY AND ANNOTATE - ' + reports[
                                    i].name + ' -  With the current configuration the report at the row: ' + str(
                                    ind) + ' would not be displayed since the columns to display are all empty for that report.'

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
                            message = 'REPORTS FILE - ' + reports[i].name + ' - The column ' + el + ' is empty at the row: ' + str(ind) + '.'
                            return message

        if jsonAnn is not None and jsonDisp is not None:
            if(type_req == 'json_fields' and len(jsonAnn) == 0) and len(jsonDisp) == 0 and len(ann) == 0:
                message = 'REPORT FIELDS TO ANNOTATE - You must provide at least one field to display and/or one field to display and annotate.'
                return message

            elif(type_req == 'json_fields' and len(jsonAnn) == 0):
                message = 'WARNING REPORT FIELDS TO ANNOTATE - ok, but with this configuration you will not be able to perform mention annotation and linking. Please, select also at least a field to annotate if you want to find some mentions and link them'
                return message
        # if jsonAnnUp is not None and jsonDispUp is not None:
        #     if type_req == 'reports' and len(jsonAnnUp) == 0 and len(jsonDispUp) == 0:
        #         message = 'REPORT FIELDS - You must provide at least one field to display and/or one field to display and annotate.'
        #         return message


        if type_req == 'labels' and len(labels) == 0:
            message = 'LABELS - Please insert a labels file.'
            return message

        if type_req == 'concepts' and len(concepts) == 0:
            message = 'CONCEPTS - Please insert a concepts file.'
            return message

        if type_req == 'reports' and len(reports) == 0:
            message = 'REPORTS - Please insert a reports file.'
            return message



        return message

    except (Exception,psycopg2.Error) as e:
        print(e)
        message='An error occurred in ' + type_req + ' file(s). Please check if it is similar to the example we provided.'
        return message

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
    print(version)
    return version



def report_get_start_end(json_keys,json_keys_to_ann,report,language):
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

    return json_dict
