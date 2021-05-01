from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.contrib.auth.models import User as User1
from MedTag_app.utils_ornella import *
from MedTag_app.utils_fabio import *
from django.contrib.auth.decorators import login_required
import hashlib
from MedTag_app.decorators import *
from MedTag_app.data import *


# ExaMode Ground Truth views here.
def index(request):
    """Home page for app (and project)"""
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTag_app/index.html', context)
    else:
        return redirect('MedTag_app:login')
#


def new_credentials(request):
    error_resp = {'error':'something went wrong with these options'}
    if request.method == 'POST':
        request_body_json = json.loads(request.body)
        usecase = request_body_json['usecase']
        request.session['usecase'] = usecase

        json_resp =  get_fields_from_json_usecase(usecase)
        request.session['fields'] = json_resp['fields']
        request.session['fields_to_ann'] = json_resp['fields_to_ann']

        language = request_body_json['language']
        request.session['language'] = language
        institute = request_body_json['institute']
        request.session['institute'] = institute
        # print('new_cred')
        json_resp ={'message':'ok'}
        return JsonResponse(json_resp)

    return JsonResponse(error_resp)

def logout(request):
    try:
        del request.session['username']
        del request.session['usecase']
        del request.session['language']
        del request.session['institute']
        del request.session['profile']
        del request.session['fields']
        del request.session['fields_to_ann']

        return redirect('MedTag_app:login')
    except KeyError:
        pass
    finally:
        request.session.flush()

    return redirect('MedTag_app:login')
# def logout(request):
#         auth_logout(request)
#         return redirect('MedTag_app:login')

def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password1 = request.POST.get('password',None)

        profile = request.POST.get('profile',None)
        if(profile is None):
            context = {'errorMessage': "Please set your profile."}
            return render(request, 'MedTag_app/registration.html', context)

        if User.objects.filter(username = username).exists():
            context = {'errorMessage': "This username is not available. Please, choose another one."}
            return render(request, 'MedTag_app/registration.html', context)
        try:
            with transaction.atomic():
                # user_official = User1.objects.create_user(username=username,
                #                                 password=password1)
                # # print(user_official)
                password = hashlib.md5(password1.encode()).hexdigest()
                user_ours = User.objects.create(username = username,profile=profile,password = password)
                # print(user_ours)
                # user = authenticate(username = username, password = password1)
                # auth_login(request,user)
                request.session['username'] = username
                request.session['profile'] = profile

                return redirect('MedTag_app:index')
        except (Exception) as error:
            # print(error)
            context = {'errorMessage': "Something went wrong, probably you did not set any profile"}
            return render(request, 'MedTag_app/registration.html', context)
    return render(request, 'MedTag_app/registration.html')

#@login_required(login_url='/login')
def select_options(request):
    username = request.session.get('username', False)
    if(username):
        if(request.method == 'POST'):
            request_body_json = json.loads(request.body)
            usecase = request_body_json['usecase']
            language = request_body_json['language']
            institute = request_body_json['institute']
            # usecase = 'Colon'
            # language = 'English'
            # institute = 'AOEC - Azienda Ospedaliera Cannizzaro'
            if language is not None and usecase is not None and institute is not None:
                request.session['usecase'] = usecase
                json_resp = get_fields_from_json_usecase(usecase)
                request.session['fields'] = json_resp['fields']
                request.session['fields_to_ann'] = json_resp['fields_to_ann']
                request.session['language'] = language
                request.session['institute'] = institute
                jsonresp = {'message':'ok'}
                return JsonResponse(jsonresp)
                # return redirect('MedTag_app:index')
            else:
                context = {'errorMessage': "Something went wrong! Please try to select your options again or contact us!"}
                return render(request, 'MedTag_app/index.html', context)
        else:
            #jsonDict = get_distinct()
            # print('nada')
            context = {'username': username}
            return render(request, 'MedTag_app/index.html',context)

    else:
        # print('esco')
        return redirect('MedTag_app:logout')
        # context = {'errorMessage': "Something went wrong! Please login"}
        # return render(request, 'MedTag_app/login.html', context)

#@login_required(login_url='/login')
def credits(request):
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTag_app/index.html', context)
    else:
        return redirect('MedTag_app:login')

def configure(request):
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTag_app/index.html', context)
    else:
        return redirect('MedTag_app:login')

def updateConfiguration(request):
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTag_app/index.html', context)
    else:
        return redirect('MedTag_app:login')

def infoAboutConfiguration(request):
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTag_app/index.html', context)
    else:
        return redirect('MedTag_app:login')

#@login_required(login_url='/login')
def tutorial(request):
    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTag_app/index.html', context)
    else:
        return redirect('MedTag_app:login')

#@login_required(login_url='/login')
# def about(request):
#     username = request.session.get('username', False)
#     if(username):
#         context = {'username': username}
#         return render(request, 'MedTag_app/index.html', context)
#     else:
#         return redirect('MedTag_app:login')

def get_session_params(request):
    json_resp = {}
    usecase = request.session.get('usecase',None)
    language = request.session.get('language',None)
    institute = request.session.get('institute',None)
    if usecase is not None and language is not None and institute is not None:
        json_resp['usecase'] = usecase
        json_resp['language'] = language
        json_resp['institute'] = institute
    else:
        json_resp['usecase'] = ''
        json_resp['language'] = ''
        json_resp['institute'] = ''
    return JsonResponse(json_resp)


def login(request):

    if request.method == 'POST':
        md5_pwd = ''
        admin = False

        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username:
            username = username.replace("\"", "").replace("'", "")
        if password:
            password = password.replace("\"", "").replace("'", "")
            md5_pwd = hashlib.md5(password.encode()).hexdigest()
        if (username != False and password != False):
            user = User.objects.filter(username = username, password = md5_pwd)


            if user.exists():
                # print('LOGGATO')
                user = User.objects.get(username=username, password=md5_pwd)
                print("username: " + username)
                request.session['username'] = username
                request.session['profile'] = user.profile
                return redirect('MedTag_app:index')
                #return redirect('MedTag_app:select_options')

        profile_list = User.objects.values_list('profile', flat=True).distinct()
        if 'Admin' in profile_list:
            admin = True
        context = {'errorMessage': "Your username and password didn't match.","admin":admin}
        return render(request, 'MedTag_app/login.html', context)

    else:
        username = request.session.get('username', False)
        language = request.session.get('language', False)
        usecase = request.session.get('usecase', False)
        institute = request.session.get('institute', False)

        admin = False
        profile_list = User.objects.values_list('profile', flat=True).distinct()
        if 'Admin' in profile_list:
            admin = True
        context = {'admin': admin}
        # print('user',username)
        # print('user',usecase)
        # print('user',language)
        # print('user',institute)
        if username:
            return redirect('MedTag_app:index')

        return render(request, 'MedTag_app/login.html',context)

        # try:
        #     del request.session['username']
        #
        #
        #     # print('flushed1')
        # except:
        #     pass
        # try:
        #     del request.session['usecase']
        #     del request.session['institute']
        #     del request.session['language']
        #     # print('flushed2')
        # except:
        #     pass
        # request.session.flush()

    #     user = authenticate(request, username=username, password=password)
    #     # print('AUTENTICATO')
    #     # print(user)
    #     if user is not None:
    #         auth_login(request, user)
    #         # print('LOGGATO')
    #         # print("username: " + username)
    #         request.session['username'] = username
    #
    #         return redirect('MedTag_app:index')
    #
    #
    #     else:
    #         # print('the user does not exist')
    #         context = {'errorMessage': "Your username or your password were incorrect."}
    #         return render(request, 'MedTag_app/login.html', context)
    #
    # else:
    #     return render(request, 'MedTag_app/login.html')

#         """Login page for app (and project)"""
#         # # print("Login requested")
#         # context = {'errorMessage': ""}
#         # md5_pwd = ''
#         # username = request.POST.get('username', False)
#         # password = request.POST.get('password', False)
#         # if username:
#         #     username = username.replace("\"", "").replace("'", "")
#         # if password:
#         #     password = password.replace("\"", "").replace("'", "")
#         #     md5_pwd = hashlib.md5(password.encode()).hexdigest()
#         # if (username != False and password != False):
#         #     try:
#         #         rows = User.objects.filter(username=username,password=md5_pwd)
#         #         if len(rows) > 0:
#         #             # print(len(rows))
#         #             # print("username: " + username)
#         #             request.session['username'] = username
#         #
#         #             return redirect('MedTag_app:index')
#         #
#         #         else:
#         #             context = {'errorMessage': "Your username and password didn't match."}
#         #             return render(request, 'MedTag_app/login.html', context)
#         #
#         #     except (Exception) as error:
#         #         # print("Error while connecting to PostgreSQL", error)
#         #
#         #
#         # return render(request, 'MedTag_app/login.html', context)
#
#
#





# LABELS ANNOTATION WITH AJAX

#@login_required(login_url='/login')
def annotation(request):
    ###
    # request.session['usecase'] = 'Colon'
    # request.session['language'] = 'English'
    # request.session['institute'] = 'AOEC - Azienda Ospedaliera Cannizzaro'
    ###
    username = request.session['username']
    usecase = request.session['usecase']
    language = request.session['language']
    labels = get_labels(usecase)

    context = {'username':username,'labels':labels}
    return render(request, 'MedTag_app/annotation1.html', context)

#@login_required(login_url='/login')
def annotationlabel(request,action=None):
    username = request.session['username']
    usecase = request.session['usecase']
    language = request.session['language']
    # print('username',username)
    # print('usecase',usecase)
    # print('language',language)
    # username = 'ornella_irrera'
    # usecase = 'Colon'
    # language = 'English'
    #type = request.session['type']
    type = 'labels'
    labels = get_labels(usecase)
    json_response = {}

    # GET the labels annotated by the user for the report report_id
    if request.method == 'GET' and action.lower() == 'user_labels':
        # report_id = action
        report_id = request.GET.get('report_id')
        # print(report_id)
        #report_id = 'd47d8d63cf3b9f4f4a51c85030ff5e2f'
        report1 = Report.objects.get(id_report = report_id,language = language)
        labels = Associate.objects.filter(username=username, id_report=report1,language = language).values('seq_number', 'label')
        json_dict = {}
        json_dict['labels'] = []

        if len(labels) > 0:
            for el in labels:
                json_val = {}
                json_val['label'] = (el['label'])
                json_val['seq_number'] = (el['seq_number'])
                json_dict['labels'].append(json_val)


        return JsonResponse(json_dict)

    elif request.method == 'GET' and action.lower() == 'all_labels':
        # report_id = action
        labels = AnnotationLabel.objects.filter(name=usecase).values('seq_number','label')
        json_dict = {}
        if len(labels) > 0:
            json_dict['labels'] = []
            for el in labels:
                json_val = {}
                json_val['label'] = (el['label'])
                json_val['seq_number'] = (el['seq_number'])
                json_dict['labels'].append(json_val)

        else:
            json_dict['labels'] = []
            # json_dict = {'error': 'No entries found for usecase :'+usecase+'.'}

        return JsonResponse(json_dict)


    elif request.method == 'POST' and action.lower() == 'delete':
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username)
        language = request.session['language']
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting parameters.'}
            return json_response
        try:
            with transaction.atomic():
                to_del = Associate.objects.filter(username=user, id_report=report1,language = language)
                json_response = delete_all_annotation(to_del, user, report1,language, type)
                return JsonResponse(json_response)
        except (Exception) as error:
            # print(error)
            json_response = {'error': 'An error occurred saving the ground_truth and the labels'}
            return JsonResponse(json_response)

    if request.method == 'POST' and action.lower() == 'insert':
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username)
        language = request.session['language']
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response)
        labels_to_save = request_body_json['labels']
        if len(labels_to_save) == 0:
            rows = Associate.objects.filter(username = user, id_report = report1, language = language)
            if rows.exists():
                json_response = delete_all_annotation(rows,user,report1,language,type)
            else:
                json_response = {'message': 'Nothing to save.'}
            return JsonResponse(json_response)

        if len(labels_to_save) == 0 and Associate.objects.filter(username = user, id_report =report1,language =language).exists():
            try:
                with transaction.atomic():
                    # json_response = delete_all_mentions(user, report1, type)
                    json_response = delete_all_annotation(user, report1,language, type)
                    return JsonResponse(json_response)
            except Exception as error:
                # print(error)
                json_response = {'error': 'An error occurred.'}
                return JsonResponse(json_response, status=500)

        elif len(labels_to_save) == 0 and not Associate.objects.filter(username = user, id_report =report1,language =language).exists():
                json_response = {'message':'Nothing to do'}
                return JsonResponse(json_response)

        update = True
        existing_rows = Associate.objects.filter(username = user, id_report =report1,language =language)
        if existing_rows.exists():
            if existing_rows.count() == len(labels_to_save):
                # print(labels_to_save)
                lab_saved = []
                # for el in labels_to_save:
                #     # el = json.loads(el)
                #     # el = el.replace('\r', '')
                #     # key = [item[1] for item in labels if item[0] == el]
                #     tup = (el['label'], el['seq_number'])
                #     lab_saved.append(tup)

                for label in labels_to_save:
                    label1 = AnnotationLabel.objects.get(name=usecase, label=label['label'], seq_number=label['seq_number'])


                    if not Associate.objects.filter(username=user, seq_number=label1.seq_number, label=label1,
                                                    id_report=report1, language=language).exists():
                        update = True
                        break
                    else:
                        update = False

        if update == True:

            try:
                with transaction.atomic():
    # Remove all the existing labels inserted by the user for that report. The existing ground truth is kept untile the deletion is successful
                    to_del = Associate.objects.filter(username=user, id_report=report1,language = language)
                    json_resp_delete = delete_all_annotation(to_del,user,report1,language,type)
                    # print(json_resp_delete)

                    json_resp_labels = update_annotation_labels(labels_to_save,usecase,user,report1,language)
                    # print(json_resp_labels)

                    #type = 'll'
                    jsonDict = serialize_gt(type, usecase, username, report_id,language)
                    gt = GroundTruthLogFile.objects.create(username=user, id_report=report1, language = language, gt_json=jsonDict, gt_type=type,
                                                          insertion_time=Now())
                    # print('salvo gt')
                    # print(gt)


            except (Exception) as error:
                print(error)
                # print('rolled back')
                json_response = {'error': 'An error occurred saving the ground_truth and the labels, the transaction rolledback'}
                return JsonResponse(json_response)

            json_response = {'message': 'Labels and Ground truth saved.'}

            return JsonResponse(json_response)
        else:
            json_response = {'message':'no changes detected'}
            return JsonResponse(json_response)


#END LABELS ANNOTATION

# MENTIONS WITH AJAX


#@login_required(login_url='/login')
def mentions(request):
    username = request.session.get('username')
    if username:
        context = {'username':username}
        return render(request, 'MedTag_app/mention1.html', context)
    else:
        json_resp = {'error':'authentication needed'}
        return JsonResponse(json_resp)

#@login_required(login_url='/login_view')
def mention_insertion(request,action=None):
    # print('ENTRO MENTION IDENTIFICATION')
    # username = 'ornella_irrera'
    # language = 'English'
    # usecase = 'Colon'

    username = request.session['username']
    language = request.session['language']
    usecase = request.session['usecase']
    type = 'mentions'
    #reports = (request.session['reports'])
    json_response = {}
    if request.method == 'GET':
        report_id = request.GET.get('report_id')
        report1 = Report.objects.get(id_report=report_id,language=language)

        try:
            a = Annotate.objects.filter(username=username, id_report=report1,language = language).values('start', 'stop')
            json_dict = {}
            json_dict['mentions'] = []
            for el in a:
                mention_text = Mention.objects.get(start=int(el['start']), stop=int(el['stop']), id_report=report1,language = language)

                json_val = {}
                json_val['start'] = (el['start'])
                json_val['stop'] = (el['stop'])
                json_val['mention_text'] = mention_text.mention_text
                json_dict['mentions'].append(json_val)

            return JsonResponse(json_dict)
        except (Exception) as error:
            # print(error)
            json_response = {'error': 'Sorry, an erorr occurred during the GET request.'}
            return JsonResponse(json_response,status=500)

    elif request.method == 'POST' and action.lower() == 'delete':
        #report_id = request.POST.get('report_id')
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username)
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting parameters.'}
            return JsonResponse(json_response,status=500)

        ass = Annotate.objects.filter(username=user, id_report=report1.id_report,language = language).values('start', 'stop')
        # print(len(ass))
        if len(ass) == 0:
            json_response = {'message': 'Nothing to delete.'}
            return JsonResponse(json_response)
        try:
            with transaction.atomic():
                json_response = delete_all_mentions(user, report1,language, type,usecase)
                return JsonResponse(json_response)

        except (Exception) as error:
            # print(error)
            json_response = {'error': 'An error occurred.'}
            return JsonResponse(json_response, status=500)


    elif request.method == 'POST' and action.lower() == 'insert':
        json_response = {'message':'Mentions and Ground truth saved.'}
        #report_id = request.POST.get('report_id')
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username = username)
        report1 = Report.objects.get(id_report = report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response,status=500)



        #mentions = request.POST.getlist('mentions')
        #mentions = ['{"mention_text":"Colon Tubular Adenoma","start":375,"stop":395}','{"mention_text":"Right Colon","start":501,"stop":511}']
        mentions = request_body_json['mentions']
        if len(mentions) == 0 and Annotate.objects.filter(username = user, id_report =report1,language =language).exists():
            try:
                with transaction.atomic():
                    # json_response = delete_all_mentions(user, report1, type)
                    json_response = delete_all_mentions(user, report1,language, type,usecase)
                #js = clean_mentions(user, report1, language)
                return JsonResponse(json_response)
            except Exception as error:
                # print(error)
                json_response = {'error': 'An error occurred.'}
                return JsonResponse(json_response, status=500)

        elif len(mentions) == 0 and not Annotate.objects.filter(username = user, id_report =report1,language =language).exists():
                json_response = {'message':'Nothing to do'}
                return JsonResponse(json_response)

        update = True
        existing_rows = Annotate.objects.filter(username = user, id_report =report1,language =language)
        if existing_rows.exists():
            if existing_rows.count() == len(mentions):

                for ment in mentions:
                    #ment = json.loads(mention)
                    mentionDB = Mention.objects.filter(start=int(ment['start']),stop=int(ment['stop']),mention_text=ment['mention_text'],
                                                       id_report = report1,language = language)


                    if mentionDB.exists():
                        if mentionDB.count() > 1:
                            json_response = {'error': 'something is wrong in mentions!'}
                            return JsonResponse(json_response, status=500)

                        mentionDB = mentionDB.first()
                        anno = Annotate.objects.filter(username = user, id_report =report1,language =language,
                                                        start = mentionDB,stop = mentionDB.stop)
                        if anno.exists():
                            if anno.count() > 1:
                                json_response = {'error': 'something is wrong in annotations!'}
                                return JsonResponse(json_response, status=500)

                            update = False
                        else:
                            update = True
                            break
                    else: #Se anche una sola instanza è differente allora faccio update
                        update = True
                        break



        if update == True:
            try:
                with transaction.atomic():
                    # json_resp_delete = delete_all_mentions(user, report1,language, type, usecase)
                    # # print(json_resp_delete)
                    json_response = update_mentions(mentions,report1,language,user,usecase)
                    # print(json_response)
                    if GroundTruthLogFile.objects.filter(username = user, language = language, id_report = report1, gt_type = 'mentions').exists():
                        GroundTruthLogFile.objects.filter(username=user, language=language, id_report=report1,
                                                          gt_type='mentions').delete()
                    jsonDict = serialize_gt(type, usecase, username, report_id,language)
                    c = GroundTruthLogFile.objects.create(username=user, id_report=report1,language = language, gt_json=jsonDict, gt_type=type,
                                                          insertion_time=Now())
                    # print('salvo gt')
            except (Exception) as error:
                # print(error)
                json_response = {'error':'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response, status=500)
        else:
            json_response = {'message':'Nothing changed'}

       # # print('risposta insert',json_response)
        return JsonResponse(json_response)

# END MENTIONS WITH AJAX

# CONCEPT - MENTIONS WITH AJAX
#@login_required(login_url='/login')
def link(request):
    username = request.session['username']
    concepts_diagnosis = get_list_concepts('Diagnosis')
    concepts_antaomical = get_list_concepts('Anatomical Location')
    concepts_Procedure = get_list_concepts('Procedure')
    concepts_test = get_list_concepts('Test')
    concepts_general = get_list_concepts('General Entity')
    context = {'username':username,'diagnosis_concepts':concepts_diagnosis,'location_concepts':concepts_antaomical,
               'Procedure_concepts':concepts_Procedure,'Test_concepts':concepts_test,'General_concepts':concepts_general}
    return render(request, 'MedTag_app/linked.html', context)


def insert_link(request,action=None):
    # print('ENTRO INSERT LINK')
    username = request.session['username']
    language = request.session['language']
    usecase = request.session['usecase']
    # username = 'ornella_irrera'
    # language = 'English'
    # usecase = 'Colon'
    type = 'concept-mention'

    if request.method == 'GET' and action.lower() == 'linked':
        try:
            report_id = request.GET.get('report_id')
            report1 = Report.objects.get(id_report=report_id,language = language )
            associations = Linked.objects.filter(username=username,language = language, id_report=report1.id_report).values('name','start', 'stop', 'concept_url')
            json_dict = {}
            json_dict['associations'] = []
            for el in associations:
                mention_text = Mention.objects.get(start=int(el['start']), stop=int(el['stop']), id_report=report1,language =language)
                json_val = {}
                concept_name = Concept.objects.get(concept_url = el['concept_url'])
                json_val['start'] = (el['start'])
                json_val['stop'] = (el['stop'])
                json_val['mention_text'] = mention_text.mention_text
                json_val['semantic_area'] = el['name']
                json_val['concept_name'] = concept_name.name.replace('\n','') #Rimuovo il replace
                json_val['concept_url'] = el['concept_url']
                json_dict['associations'].append(json_val)
            # print(json_dict)
            return JsonResponse(json_dict)
        except (Exception) as error:
            # print(error)
            json_response = {'error': 'An error occurred during the GET request.'}
            return JsonResponse(json_response, status=500)

    if request.method == 'GET' and action.lower() == 'mentions':
        report_id = request.GET.get('report_id')
        report1 = Report.objects.get(id_report=report_id,language = language)
        try:
            a = Annotate.objects.filter(username=username, id_report=report1, language=language).values('start', 'stop')
            json_dict = {}
            json_dict['mentions1'] = []
            for el in a:
                mention_text = Mention.objects.get(start=int(el['start']), stop=int(el['stop']), id_report=report1,
                                                   language=language)

                json_val = {}
                json_val['start'] = (el['start'])
                json_val['stop'] = (el['stop'])
                json_val['mention_text'] = mention_text.mention_text
                json_dict['mentions1'].append(json_val)

            return JsonResponse(json_dict)
        except (Exception) as error:
            # print(error)
            json_response = {'error': 'Sorry, an erorr occurred during the GET request.'}
            return JsonResponse(json_response, status=500)

    elif request.method == 'POST' and action.lower() == 'insert_mention':
        json_response = {'message': 'Your mentions were correctly inserted'}
        user = User.objects.get(username=username)
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        # print(report_id)

        mentions = request_body_json['mentions']
        report1 = Report.objects.get(id_report=report_id, language=language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response)

        if len(mentions) > 0:
            try:
                with transaction.atomic():
                    mention = mentions[0]
                    m = Mention.objects.filter(start = mention['start'], stop = mention['stop'], id_report = report1, language = language)
                    if not Mention.objects.filter(start = mention['start'], stop = mention['stop'], id_report = report1, language = language).exists():
                        Mention.objects.create(start = mention['start'], stop = mention['stop'],mention_text = mention['mention_text'], id_report = report1, language = language)
                    menti = Mention.objects.get(start = mention['start'], stop = mention['stop'], id_report = report1, language = language)
                    Annotate.objects.create(username = user, insertion_time = Now(),start = menti, stop = menti.stop, id_report = report1, language = language)
                # json_response = update_mentions(mentions, report1, language, user,usecase)
                    type = 'mentions'
                    if GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                         gt_type=type).exists():
                        GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                          gt_type=type).delete()

                    jsonDict = serialize_gt(type, usecase, username, report_id, language)
                    groundtruth = GroundTruthLogFile.objects.create(username=user, id_report=report1, language=language,
                                                                    gt_json=jsonDict,
                                                                    gt_type=type, insertion_time=Now())
                    # print('salvo gt')
                    # # print(groundtruth)
                    return JsonResponse(json_response)


            except (Exception) as error:
                # print(error)
                json_response = {'error': 'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response, status=500)
        else:
            json_response = {'message': 'nothing to save'}
            return JsonResponse(json_response)



    elif request.method == 'POST' and action.lower() == 'delete':
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username)
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting parameters.'}
            return json_response

        to_del = Linked.objects.filter(username=user, id_report=report1.id_report,language = language)
        if len(to_del) == 0:
            json_response = {'message': 'Nothing to delete.'}
            return JsonResponse(json_response)

        try:
            with transaction.atomic():
                json_response = delete_all_associations(user, report1, language, type,usecase)
            return JsonResponse(json_response)
        except (Exception) as error:
            # print(error)
            json_response = {'error': 'Sorry, an erorr occurred, rolled back.'}
            return JsonResponse(json_response,status=500)

    elif request.method == 'POST' and action.lower() == 'insert':

        json_response = {'message': 'Associations and Ground truth saved.'}
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username)
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response)

        concepts = request_body_json['linked']
        ## print(concepts)
        #concepts = ['{"semantic_area":"Diagnosis", "concept_url":"http://purl.obolibrary.org/obo/MONDO_0006498", "mention_text":"tubular adenoma", "start":1620, "stop":1634}',
        #'{"semantic_area":"Test", "concept_url":"http://purl.obolibrary.org/obo/MONDO_0006498", "mention_text":"moderate dysplasia.", "start":1641, "stop":1659}']

        #In this case the user manually deletes all the associations (NOT WITH CLEAR BUTTON) and saves.
        if len(concepts) == 0 and Linked.objects.filter(username=user, id_report=report1, language=language).exists():
            try:
                with transaction.atomic():
                    json_response = delete_all_associations(user, report1,language, type,usecase)
                #js = clean_mentions(user,report1,language)
                return JsonResponse(json_response)
            except (Exception) as error:
                # print(error)
                json_response = {'error': 'Sorry, an erorr occurred, rolled back.'}
                return JsonResponse(json_response, status=500)

        elif len(concepts) == 0 and not Linked.objects.filter(username=user, id_report=report1, language=language).exists():
            json_response ={'message':'Nothing to do'}
            return JsonResponse(json_response)

        # mention_texts = request.POST.getlist('vals')
        # indexes = request.POST.getlist('indexes')
        # conceptUrls = request.POST.getlist('concept_url')
        # semantic_area = request.POST.getlist('semantic_area')

        update = True
        existing_rows = Linked.objects.filter(username=user, id_report=report1, language=language)
        if existing_rows.exists():
            if existing_rows.count() == len(concepts):

                for concept in concepts:
                    #conc = json.loads(concept)
                    conc = concept
                    ment = Mention.objects.filter(start=conc['start'], stop=conc['stop'],
                                                       mention_text=conc['mention_text'],
                                                       id_report=report1, language=language)

                    if ment.exists():
                        ment = ment.first()
                        concept_model = Concept.objects.get(concept_url=conc['concept_url'])
                        area = SemanticArea.objects.get(name=conc['semantic_area'])
                        anno = Linked.objects.filter(username=user, id_report=report1, language=language,
                                                       start=ment, stop=ment.stop,concept_url = concept_model,name=area)
                        if anno.exists():
                            update = False
                        else:
                            update = True
                            break
                    else:  # Se anche una sola instanza è differente allora faccio update
                        update = True
                        break


        if update == True:

            try:
                with transaction.atomic():
                    # json_resp_delete = delete_all_associations(user, report1,language, type,usecase)
                    # # print(json_resp_delete)
                    json_response = update_associations(concepts, user, report1,language,usecase)
                    # print(json_response)
                    if GroundTruthLogFile.objects.filter(username=user, language = language,id_report=report1, gt_type='concept-mention').exists():
                        obj = GroundTruthLogFile.objects.filter(username=user, language = language,id_report=report1, gt_type='concept-mention')
                        obj.delete()
                    jsonDict = serialize_gt(type, usecase, username, report_id,language)
                    groundtruth = GroundTruthLogFile.objects.create(username=user, language = language,id_report=report1, gt_json=jsonDict, gt_type=type,
                                                          insertion_time=Now())
                    # print('salvo gt')
                    ## print(groundtruth)

            except (Exception) as error:
                # print(error)
                json_response = {'error': 'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response,status=500)
        else:
            json_response = {'message': 'Nothing changed'}



        return JsonResponse(json_response)



    elif request.method == 'POST' and action.lower() == 'update_concepts':


        user = User.objects.get(username = username)
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        report1 = Report.objects.get(id_report=report_id, language=language)
        # print(report_id)
        prev_ass = Linked.objects.filter(username = user, language = language, id_report = report1)
        prev_cont = Contains.objects.filter(username = user, language = language, id_report = report1)
        prev_concepts = []
        prev_cont_concepts = []
        concepts = request_body_json['concepts']
        # print(concepts)
        if len(concepts)>0:
            next_ass_concepts = []
            # for el in prev_ass:
            #     # print(el)
            #     concept = Concept.objects.get(concept_url = el['concept_url'])
            #     prev_concepts.append(concept.concept_url)
            #
            # for el in prev_cont:
            #     concept = Concept.objects.get(concept_url=el['concept_url'])
            #     prev_cont_concepts.append(concept.concept_url)
            #
            # for el in concepts:
            #     concept = Concept.objects.get(concept_url=el['concept_url'])
            #     next_ass_concepts.append(concept.concept_url)


            update = False
            try:
                with transaction.atomic():
            #In questo caso aggiungo e basta!! Non posso rimuoverli, quindi vedo se esistono e in caso li aggiungo
                    for concept in concepts:
                        concept = json.loads(concept)

                        # print(concept)
                        concept_db = Concept.objects.get(concept_url=concept['concept_url'])
                        area_db = SemanticArea.objects.get(name=concept['semantic_area'])
                        contains = Contains.objects.filter(username = user, language = language, id_report = report1, concept_url=concept_db,name=area_db)
                        if not contains.exists():
                            update = True
                            c = Contains.objects.create(username = user,language = language, id_report = report1, concept_url=concept_db,name=area_db,insertion_time = Now() )


                    if update == True:
                        if GroundTruthLogFile.objects.filter(username=user, id_report=report1, language=language,
                                                             gt_type='concepts').exists():
                            GroundTruthLogFile.objects.filter(username=user, id_report=report1, language = language, gt_type='concepts').delete()

                        jsonDict = serialize_gt(type, usecase, username, report_id,language)
                        groundtruth = GroundTruthLogFile.objects.create(username=user, id_report=report1, language = language, gt_json=jsonDict,
                                                                                gt_type='concepts',insertion_time=Now())
                        # print('salvo gt')
                        ## print(groundtruth)
                        json_response = {'message':'update successful'}
                        return JsonResponse(json_response)
                    else:
                        json_response = {'message': 'nothing to update'}
                        return JsonResponse(json_response)
            except (Exception) as error:
                # print(error)
                json_response = {'error': 'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response,status=500)
        else:

            json_response = {'message': 'Empty list.'}

            return JsonResponse(json_response)


# END CONCEPT - MENTIONS WITH AJAX

#CONTAINS
#@login_required(login_url='/login')
def concepts(request):
    username = request.session.get('username',False)
    context = {'username':username}
    return render(request, 'MedTag_app/test/test-contains.html', context)

def contains(request, action=None):
    username = request.session.get('username', False)
    language = request.session.get('language', False)
    # # print("username: "+username)

    error_json = {"Error": "No user authenticated"}

    if (username):
        response_json = {}
        context = {'username': username}
        if request.method == 'GET':
            report = request.GET.get('report_id')
            report1 = Report.objects.get(id_report=report, language = language)
            user = username
            user = User.objects.get(username = username)
            #try:
            #     a = Contains.objects.filter(username=user, id_report=report1, language=language)
            #     json_dict = {}
            #     json_dict['concepts'] = []
            #     reports = {}
            #     for con in a:
            #         semanticArea = SemanticArea.objects.get(name=con.name_id)
            #         concept = Concept.objects.get(concept_url = con.concept_url_id)
            #         report_dict = {"concept_url": str(concept.concept_url),
            #                        "concept_name": str(concept.name),
            #                        "semantic_area": str(semanticArea.name)}
            #         namesem = semanticArea.name
            #         reports[str(namesem)].append(report_dict)
            #     json_dict['concepts'] = reports
            #     return JsonResponse(json_dict)
            # except Exception as error:
            #     # print(error)
            #     json_dict = {'error':'an error occurred'}
            #     return JsonResponse(json_dict)
            response_json = get_contains_records(report=report1, language=language, user=user)
            return JsonResponse(response_json)

        elif request.method == 'POST' and action.lower() == 'insert':
            request_body_json = json.loads(request.body)
            concepts_list = request_body_json['concepts_list']
            report = request_body_json['report_id']
            report1 = Report.objects.get(id_report=report)

            username = request.session.get('username', False)
            user1 = User.objects.get(username=username)
            usecase = request.session.get('usecase',False)
            type = 'concepts'

            #concepts_list = request.POST.getList('concept_list',None)
            # element of concept_list: {'concept_url':'','semantic_area':''}

            #concepts_list = ['{"semantic_area":"Diagnosis","concept_url":"http://purl.obolibrary.org/obo/MONDO_0006498"}','{"semantic_area":"Procedure","concept_url":"http://purl.obolibrary.org/obo/NCIT_C4847"}']
            if report is not None and concepts_list is not None:
                user = username
                #semantic_area = request.POST.get("semantic_area")
                count = 0
                already_inserted_list = []
                try:
                    with transaction.atomic():
                        for concept in concepts_list:

                            concept = json.loads(concept)
                            # print(concept)
                            concept_url = concept['concept_url']
                            semantic_area = concept['semantic_area']
                            if not check_concept_report_existance(report, concept_url, user, semantic_area,language):
                                # Insert a new record
                                if populate_contains_table(report, concept_url, user, semantic_area,language):
                                    count += 1
                                else:
                                    error_json = {"error message": "insert in table 'contains' failed"}
                                    return JsonResponse(error_json)
                            else:
                                already_inserted_list.append(concept)
                        jsonDict = serialize_gt(type, usecase, username, report,language)
                        groundtruth = GroundTruthLogFile.objects.create(username=user1, id_report=report1,
                                                                        language = language,
                                                                        gt_json=jsonDict,
                                                                        gt_type=type, insertion_time=Now())
                        # print(groundtruth)
                except (Exception) as error:
                     print(error)
                     print('rolled back')

                if count == len(concepts_list):
                    response_json = {"message": "All concepts inserted successfully"}
                else:
                    response_json = {"message": "Some concepts have been already inserted: ["+ ", ".join(already_inserted_list)+"]"}
            else:
                response_json = {"error": "Missing data"}

        elif request.method == 'POST' and action.lower() == 'update':
            request_body_json = json.loads(request.body)
            concepts_list = request_body_json['concepts_list']
            report = request_body_json['report_id']
            report1 = Report.objects.get(id_report = report,language = language)
            username = request.session.get('username',False)
            user1 = User.objects.get(username = username)
            usecase = request.session.get('usecase',False)
            #usecase = 'Colon' #fase test
            type = 'concepts'


            #concepts_list = ['{"semantic_area":"Diagnosis","concept_url":"http://purl.obolibrary.org/obo/MONDO_0006498"}','{"semantic_area":"Procedure","concept_url":"http://purl.obolibrary.org/obo/NCIT_C4847"}']



            if report is not None and concepts_list is not None:
                user = username
                #semantic_area = request.POST.get("semantic_area")
                count = 0




                rows = Contains.objects.filter(username = user1, id_report = report1, language = language)
                if rows.exists() and len(concepts_list) == 0:
                    with transaction.atomic():
                        json_response=delete_contains_record(report1, language, None, user, None)
                        return JsonResponse(json_response,safe=False)
                elif not rows.exists() and len(concepts_list) == 0:
                    json_response = {'message':'nothing to do'}
                    return JsonResponse(json_response)

                update = True
                if rows.exists():
                    if rows.count() == len(concepts_list):
                        for concept in concepts_list:
                            ## print('concetto',concept)

                            concept_url = concept['concept_url']
                            semantic_area = concept['semantic_area']
                            concept_model = Concept.objects.get(concept_url = concept_url)
                            concepts = Contains.objects.filter(name=semantic_area, username = user1, id_report = report1, language = language, concept_url = concept_model)
                            if concepts.exists():
                                update = False
                            else:
                                update = True
                                break

# Delete previous data for the specified user and report
                if update == True:
                    try:
                        with transaction.atomic():
                            js = delete_contains_record(report1,language, None, user, None)
                            # Insert new data
                            for concept in concepts_list:
                                    # Insert a new record
                                    concept_url = concept['concept_url']
                                    semantic_area = concept['semantic_area']
                                    if populate_contains_table(report, concept_url, user, semantic_area,language):
                                        count += 1
                                    else:
                                        error_json = {"error message": "insert in table 'contains' failed"}
                                        return JsonResponse(error_json)
                            jsonDict = serialize_gt(type, usecase, username, report,language)
                            if GroundTruthLogFile.objects.filter(username=user1, id_report=report1,language = language, gt_type=type).exists():
                                GroundTruthLogFile.objects.filter(username=user1, id_report=report1, language=language,gt_type=type).delete()

                            groundtruth = GroundTruthLogFile.objects.create(username=user1, id_report=report1,
                                                                            gt_json=jsonDict,language = language,
                                                                            gt_type=type, insertion_time=Now())
                            ## print(groundtruth)

                    except (Exception) as error:
                         print(error)
                         print('rolled back')

                    if count == len(concepts_list):
                        response_json = {"message": "Update successfull"}
                    else:
                        response_json = {"error": "Update unsuccessfull"}
            else:
                response_json = {"error": "Missing data"}


        elif request.method == 'POST' and action.lower() == 'delete':

            request_body_json = json.loads(request.body)
            report = request_body_json['report_id']
            report1 = Report.objects.get(id_report=report,language = language)
            username = request.session.get('username', False)
            user1 = User.objects.get(username=username)
            usecase = request.session.get('usecase',False)
            type = 'concepts'

            if report is not None and language is not None:
                response_json = delete_contains_record(report, language, None, user1, None)
            else:
                response_json = {"Error": "Missing data"}

        return JsonResponse(response_json)

    else:
        return JsonResponse(error_json)

# TEST AND OTHER FUNCTIONS
# This view allows to test the four actions a user can perform.
def test(request, table):
    username = request.session.get('username', False)
    # print("username: "+username)

    error_json = {"Error": "No user authenticated"}

    if (username):
        context = {'username': username}
        if table == "contains":
            return render(request, 'MedTag_app/test/test-contains.html', context)
        elif table == "associate":
            return render(request, 'MedTag_app/test/test-annotation.html', context)
        elif table == "annotate":
            return render(request, 'MedTag_app/test/test-mentions.html', context)
        elif table == 'linked':
            return render(request, 'MedTag_app/test/test-linked.html', context)


    return JsonResponse(error_json)



# This view returns the list of reports related to a single usecase and language selected by the user.
def get_reports(request):

    inst = request.GET.get('institute',None)
    use = request.GET.get('usec',None)
    lang = request.GET.get('lang',None)
    if(inst != None and use != None and lang != None):
        rep = Report.objects.filter(institute = inst, name = use, language = lang)
        json_count = {'count':len(rep)}
        return JsonResponse(json_count)

    usecase = request.session.get('usecase',None)
    language = request.session.get('language',None)
    institute = request.session.get('institute',None)
    username = request.session['username']
    token = request.GET.get('configure',None)
    # usecase = 'Lung'
    # language = 'Italian'
    jsonError = {'error':'something wrong with params!'}
    if usecase is not None and language is not None and institute is not None:
        reports1 = Report.objects.filter(name = usecase, language = language, institute = institute)
        json_resp = {}
        json_resp['report'] = []
        #reps = []
        if reports1.exists():
            reports = reports1.values('id_report','report_json')
            #print(reports)
            for report in reports:
                json_rep = {}
                json_rep['id_report'] = report['id_report']
                json_rep['report_json'] = report['report_json']
                json_resp['report'].append(json_rep)

            json_resp['report'].sort(key=lambda json: json['id_report'], reverse=False)


            json_resp['index'] = 0


            if token is not None:
                # usecase = 'Lung'
                # language = 'Italian'
                gt = get_last_groundtruth(username, usecase, language, institute)

            else:
                gt = get_last_groundtruth(username)

            if gt is not None:
                id_report = gt['id_report']
                use = gt['use_case']
                lang = gt['language']
                institute = gt['institute']
                report_json = Report.objects.get(id_report = id_report, name = use, language = lang, institute = institute)
                rep_json = report_json.report_json
                index = json_resp['report'].index({'id_report':id_report,'report_json':rep_json})
                ## print('index',str(index))
                #arr1 = json_resp['report'][0:index]
                #arr2 = json_resp['report'][index:]
                json_resp['index'] = int(index)
                ## print('indicefinale',json_resp['index'])
                #arr3 = arr2 + arr1


                ## print(json_resp['report'][0])

        # if json_resp['report'].length==0:
        #     json_resp['message'] = 'No reports found.'

        return JsonResponse(json_resp)
    else: return JsonResponse(jsonError,status=500)

def get_admin(request):
    jsonResp = {}
    jsonResp['admin'] = ''
    # if User.objects.filter(profile = 'Admin').exists():
    #     name = User.objects.get(profile = 'Admin')
    if User.objects.filter(profile = 'Admin').exists():
        name = User.objects.get(profile = 'Admin')
        admin = name.username
        jsonResp['admin'] = admin

    return JsonResponse(jsonResp)

def check_input_files(request):

    reports = []

    labels = []
    concepts = []
    type1 = request.POST.get('type',None)
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)
    for filename, file in request.FILES.items():
        # name = request.FILES[filename].name
        if filename.startswith('reports'):
            reports.append(file)

        elif filename.startswith('concepts'):
            concepts.append(file)
        elif filename.startswith('labels'):
            labels.append(file)

    jsonDisp = request.POST.get('json_disp','')
    jsonAnn = request.POST.get('json_ann','')
    # print('ciao')
    # a = jsonDisp
    # print(type(a))
    # print(jsonDisp)
    # print(jsonAnn)
    jsonResp = check_file(type1,reports,labels,concepts,jsonDisp,jsonAnn,username,password)
    # if  len(json_keys) > 0:
    #     jsonResp = {'message': msg,'keys':json_keys}
    #     print(json_keys)
    # else:
    #     jsonResp = {'message':msg}
    print(jsonResp)

    return JsonResponse(jsonResp)

def get_gt_list(request):
    groundTruths = []
    json_resp = {}
    list_gt = GroundTruthLogFile.objects.all()
    for el in list_gt:
        groundTruths.append(el.gt_json)
    json_resp['ground_truths'] = groundTruths
    return JsonResponse(json_resp)

def check_files_for_update(request):
    reports = []
    usecase = []
    areas = []
    labels = []
    concepts = []
    jsonAnn = ''
    type1 = request.POST.get('type',None)
    username = request.POST.get('username',None)
    for filename, file in request.FILES.items():
        # name = request.FILES[filename].name
        if filename.startswith('reports'):
            reports.append(file)

        elif filename.startswith('concepts'):
            concepts.append(file)
        elif filename.startswith('labels'):
            labels.append(file)

    jsonDisp = request.POST.get('json_disp',None)
    jsonAnn = request.POST.get('json_ann',None)
    jsonDispUp = request.POST.get('json_disp_update',None)
    jsonAnnUp = request.POST.get('json_ann_update',None)
    # print('ciao')
    # a = jsonDisp
    # print(type(a))
    # print(jsonDisp)
    # print(jsonAnn)
    json_keys,msg = check_for_update(type1,reports,labels,concepts,areas,usecase,jsonDisp,jsonAnn,jsonDispUp,jsonAnnUp)
    if  len(json_keys) > 0:
        jsonResp = {'message': msg,'keys':json_keys}
        print(json_keys)
    else:
        jsonResp = {'message':msg}


    return JsonResponse(jsonResp)
from django.db import connection
def update_db(request):

    reports = []
    usecase = []
    areas = []
    labels = []
    concepts = []
    type1 = request.POST.get('type', None)
    for filename, file in request.FILES.items():
        # name = request.FILES[filename].name
        if filename.startswith('reports'):
            reports.append(file)

        elif filename.startswith('concepts'):
            concepts.append(file)
        elif filename.startswith('labels'):
            labels.append(file)


    jsonDisp = request.POST.get('json_disp', None)
    jsonAnn = request.POST.get('json_ann', None)

    jsonDispUp = request.POST.get('json_disp_update', '')
    jsonAnnUp = request.POST.get('json_ann_update', '')

    msg = update_db_util(type1,reports,labels,concepts,areas,usecase,jsonDisp,jsonAnn,jsonDispUp,jsonAnnUp)
    if msg['message'] == 'Ok':
        keys = get_fields_from_json()
        request.session['fields'] = keys['fields']
        request.session['fields_to_ann'] = keys['fields_to_ann']
    return JsonResponse(msg)





def configure_db(request):
    reports = []
    usecase = []
    areas = []
    labels = []
    concepts = []
    type = request.POST.get('type',None)
    for filename, file in request.FILES.items():
        # name = request.FILES[filename].name
        if filename.startswith('reports'):
            reports.append(file)
        elif filename.startswith('usecase'):
            usecase.append(file)
        elif filename.startswith('areas'):
            areas.append(file)
        elif filename.startswith('concepts'):
            concepts.append(file)
        elif filename.startswith('labels'):
            labels.append(file)

    jsonDisp = request.POST.get('json_disp',None)
    jsonAnn = request.POST.get('json_ann',None)
    jsonAll = request.POST.get('json_all',None)
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)

    msg = configure_data(reports,labels,areas,usecase,concepts,jsonDisp,jsonAnn,jsonAll,username,password)

    return JsonResponse(msg)

def get_keys(request):
    keys=[]
    reports = Report.objects.all()
    for report in reports:
        json_rep = report.report_json
        for el in json_rep.keys():
            if el not in keys:
                keys.append(el)
    json_resp = {'keys':keys}
    return JsonResponse(json_resp)

def download_ground_truths(request):
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path1 = os.path.join(workpath, './static/temp/temp.csv')
    if os.path.exists(path1):
        os.remove(path1)
    username = request.session['username']
    inst = request.GET.get('institute',None)
    if inst == '':
        inst = None
    use = request.GET.get('usec',None)
    if use == '':
        use = None
    all = request.GET.get('all_gt',None)
    lang = request.GET.get('lang',None)
    if lang == '':
        lang = None
    action = request.GET.get('action',None)
    format = request.GET.get('format',None)
    json_resp = {}
    json_resp['ground_truth'] = []
    if format == 'json' or all =='all' :
        json_resp = create_json_to_download(username,use,inst,lang,action,all)
        return JsonResponse(json_resp)

    elif format == 'csv':
        content = create_csv_to_download(username,use,inst,lang,action)
        if content:
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            path = os.path.join(workpath, './static/temp/temp.csv')
            path = open(path,'r')
            return HttpResponse(path, content_type='text/csv')



def download_all_ground_truths(request):
    json_resp = {}
    json_resp['ground_truth'] = []
    gt = GroundTruthLogFile.objects.all()
    for el in gt:
        gt_json = el.gt_json
        json_resp['ground_truth'].append(gt_json)


    return JsonResponse(json_resp)


# Ritorno un array di true e false: per ogni report viene tornato TRUE se l'utente ha annotato, false se non ha annotato
from datetime import datetime, timezone
def get_reports_from_action(request):
    username = request.session['username']
    usecase = request.session['usecase']
    language = request.session['language']


    report_to_ret = []
    action = request.GET.get('action',None)
    user = User.objects.get(username = username)
    gt = GroundTruthLogFile.objects.filter(username = user, language = language, gt_type = action)
    if gt.exists():
        id = ''
        for element in gt:

            ## print(element.insertion_time.replace(tzinfo=timezone.utc).astimezone(tz=None))
            val = (element.id_report_id,element.insertion_time.replace(tzinfo=timezone.utc).astimezone(tz=None))

            report_to_ret.append(val)


    jsonDict = {}
    jsonDict['reports_presence'] = report_to_ret
    return JsonResponse(jsonDict)



def get_last_gt(request):
    # print('LAST GT')
    #
    # username = 'ornella_irrera'
    # usecase = 'Colon'
    # language = 'English'
    # institute = 'AOEC - Azienda Ospedaliera Cannizzaro'
    username = request.session['username']
    language = request.session['language']
    usecase = request.session['usecase']
    institute = request.session['institute']
    # # print('language123',language)
    # # print('usecase123',usecase)
    # # print('institute123',institute)
    #language = request.session['language']

    user = User.objects.get(username = username)
    jsonDict = {}
    gt_json = ''
    token = request.GET.get('configure',None)
    # msg_json = {'message':'No groundtruth associated to this user!'}
    if token is None:
        gt_json = get_last_groundtruth(username)

    else:
        # usecase = 'Lung'
        # language = 'Italian'
        gt_json = get_last_groundtruth(username,usecase,language,institute)
        # print(get_last_groundtruth(username,usecase,language,institute))

    if gt_json is None:
        jsonDict['groundtruth'] = ''
        jsonDict['report'] = ''
        jsonDict['report_id'] = ''
    else:
        jsonDict['groundtruth'] = gt_json
        id_report = gt_json['id_report']
        language = gt_json['language']
        report = Report.objects.get(id_report=id_report, language=language)
        jsonDict['report'] = report.report_json
        jsonDict['report_id'] = id_report
    return JsonResponse(jsonDict)


# This view return a json response containing all the concept_urls related to a semantic_area.
from django.db import connection

def conc_view(request):
    usecase = request.session['usecase']
    jsonDict = {}
    concepts = {}
    jsonDict['concepts'] = []
    # diagnosis = get_concepts_by_usecase_area(usecase, 'Diagnosis')
    # anatomical = get_concepts_by_usecase_area(usecase, 'Anatomical Location')
    # procedure = get_concepts_by_usecase_area(usecase, 'Procedure')
    # test = get_concepts_by_usecase_area(usecase, 'Test')
    # general = get_concepts_by_usecase_area(usecase, 'General Entity')
    notEmpty = False
    areas = SemanticArea.objects.all()
    for area in areas:
        name = area.name
        concepts[name] = get_concepts_by_usecase_area(usecase, name)

    for area in areas:
        name = area.name
        if len(concepts[name]) > 0:
            notEmpty = True
            break
    if notEmpty == True:
        jsonDict['concepts'] = concepts
    else:
        jsonDict['concepts'] = []
    # jsonDict['Diagnosis'] = diagnosis
    # jsonDict['Anatomical Location'] = anatomical
    # jsonDict['Procedure'] = procedure
    # jsonDict['Test'] = test
    # jsonDict['General Entity'] = general
    return JsonResponse(jsonDict)

def get_semantic_area(request):
    json_dict = {}
    arr = []
    arr_sem = SemanticArea.objects.all().values('name')
    for area in arr_sem:
        arr.append(area['name'])
    json_dict['area'] = arr
    return JsonResponse(json_dict)


# This view returns the json of a specific report defined by its id and its language.
def report(request,report_id,language):
    json_resp = {}
    error_json = {'error':'the report does not exist!'}

    if Report.objects.filter(id_report = report_id, language = language).exists():
        report = Report.objects.get(id_report = report_id, language = language)
        json_resp['report_json'] = report.report_json
        # report1 = json.dumps(report.report_json)
        # json_resp['report_json'] = report1
        # # print(json_resp['report_json'])
        # # print(type(report1))
        return JsonResponse(json_resp['report_json'])

    return error_json



def report_start_end(request):
    count_words = 0
    report = request.GET.get('report_id')
    usecase = request.session['usecase']

    #json_resp = get_fields_from_json_usecase(usecase)


    json_keys_to_display = request.session['fields']
    json_keys_to_ann = request.session['fields_to_ann']

    json_keys = json_keys_to_display + json_keys_to_ann
   # print(json_keys_to_display)
    language = request.session['language']

    json_dict = {}
    json_dict['rep_string'] = {}
    report_json = Report.objects.get(id_report = report, language = language)
    report_json = report_json.report_json
   # print(report_json)
    #convert to string
    report_string = json.dumps(report_json)
   # print(report_string)
    try:
        for key in json_keys:
            # print(report_json[key])
            if(report_json.get(key) is not None and report_json.get(key) != ""):
                element = report_json[key]
                element_1 = json.dumps(element)
                if element_1.startswith('"') and element_1.endswith('"'):
                    element_1 = element_1.replace('"','')
                # if not isinstance(element, int):
                #     count = element.split(' ')
                #     if key in json_keys_to_ann:
                #         print(key +' : '+str(len(count)))
                #         count_words = count_words + len(count)
                #
                # else:
                #     if key in json_keys_to_ann:
                #         count = [1]
                #         count_words = count_words + 1
                before_element = report_string.split(key)[0]
                after_element = report_string.split(key)[1]
                until_element_value = len(before_element) + len(key) + len(after_element.split(str(element_1))[0])
                start_element = until_element_value + 1
                end_element = start_element + len(str(element_1)) - 1
                element = {'text':element, 'start':start_element,'end':end_element}
                json_dict['rep_string'][key] = element
                # if key in json_keys_to_ann:
                #     print(key)
                #     print(report_json[key])
                #     count_words = count_words + len(count)
                #     print(count_words)

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
    # print(json_dict)
    return JsonResponse(json_dict)

def get_usecase_inst_lang(request):
    jsonDict = get_distinct()


    return JsonResponse(jsonDict)





def get_fields(request):
    # print(os.getcwd())
    json_resp = {}
    json_resp['fields'] = []
    json_resp['fields_to_ann'] = []
    json_resp = get_fields_from_json_usecase(request.session['usecase'])


    return JsonResponse(json_resp)

import csv
from django.http import HttpResponse
def download_examples(request):
    # Create the HttpResponse object with the appropriate CSV header.
    file_required = request.GET.get('token',None)
    path = ''
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    if file_required == 'reports':
        path = os.path.join(workpath, './static/examples/report.csv')

    elif file_required == 'concepts':
        path = os.path.join(workpath, './static/examples/concept.csv')

    elif file_required == 'labels':
        path = os.path.join(workpath, './static/examples/labels.csv')



    content = open(path,'r')
    return HttpResponse(content, content_type='text/csv')

def download_templates(request):
    # Create the HttpResponse object with the appropriate CSV header.
    file_required = request.GET.get('token',None)
    path = ''
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in

    if file_required == 'reports':
        path = os.path.join(workpath, './static/templates/report.csv')

    elif file_required == 'concepts':
        path = os.path.join(workpath, './static/templates/concept.csv')

    elif file_required == 'labels':
        path = os.path.join(workpath, './static/templates/labels.csv')

    content = open(path,'r')
    return HttpResponse(content, content_type='text/csv')

def get_keys_from_csv(request):
    reports = []
    json_resp = {}
    for filename, file in request.FILES.items():
        # name = request.FILES[filename].name
        if filename.startswith('reports'):
            reports.append(file)

    json_resp['keys'] = get_keys_csv(reports)
    print(json_resp['keys'])
    return JsonResponse(json_resp)

def get_keys_from_csv_update(request):
    reports = []
    json_resp = {}
    for filename, file in request.FILES.items():
        # name = request.FILES[filename].name
        if filename.startswith('reports'):
            reports.append(file)

    json_resp['keys'] = get_keys_csv_update(reports)

    print(json_resp['keys'])
    return JsonResponse(json_resp)
#----------------------------------------------------------------------------------------------------------


