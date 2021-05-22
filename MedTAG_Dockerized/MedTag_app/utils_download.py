import psycopg2
import csv
from MedTag_app.utils import *
from bioc import *
from datetime import datetime

def generate_bioc(json_keys,json_keys_to_ann,username,action,language,usecase,institute,form):
    try:
        writer = BioCXMLWriter()
        writer.collection = BioCCollection()
        collection = writer.collection
        date = datetime.today().strftime('%Y%m%d')
        collection.date = date
        collection.source = 'MEDTAG Collection'
        collection.put_infon('username', username)
        if action == 'mentions':
            collection.put_infon('annotation_type', 'mentions')
            collection.key = 'mentions.key'

            with connection.cursor() as cursor:
                if language is None and institute is None and usecase is None:
                    cursor.execute("SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language AND a.username = %s",[str(username)])

                elif language is not None and institute is None and usecase is None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s ", [str(username),str(language)])

                elif language is None and institute is not None and usecase is None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.institute = %s ",
                        [str(username),str(institute)])

                elif language is None and institute is None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.name = %s ",
                        [str(username),str(usecase)])

                elif language is not None and institute is not None and usecase is None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.institute = %s",
                        [str(username),str(language),str(institute)])

                elif language is None and institute is not None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.institute = %s AND r.name = %s",
                        [str(username),str(institute),str(usecase)])
                elif language is not None and institute is None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s",
                        [str(username),str(language),str(usecase)])

                elif language is not None and institute is not None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(language),str(usecase),str(institute)])

                reports = cursor.fetchall()

            documents = []
            # reports = Annotate.objects.filter(username=username).values('id_report','language').distinct()
            for couple in reports:
                document = ''
                report = Report.objects.get(name = couple[0],id_report=couple[1],institute = couple[3], language=couple[2])
                json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                anno = Annotate.objects.filter(username=username,id_report = report,language = report.language)
                document = BioCDocument()
                document.id = str(report.id_report)
                document.put_infon('usecase', report.name_id)
                document.put_infon('language', report.language)
                document.put_infon('institute', report.institute)

                annotations = []
                count = 0
                for el in anno:
                    mention = Mention.objects.get(start = el.start_id,stop = el.stop,id_report=report,language = report.language)
                    json_dict = report_get_start_end(json_keys,json_keys_to_ann,report.id_report,report.language)
                    annotation = BioCAnnotation()
                    annotation.id = str(count)
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
            # print(writer)



        elif action == 'concept-mention':
            collection.put_infon('annotation_type', 'linking')
            collection.key = 'linking.key'

            with connection.cursor() as cursor:
                if language is None and institute is None and usecase is None:
                    cursor.execute("SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language AND a.username = %s",[str(username)])

                elif language is not None and institute is None and usecase is None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s ", [str(username),str(language)])

                elif language is None and institute is not None and usecase is None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.institute = %s ",
                        [str(username),str(institute)])

                elif language is None and institute is None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.name = %s ",
                        [str(username),str(usecase)])

                elif language is not None and institute is not None and usecase is None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.institute = %s",
                        [str(username),str(language),str(institute)])

                elif language is None and institute is not None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.institute = %s AND r.name = %s",
                        [str(username),str(institute),str(usecase)])
                elif language is not None and institute is None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s",
                        [str(username),str(language),str(usecase)])

                elif language is not None and institute is not None and usecase is not None:
                    cursor.execute(
                        "SELECT DISTINCT r.name,r.id_report,r.language,r.institute FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(language),str(usecase),str(institute)])

                reports = cursor.fetchall()

            documents = []
            # reports = Annotate.objects.filter(username=username).values('id_report','language').distinct()
            for couple in reports:
                document = ''
                report = Report.objects.get(name = couple[0],id_report=couple[1],institute = couple[3], language=couple[2])
                json_dict = report_get_start_end(json_keys, json_keys_to_ann, report.id_report, report.language)
                anno = Linked.objects.filter(username=username,id_report = report,language = report.language)
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
            # print(writer)


        workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
        path = os.path.join(workpath, './static/BioC/BioC.dtd')
        path1 = os.path.join(workpath, './static/BioC/to_download.xml')

        writer.write(path1)
        dtd_file = path
        xml_reader = BioCXMLReader(path1, dtd_valid_file=dtd_file)
        xml_reader.read()
        if form == 'json':
            # workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            # path = os.path.join(workpath, './static/BioC/BioC.dtd')
            # path1 = os.path.join(workpath, './static/BioC/to_download.xml')
            #
            # writer.write(path1)
            # dtd_file = path
            # xml_reader = BioCXMLReader(path1, dtd_valid_file=dtd_file)
            # xml_reader.read()

            json_writer = BioCJSONWriter()
            json_writer.collection = xml_reader.collection
            # path1 = os.path.join(workpath, './static/BioC/to_download.xml')
            # json_writer.write('output_bioc.json')
            # print(json_writer)
        #
        # # writer.write(path +'to_download.xml')
        #writer.write(response)

    except Exception as e:
        print(e)
        return False

    else:
        os.remove(path1)
        if form == 'json':
            # os.remove(path1)
            return json_writer
        # return True
        return writer

def create_csv_to_download1(username,use,inst,lang,action,response):
    row_list = []
    if action == 'labels':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'label'])
    elif action == 'mentions':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'start','stop','mention_text'])
    elif action == 'concept-mention':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'start', 'stop', 'mention_text','concept_name','concept_url','area'])
    elif action == 'concepts':
        row_list.append(['username', 'id_report', 'language', 'institute', 'usecase', 'concept_url','concept_name','area'])
    try:
        with connection.cursor() as cursor:
            if use is not None and lang is not None and inst is not None:
                if action == 'labels':
                   cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(lang), str(use), str(inst)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(lang), str(use), str(inst)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(lang), str(use), str(inst)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(lang), str(use), str(inst)])

            elif use is None and lang is None and inst is None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s",[str(username)])
                elif action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s",[str(username)])
                elif action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s",[str(username)])
                elif action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s",[str(username)])

            elif use is not None and lang is not None and inst is None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.name = %s ",
                        [str(username),str(lang), str(use)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.name = %s ",
                        [str(username),str(lang), str(use)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.language = %s AND r.name = %s",
                        [str(username),str(lang), str(use)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.name = %s ",
                        [str(username),str(lang), str(use)])

            elif use is not None and lang is None and inst is not None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT  a.username,r.id_report,r.language,r.institute,r.name, a.label  FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(use), str(inst)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(use), str(inst)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(use), str(inst)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.name = %s AND r.institute = %s",
                        [str(username),str(use), str(inst)])

            if use is None and lang is not None and inst is not None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s AND r.institute = %s",
                        [str(username),str(lang), str(inst)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s  AND r.institute = %s",
                        [str(username),str(lang), str(inst)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.language = %s  AND r.institute = %s",
                        [str(username),str(lang), str(inst)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s AND r.institute = %s",
                        [str(username),str(lang), str(inst)])

            if use is not None and lang is None and inst is None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.name = %s ",
                        [str(username),str(use)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.name = %s ",
                        [str(username),str(use)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.name = %s ",
                        [str(username),str(use)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.name = %s",
                        [str(username),str(use)])

            elif use is None and lang is not None and inst is None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.language = %s",
                        [str(username),str(lang)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s",
                        [str(username),str(lang)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,c.concept_url, c.name, a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.language = %s",
                        [str(username),str(lang)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop WHERE a.username = %s AND r.language = %s",
                        [str(username),str(lang)])

            elif use is None and lang is None and inst is not None:
                if action == 'labels':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, a.label FROM report AS r INNER JOIN associate AS a ON r.id_report = a.id_report AND r.language = a.language WHERE a.username = %s AND r.institute = %s",
                        [str(username),str(inst)])
                if action == 'mentions':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text FROM report AS r INNER JOIN annotate AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop  WHERE a.username = %s AND r.institute = %s",
                        [str(username),str(inst)])
                if action == 'concepts':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name, c.name, c.concept_url,a.name FROM report AS r INNER JOIN contains AS a ON r.id_report = a.id_report  AND r.language = a.language INNER JOIN concept AS c ON c.concept_url = a.concept_url WHERE a.username = %s AND r.institute = %s",
                        [str(username),str(inst)])
                if action == 'concept-mention':
                    cursor.execute(
                        "SELECT DISTINCT a.username,r.id_report,r.language,r.institute,r.name,a.start,a.stop,m.mention_text,c.name,c.concept_url,a.name FROM report AS r INNER JOIN linked AS a ON r.id_report = a.id_report AND r.language = a.language INNER JOIN concept as c ON a.concept_url = c.concept_url INNER JOIN mention AS m ON m.id_report = a.id_report AND m.language = a.language AND a.start = m.start AND a.stop = m.stop  WHERE a.username = %s AND r.institute = %s",
                        [str(username),str(inst)])

            reports = cursor.fetchall()
            reports = sorted(reports, key=lambda x: x[1])

            for el in reports:

                row = list(el)
                if action == 'mentions' or action == 'concept-mention':
                    row[7] = re.sub('[^a-zA-Z0-9n\-_/\' ]+', '', row[7])
                row_list.append(row)
    except Exception as e:
        print(e)
        return False
    else:
        # workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
        # path = os.path.join(workpath, './static/temp/')
        writer = csv.writer(response)
        writer.writerows(row_list)
        return response
        # with open(path +'temp.csv', 'w', newline='') as file:
        #     try:
        #         writer = csv.writer(file)
        #         writer.writerows(row_list)
        #
        #         return True
        #     except Exception as e:
        #         print(e)
        #         return False


def create_json_to_download(username,use = None,inst = None,lang = None, action = None,all = None):
    json_resp = {}
    json_resp['ground_truth'] = []
    json_resp['username'] = username
    if all != 'all' and action != None and action != '':
        json_resp['action'] = action
        if action == 'concept-mention':
            json_resp['action'] = 'linking'

    if all == 'all':
        json_resp['ground_truth'] = {}
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
                json_resp_add[b].append(gt_json)
        json_resp['ground_truth'] = json_resp_add

    elif use is None and lang is None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if el.gt_type == action:
                    json_resp['ground_truth'].append(gt_json)


    elif use is not None and lang is not None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (gt_json['institute'] == inst and gt_json['use_case'] == use and el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is not None and lang is not None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (gt_json['use_case'] == use and el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is not None and lang is None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (gt_json['institute'] == inst and gt_json['use_case'] == use and el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)


    elif use is None and lang is not None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (gt_json['institute'] == inst and el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is not None and lang is None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (gt_json['use_case'] == use and el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is None and lang is None and inst is not None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (gt_json['institute'] == inst and el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)

    elif use is None and lang is not None and inst is None and action is not None:
            gt = GroundTruthLogFile.objects.filter(username=username, language=lang)
            for el in gt:
                gt_json = el.gt_json
                del gt_json['gt_type']
                del gt_json['username']

                if (el.gt_type == action):
                    json_resp['ground_truth'].append(gt_json)

    return (json_resp)


