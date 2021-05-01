import psycopg2
import datetime
from MedTag_app.models import *
from django.http import JsonResponse
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
            print(record)

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


    print(records)
    print(reports_dict)
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