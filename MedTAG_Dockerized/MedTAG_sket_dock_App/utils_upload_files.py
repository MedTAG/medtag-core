import psycopg2
import re
import json
from MedTAG_sket_dock_App.models import *
import os
import pandas as pd
import numpy
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
from MedTAG_sket_dock_App.utils import *


def check_uploaded_files(files):

    """This method checks whether the files uploaded by the user to copy the ground-truths are well formatted"""

    json_resp = {}
    json_resp['message'] = ''
    for i in range(len(files)):
        # Error if the file is not csv
        if not files[i].name.endswith('csv'):
            json_resp['message'] = 'ERROR - ' + files[i].name + ' - The file must be .csv'
            return json_resp

        try:
            df = pd.read_csv(files[i])
            df = df.where(pd.notnull(df), None)
            df = df.reset_index(drop=True)  # Useful if the csv includes only commas
        except Exception as e:
            print(e)
            json_resp['message'] = 'ERROR - ' + files[
                i].name + ' - An error occurred while parsing the csv. Check if it is well formatted. Check if it contains as many columns as they are declared in the header.'
            return json_resp

        else:
            # check if colunns are allowed and without duplicates
            cols = list(df.columns)
            labels = ['username', 'annotation_mode', 'id_report', 'language', 'batch', 'institute', 'usecase', 'label']
            mentions = ['username', 'annotation_mode', 'id_report', 'language', 'batch', 'institute', 'usecase',
                        'start', 'stop',
                        'mention_text']
            concepts = ['username', 'annotation_mode', 'id_report', 'language', 'batch', 'institute', 'usecase',
                        'concept_url',
                        'concept_name', 'area']
            linking = ['username', 'annotation_mode', 'id_report', 'language', 'batch', 'institute', 'usecase', 'start',
                       'stop',
                       'mention_text', 'concept_name', 'concept_url', 'area']

            if set(cols) != set(labels) and set(cols) != set(mentions) and set(cols) != set(concepts) and set(cols) != set(linking):
                json_resp['message'] = 'ERROR - ' + files[
                    i].name + ' - The set of columns you inserted in the csv does not correspond to those we ask. ' \
                              'Check the examples.'
                return json_resp


            if 'usecase' in cols:
                df['usecase'] = df['usecase'].str.lower()

            # Check if the csv is empty with 0 rows
            if df.shape[0] == 0:
                json_resp['message'] = 'ERROR - ' + files[
                    i].name + ' - You must provide at least a row.'
                return json_resp

    if len(files) > 0:
        if json_resp['message'] == '':
            json_resp['message'] = 'Ok'
    return json_resp


def upload_files(files,user_to,overwrite):

    """This method handles the upload of csv files to copy th annotations from"""

    json_resp = {'message':'Ok'}
    mode_rob = NameSpace.objects.get(ns_id='Robot')
    mode_hum = NameSpace.objects.get(ns_id='Human')
    print(user_to)
    username_rob = User.objects.get(username='Robot_user', ns_id=mode_rob)
    try:
        with transaction.atomic():
            for i in range(len(files)):
                df = pd.read_csv(files[i])
                df = df.where(pd.notnull(df), None)
                df = df.reset_index(drop=True)  # Useful if the csv includes only commas
                df.sort_values(['id_report','language','annotation_mode'])
                cols = list(df.columns)
                labels = ['username', 'annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'label']
                mentions = ['username', 'annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'start', 'stop',
                         'mention_text']
                concepts = ['username', 'annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'concept_url',
                         'concept_name', 'area']
                linking = ['username', 'annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'start', 'stop',
                         'mention_text', 'concept_name', 'concept_url', 'area']


                for i, g in df.groupby(['id_report','language','annotation_mode']):
                    count_rows = g.shape[0]

                    deleted_mentions = False

                    if df.annotation_mode.unique()[0] == 'Manual':
                        a = 'Human'
                    else:
                        a = 'Robot'
                    report_cur = Report.objects.get(id_report = str(g.id_report.unique()[0]), language = g.language.unique()[0] )
                    mode = NameSpace.objects.get(ns_id =a)
                    anno_mode = mode
                    if a == 'Robot' and GroundTruthLogFile.objects.filter(username = username_rob).count() == 0:
                        json_resp = {'message':'automatic missing'}
                        return json_resp
                    report = report_cur
                    g = g.reset_index()
                    action = ''

                    user = User.objects.get(username=user_to, ns_id=mode)

                    if set(cols) == set(labels):
                        user_to_gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                       id_report=report, language=report.language,
                                                                       gt_type='labels')

                        if overwrite == False:
                            if mode.ns_id == 'Robot':
                                if not user_to_gt.exists():

                                    Associate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                             language=report.language).delete()
                        else:
                            GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report,
                                                              language=report.language,
                                                              gt_type='labels').delete()
                            Associate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                     language=report.language).delete()


                    elif set(cols) == set(mentions):
                        user_to_gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                       id_report=report, language=report.language,
                                                                       gt_type='mentions')
                        robot_gt = GroundTruthLogFile.objects.filter(username=username_rob, ns_id=mode_rob,
                                                                     id_report=report, language=report.language,
                                                                     gt_type='mentions')
                        # ins_time = ''
                        # if robot_gt.exists():
                        #     rob_first_gt = robot_gt.first()
                        #     ins_time = rob_first_gt.insertion_time

                        if overwrite == False:
                            if mode.ns_id == 'Robot':
                                if not user_to_gt.exists():
                                    # user_to_gt_first = user_to_gt.first()
                                    # if user_to_gt_first.insertion_time == ins_time:
                                    #     GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                    #                                       id_report=report,
                                    #                                       language=report.language,
                                    #                                       gt_type='mentions').delete()
                                    if Linked.objects.filter(username=user, ns_id=mode, id_report=report,
                                                             language=report.language).exists():
                                        GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                          id_report=report,
                                                                          language=report.language,
                                                                          gt_type='concept-mention').delete()
                                        GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                          id_report=report,
                                                                          language=report.language,
                                                                          gt_type='concepts').delete()
                                    Annotate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                            language=report.language).delete()
                                    links = Linked.objects.filter(username=user, ns_id=mode, id_report=report,
                                                                  language=report.language)
                                    for e in links:
                                        concept = e.concept_url
                                        Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                                language=report.language, concept_url=concept).delete()
                                    links.delete()
                        else:
                            GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                              id_report=report,
                                                              language=report.language,
                                                              gt_type='mentions').delete()
                            if Linked.objects.filter(username=user, ns_id=mode,id_report=report,language=report.language).exists():
                                GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                  id_report=report,
                                                                  language=report.language,
                                                                  gt_type='concept-mention').delete()
                                GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                  id_report=report,
                                                                  language=report.language,
                                                                  gt_type='concepts').delete()

                            Annotate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                     language=report.language).delete()
                            links = Linked.objects.filter(username=user, ns_id=mode, id_report=report,
                                                           language=report.language)
                            for e in links:
                                concept = e.concept_url
                                Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                        language=report.language, concept_url=concept).delete()
                            links.delete()

                    elif set(cols) == set(concepts):
                        user_to_gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                       id_report=report, language=report.language,
                                                                       gt_type='concepts')
                        robot_gt = GroundTruthLogFile.objects.filter(username=username_rob, ns_id=mode_rob,
                                                                     id_report=report, language=report.language,
                                                                     gt_type='concepts')
                        # ins_time = ''
                        # if robot_gt.exists():
                        #     rob_first_gt = robot_gt.first()
                        #     ins_time = rob_first_gt.insertion_time

                        if overwrite == False:
                            if mode.ns_id == 'Robot':
                                if not user_to_gt.exists():
                                    # user_to_gt_first = user_to_gt.first()
                                    # if user_to_gt_first.insertion_time == ins_time:
                                    #     GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                    #                                       id_report=report,
                                    #                                       language=report.language,
                                    #                                       gt_type='concepts').delete()
                                    Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                            language=report.language).delete()
                        else:
                            GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report,
                                                              language=report.language,
                                                              gt_type='concepts').delete()
                            Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                     language=report.language).delete()

                    elif set(cols) == set(linking):
                        user_to_gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                       id_report=report, language=report.language,
                                                                       gt_type='concept-mention')

                        if overwrite == False:
                            if mode.ns_id == 'Robot':
                                if not user_to_gt.exists():

                                    GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                      id_report=report,
                                                                      language=report.language,
                                                                      gt_type='concepts').delete()

                                    GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                                      id_report=report,
                                                                      language=report.language,
                                                                      gt_type='mentions').delete()
                                    links = Linked.objects.filter(username=user, ns_id=mode, id_report=report,
                                                                  language=report.language)
                                    for e in links:
                                        concept = e.concept_url
                                        area = e.name
                                        Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                                language=report.language, name=area,
                                                                concept_url=concept).delete()

                                    links.delete()
                                    Annotate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                            language=report.language).delete()

                        else:
                            GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                              id_report=report,
                                                              language=report.language,
                                                              gt_type='concepts').delete()
                            GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                              id_report=report,
                                                              language=report.language,
                                                              gt_type='concept-mention').delete()
                            GroundTruthLogFile.objects.filter(username=user, ns_id=mode,
                                                              id_report=report,
                                                              language=report.language,
                                                              gt_type='mentions').delete()


                            links = Linked.objects.filter(username=user, ns_id=mode, id_report=report,
                                                           language=report.language)

                            for ll in links:
                                concept = ll.concept_url
                                area = ll.name
                                Contains.objects.filter(username=user, ns_id=mode, id_report=report,
                                                        language=report.language, concept_url=concept,name = area).delete()

                            Annotate.objects.filter(username=user, ns_id=mode, id_report=report,
                                                    language=report.language).delete()
                            links.delete()



                    for i in range(count_rows):
                        usecase = str(df.loc[i, 'usecase'])
                        usecase_obj = UseCase.objects.get(name=usecase)
                        mode = str(g.loc[i, 'annotation_mode'])
                        id_report = str(g.loc[i, 'id_report'])
                        language = str(g.loc[i, 'language'])
                        institute = str(g.loc[i, 'institute'])
                        # user_from = str(g.loc[i, 'username'])
                        if mode == 'Manual':
                            mode = 'Human'
                        elif mode == 'Automatic':
                            mode = 'Robot'

                        # username_from = User.objects.get(username=user_from, ns_id=mode)
                        mode = NameSpace.objects.get(ns_id = mode)
                        report = Report.objects.get(id_report=id_report, language=language, institute=institute)

                        if set(cols) == set(labels):
                            label = AnnotationLabel.objects.get(label = str(g.loc[i, 'label']),name = usecase_obj)

                            if (overwrite == False and not GroundTruthLogFile.objects.filter(username=user,
                                                                                             ns_id=mode,
                                                                                             id_report=report,
                                                                                             language=report.language,
                                                                                             gt_type='labels').exists()) or overwrite == True:
                                if not Associate.objects.filter(username=user, ns_id=mode, id_report=report, label=label,seq_number=label.seq_number,
                                                         language=report.language).exists():
                                    Associate.objects.create(username=user, ns_id=mode, id_report=report, label=label,
                                                         seq_number=label.seq_number,
                                                         language=report.language, insertion_time=Now())
                                action = 'labels'

                        elif set(cols) == set(mentions):

                            mention = Mention.objects.get(id_report = report, language = language, start = int(g.loc[i, 'start']),
                                                          stop = int(g.loc[i, 'stop']))

                            if (overwrite == False and not GroundTruthLogFile.objects.filter(username=user,
                                                                                             ns_id=mode,
                                                                                             id_report=report,
                                                                                             language=report.language,
                                                                                             gt_type='mentions').exists()) or overwrite == True:
                                if not Annotate.objects.filter(username=user, ns_id=mode, id_report=report,start = mention,stop = mention.stop,
                                                            language=report.language).exists():
                                    Annotate.objects.create(username=user, ns_id=mode, id_report=report,start = mention,stop = mention.stop,
                                                            language=report.language, insertion_time=Now())
                                action = 'mentions'

                        elif set(cols) == set(concepts):

                            concept = Concept.objects.get(concept_url = str(g.loc[i, 'concept_url']))
                            area = SemanticArea.objects.get(name=str(g.loc[i, 'area']))


                            if (overwrite == False and not GroundTruthLogFile.objects.filter(username=user,
                                                                                             ns_id=mode,
                                                                                             id_report=report,
                                                                                             language=report.language,
                                                                                             gt_type='concepts').exists()) or overwrite == True:
                                if not Contains.objects.filter(username = user, ns_id =mode, id_report = report,concept_url = concept,name = area,
                                                               language = report.language).exists():
                                    Contains.objects.create(username = user, ns_id =mode, id_report = report,concept_url = concept,name = area,
                                                               language = report.language,insertion_time = Now())
                                action = 'concepts'
                        elif set(cols) == set(linking):

                            concept = Concept.objects.get(concept_url = str(g.loc[i, 'concept_url']))
                            area = SemanticArea.objects.get(name=str(g.loc[i, 'area']))
                            mention = Mention.objects.get(id_report=report, language=language,start=int(g.loc[i, 'start']),
                                                          stop=int(g.loc[i, 'stop']))


                            if (overwrite == False and not GroundTruthLogFile.objects.filter(username=user,
                                                                                             ns_id=mode,
                                                                                             id_report=report,
                                                                                             language=report.language,
                                                                                             gt_type='concept-mention').exists()) or overwrite == True:

                                if not deleted_mentions:
                                    Annotate.objects.filter(username=user, ns_id=mode, id_report=report,language=report.language).delete()
                                    deleted_mentions = True

                                a = Annotate.objects.filter(username = user, ns_id = mode, id_report = report,
                                                               language = report.language,start=mention,stop = mention.stop)
                                c = Contains.objects.filter(username = user, ns_id = mode, id_report = report,concept_url = concept,name = area,
                                                               language = report.language)
                                l = Linked.objects.filter(username = user, ns_id = mode, id_report = report,concept_url = concept,name = area,
                                                               language = report.language,start=mention,stop = mention.stop)
                                if not a.exists():
                                    Annotate.objects.create(username=user, ns_id=mode, id_report=report,
                                                            language=report.language, start=mention, stop=mention.stop, insertion_time = Now())

                                if not c.exists():
                                    Contains.objects.create(username = user, ns_id = mode, id_report = report,concept_url = concept,name = area,
                                                               language = report.language,insertion_time = Now())
                                if not l.exists():
                                    Linked.objects.create(username = user, ns_id = mode, id_report = report,concept_url = concept,name = area,
                                                               language = report.language,start=mention,stop = mention.stop,insertion_time = Now())
                                action = 'concept-mention'


                    if action != '':

                        # gt_json = serialize_gt(action, usecase, user_to, report_cur.id_report, report_cur.language,
                        #                        anno_mode)
                        # GroundTruthLogFile.objects.create(username=user, ns_id=anno_mode, gt_type=action,gt_json=gt_json, insertion_time=Now(),id_report=report_cur, language=language)
                        if action == 'concept-mention':
                            gt_json = serialize_gt('mentions', usecase, user_to, report_cur.id_report, report_cur.language,
                                                   anno_mode)
                            GroundTruthLogFile.objects.create(username=user, ns_id=anno_mode, gt_type='mentions',
                                                              gt_json=gt_json, insertion_time=Now(),
                                                              id_report=report_cur, language=language)
                            gt_json = serialize_gt('concepts', usecase, user_to, report_cur.id_report, report_cur.language,
                                                   anno_mode)
                            GroundTruthLogFile.objects.create(username=user, ns_id=anno_mode, gt_type='concepts',
                                                              gt_json=gt_json, insertion_time=Now(),
                                                              id_report=report_cur, language=language)
                        if action == 'mentions':
                            gt_json = serialize_gt('concepts', usecase, user_to, report_cur.id_report, report_cur.language,
                                                   anno_mode)
                            if Contains.objects.filter(id_report=report_cur, language=language,username=user, ns_id=anno_mode).count()>0 and Linked.objects.filter(id_report=report_cur, language=language,username=user, ns_id=anno_mode).count()>0:
                                GroundTruthLogFile.objects.create(username=user, ns_id=anno_mode, gt_type='concepts',
                                                                  gt_json=gt_json, insertion_time=Now(),
                                                                  id_report=report_cur, language=language)

    except Exception as e:
        print(e)
        json_resp = {'message':'an error occurred, remember that your configuration must be the same of the one of the user you are uploading the annotations of.'}
    finally:
        return json_resp
