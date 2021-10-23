import psycopg2
import csv
from MedTAG_sket_dock_App.utils import *
from bioc import *
from datetime import date

"""This file manages the creation of the files to be downloaded by the users"""


def generate_bioc(json_keys,json_keys_to_ann,username,action,language,usecase,institute,form,annotation_mode,report_type,batch):

    """This method creates the BioC files both XML and JSON depending on the language, usecase, institute chosen"""

    try:
        usec = UseCase.objects.get(name=usecase)
        batch_num = []
        if batch is None:
            b = Report.objects.filter(name=usec).values('batch')
            for el in b:
                if el['batch'] not in batch_num:
                    batch_num.append(el['batch'])
        else:
            batch_num.append(batch)
        writer = BioCXMLWriter()
        json_writer = BioCJSONWriter()
        writer.collection = BioCCollection()
        json_writer.collection = BioCCollection()
        collection = writer.collection
        collection1 = json_writer.collection
        today = str(date.today())
        collection.date = today
        collection.source = 'MEDTAG Collection'
        collection.put_infon('username', username)
        collection1.date = today
        collection1.source = 'MEDTAG Collection'
        collection1.put_infon('username', username)
        if action == 'mentions':
            collection.put_infon('annotation_type', 'mentions')
            collection.key = 'mentions.key'
            collection1.put_infon('annotation_type', 'mentions')
            collection1.key = 'mentions.key'

            with connection.cursor() as cursor:

                if report_type == 'reports':
                    if annotation_mode == 'Human':
                        cursor.execute(
                            "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.name = %s AND r.language = COALESCE(%s,r.language) AND r.institute = COALESCE(%s,r.institute) AND a.ns_id = %s AND r.batch = COALESCE(%s,r.batch) AND r.institute!=%s",
                            [str(username), str(usecase),(language),institute, str(annotation_mode), batch, 'PUBMED'])

                    elif annotation_mode == 'Robot':
                        cursor.execute(
                            "SELECT  DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language   INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and m.start = a.start and m.stop = a.stop  WHERE r.name = %s and  a.ns_id = %s and a.username = %s  and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE (%s,r.batch) AND r.institute = COALESCE(%s,r.institute) AND r.language = COALESCE(%s,r.language) AND r.institute != %s)",
                            [str(usecase), 'Robot', str(username), 'mentions', 'Robot','Robot_user',str(username), batch,institute,language, 'PUBMED'])


                    reports = cursor.fetchall()
                elif report_type == 'pubmed':
                    if annotation_mode == 'Human':
                        cursor.execute(
                            "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s AND a.ns_id = %s  AND r.batch = COALESCE(%s,r.batch) AND r.language = =%s",
                            [str(username), str('english'), str(usecase), str('PUBMED'), str(annotation_mode),
                             batch,'english'])
                    elif annotation_mode == 'Robot':
                        cursor.execute(
                            "SELECT  DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language  INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and m.start = a.start and m.stop = a.stop  WHERE r.name = %s and a.ns_id = %s and a.username = %s AND r.institute = %s and r.language = %s and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE(%s,r.batch) AND r.language = =%s  ",
                            [str(usecase), 'Robot', str(username), 'PUBMED', str(language), 'mentions',
                             'Robot',
                             'Robot_user',
                             str(username), batch,'english'])


                    reports = cursor.fetchall()
            documents = []
            # reports = Annotate.objects.filter(username=username).values('id_report','language').distinct()
            for couple in reports:
                document = ''
                report = Report.objects.get(name=couple[0], id_report=couple[1], institute=couple[3],
                                            language=couple[2])
                json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                ns_cur = NameSpace.objects.get(ns_id=annotation_mode)
                anno = Annotate.objects.filter(username=username, id_report=report,ns_id = ns_cur, language=report.language)
                document = BioCDocument()
                document.id = str(report.id_report)
                document.put_infon('usecase', report.name_id)
                document.put_infon('language', report.language)
                document.put_infon('institute', report.institute)

                annotations = []
                count = 0
                for el in anno:
                    mention = Mention.objects.get(start=el.start_id, stop=el.stop, id_report=report,
                                                  language=report.language)
                    json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                    annotation = BioCAnnotation()
                    annotation.id = str(count)

                    count = count + 1
                    loc_ann = BioCLocation()
                    loc_ann.offset = str(mention.start)
                    loc_ann.length = str(mention.stop - mention.start + 1)
                    annotation.add_location(loc_ann)
                    mention_text = mention.mention_text
                    mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)

                    annotation.text = mtext
                    couple = (annotation, mention.start, mention.stop)
                    annotations.append(couple)
                seen = []
                for key in json_keys_to_ann:
                    passage = BioCPassage()
                    passage.put_infon('section', key)
                    check = False

                    keys = json_dict['rep_string'].keys()
                    if key in keys:
                        if json_dict['rep_string'].get(key) != '':
                            # if json_dict['rep_string'].get(key) is not None and json_dict['rep_string'].get(key) != '':
                            passage.text = json_dict['rep_string'][key]['text']
                            start = str(json_dict['rep_string'][key]['start'])
                            passage.offset = start
                            for el in annotations:
                                if el not in seen:

                                    if int(el[1]) >= int(json_dict['rep_string'][key]['start']) and int(el[2]) <= int(
                                            json_dict['rep_string'][key]['end']):
                                        check = True
                                        passage.add_annotation(el[0])
                                        seen.append(el)
                            if check:
                                document.add_passage(passage)
                collection.add_document(document)
                collection1.add_document(document)
            print(writer)
            print(json_writer)

        elif action == 'concept-mention':
            collection.put_infon('annotation_type', 'linking')
            collection.key = 'linking.key'
            collection1.put_infon('annotation_type', 'linking')
            collection1.key = 'linking.key'

            with connection.cursor() as cursor:

                if report_type == 'reports':
                    if annotation_mode == 'Human':
                        cursor.execute(
                            "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.name = %s AND a.ns_id = %s  AND r.batch =COALESCE(%s,r.batch) AND r.institute=COALESCE(%s,r.institute) AND r.language = COALESCE(%s, r.language) AND r.institute != %s",
                            [str(username), str(usecase), str(annotation_mode), batch,institute,language,'PUBMED'])


                    elif annotation_mode == 'Robot':
                        cursor.execute(
                            "SELECT  DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and a.start = m.start and a.stop = m.stop INNER JOIN concept as c on c.concept_url = a.concept_url inner join semantic_area as s on s.name = a.name WHERE r.name = %s AND a.ns_id = %s and a.username = %s  and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s  AND r.batch = COALESCE(%s,r.batch) AND r.institute=COALESCE(%s,r.institute) AND r.language = COALESCE(%s,r.language) AND r.institute != %s)  ",
                            [str(usecase), 'Robot', str(username), 'concept-mention', 'Robot',
                             'Robot_user',
                             str(username), batch,institute,language, 'PUBMED'])


                    reports = cursor.fetchall()
                elif report_type == 'pubmed':
                    if language is not None and institute is not None and usecase is not None:
                        if annotation_mode == 'Human':
                            cursor.execute(
                            "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s AND a.ns_id = %s  AND r.batch IN %s",
                            [str(username), str('english'), str(usecase), str('PUBMED'),str(annotation_mode),tuple(batch_num)])
                        elif annotation_mode == 'Robot':
                            cursor.execute(
                                "SELECT  DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and a.start = m.start and a.stop = m.stop INNER JOIN concept as c on c.concept_url = a.concept_url inner join semantic_area as s on s.name = a.name WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = %s and r.language = %s and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s  AND r.batch IN %s)  ",
                                [str(usecase), 'Robot', str(username), str('PUBMED'), str(language), 'concept-mention', 'Robot',
                                 'Robot_user',
                                 str(username),tuple(batch_num)])

                    reports = cursor.fetchall()
            documents = []
            # reports = Annotate.objects.filter(username=username).values('id_report','language').distinct()
            for couple in reports:
                document = ''
                report = Report.objects.get(name = couple[0],id_report=couple[1],institute = couple[3], language=couple[2])
                json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                ns = NameSpace.objects.get(ns_id = annotation_mode)
                anno = Linked.objects.filter(username=username,ns_id = ns,id_report = report,language = report.language)
                document = BioCDocument()
                document.id = str(report.id_report)
                document.put_infon('usecase', report.name_id)
                document.put_infon('language', report.language)
                document.put_infon('institute', report.institute)

                annotations = []
                count = 0
                for el in anno:
                    mention = Mention.objects.get(start = el.start_id,stop = el.stop,id_report=report,language = report.language)
                    concept = Concept.objects.get(concept_url = el.concept_url_id)
                    json_dict = report_get_start_end(json_keys,json_keys_to_ann,report.id_report,report.language)
                    annotation = BioCAnnotation()
                    annotation.id = str(count)
                    annotation.put_infon('concept_name', concept.name)
                    annotation.put_infon('concept_url', concept.concept_url)
                    count = count+1
                    loc_ann = BioCLocation()
                    loc_ann.offset = str(mention.start)
                    loc_ann.length = str(mention.stop - mention.start + 1)
                    annotation.add_location(loc_ann)
                    mention_text = mention.mention_text
                    mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)

                    annotation.text = mtext
                    couple = (annotation,mention.start,mention.stop)
                    annotations.append(couple)
                seen = []
                for key in json_keys_to_ann:
                    passage = BioCPassage()
                    passage.put_infon('section', key)
                    check = False

                    keys = json_dict['rep_string'].keys()
                    if key in keys:
                        if json_dict['rep_string'].get(key) != '':
                    # if json_dict['rep_string'].get(key) is not None and json_dict['rep_string'].get(key) != '':
                            passage.text = json_dict['rep_string'][key]['text']
                            start = str(json_dict['rep_string'][key]['start'])
                            passage.offset = start
                            for el in annotations:
                                if el not in seen:
                                    # start1 = int(el[1])
                                    # start2 = int(json_dict['rep_string'][key]['start'])
                                    # stop1 = int(el[2])
                                    # stop2 = int(json_dict['rep_string'][key]['end'])
                                    if int(el[1]) >= int(json_dict['rep_string'][key]['start']) and int(el[2]) <= int(json_dict['rep_string'][key]['end']):
                                        check = True
                                        passage.add_annotation(el[0])
                                        seen.append(el)
                                    # passage.add_annotation(el[0])
                            if check:
                                document.add_passage(passage)
                collection.add_document(document)
                collection1.add_document(document)
            print(writer)




    except Exception as e:
        print(e)
        return False

    else:
        #os.remove(path1)
        if form == 'json':
            # os.remove(path1)
            return json_writer
        # return True
        return writer


def create_csv_to_download(report_type,annotation_mode,username,use,inst,lang,action,response,batch):

    """This method creates a csv to download depending on the language, the usecase, the institute chosen."""

    usecase = UseCase.objects.get(name=use)
    batch_num = []
    if batch is None:
        b = Report.objects.filter(name=usecase).values('batch')
        for el in b:
            if el['batch'] not in batch_num:
                batch_num.append(el['batch'])
    else:
        batch_num.append(batch)

    row_list = []
    if action == 'labels':
        row_list.append(['username', 'annotation_mode','id_report', 'language','batch', 'institute', 'usecase', 'label'])
    elif action == 'mentions':
        row_list.append(['username','annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'start','stop','mention_text'])
    elif action == 'concept-mention':
        row_list.append(['username','annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'start', 'stop', 'mention_text','concept_name','concept_url','area'])
    elif action == 'concepts':
        row_list.append(['username','annotation_mode', 'id_report', 'language','batch', 'institute', 'usecase', 'concept_url','concept_name','area'])
    try:
        if report_type == 'reports':
            with connection.cursor() as cursor:
                # if use is not None and lang is not None and inst is not None:
                if annotation_mode == 'Human':
                    if action == 'labels':
                       cursor.execute(
                            "SELECT  DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN associate as aa on aa.id_report = a.id_report and aa.language = a.language and a.label = aa.label and aa.ns_id = a.ns_id  and aa.seq_number = a.seq_number WHERE a.username = %s AND r.language = COALESCE(%s,r.language) AND r.name = %s AND r.institute = COALESCE(%s,r.institute) AND a.ns_id = %s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s",
                            [str(username),(lang), str(use), (inst),str(annotation_mode),(batch),'PUBMED'])
                    if action == 'mentions':
                        cursor.execute(
                            "SELECT  DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = COALESCE(%s,r.language) AND r.name = %s AND r.institute = COALESCE(%s,r.institute) AND a.ns_id = %s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s",
                            [str(username),(lang), str(use), (inst),str(annotation_mode),(batch),'PUBMED'])
                    if action == 'concepts':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.language = COALESCE(%s,r.language) AND r.name = %s AND r.institute = COALESCE(%s,r.institute) AND a.ns_id = %s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s",
                            [str(username),(lang), str(use), (inst),str(annotation_mode),(batch),'PUBMED'])
                    if action == 'concept-mention':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = COALESCE(%s,r.language) AND r.name = %s AND r.institute = COALESCE(%s,r.institute) AND a.ns_id = %s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s",
                            [str(username),(lang), str(use), (inst),str(annotation_mode),(batch),'PUBMED'])
                elif annotation_mode == 'Robot':
                    if action == 'labels':

                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = COALESCE(%s,r.institute) and r.language = COALESCE(%s,r.language) and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s)  ",
                            [str(use), 'Robot', str(username), (inst), (lang), 'labels', 'Robot', 'Robot_user',
                             str(username), batch, 'PUBMED'])
                        # cursor.execute(
                        #     "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = COALESCE(%s,r.institute) and r.language = COALESCE(%s,r.language) and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s)  ",
                        #     [str(use), 'Robot', str(username), str(inst), str(lang), 'labels', 'Robot', 'Robot_user',
                        #      str(username), batch, 'PUBMED'])

                    if action == 'mentions':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language  INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and m.start = a.start and m.stop = a.stop  WHERE r.name = %s and a.ns_id = %s and a.username = %s AND r.institute = COALESCE(%s,r.institute) and r.language = COALESCE(%s,r.language) and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s)  ",
                            [str(use),'Robot', str(username), (inst), (lang), 'mentions', 'Robot', 'Robot_user',
                             str(username),batch,'PUBMED'])

                    if action == 'concepts':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.concept_url,c.name,a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report AND r.language = a.language  INNER JOIN concept as c on c.concept_url = a.concept_url INNER JOIN semantic_area as s on a.name = s.name WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = COALESCE(%s,r.institute) and r.language = COALESCE(%s,r.language) and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s)  ",
                            [str(use),'Robot', str(username), (inst), (lang), 'concepts', 'Robot', 'Robot_user',
                             str(username),batch,'PUBMED'])

                    if action == 'concept-mention':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and a.start = m.start and a.stop = m.stop INNER JOIN concept as c on c.concept_url = a.concept_url inner join semantic_area as s on s.name = a.name WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = COALESCE(%s,r.institute) and r.language = COALESCE(%s,r.language) and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch = COALESCE(%s,r.batch) AND r.institute != %s)  ",
                            [str(use),'Robot', str(username), (inst), (lang), 'concept-mention', 'Robot', 'Robot_user',
                             str(username),batch,'PUBMED'])


                reports = cursor.fetchall()
                reports = sorted(reports, key=lambda x: x[1])

                for el in reports:
                    row = list(el)
                    if row[1] == 'Human':
                        row[1] = 'Manual'
                    else:
                        row[1] = 'Automatic'

                    if action == 'mentions' or action == 'concept-mention':
                        row[9] = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', row[9])
                    row_list.append(row)

        elif report_type == 'pubmed':
            with connection.cursor() as cursor:
                # if use is not None and lang is not None and inst is not None:
                if annotation_mode == 'Human':
                    if action == 'labels':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s AND a.ns_id = %s AND r.batch =COALESCE(%s,r.batch)",
                            [str(username), 'english', str(use), 'PUBMED','Human',batch])
                    if action == 'mentions':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s AND a.ns_id = %s AND r.batch =COALESCE(%s,r.batch)",
                            [str(username), 'english', str(use), 'PUBMED','Human',batch])
                    if action == 'concepts':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s AND a.ns_id = %s AND r.batch =COALESCE(%s,r.batch)",
                            [str(username), 'english', str(use), 'PUBMED','Human',batch])
                    if action == 'concept-mention':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s AND a.ns_id = %s AND r.batch =COALESCE(%s,r.batch)",
                            [str(username), 'english', str(use), 'PUBMED','Human',batch])
                elif annotation_mode == 'Robot':
                    if action == 'labels':
                        cursor.execute(
                            "SELECT  a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language  WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = %s and r.language = %s and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch =COALESCE(%s,r.batch))  ",
                            [str(use), 'Robot', str(username), 'PUBMED', 'english', 'labels', 'Robot',
                             'Robot_user', str(username),batch])

                    if action == 'mentions':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language  INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and m.start = a.start and m.stop = a.stop  WHERE r.name = %s and  a.ns_id = %s and a.username = %s AND r.institute = %s and r.language = %s and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch =COALESCE(%s,r.batch))  ",
                            [str(use), 'Robot', str(username), str(inst), str(lang), 'mentions', 'Robot',
                             'Robot_user',str(username),batch])

                    if action == 'concepts':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.concept_url,c.name,a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c on c.concept_url = a.concept_url INNER JOIN semantic_area as s on a.name = s.name WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = %s and r.language = %s and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch =COALESCE(%s,r.batch))  ",
                            [str(use), 'Robot', str(username), str(inst), str(lang), 'concepts', 'Robot',
                             'Robot_user',
                             str(username),batch])

                    if action == 'concept-mention':
                        cursor.execute(
                            "SELECT DISTINCT a.username,a.ns_id,r.id_report,r.language,r.batch,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention as m on m.id_report = a.id_report and m.language = a.language and a.start = m.start and a.stop = m.stop INNER JOIN concept as c on c.concept_url = a.concept_url inner join semantic_area as s on s.name = a.name WHERE r.name = %s AND a.ns_id = %s and a.username = %s AND r.institute = %s and r.language = %s and (a.id_report,a.language) IN (select g.id_report,g.language FROM ground_truth_log_file as g inner join ground_truth_log_file as gg on g.id_report = gg.id_report and g.language = gg.language and g.gt_type = gg.gt_type and g.ns_id = gg.ns_id where g.gt_type = %s and g.ns_id = %s and gg.insertion_time != g.insertion_time and gg.username = %s and g.username =%s AND r.batch =COALESCE(%s,r.batch))  ",
                            [str(use), 'Robot', str(username), str(inst), str(lang), 'concept-mention', 'Robot',
                             'Robot_user',
                             str(username),batch])

                reports = cursor.fetchall()
                reports = sorted(reports, key=lambda x: x[1])

                for el in reports:
                    row = list(el)
                    if row[1] == 'Human':
                        row[1] = 'Manual'
                    else:
                        row[1] = 'Automatic'

                    if action == 'mentions' or action == 'concept-mention':
                        row[9] = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', row[9])
                    row_list.append(row)

    except Exception as e:
        print(e)
        return False
    else:

        writer = csv.writer(response)
        writer.writerows(row_list)
        return response

def create_json_to_download(report_type,action,username,use,annotation_mode = None,inst = None,lang = None,all = None,batch = None):
    json_resp = {}
    #modified 22/10

    if all != 'all' and action != None and action != '':
        json_resp['action'] = action
        if action == 'concept-mention':
            json_resp['action'] = 'linking'

    if all == 'all':
        json_resp['groundtruths'] = {}
        types = ['labels','mentions','concepts','concept-mention']
        json_resp_add = {}

        for typ in types:
            a = typ
            if typ == 'concept-mention':
                a = 'linking'
            b = a + '_ground_truths'
            json_resp_add[b] = []

            gt = GroundTruthLogFile.objects.filter(username=username,gt_type = typ)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']
                gt_json['id_report_hashed'] = gt_json['id_report']
                del gt_json['id_report']
                if 'id_report_not_hashed' in gt_json.keys():
                    gt_json['id_report'] = gt_json['id_report_not_hashed']
                json_resp_add[b].append(gt_json)
        json_resp['groundtruths'] = json_resp_add
        return json_resp

    cursor = connection.cursor()
    usecase = UseCase.objects.get(name=use)
    batch_num = []
    if batch is None:
        b = Report.objects.filter(name=usecase).values('batch')
        for el in b:
            if el['batch'] not in batch_num:
                batch_num.append(el['batch'])
    else:
        batch_num.append(batch)

    json_resp['groundtruths'] = []
    json_resp['username'] = username
    json_resp['usecase'] = use
    if annotation_mode == 'Human':
        json_resp['annotation_mode'] = 'Manual'
    else:
        json_resp['annotation_mode'] = 'Automatic'

    if report_type == 'reports':

        if annotation_mode != 'both':
            cursor.execute(
                "SELECT DISTINCT r.id_report,r.language,r.institute FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND g.language = r.language WHERE gt_type = %s AND r.name = %s AND g.ns_id = %s AND r.language = COALESCE(%s, r.language) AND r.institute = COALESCE(%s,r.institute) AND institute != %s AND r.batch = COALESCE(%s,r.batch)",
                [str(action), str(use), str(annotation_mode),lang, inst, 'PUBMED',batch])
            if annotation_mode == 'Robot':
                cursor.execute(
                    "SELECT DISTINCT r.id_report,r.language,r.institute FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND g.language = r.language inner join ground_truth_log_file as gg on gg.id_report = g.id_report and gg.language = g.language and gg.gt_type = g.gt_type and gg.ns_id = g.ns_id WHERE gg.insertion_time != g.insertion_time and g.gt_type = %s AND r.name = %s AND g.ns_id = %s AND r.language = COALESCE(%s, r.language) AND r.institute = COALESCE(%s,r.institute) AND institute != %s and g.username != %s and gg.username = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(action), str(use), str(annotation_mode),lang,inst, 'PUBMED', 'Robot_user', 'Robot_user',batch])

        ids = cursor.fetchall()
        id_rep = []
        for el in ids:
            if el[0] not in id_rep:
                id_rep.append(el[0])

        for el in ids:
            json_val = {}
            json_val['id_report'] = el[0]
            json_val['language'] = el[1]
            json_val['institute'] = el[2]
            if action == 'labels':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.label FROM associate AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND g.username = %s AND g.ns_id = %s  AND r.language = COALESCE(%s, r.language) AND r.institute = COALESCE(%s,r.institute) AND institute != %s AND r.id_report = %s AND r.language = %s AND r.institute = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username),str(annotation_mode),lang,inst,'PUBMED',str(el[0]),str(el[1]),str(el[2]),batch])
                ans = cursor.fetchall()
                json_val['labels'] = []
                for el in ans:
                    json_lab = {}

                    json_lab['label'] = el[4]
                    json_val['labels'].append(json_lab)
                json_resp['groundtruths'].append(json_val)

            if action == 'mentions':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.start,g.stop,m.mention_text FROM annotate AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language INNER JOIN mention AS m ON m.id_report = g.id_report AND g.language = m.language AND m.start = g.start AND m.stop = g.stop WHERE r.name = %s AND g.username = %s AND g.ns_id = %s  AND r.language = COALESCE(%s, r.language) AND r.institute = COALESCE(%s,r.institute) AND institute != %s AND r.id_report = %s  AND r.language = %s AND r.institute = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username),str(annotation_mode),lang,inst,'PUBMED',str(el[0]),str(el[1]),str(el[2]),batch])
                ans = cursor.fetchall()
                json_val['mentions'] = []
                for el in ans:
                    json_ment = {}

                    json_ment['start'] = el[4]
                    json_ment['stop'] = el[5]
                    json_ment['mention_text'] = el[6]
                    json_val['mentions'].append(json_ment)
                json_resp['groundtruths'].append(json_val)

            if action == 'concept-mention':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.start,g.stop,m.mention_text,g.name,g.concept_url,c.name FROM linked AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language INNER JOIN  concept AS c ON c.concept_url = g.concept_url INNER JOIN mention AS m ON m.id_report = r.id_report AND m.language = r.language AND m.start = g.start AND g.stop = m.stop WHERE r.name = %s AND g.username = %s AND g.ns_id = %s  AND r.language = COALESCE(%s, r.language) AND r.institute = COALESCE(%s,r.institute) AND institute != %s AND r.id_report = %s  AND r.language = %s AND r.institute = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username),str(annotation_mode),lang,inst,'PUBMED',str(el[0]),str(el[1]),str(el[2]),batch])
                ans = cursor.fetchall()
                json_val['linking'] = []
                for el in ans:
                    json_link = {}
                    json_link['start'] = el[4]
                    json_link['stop'] = el[5]
                    json_link['mention_text'] = el[6]
                    json_link['area'] = el[7]
                    json_link['concept_url'] = el[8]
                    json_link['concept_name'] = el[9]
                    json_val['linking'].append(json_link)
                json_resp['groundtruths'].append(json_val)
            if action == 'concepts':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.name,g.concept_url,c.name FROM contains AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language INNER JOIN  concept AS c ON c.concept_url = g.concept_url WHERE r.name = %s AND g.username = %s AND g.ns_id = %s AND r.language = COALESCE(%s, r.language) AND r.institute = COALESCE(%s,r.institute) AND institute != %s AND r.id_report = %s  AND r.language = %s AND r.institute = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username),str(annotation_mode),lang,inst,'PUBMED',str(el[0]),str(el[1]),str(el[2]),batch])
                ans = cursor.fetchall()
                json_val['concepts'] = []
                for el in ans:
                    json_conc = {}


                    json_conc['area'] = el[4]
                    json_conc['concept_url'] = el[5]
                    json_conc['concept_name'] = el[6]
                    json_val['concepts'].append(json_conc)
                json_resp['groundtruths'].append(json_val)


    elif report_type == 'pubmed':
        cursor.execute(
            "SELECT DISTINCT r.id_report,r.language,r.institute FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND g.language = r.language WHERE gt_type = %s AND r.name = %s AND g.ns_id = %s AND institute = %s and r.language = %s AND r.batch = COALESCE(%s,r.batch)",
            [str(action), str(use), str(annotation_mode), str(lang), str(inst),batch])
        if annotation_mode == 'Robot':
            cursor.execute(
                "SELECT DISTINCT r.id_report,r.language,r.institute FROM report AS r INNER JOIN ground_truth_log_file AS g ON r.id_report = g.id_report AND g.language = r.language inner join ground_truth_log_file as gg on gg.id_report = g.id_report and gg.language = g.language and gg.gt_type = g.gt_type and gg.ns_id = g.ns_id WHERE gg.insertion_time != g.insertion_time and g.gt_type = %s AND r.name = %s AND g.ns_id = %s AND institute = %s and r.language = %s and g.username != %s and gg.username = %s AND r.batch = COALESCE(%s,r.batch)",
                [str(action), str(use), str(annotation_mode), str(lang), str(inst), 'Robot_user', 'Robot_user',batch])
        ids = cursor.fetchall()
        id_rep = []
        for el in ids:
            if el[0] not in id_rep:
                id_rep.append(el[0])

        json_resp['institute'] = inst
        json_resp['language'] = lang
        for el in ids:
            json_val = {}
            json_val['id_report'] = el[0]

            if action == 'labels':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.label FROM associate AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language WHERE r.name = %s AND g.username = %s AND g.ns_id = %s AND r.language = %s AND r.institute = %s AND r.id_report = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username), str(annotation_mode), str(lang), str(inst), str(el[0]),batch])
                ans = cursor.fetchall()
                json_val['labels'] = []
                for el in ans:
                    json_lab = {}
                    json_lab['label'] = el[4]
                    json_val['labels'].append(json_lab)
                json_resp['groundtruths'].append(json_val)

            if action == 'mentions':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.start,g.stop,m.mention_text FROM annotate AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language INNER JOIN mention AS m ON m.id_report = g.id_report AND g.language = m.language AND m.start = g.start AND m.stop = g.stop WHERE r.name = %s AND g.username = %s AND g.ns_id = %s AND r.language = %s AND r.institute = %s AND r.id_report = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username), str(annotation_mode), str(lang), str(inst), str(el[0]),batch])
                ans = cursor.fetchall()
                json_val['mentions'] = []
                for el in ans:
                    json_ment = {}

                    json_ment['start'] = el[4]
                    json_ment['stop'] = el[5]
                    json_ment['mention_text'] = el[6]
                    json_val['mentions'].append(json_ment)
                json_resp['groundtruths'].append(json_val)

            if action == 'concept-mention':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.start,g.stop,m.mention_text,g.name,g.concept_url,c.name FROM linked AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language INNER JOIN  concept AS c ON c.concept_url = g.concept_url INNER JOIN mention AS m ON m.id_report = r.id_report AND m.language = r.language  AND m.start = g.start AND g.stop = m.stop WHERE r.name = %s AND g.username = %s AND g.ns_id = %s AND r.language = %s AND r.institute = %s AND r.id_report = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username), str(annotation_mode), str(lang), str(inst), str(el[0]),batch])
                ans = cursor.fetchall()
                json_val['linking'] = []
                for el in ans:
                    json_ass = {}

                    json_ass['start'] = el[4]
                    json_ass['stop'] = el[5]
                    json_ass['mention_text'] = el[6]
                    json_ass['area'] = el[7]
                    json_ass['concept_url'] = el[8]
                    json_ass['concept_name'] = el[9]
                    json_val['linking'].append(json_ass)
                json_resp['groundtruths'].append(json_val)

            if action == 'concepts':
                cursor.execute(
                    "SELECT r.id_report,r.language,r.institute,g.ns_id,g.name,g.concept_url,c.name FROM contains AS g INNER JOIN report AS r ON r.id_report = g.id_report AND r.language = g.language INNER JOIN  concept AS c ON c.concept_url = g.concept_url WHERE r.name = %s AND g.username = %s AND g.ns_id = %s AND r.language = %s AND r.institute = %s AND r.id_report = %s AND r.batch = COALESCE(%s,r.batch)",
                    [str(use), str(username), str(annotation_mode), str(lang), str(inst), str(el[0]),batch])
                ans = cursor.fetchall()
                json_val['concepts'] = []
                for el in ans:
                    json_conc = {}

                    json_conc['area'] = el[4]
                    json_conc['concept_url'] = el[5]
                    json_conc['concept_name'] = el[6]
                    json_val['concepts'].append(json_conc)
                json_resp['groundtruths'].append(json_val)


    # print(json_resp)
    return json_resp


from MedTAG_sket_dock_App.utils_majority_vote import *
def download_majority_gt(chosen_users,report_list,action,mode,format,response = None):
    if format == 'json':
        json_to_ret = create_majority_json(chosen_users,report_list,action,mode)
        return json_to_ret
    elif format == 'csv':
        row_list = []
        if action == 'labels':
            row_list.append([ 'annotation_mode','action', 'id_report', 'language', 'institute', 'usecase', 'label','total_human_annotations','total_robot_annotations'])

        elif action == 'mentions':
            row_list.append(
                    ['annotation_mode','action', 'id_report', 'language', 'institute', 'usecase', 'start', 'stop',
                     'mention_text','mention_annotators','total_human_annotations','total_robot_annotations'])

        elif action == 'concept-mention':
            row_list.append(
                ['annotation_mode','action', 'id_report', 'language', 'institute', 'usecase', 'start', 'stop',
                 'mention_text','concept_name', 'concept_url', 'area','total_human_annotations','total_robot_annotations'])


        elif action == 'concepts':
            row_list.append(
                ['annotation_mode','action', 'id_report', 'language', 'institute', 'usecase', 'concept_url',
                 'concept_name', 'area','total_human_annotations','total_robot_annotations'])

        try:
            # for report in report_list:

            row_list.extend(create_majority_csv(chosen_users,report_list,action,mode))
        except Exception as e:
            print(e)
            return False
        else:

            writer = csv.writer(response)
            writer.writerows(row_list)
            return response

    elif format.startswith('bioc'):
        ret = True
        try:
            writer = BioCXMLWriter()
            json_writer = BioCJSONWriter()
            writer.collection = BioCCollection()
            json_writer.collection = BioCCollection()
            collection = writer.collection
            collection1 = json_writer.collection
            today = str(date.today())
            collection.date = today
            collection.source = 'MEDTAG Collection'
            collection.put_infon('gt_type', 'MAJORITY VOTE')
            collection1.date = today
            collection1.source = 'MEDTAG Collection'
            collection1.put_infon('gt_type', 'MAJORITY VOTE')
            if action == 'mentions':
                collection.put_infon('annotation_type', 'mentions')
                collection.key = 'mentions.key'
                collection1.put_infon('annotation_type', 'mentions')
                collection1.key = 'mentions.key'
                for rep in report_list:
                    report = Report.objects.get(id_report=rep['id_report'],language=rep['language'])
                    data = get_fields_from_json()
                    json_keys_to_display_human = data['fields']
                    json_keys_to_display_human.extend(['authors', 'volume', 'journal', 'year'])
                    json_keys_to_ann_human = data['fields_to_ann']
                    json_keys_to_ann_human.extend(['abstract', 'title'])
                    json_keys_to_display_human = list(set(json_keys_to_display_human))
                    json_keys_to_ann_human = list(set(json_keys_to_ann_human))
                    json_keys_to_ann_robot = []
                    if mode == 'Robot':
                        workpath = os.path.dirname(
                            os.path.abspath(__file__))  # Returns the Path your .py file is in
                        with open(os.path.join(workpath,
                                               './automatic_annotation/auto_fields/auto_fields.json')) as out:
                            data = json.load(out)
                            json_keys_to_ann_robot = data['extract_fields'][report.name.name]
                            json_keys_to_ann_robot.append('abstract')
                            json_keys_to_ann_robot.append('title')
                            json_keys_to_ann_robot = list(set(json_keys_to_ann_robot))

                    json_keys = []
                    json_keys_to_ann = []
                    if mode == 'Human':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_human))
                        json_keys_to_ann = json_keys_to_ann_human
                    elif mode == 'Robot':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_robot))
                        json_keys_to_ann = json_keys_to_ann_robot
                    elif mode == 'both':
                        json_keys = list(
                            set(json_keys_to_display_human + json_keys_to_ann_robot + json_keys_to_ann_human))
                        json_keys_to_ann = list(set(json_keys_to_ann_robot + json_keys_to_ann_human))

                    json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                    document = BioCDocument()
                    document.id = str(report.id_report)
                    document.put_infon('usecase', report.name_id)
                    document.put_infon('language', report.language)
                    document.put_infon('institute', report.institute)
                    gt_dict = create_majority_vote_gt(action, chosen_users, mode, report)

                    annotations = []
                    count = 0
                    for val in gt_dict[mode]:
                        annotation = BioCAnnotation()
                        annotation.id = str(count)
                        count = count + 1
                        loc_ann = BioCLocation()
                        loc_ann.offset = str(val['start'])
                        loc_ann.length = str(val['stop'] - val['start'] + 1)
                        annotation.add_location(loc_ann)
                        mention_text = val['mention']
                        mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)

                        annotation.text = mtext
                        couple = (annotation, val['start'], val['stop'])
                        annotations.append(couple)

                    seen = []
                    for key in json_keys_to_ann:
                        passage = BioCPassage()
                        passage.put_infon('section', key)
                        check = False
                        keys = json_dict['rep_string'].keys()
                        if key in keys:
                            if json_dict['rep_string'].get(key) != '':
                                passage.text = json_dict['rep_string'][key]['text']
                                start = str(json_dict['rep_string'][key]['start'])
                                passage.offset = (start)
                                for el in annotations:
                                    if el not in seen:

                                        if int(el[1]) >= int(json_dict['rep_string'][key]['start']) and int(
                                                el[2]) <= int(json_dict['rep_string'][key]['end']):
                                            check = True
                                            passage.add_annotation(el[0])
                                            seen.append(el)
                                if check:
                                    document.add_passage(passage)
                    collection.add_document(document)
                    collection1.add_document(document)

            elif action == 'concept-mention':
                collection.put_infon('annotation_type', 'linking')
                collection.key = 'linking.key'
                collection1.put_infon('annotation_type', 'linking')
                collection1.key = 'linking.key'

                for rep in report_list:
                    report = Report.objects.get(id_report=rep['id_report'],
                                                language=rep['language'])
                    data = get_fields_from_json()
                    json_keys_to_display_human = data['fields']
                    json_keys_to_display_human.extend(['authors', 'volume', 'journal', 'year'])
                    json_keys_to_ann_human = data['fields_to_ann']
                    json_keys_to_ann_human.extend(['abstract', 'title'])
                    json_keys_to_display_human = list(set(json_keys_to_display_human))
                    json_keys_to_ann_human = list(set(json_keys_to_ann_human))
                    json_keys_to_ann_robot = []
                    if mode == 'Robot':
                        workpath = os.path.dirname(
                            os.path.abspath(__file__))  # Returns the Path your .py file is in
                        with open(os.path.join(workpath,
                                               './automatic_annotation/auto_fields/auto_fields.json')) as out:
                            data = json.load(out)
                            json_keys_to_ann_robot = data['extract_fields'][report.name.name]
                            json_keys_to_ann_robot.append('abstract')
                            json_keys_to_ann_robot.append('title')
                            json_keys_to_ann_robot = list(set(json_keys_to_ann_robot))

                    json_keys = []
                    json_keys_to_ann = []
                    if mode == 'Human':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_human))
                        json_keys_to_ann = json_keys_to_ann_human
                    elif mode == 'Robot':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_robot))
                        json_keys_to_ann = json_keys_to_ann_robot
                    elif mode == 'both':
                        json_keys = list(
                            set(json_keys_to_display_human + json_keys_to_ann_robot + json_keys_to_ann_human))
                        json_keys_to_ann = list(set(json_keys_to_ann_robot + json_keys_to_ann_human))
                    json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                    document = BioCDocument()
                    document.id = str(report.id_report)
                    document.put_infon('usecase', report.name_id)
                    document.put_infon('language', report.language)
                    document.put_infon('institute', report.institute)
                    gt_dict = create_majority_vote_gt(action, chosen_users, mode, report)

                    annotations = []
                    count = 0
                    maj_annotations = []
                    for val in gt_dict[mode]:
                        data = get_fields_from_json()
                        json_keys_to_display = data['fields']
                        json_keys_to_ann = data['fields_to_ann']

                        json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)

                        annotation = BioCAnnotation()
                        annotation.id = str(count)
                        annotation.put_infon('concept_name', val['concept_name'])
                        annotation.put_infon('concept_url', val['concept_url'])
                        count = count + 1
                        loc_ann = BioCLocation()
                        loc_ann.offset = str(val['start'])
                        loc_ann.length = str(val['stop']- val['start'] + 1)
                        annotation.add_location(loc_ann)
                        mention_text = val['mention']
                        mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)

                        annotation.text = mtext
                        couple = (annotation, val['start'], val['stop'])
                        annotations.append(couple)

                    seen = []
                    for key in json_keys_to_ann:
                        passage = BioCPassage()
                        passage.put_infon('section', key)
                        check = False

                        keys = json_dict['rep_string'].keys()
                        if key in keys:
                            if json_dict['rep_string'].get(key) != '':
                                # if json_dict['rep_string'].get(key) is not None and json_dict['rep_string'].get(key) != '':
                                passage.text = json_dict['rep_string'][key]['text']
                                start = str(json_dict['rep_string'][key]['start'])
                                passage.offset = (start)
                                for el in annotations:
                                    if el not in seen:
                                        if int(el[1]) >= int(json_dict['rep_string'][key]['start']) and int(
                                                el[2]) <= int(json_dict['rep_string'][key]['end']):
                                            check = True
                                            passage.add_annotation(el[0])
                                            seen.append(el)
                                if check:
                                    document.add_passage(passage)
                    collection.add_document(document)
                    collection1.add_document(document)
                    # documents.append(document)

            # workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            # path = os.path.join(workpath, './static/BioC/BioC.dtd')
            # path1 = os.path.join(workpath, './static/BioC/to_download.xml')
            # print(writer.collection)
            #
            # writer.write(path1)
            # print(writer)

            # dtd_file = path
            # xml_reader = BioCXMLReader(path1, dtd_valid_file=dtd_file)
            # xml_reader.read()
            # if format.endswith('json'):
            #     json_writer = BioCJSONWriter()
            #     json_writer.collection = xml_reader.collection


        except Exception as e:
            print(e)
            return False

        else:
            ret = False
            #os.remove(path1)
            if format.endswith('json'):
                # os.remove(path1)
                return json_writer
            return writer

from itertools import chain
def download_report_gt(report_list,action,mode=None,format = None,response = None):

    """This method creates the files to download from the reports table accessible only by the admin."""
    cursor = connection.cursor()
    if format == 'json':
        json_resp = {}
        json_resp['action'] = action
        if mode == 'Robot':
            json_resp['annotation_mode'] = 'Automatic'
        elif mode =='Human':
            json_resp['annotation_mode'] = 'Manual'
        elif mode == 'both':
            json_resp['annotation_mode'] = 'Manual_and_Automatic'

        json_resp['ground_truth_list'] = []
        for report in report_list:
            rep = Report.objects.get(id_report = report['id_report'],language = report['language'])

            ns_id_human = NameSpace.objects.get(ns_id = 'Human')
            gt_human = GroundTruthLogFile.objects.filter(id_report = rep,language = rep.language,gt_type=action,ns_id = ns_id_human)

            ns_id_robot = NameSpace.objects.get(ns_id = 'Robot')
            agent = User.objects.get(username = 'Robot_user',ns_id = ns_id_robot)
            gt_agent = GroundTruthLogFile.objects.filter(username = agent,id_report = rep,language = rep.language,gt_type=action,ns_id = ns_id_robot)
            ins_arr = []
            for el in gt_agent:
                ins_arr.append(el.insertion_time)

            gt_list = GroundTruthLogFile.objects.filter(id_report = rep,language = rep.language,gt_type=action,ns_id = ns_id_robot).exclude(insertion_time__in=ins_arr)

            if mode == 'both':
                gt = chain(gt_human,gt_list)
            elif mode == 'Human':
                gt = gt_human
            elif mode == 'Robot':
                gt = gt_list

            for el in gt:
                if el.username_id != 'Robot_user':
                    gt_j = el.gt_json
                    if mode != 'both':
                        del gt_j['mode']
                    json_resp['ground_truth_list'].append(el.gt_json)

        return json_resp

    elif format == 'csv':
        row_list = []
        if action == 'labels':
            row_list.append(['username', 'user_type', 'id_report', 'language', 'institute', 'usecase', 'label'])

        elif action == 'mentions':
            row_list.append(
                    ['username', 'user_type', 'id_report', 'language', 'institute', 'usecase', 'start', 'stop',
                     'mention_text'])
        elif action == 'concept-mention':
            row_list.append(
                    ['username', 'user_type', 'id_report', 'language', 'institute', 'usecase', 'start', 'stop',
                     'mention_text',
                     'concept_name', 'concept_url', 'area'])

        elif action == 'concepts':
            row_list.append(
                    ['username', 'user_type', 'id_report', 'language', 'institute', 'usecase', 'concept_url',
                     'concept_name', 'area'])

        try:
            for report in report_list:
                rep = Report.objects.get(id_report=report['id_report'], language=report['language'])
                cursor = connection.cursor()
                if action == 'labels':
                    cursor.execute(
                        "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.id_report = %s AND r.language = %s  AND ns_id = %s ",
                        [str(report['id_report']), str(report['language']), 'Human'])
                    reports_human_labels = cursor.fetchall()

                    agent_ns = NameSpace.objects.get(ns_id = 'Robot')
                    agent = User.objects.get(username = 'Robot_user',ns_id = agent_ns)
                    ass = Associate.objects.filter(username = agent,ns_id = agent_ns,id_report = rep,language = rep.language)
                    ins_arr = []
                    reports_robot_labels = []
                    for el in ass:
                        ins_arr.append(el.insertion_time)
                    if len(ins_arr) > 0:
                        cursor.execute(
                            "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.id_report = %s AND r.language = %s  AND ns_id = %s AND a.insertion_time not in %s",
                            [str(report['id_report']), str(report['language']), 'Robot',tuple(ins_arr)])
                        reports_robot_labels = cursor.fetchall()
                    if mode == 'both':
                        reports = chain(reports_human_labels, reports_robot_labels)
                    elif mode == 'Human':
                        reports = reports_human_labels
                    elif mode == 'Robot':
                        reports = reports_robot_labels

                if action == 'mentions':
                   cursor.execute(
                       "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s  AND ns_id = %s",
                       [str(report['id_report']), str(report['language']), 'Human'])
                   reports_human_mentions = cursor.fetchall()
                   agent_ns = NameSpace.objects.get(ns_id='Robot')
                   agent = User.objects.get(username='Robot_user', ns_id=agent_ns)
                   ass = Annotate.objects.filter(username=agent, ns_id=agent_ns, id_report=rep,
                                                  language=rep.language)
                   ins_arr = []
                   reports_robot_mentions = []
                   for el in ass:
                       ins_arr.append(el.insertion_time)
                   if len(ins_arr) > 0:
                       cursor.execute(
                           "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s  AND ns_id = %s and a.insertion_time not in %s",
                           [str(report['id_report']), str(report['language']), 'Robot',tuple(ins_arr)])
                       reports_robot_mentions = cursor.fetchall()

                   if mode == 'both':
                       reports = chain(reports_human_mentions, reports_robot_mentions)
                   elif mode == 'Human':
                       reports = reports_human_mentions
                   elif mode == 'Robot':
                       reports = reports_robot_mentions
                elif action == 'concepts':
                   cursor.execute(
                       "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE r.id_report = %s AND r.language = %s  AND ns_id = %s",
                       [str(report['id_report']), str(report['language']), 'Human'])
                   reports_human_concepts = cursor.fetchall()
                   agent_ns = NameSpace.objects.get(ns_id='Robot')
                   agent = User.objects.get(username='Robot_user', ns_id=agent_ns)
                   ass = Contains.objects.filter(username=agent, ns_id=agent_ns, id_report=rep,
                                                 language=rep.language)
                   ins_arr = []
                   reports_robot_concepts =[]
                   for el in ass:
                       ins_arr.append(el.insertion_time)
                   if len(ins_arr) > 0:
                       cursor.execute(
                           "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE r.id_report = %s AND r.language = %s  AND ns_id = %s and a.insertion_time not in %s",
                           [str(report['id_report']), str(report['language']), 'Robot',tuple(ins_arr)])
                       reports_robot_concepts = cursor.fetchall()

                   if mode == 'both':
                       reports = chain(reports_human_concepts, reports_robot_concepts)
                   elif mode == 'Human':
                       reports = reports_human_concepts
                   elif mode == 'Robot':
                       reports = reports_robot_concepts

                elif action == 'concept-mention':
                    cursor.execute(
                        "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s AND ns_id = %s",
                        [str(report['id_report']), str(report['language']), 'Human'])
                    reports_human_linking = cursor.fetchall()
                    agent_ns = NameSpace.objects.get(ns_id='Robot')
                    agent = User.objects.get(username='Robot_user', ns_id=agent_ns)
                    ass = Linked.objects.filter(username=agent, ns_id=agent_ns, id_report=rep,
                                                  language=rep.language)
                    ins_arr = []
                    reports_robot_linking = []
                    for el in ass:
                        ins_arr.append(el.insertion_time)
                    if len(ins_arr) >0:
                        cursor.execute(
                            "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s AND ns_id = %s and a.insertion_time not in %s",
                            [str(report['id_report']), str(report['language']), 'Robot',tuple(ins_arr)])
                        reports_robot_linking = cursor.fetchall()
                    if mode == 'both':
                        reports = chain(reports_human_linking,reports_robot_linking)
                    elif mode == 'Human':
                        reports = reports_human_linking
                    elif mode == 'Robot':
                        reports = reports_robot_linking

                for el in reports:
                    row = list(el)
                    if row[0] != 'Robot_user':
                        if row[1] == 'Human':
                            row[1] = 'Manual'
                        else:
                            row[1] = 'Automatic'
                        if action == 'mentions' or action == 'concept-mention':
                            row[8] = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', row[8])
                        row_list.append(row)




        except Exception as e:
            print(e)
            return False
        else:

            writer = csv.writer(response)
            writer.writerows(row_list)
            return response

    elif format.startswith('bioc'):
        if mode is not None and mode != 'both':
            ns = NameSpace.objects.get(ns_id=mode)
        try:
            writer = BioCXMLWriter()
            json_writer = BioCJSONWriter()
            writer.collection = BioCCollection()
            json_writer.collection = BioCCollection()
            collection = writer.collection
            collection1 = json_writer.collection
            today = str(date.today())
            collection.date = today
            collection.source = 'MEDTAG Collection'
            collection1.date = today
            collection1.source = 'MEDTAG Collection'

            if action == 'mentions':
                collection.put_infon('annotation_type', 'mentions')
                collection.key = 'mentions.key'
                collection1.put_infon('annotation_type', 'mentions')
                collection1.key = 'mentions.key'
                for rep in report_list:
                    print(rep['id_report'])
                    report = Report.objects.get(id_report=rep['id_report'],language=rep['language'])

                    cursor.execute(
                        "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s  AND ns_id = %s",
                        [str(rep['id_report']), str(rep['language']), 'Human'])
                    reports_human_mentions = cursor.fetchall()

                    agent_ns = NameSpace.objects.get(ns_id='Robot')
                    agent = User.objects.get(username='Robot_user', ns_id=agent_ns)
                    ass = Annotate.objects.filter(username=agent, ns_id=agent_ns, id_report=report,
                                                  language=report.language)
                    ins_arr = []
                    reports_robot_mentions = []
                    for el in ass:
                        ins_arr.append(el.insertion_time)

                    if len(ins_arr) > 0:
                        cursor.execute(
                            "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s  AND ns_id = %s and a.insertion_time not in %s",
                            [str(rep['id_report']), str(rep['language']), 'Robot', tuple(ins_arr)])
                        reports_robot_mentions = cursor.fetchall()
                    if mode == 'both':
                        reports = list(chain(reports_human_mentions, reports_robot_mentions))
                    elif mode == 'Human':
                        reports = reports_human_mentions
                    elif mode == 'Robot':
                        reports = reports_robot_mentions



                    data = get_fields_from_json()
                    json_keys_to_display_human = data['fields']
                    json_keys_to_display_human.extend(['authors','volume','journal','year'])
                    json_keys_to_ann_human = data['fields_to_ann']
                    json_keys_to_ann_human.extend(['abstract','title'])
                    json_keys_to_display_human = list(set(json_keys_to_display_human))
                    json_keys_to_ann_human = list(set(json_keys_to_ann_human))
                    json_keys_to_ann_robot = []
                    workpath = os.path.dirname(
                        os.path.abspath(__file__))  # Returns the Path your .py file is in
                    with open(os.path.join(workpath,
                                           './automatic_annotation/auto_fields/auto_fields.json')) as out:
                        data = json.load(out)
                        json_keys_to_ann_robot = data['extract_fields'][report.name.name]
                        json_keys_to_ann_robot.append('abstract')
                        json_keys_to_ann_robot.append('title')
                        json_keys_to_ann_robot = list(set(json_keys_to_ann_robot))

                    json_keys = []
                    json_keys_to_ann = []
                    if mode == 'Human':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_human))
                        json_keys_to_ann = json_keys_to_ann_human
                    elif mode == 'Robot':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_robot))
                        json_keys_to_ann = json_keys_to_ann_robot
                    elif mode == 'both':
                        json_keys = list(
                            set(json_keys_to_display_human + json_keys_to_ann_robot + json_keys_to_ann_human))
                        json_keys_to_ann = list(set(json_keys_to_ann_robot + json_keys_to_ann_human))

                    document = BioCDocument()
                    document.id = str(report.id_report)
                    document.put_infon('usecase', report.name_id)
                    document.put_infon('language', report.language)
                    document.put_infon('institute', report.institute)

                    document1 = BioCDocument()
                    document1.id = str(report.id_report)
                    document1.put_infon('usecase', report.name_id)
                    document1.put_infon('language', report.language)
                    document1.put_infon('institute', report.institute)

                    annotations = []
                    count = 0
                    maj_annotations = []
                    for el in reports:
                        # print(el)
                        mention = Mention.objects.get(start=el[6], stop=el[7], id_report=report,language=report.language)
                        json_dict = report_get_start_end(json_keys,json_keys_to_ann,report.id_report,report.language)
                        annotation = BioCAnnotation()
                        annotation.id = str(count)
                        count = count + 1
                        loc_ann = BioCLocation()
                        loc_ann.offset = str(mention.start)
                        loc_ann.length = str(mention.stop - mention.start + 1)
                        annotation.add_location(loc_ann)
                        mention_text = mention.mention_text
                        mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)

                        annotation.text = mtext
                        couple = (annotation, mention.start, mention.stop)
                        annotations.append(couple)

                    seen = []
                    for key in json_keys_to_ann:
                        passage = BioCPassage()
                        passage.put_infon('section', key)
                        check = False

                        keys = json_dict['rep_string'].keys()
                        if key in keys:
                            if json_dict['rep_string'].get(key) != '':
                                passage.text = json_dict['rep_string'][key]['text']
                                start = str(json_dict['rep_string'][key]['start'])
                                passage.offset = (start)
                                for el in annotations:
                                    if el not in seen:

                                        if int(el[1]) >= int(json_dict['rep_string'][key]['start']) and int(
                                                el[2]) <= int(json_dict['rep_string'][key]['end']):
                                            check = True
                                            passage.add_annotation(el[0])
                                            seen.append(el)
                                        # passage.add_annotation(el[0])
                                if check:
                                    document.add_passage(passage)
                                    document1.add_passage(passage)
                    collection.add_document(document)
                    for doc in collection:
                        print(doc.id)
                    collection1.add_document(document)

            elif action == 'concept-mention':
                collection.put_infon('annotation_type', 'linking')
                collection.key = 'linking.key'
                collection1.put_infon('annotation_type', 'linking')
                collection1.key = 'linking.key'


                documents = []
                # reports = Annotate.objects.filter(username=username).values('id_report','language').distinct()
                for rep in report_list:
                    document = ''
                    report = Report.objects.get(id_report=rep['id_report'],
                                                language=rep['language'])

                    cursor.execute(
                        "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s AND ns_id = %s",
                        [str(rep['id_report']), str(rep['language']), 'Human'])
                    reports_human_linking = cursor.fetchall()
                    agent_ns = NameSpace.objects.get(ns_id='Robot')
                    agent = User.objects.get(username='Robot_user', ns_id=agent_ns)
                    ass = Linked.objects.filter(username=agent, ns_id=agent_ns, id_report=report,
                                                language=report.language)
                    ins_arr = []
                    reports_robot_linking = []
                    for el in ass:
                        ins_arr.append(el.insertion_time)
                    if len(ins_arr) > 0:
                        cursor.execute(
                            "SELECT a.username,a.ns_id,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE r.id_report = %s AND r.language = %s AND ns_id = %s and a.insertion_time not in %s",
                            [str(rep['id_report']), str(rep['language']), 'Robot', tuple(ins_arr)])
                        reports_robot_linking = cursor.fetchall()
                    if mode == 'both':
                        reports = list(chain(reports_human_linking, reports_robot_linking))
                    elif mode == 'Human':
                        reports = reports_human_linking
                    elif mode == 'Robot':
                        reports = reports_robot_linking

                    data = get_fields_from_json()
                    json_keys_to_display_human = data['fields']
                    json_keys_to_display_human.extend(['authors', 'volume', 'journal', 'year'])
                    json_keys_to_ann_human = data['fields_to_ann']
                    json_keys_to_ann_human.extend(['abstract', 'title'])
                    json_keys_to_display_human = list(set(json_keys_to_display_human))
                    json_keys_to_ann_human = list(set(json_keys_to_ann_human))
                    json_keys_to_ann_robot = []
                    workpath = os.path.dirname(
                        os.path.abspath(__file__))  # Returns the Path your .py file is in
                    with open(os.path.join(workpath,
                                           './automatic_annotation/auto_fields/auto_fields.json')) as out:
                        data = json.load(out)
                        json_keys_to_ann_robot = data['extract_fields'][report.name.name]
                        json_keys_to_ann_robot.append('abstract')
                        json_keys_to_ann_robot.append('title')
                        json_keys_to_ann_robot = list(set(json_keys_to_ann_robot))

                    json_keys = []
                    json_keys_to_ann = []
                    if mode == 'Human':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_human))
                        json_keys_to_ann = json_keys_to_ann_human
                    elif mode == 'Robot':
                        json_keys = list(set(json_keys_to_display_human + json_keys_to_ann_robot))
                        json_keys_to_ann = json_keys_to_ann_robot
                    elif mode == 'both':
                        json_keys = list(
                            set(json_keys_to_display_human + json_keys_to_ann_robot + json_keys_to_ann_human))
                        json_keys_to_ann = list(set(json_keys_to_ann_robot + json_keys_to_ann_human))

                    document = BioCDocument()
                    document.id = str(report.id_report)
                    document.put_infon('usecase', report.name_id)
                    document.put_infon('language', report.language)
                    document.put_infon('institute', report.institute)

                    annotations = []
                    count = 0
                    maj_annotations = []
                    for el in reports:


                        mention = Mention.objects.get(start=el[6], stop=el[7], id_report=report,
                                                      language=report.language)
                        concept = Concept.objects.get(concept_url=el[10])
                        json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)

                        annotation = BioCAnnotation()
                        annotation.id = str(count)
                        annotation.put_infon('concept_name', concept.name)
                        annotation.put_infon('concept_url', concept.concept_url)
                        count = count + 1
                        loc_ann = BioCLocation()
                        loc_ann.offset = str(mention.start)
                        loc_ann.length = str(mention.stop - mention.start + 1)
                        annotation.add_location(loc_ann)
                        mention_text = mention.mention_text
                        mtext = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', mention_text)

                        annotation.text = mtext
                        couple = (annotation, mention.start, mention.stop)
                        annotations.append(couple)

                    seen = []
                    for key in json_keys_to_ann:
                        passage = BioCPassage()
                        passage.put_infon('section', key)
                        check = False

                        keys = json_dict['rep_string'].keys()
                        if key in keys:
                            if json_dict['rep_string'].get(key) != '':
                                # if json_dict['rep_string'].get(key) is not None and json_dict['rep_string'].get(key) != '':
                                passage.text = json_dict['rep_string'][key]['text']
                                start = str(json_dict['rep_string'][key]['start'])
                                passage.offset = (start)
                                for el in annotations:
                                    if el not in seen:
                                        # start1 = int(el[1])
                                        # start2 = int(json_dict['rep_string'][key]['start'])
                                        # stop1 = int(el[2])
                                        # stop2 = int(json_dict['rep_string'][key]['end'])
                                        if int(el[1]) >= int(json_dict['rep_string'][key]['start']) and int(
                                                el[2]) <= int(json_dict['rep_string'][key]['end']):
                                            check = True
                                            passage.add_annotation(el[0])
                                            seen.append(el)
                                        # passage.add_annotation(el[0])
                                if check:
                                    document.add_passage(passage)

                    collection.add_document(document)
                    for doc in collection:
                        print(doc.id)
                    collection1.add_document(document)
                    # print(writer)
                    # documents.append(document)



        except Exception as e:
            print(e)
            return False

        else:
            # os.remove(path1)
            if format.endswith('json'):
                # os.remove(path1)
                return json_writer
            # return True
            return writer


