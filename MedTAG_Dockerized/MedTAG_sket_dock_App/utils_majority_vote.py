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

def create_majority_vote_gt(action,users,mode,report):

    """This method creates the majority vote ground truth."""

    ns_human = NameSpace.objects.get(ns_id='Human')
    ns_robot = NameSpace.objects.get(ns_id='Robot')
    # print(report.id_report)
    agent = User.objects.get(username='Robot_user',ns_id=ns_robot)
    # users = User.objects.filter(username__in=users1)
    majority_gt = {}
    majority_gt['Human'] = []
    majority_gt['Robot'] = []
    majority_gt['both'] = []
    cursor = connection.cursor()
    try:
        if action == 'labels':
            labels = AnnotationLabel.objects.filter(name=report.name,seq_number__gt=20)
            json_val = {}
            total_gt = GroundTruthLogFile.objects.filter(gt_type='labels', ns_id=ns_human,
                                                                     username__in=users, id_report=report,
                                                                     language=report.language).count()
            # json_val['total_gt'] = total_gt
            # majority_gt['Human'].append(json_val)

            for lab in labels:
                cursor.execute("SELECT username,label,seq_number FROM associate WHERE label = %s AND seq_number = %s AND ns_id = %s AND id_report = %s AND language = %s AND username IN %s",[lab.label,int(lab.seq_number),'Human',str(report.id_report),str(report.language),tuple(users)])
                json_val = {}
                assos_human = cursor.fetchall()
                json_val['users_list'] = []
                for ass in assos_human:
                    # print(ass)
                    if ass[0] not in json_val['users_list']:
                        json_val['users_list'].append(ass[0])
                json_val['count'] = len(assos_human)
                json_val['label'] = lab.label
                json_val['total_gt'] = total_gt
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Human'].append(json_val)



            labels = AnnotationLabel.objects.filter(name=report.name,seq_number__lte=20)
            cursor.execute(
                "SELECT a.username FROM ground_truth_log_file AS a INNER JOIN ground_truth_log_file AS aa ON a.id_report = aa.id_report and a.gt_type = aa.gt_type and a.language = aa.language  WHERE aa.username=%s AND a.gt_type = %s AND a.ns_id = %s AND a.id_report = %s AND a.language = %s AND a.username IN %s AND a.insertion_time != aa.insertion_time",
                ['Robot_user', 'labels', 'Robot', str(report.id_report), str(report.language),
                 tuple(users)])
            ans = cursor.fetchall()
            total_gt = len(ans)
            # json_val['total_gt'] = total_gt
            # majority_gt['Robot'].append(json_val)
            for lab in labels:
                json_val = {}
                json_val['users_list'] = []
                time = '0001-01-01 00:00:00.000000+00'

                anno_robot = Associate.objects.filter(username=agent, ns_id=ns_robot, label=lab,seq_number__lte=lab.seq_number, id_report=report,
                                                       language=report.language)
                if anno_robot.exists() and anno_robot.count() == 1:
                    anno_robot = anno_robot.first()
                    time = anno_robot.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')

                users1 = User.objects.filter(username__in=users,ns_id=ns_robot)
                anno_users = Associate.objects.filter(username__in=users1, ns_id=ns_robot, label=lab,seq_number__lte=lab.seq_number, id_report=report,
                                                       language=report.language).exclude(insertion_time=time)
                for el in anno_users:
                    # print(el.username_id)
                    if el.username_id not in json_val['users_list']:
                        json_val['users_list'].append(el.username_id)

                json_val['count'] = len(anno_users)
                json_val['label'] = lab.label

                json_val['total_gt'] = total_gt

                # print(json_val)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Robot'].append(json_val)



            if mode == 'both':

                # json_val = {}
                # json_val['total_human_gt'] = majority_gt['Human'][0]['total_gt']
                # json_val['total_robot_gt'] = majority_gt['Robot'][0]['total_gt']
                # majority_gt['both'].append(json_val)

                labels = AnnotationLabel.objects.filter(name=report.name,seq_number__lte=20)
                for lab in labels:
                    found = False
                    json_val = {}
                    json_val['users_list'] = []
                    # total_gt = GroundTruthLogFile.objects.filter(gt_type='labels',username__in=users,id_report = report,language = report.language)
                    for j_val in majority_gt['Human']:
                        for js_val in majority_gt['Robot']:
                            json_val['count'] = int(j_val['count']) + int(js_val['count'])
                            json_val['label'] = j_val['label']
                            json_val['total_human_gt'] = j_val['total_gt']
                            json_val['total_robot_gt'] = js_val['total_gt']
                            json_val['manual_annotators'] = j_val['users_list']

                            json_val['robot_annotators'] = js_val['users_list']
                            if lab.label == j_val['label'] == js_val['label']:
                                found = True

                                json_val['total_gt'] = j_val['total_gt'] + js_val['total_gt']
                                json_val['users_list'] = list(set(js_val['users_list'] + j_val['users_list']))

                                if json_val['count'] > (json_val['total_gt'] / 2):
                                    majority_gt['both'].append(json_val)
                            if found:
                                break
                        if found:
                            break


        elif action == 'mentions':
            # if mode == 'Human':
            users1 = User.objects.filter(username__in=users,ns_id=ns_human)
            mentions = Annotate.objects.filter(username__in=users1,ns_id=ns_human,id_report = report, language = report.language).distinct('start')
            total_gt = GroundTruthLogFile.objects.filter(username__in=users1,gt_type='mentions',ns_id=ns_human,id_report = report,language = report.language)
            # if len(mentions) == 0:
            #     json_val = {}
            #     json_val['total_gt'] = 0
            #     majority_gt['Human'].append(json_val)

            for el in mentions:
                json_val = {}
                mention = Mention.objects.get(start=el.start_id,stop=el.stop,id_report = report, language = report.language)
                anno = Annotate.objects.filter(username__in = users1,id_report = report,language = report.language,start = mention,stop=mention.stop,ns_id=ns_human)
                json_val['count'] = anno.count()
                json_val['total_gt'] = total_gt.count()
                json_val['mention'] = mention.mention_text
                json_val['start'] = mention.start
                json_val['stop'] = mention.stop
                json_val['users_list'] = []

                for ass in anno:
                    if ass.username_id not in json_val['users_list']:
                        json_val['users_list'].append(ass.username_id)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Human'].append(json_val)

            # if mode == 'Robot':
            users1 = User.objects.filter(username__in=users,ns_id=ns_robot)
            mentions = Annotate.objects.filter(username__in=users1,ns_id=ns_robot, id_report=report,
                                               language=report.language).distinct('start')

            cursor.execute(
                "SELECT a.username FROM ground_truth_log_file AS a INNER JOIN ground_truth_log_file AS aa ON a.id_report = aa.id_report and a.gt_type = aa.gt_type and a.language = aa.language  WHERE aa.username=%s AND a.gt_type = %s AND a.ns_id = %s AND a.id_report = %s AND a.language = %s AND a.username IN %s AND a.insertion_time != aa.insertion_time",
                ['Robot_user', 'mentions', 'Robot', str(report.id_report), str(report.language),
                 tuple(users)])
            ans = cursor.fetchall()
            total_gt = len(ans)
            # json_val = {}
            # json_val['total_gt'] = total_gt
            # majority_gt['Robot'].append(json_val)

            for mention in mentions:
                json_val = {}
                json_val['users_list'] = []
                ins_time = '0001-01-01 00:00:00.000000+00'
                ins_time_gt = '0001-01-01 00:00:00.000000+00'
                ment = Mention.objects.get(id_report = report,language = report.language, start = mention.start_id,stop = mention.stop)
                robot_anno = Annotate.objects.filter(username=agent, ns_id=ns_robot, id_report=report,start = ment,stop = ment.stop,
                                        language=report.language)
                robot_anno_gt = GroundTruthLogFile.objects.filter(username=agent, ns_id=ns_robot, id_report=report,gt_type='mentions',
                                        language=report.language)

                if robot_anno.exists() and robot_anno.count() == 1:
                    robot_anno = robot_anno.first()
                    ins_time = robot_anno.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')

                if robot_anno_gt.exists() and robot_anno_gt.count() == 1:
                    robot_anno_gt = robot_anno_gt.first()
                    ins_time_gt = robot_anno_gt.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')

                # total_gt = GroundTruthLogFile.objects.filter(username__in=users1,ns_id=ns_robot,id_report = report,language = report.language,gt_type='mentions').exclude(insertion_time = ins_time_gt)
                user_anno = Annotate.objects.filter(username__in=users1, ns_id=ns_robot, id_report=report, start=ment,
                                                    stop=ment.stop,
                                                    language=report.language).exclude(insertion_time = ins_time)
                json_val['total_gt'] = total_gt
                json_val['count'] = user_anno.count()
                json_val['start'] = ment.start
                json_val['stop'] = ment.stop
                json_val['mention'] = ment.mention_text
                for el in user_anno:
                    if el.username_id not in json_val['users_list']:
                        json_val['users_list'].append(el.username_id)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Robot'].append(json_val)

            if mode == 'both':
                annotations = Annotate.objects.filter(username__in=users1,id_report = report,language = report.language).distinct('start')
                human_gt = GroundTruthLogFile.objects.filter(gt_type='mentions', ns_id=ns_human, id_report=report,
                                                             language=report.language, username__in=users1)
                rob_gt = GroundTruthLogFile.objects.get(gt_type = 'mentions',id_report = report,language = report.language,username=agent,ns_id=ns_robot)
                robot_gt = GroundTruthLogFile.objects.filter(gt_type='mentions', ns_id=ns_robot, id_report=report,
                                                             language=report.language, username__in=users1).exclude(insertion_time = rob_gt.insertion_time)
                # json_val = {}
                # json_val['total_human_gt'] = human_gt.count()
                # json_val['total_robot_gt'] = robot_gt.count()
                # majority_gt['both'].append(json_val)

                for mention in annotations:
                    json_val = {}
                    json_val['users_list'] = []
                    json_val['total_human_gt'] = human_gt.count()
                    json_val['total_robot_gt'] = robot_gt.count()
                    json_val['total_gt'] = robot_gt.count() + human_gt.count()
                    ins_time = '0001-01-01 00:00:00.000000+00'
                    ment = Mention.objects.get(id_report=report, language=report.language, start=mention.start_id,
                                               stop=mention.stop)
                    robot_anno = Annotate.objects.filter(username=agent, ns_id=ns_robot, id_report=report, start=ment,
                                                         stop=ment.stop,
                                                         language=report.language)
                    if robot_anno.exists() and robot_anno.count() == 1:
                        robot_anno = robot_anno.first()
                        ins_time = robot_anno.insertion_time
                        if 'Robot_user' not in json_val['users_list']:
                            json_val['users_list'].append('Robot_user')

                    users_anno = Annotate.objects.filter(username__in=users1,ns_id = ns_human, id_report=report,
                                                        start=ment, stop=ment.stop,
                                                        language=report.language)
                    users_robot_anno = Annotate.objects.filter(username__in=users1,ns_id = ns_robot, id_report=report,
                                                        start=ment, stop=ment.stop,
                                                        language=report.language).exclude(insertion_time = ins_time)
                    json_val['count'] = len(users_anno) + len(users_robot_anno)
                    json_val['mention'] = ment.mention_text
                    json_val['start'] = ment.start
                    json_val['stop'] = ment.stop
                    json_val['manual_annotators'] = []
                    json_val['robot_annotators'] = []
                    for el in users_anno:
                        if el.username_id not in json_val['manual_annotators']:
                            json_val['manual_annotators'].append(el.username_id)
                        if el.username_id not in json_val['users_list']:
                            json_val['users_list'].append(el.username_id)
                    for el in users_robot_anno:
                        if el.username_id not in json_val['robot_annotators']:
                            json_val['robot_annotators'].append(el.username_id)
                        if el.username_id not in json_val['users_list']:
                            json_val['users_list'].append(el.username_id)

                    if json_val['count'] > (json_val['total_gt'] / 2):
                        majority_gt['both'].append(json_val)

        elif action == 'concepts':
            # if mode == 'Human':
            users1 = User.objects.filter(username__in=users,ns_id=ns_human)
            concepts = Contains.objects.filter(username__in=users, ns_id=ns_human, id_report=report,
                                              language=report.language).distinct('concept_url', 'name')
            total_gt = GroundTruthLogFile.objects.filter(gt_type='concepts', ns_id=ns_human, id_report=report,
                                                         language=report.language,username__in=users1)
            # if len(concepts) == 0:
            #     json_val = {}
            #     json_val['total_gt'] = 0
            #     majority_gt['Human'].append(json_val)

            for el in concepts:
                json_val = {}
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                area = SemanticArea.objects.get(name=el.name_id)
                anno = Contains.objects.filter(username__in=users1, id_report=report,
                                               language=report.language, concept_url=concept, name=area,
                                               ns_id=ns_human)
                json_val['count'] = anno.count()
                json_val['total_gt'] = total_gt.count()
                json_val['concept_url'] = concept.concept_url
                json_val['concept_name'] = concept.name
                json_val['area'] = area.name
                json_val['users_list'] = []

                for ass in anno:
                    if ass.username_id not in json_val['users_list']:
                        json_val['users_list'].append(ass.username_id)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Human'].append(json_val)

            # if mode == 'Robot':
            users1 = User.objects.filter(username__in=users,ns_id=ns_robot)
            concepts = Contains.objects.filter(username__in=users, ns_id=ns_robot, id_report=report,
                                               language=report.language).distinct('concept_url', 'name')
            cursor.execute(
                "SELECT a.username FROM ground_truth_log_file AS a INNER JOIN ground_truth_log_file AS aa ON a.id_report = aa.id_report and a.gt_type = aa.gt_type and a.language = aa.language  WHERE aa.username=%s AND a.gt_type = %s AND a.ns_id = %s AND a.id_report = %s AND a.language = %s AND a.username IN %s AND a.insertion_time != aa.insertion_time",
                ['Robot_user', 'concepts', 'Robot', str(report.id_report), str(report.language),
                 tuple(users)])
            ans = cursor.fetchall()
            total_gt = len(ans)
            # json_val = {}
            # json_val['total_gt'] = total_gt
            # majority_gt['Robot'].append(json_val)
            for el in concepts:
                json_val = {}
                json_val['users_list'] = []
                ins_time = '0001-01-01 00:00:00.000000+00'
                ins_time_gt = '0001-01-01 00:00:00.000000+00'
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                area = SemanticArea.objects.get(name=el.name_id)

                robot_anno = Contains.objects.filter(username=agent, ns_id=ns_robot, id_report=report,concept_url=concept,
                                        name=area,language=report.language)
                robot_anno_gt = GroundTruthLogFile.objects.filter(username=agent,ns_id=ns_robot,id_report = report,language=report.language,gt_type='concepts')

                if robot_anno_gt.exists() and robot_anno_gt.count() == 1:
                    robot_anno_gt = robot_anno_gt.first()
                    ins_time_gt = robot_anno_gt.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')

                if robot_anno.exists() and robot_anno.count() == 1:
                    robot_anno = robot_anno.first()
                    ins_time = robot_anno.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')

                # total_gt1 = GroundTruthLogFile.objects.filter(username__in=users1,ns_id=ns_robot,id_report = report,language = report.language,gt_type='concepts').exclude(insertion_time = ins_time_gt)
                user_anno = Contains.objects.filter(username__in=users1, ns_id=ns_robot, id_report=report,concept_url = concept,name = area,
                                        language=report.language).exclude(insertion_time = ins_time)
                json_val['total_gt'] = total_gt
                json_val['count'] = user_anno.count()
                json_val['concept_url'] = concept.concept_url
                json_val['concept_name'] = concept.name
                json_val['area'] = area.name

                for el in user_anno:
                    if el.username_id not in json_val['users_list']:
                        json_val['users_list'].append(el.username_id)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Robot'].append(json_val)

            if mode == 'both':
                annotations = Contains.objects.filter(username__in=users1,id_report = report,language = report.language).distinct('concept_url', 'name')
                human_gt = GroundTruthLogFile.objects.filter(gt_type='concepts', ns_id=ns_human, id_report=report,
                                                             language=report.language, username__in=users1)
                rob_gt = GroundTruthLogFile.objects.get(gt_type = 'concepts',id_report = report,language = report.language,username=agent,ns_id=ns_robot)
                robot_gt = GroundTruthLogFile.objects.filter(gt_type='concepts', ns_id=ns_robot, id_report=report,
                                                             language=report.language, username__in=users1).exclude(insertion_time = rob_gt.insertion_time)
                # json_val = {}
                # json_val['total_human_gt'] = majority_gt['Human'][0]['total_gt']
                # json_val['total_robot_gt'] = majority_gt['Robot'][0]['total_gt']
                # majority_gt['both'].append(json_val)

                for el in annotations:
                    json_val = {}
                    json_val['users_list'] = []
                    json_val['total_human_gt'] = human_gt.count()
                    json_val['total_robot_gt'] = robot_gt.count()
                    json_val['total_gt'] = robot_gt.count() + human_gt.count()
                    ins_time = '0001-01-01 00:00:00.000000+00'
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    robot_anno = Contains.objects.filter(username=agent, ns_id=ns_robot, id_report=report, concept_url=concept,
                                                         name=area.name,
                                                         language=report.language)
                    if robot_anno.exists() and robot_anno.count() == 1:
                        robot_anno = robot_anno.first()
                        ins_time = robot_anno.insertion_time
                        if 'Robot_user' not in json_val['users_list']:
                            json_val['users_list'].append('Robot_user')

                    users_anno = Contains.objects.filter(username__in=users1,ns_id = ns_human, id_report=report,
                                                         concept_url=concept,
                                                         name=area.name,
                                                        language=report.language)
                    users_robot_anno = Contains.objects.filter(username__in=users1,ns_id = ns_robot, id_report=report,
                                                               concept_url=concept,
                                                               name=area.name,
                                                        language=report.language).exclude(insertion_time = ins_time)
                    json_val['count'] = len(users_anno) + len(users_robot_anno)
                    json_val['concept_url'] = concept.concept_url
                    json_val['concept_name'] = concept.name
                    json_val['area'] = area.name
                    json_val['manual_annotators'] = []
                    json_val['robot_annotators'] = []
                    for el in users_anno:
                        if el.username_id not in json_val['manual_annotators']:
                            json_val['manual_annotators'].append(el.username_id)
                        if el.username_id not in json_val['users_list']:
                            json_val['users_list'].append(el.username_id)
                    for el in users_robot_anno:
                        if el.username_id not in json_val['robot_annotators']:
                            json_val['robot_annotators'].append(el.username_id)
                        if el.username_id not in json_val['users_list']:
                            json_val['users_list'].append(el.username_id)
                    if json_val['count'] > (json_val['total_gt'] / 2):
                        majority_gt['both'].append(json_val)


        elif action == 'concept-mention':
            # if mode == 'Human':
            users1 = User.objects.filter(username__in=users, ns_id=ns_human)
            concepts = Linked.objects.filter(username__in=users, ns_id=ns_human, id_report=report,
                                               language=report.language).distinct('concept_url', 'name','start')
            total_gt = GroundTruthLogFile.objects.filter(gt_type='concept-mention', ns_id=ns_human, id_report=report,
                                                         language=report.language, username__in=users1)
            # if len(concepts) == 0:
            #     json_val = {}
            #     json_val['total_gt'] = 0
            #     majority_gt['Human'].append(json_val)

            for el in concepts:
                json_val = {}
                mention = Mention.objects.get(id_report = report, language = report.language, start=el.start_id, stop = el.stop)
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                area = SemanticArea.objects.get(name=el.name_id)
                anno = Contains.objects.filter(username__in=users1, id_report=report,
                                               language=report.language, concept_url=concept, name=area,
                                               ns_id=ns_human)
                json_val['count'] = anno.count()
                json_val['total_gt'] = total_gt.count()
                json_val['concept_url'] = concept.concept_url
                json_val['concept_name'] = concept.name
                json_val['area'] = area.name
                json_val['start'] = mention.start
                json_val['stop'] = mention.stop
                json_val['mention'] = mention.mention_text
                json_val['users_list'] = []

                for ass in anno:
                    if ass.username_id not in json_val['users_list']:
                        json_val['users_list'].append(ass.username_id)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Human'].append(json_val)

            # if mode == 'Robot':
            users1 = User.objects.filter(username__in=users, ns_id=ns_robot)
            concepts = Linked.objects.filter(username__in=users, ns_id=ns_robot, id_report=report,
                                               language=report.language).distinct('concept_url', 'name','start')
            cursor.execute(
                "SELECT a.username FROM ground_truth_log_file AS a INNER JOIN ground_truth_log_file AS aa ON a.id_report = aa.id_report and a.gt_type = aa.gt_type and a.language = aa.language  WHERE aa.username=%s AND a.gt_type = %s AND a.ns_id = %s AND a.id_report = %s AND a.language = %s AND a.username IN %s AND a.insertion_time != aa.insertion_time",
                ['Robot_user', 'concept-mention', 'Robot', str(report.id_report), str(report.language),
                 tuple(users)])
            ans = cursor.fetchall()
            total_gt = len(ans)
            # json_val = {}
            # json_val['total_gt'] = total_gt
            # majority_gt['Robot'].append(json_val)

            for el in concepts:
                json_val = {}
                json_val['users_list'] = []
                ins_time = '0001-01-01 00:00:00.000000+00'
                ins_time_gt = '0001-01-01 00:00:00.000000+00'
                concept = Concept.objects.get(concept_url=el.concept_url_id)
                area = SemanticArea.objects.get(name=el.name_id)
                mention = Mention.objects.get(id_report = report, language = report.language, start = el.start_id, stop = el.stop)

                robot_anno = Linked.objects.filter(username=agent, ns_id=ns_robot, id_report=report,
                                                     concept_url=concept,start = mention, stop = mention.stop,
                                                     name=area, language=report.language)
                robot_anno_gt = GroundTruthLogFile.objects.filter(username=agent,ns_id=ns_robot,id_report = report,language = report.language,gt_type='concept-mention')
                if robot_anno_gt.exists() and robot_anno_gt.count() == 1:
                    robot_anno_gt = robot_anno_gt.first()
                    ins_time_gt = robot_anno_gt.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')
                if robot_anno.exists() and robot_anno.count() == 1:
                    robot_anno = robot_anno.first()
                    ins_time = robot_anno.insertion_time
                    if 'Robot_user' not in json_val['users_list']:
                        json_val['users_list'].append('Robot_user')
                # total_gt = GroundTruthLogFile.objects.filter(username__in=users1, ns_id=ns_robot, id_report=report,
                #                                              language=report.language, gt_type='concept-mention').exclude(
                #     insertion_time=ins_time_gt)
                # print(total_gt.count())
                user_anno = Linked.objects.filter(username__in=users1, ns_id=ns_robot, id_report=report,
                                                    concept_url=concept,start = mention.start, stop = mention.stop,
                                                    language=report.language).exclude(insertion_time=ins_time)
                json_val['total_gt'] = total_gt
                json_val['count'] = user_anno.count()
                json_val['concept_url'] = concept.concept_url
                json_val['concept_name'] = concept.name
                json_val['area'] = area.name
                json_val['start'] = mention.start
                json_val['stop'] = mention.stop
                json_val['mention'] = mention.mention_text

                for el in user_anno:
                    if el.username_id not in json_val['users_list']:
                        json_val['users_list'].append(el.username_id)
                if json_val['count'] > (json_val['total_gt'] / 2):
                    majority_gt['Robot'].append(json_val)

            if mode == 'both':
                annotations = Linked.objects.filter(username__in=users1, id_report=report,
                                                      language=report.language).distinct('concept_url', 'name','start')
                human_gt = GroundTruthLogFile.objects.filter(gt_type='concept-mention', ns_id=ns_human, id_report=report,
                                                             language=report.language, username__in=users1)
                rob_gt = GroundTruthLogFile.objects.get(gt_type='concept-mention', id_report=report, language=report.language,
                                                        username=agent, ns_id=ns_robot)
                robot_gt = GroundTruthLogFile.objects.filter(gt_type='concept-mention', ns_id=ns_robot, id_report=report,
                                                             language=report.language, username__in=users1).exclude(
                    insertion_time=rob_gt.insertion_time)
                # if len(annotations) == 0:
                #     json_val = {}
                #     json_val['total_human_gt'] = 0
                #     json_val['total_robot_gt'] = 0
                #     majority_gt['both'].append(json_val)

                for el in annotations:
                    json_val = {}
                    json_val['users_list'] = []
                    json_val['total_human_gt'] = human_gt.count()
                    json_val['total_robot_gt'] = robot_gt.count()
                    json_val['total_gt'] = robot_gt.count() + human_gt.count()
                    ins_time = '0001-01-01 00:00:00.000000+00'
                    concept = Concept.objects.get(concept_url=el.concept_url_id)
                    area = SemanticArea.objects.get(name=el.name_id)
                    mention = Mention.objects.get(start = el.start_id, stop = el.stop, id_report= report,language = report.language)
                    robot_anno = Linked.objects.filter(username=agent, ns_id=ns_robot, id_report=report,
                                                         concept_url=concept,start = mention.start,stop = mention.stop,
                                                         name=area.name,
                                                         language=report.language)
                    if robot_anno.exists() and robot_anno.count() == 1:
                        robot_anno = robot_anno.first()
                        ins_time = robot_anno.insertion_time
                        if 'Robot_user' not in json_val['users_list']:
                            json_val['users_list'].append('Robot_user')

                    users_anno = Linked.objects.filter(username__in=users1, ns_id=ns_human, id_report=report,
                                                         concept_url=concept,start = mention.start,stop = mention.stop,
                                                         name=area.name,
                                                         language=report.language)
                    users_robot_anno = Linked.objects.filter(username__in=users1, ns_id=ns_robot, id_report=report,
                                                               concept_url=concept,start = mention.start,stop = mention.stop,
                                                               name=area.name,
                                                               language=report.language).exclude(
                        insertion_time=ins_time)
                    json_val['count'] = len(users_anno) + len(users_robot_anno)
                    json_val['concept_url'] = concept.concept_url
                    json_val['concept_name'] = concept.name
                    json_val['area'] = area.name
                    json_val['start'] = mention.start
                    json_val['stop'] = mention.stop
                    json_val['mention'] = mention.mention_text


                    json_val['manual_annotators'] = []
                    json_val['robot_annotators'] = []
                    for el in users_anno:
                        if el.username_id not in json_val['manual_annotators']:
                            json_val['manual_annotators'].append(el.username_id)
                        if el.username_id not in json_val['users_list']:
                            json_val['users_list'].append(el.username_id)
                    for el in users_robot_anno:
                        if el.username_id not in json_val['robot_annotators']:
                            json_val['robot_annotators'].append(el.username_id)
                        if el.username_id not in json_val['users_list']:
                            json_val['users_list'].append(el.username_id)
                    if json_val['count'] > (json_val['total_gt'] / 2):
                        majority_gt['both'].append(json_val)
        # print(majority_gt)
        return majority_gt
    except Exception as e:
        print(e)
        json_resp = {'error':e}
        return json_resp


def create_majority_json(users,reports,action,mode):

    """This method converts the object returned by create_majority_vote_gt into json"""

    final_json = {}
    norm = ''
    if action == 'concept-mention':
        final_json['action'] = 'linking'
    else:
        final_json['action'] = action
    if mode == 'both':
        norm = 'manual_and_auto'
    elif mode == 'Human':
        norm = 'Manual'
    elif mode == 'Robot':
        norm = 'Automatic'
    final_json['annotation_mode'] = norm
    final_json['chosen_annotators'] = users
    final_json['reports'] = []
    for report in reports:
        # print(report)
        rep = Report.objects.get(id_report = report['id_report'],language = report['language'])
        json_to_ret = {}
        gt_dict = create_majority_vote_gt(action,users,mode,rep)
        data = gt_dict[mode]
        json_to_ret['id_report'] = report['id_report']
        json_to_ret['usecase'] = report['usecase']
        json_to_ret['language'] = report['language']

        if action == 'labels':
            json_to_ret['labels_list'] = []
            for val in data:
                if int(val['count']) > int(val['total_gt'] / 2):
                    json_val = {}
                    json_to_ret['total_annotators'] = val['total_gt']
                    json_val['label'] = val['label']
                    json_val['annotators'] = val['users_list']
                    if 'Robot_user' in json_val['annotators']:
                        json_val['annotators'].remove('Robot_user')
                        json_to_ret['total_annotators'] -= 1
                    json_to_ret['labels_list'].append(json_val)

        elif action == 'mentions':
            json_to_ret['mentions_list'] = []
            for val in data:
                # print(val)
                json_to_ret['total_annotators'] = val['total_gt']
                if int(val['count']) > int(val['total_gt'] / 2):
                    json_val = {}

                    json_val['start'] = val['start']
                    json_val['stop'] = val['stop']
                    json_val['mention'] = val['mention']
                    json_val['annotators'] = val['users_list']
                    if 'Robot_user' in json_val['annotators']:
                        json_val['annotators'].remove('Robot_user')
                        json_to_ret['total_annotators'] -= 1
                    json_to_ret['mentions_list'].append(json_val)
        elif action == 'concepts':
            json_to_ret['concepts_list'] = []

            for val in data:
                json_to_ret['total_annotators'] = val['total_gt']
                if int(val['count']) > int(val['total_gt'] / 2):
                    json_val = {}

                    json_val['concept_url'] = val['concept_url']
                    json_val['concept_name'] = val['concept_name']
                    json_val['area'] = val['area']
                    json_val['annotators'] = val['users_list']
                    if 'Robot_user' in json_val['annotators']:
                        json_val['annotators'].remove('Robot_user')
                        json_to_ret['total_annotators'] -= 1
                    json_to_ret['concepts_list'].append(json_val)

        elif action == 'concept-mention':
            for val in data:
                json_to_ret['linking_list'] = []
                json_to_ret['total_annotators'] = val['total_gt']
                if int(val['count']) > int(val['total_gt'] / 2):
                    json_val = {}
                    json_val['concept_url'] = val['concept_url']
                    json_val['concept_name'] = val['concept_name']
                    json_val['area'] = val['area']
                    json_val['start'] = val['start']
                    json_val['stop'] = val['stop']
                    json_val['mention'] = val['mention']
                    json_val['annotators'] = val['users_list']
                    if 'Robot_user' in json_val['annotators']:
                        json_val['annotators'].remove('Robot_user')
                        json_to_ret['total_annotators'] -= 1
                    json_to_ret['linking_list'].append(json_val)

        final_json['reports'].append(json_to_ret)

    # print(final_json)
    return final_json

def create_majority_csv(users,reports,action,mode):

    """This method creates the majority vote ground truth in csv format"""

    row_list = []
    for report in reports:
        rep = Report.objects.get(id_report = report['id_report'],language = report['language'])
        gt_dict = create_majority_vote_gt(action, users, mode, rep)
        data = gt_dict[mode]
        for val in data:

            norm = ''
            row = []
            if mode == 'both':
                norm = 'manual_and_auto'
            elif mode == 'Human':
                norm = 'Manual'
            elif mode == 'Robot':
                norm = 'Automatic'
            row.append(norm)
            if action == 'concept-mention':
                row.append('linking')
            else:
                row.append(action)

            if 'Robot_user' in val['users_list']:
                val['users_list'].remove('Robot_user')
                val['total_gt'] = val['total_gt'] - 1
            row.append(rep.id_report)
            row.append(rep.language)
            row.append(rep.institute)
            row.append(rep.name_id)
            if action == 'labels':
                row.append(val['label'])
                row.append(', '.join(val['users_list']))
                row.append(val['total_gt'])
            elif action == 'mentions':
                row.append(val['start'])
                row.append(val['stop'])
                row.append(val['mention'])

                row.append(', '.join(val['users_list']))
                row.append(val['total_gt'])
            elif action == 'concepts':
                row.append(val['concept_url'])
                row.append(val['concept_name'])
                row.append(val['area'])
                row.append(', '.join(val['users_list']))
                row.append(val['total_gt'])
            elif action == 'concept-mention':
                row.append(val['start'])
                row.append(val['stop'])
                row.append(val['mention'])
                row.append(val['concept_name'])
                row.append(val['concept_url'])
                row.append(val['area'])
                row.append(', '.join(val['users_list']))
                row.append(val['total_gt'])
            row_list.append(row)
    return row_list

