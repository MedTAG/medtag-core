from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.contrib.auth.models import User as User1
from django.contrib.auth.models import *
from MedTAG_sket_dock_App.utils import *
from MedTAG_sket_dock_App.utils_download import *
# from MedTAG_sket_dock_App.utils_CERT import *
from django.contrib.auth.decorators import login_required
import hashlib
from django.db import transaction
from MedTAG_sket_dock_App.utils_sket import *
from django.http import JsonResponse
from MedTAG_sket_dock_App.decorators import *
from MedTAG_sket_dock_App.data import *
from datetime import datetime, timezone
from MedTAG_sket_dock_App.utils_configuration_and_update import *
from django.db import connection
from django.http import HttpResponse


# ExaMode Ground Truth views here.
def index(request):

    """Home page for app (and project)"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')
#


def new_credentials(request):

    """Change session's parameters"""

    error_resp = {'error':'something went wrong with these options'}
    if request.method == 'POST':
        json_resp ={'message':'ok'}
        request_body_json = json.loads(request.body)
        usecase = request_body_json['usecase']
        request.session['usecase'] = usecase
        language = request_body_json['language']
        request.session['language'] = language
        institute = request_body_json['institute']
        request.session['institute'] = institute
        annotation = request_body_json['annotation']

        if annotation == 'Automatic':
            request.session['mode'] = 'Robot'
            groundtruths,groundtruths1 = check_user_agent_gt_presence(request.session['username'], usecase)
            # Copy the Robot's groundtruths if it is needed.
            if groundtruths == 0:
                result = copy_rows(usecase,language,institute,'Robot_user',request.session['username'])
                if result:
                    json_resp = {'msg':'ok'}
                else:
                    json_resp = {'error':'An error occurred'}

        else:
            request.session['mode'] = 'Human'
        data = get_fields_from_json()
        request.session['fields'] = data['fields']
        request.session['fields_to_ann'] = data['fields_to_ann']
        if request.session['mode'] == 'Robot':
            workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
            with open(os.path.join(workpath,'./automatic_annotation/auto_fields/auto_fields.json')) as out:
                data = json.load(out)
                request.session['fields_to_ann'] = data['extract_fields'][usecase]

        print(request.session['fields_to_ann'])
        return JsonResponse(json_resp)

    return JsonResponse(error_resp)


def logout(request):

    """Logout: deletion of session's parameters"""

    try:
        del request.session['username']
        del request.session['usecase']
        del request.session['language']
        del request.session['institute']
        del request.session['profile']
        del request.session['fields']
        del request.session['mode']
        del request.session['fields_to_ann']

        return redirect('MedTAG_sket_dock_App:login')
    except KeyError:
        pass
    finally:
        request.session.flush()

    return redirect('MedTAG_sket_dock_App:login')


def registration(request):

    """This view handles the registration of new users: username, password and profile are inserted in the database"""

    if request.method == 'POST':
        username = request.POST.get('username',None)
        password1 = request.POST.get('password',None)

        profile = request.POST.get('profile',None)
        # mode1 = request.POST.get('mode',None)
        # mode = NameSpace.objects.get(ns_id=mode1)
        if(profile is None):
            context = {'errorMessage': "Please set your profile."}
            return render(request, 'MedTAG_sket_dock_App/registration.html', context)

        if User.objects.filter(username = username).exists():
            context = {'errorMessage': "This username is not available. Please, choose another one."}
            return render(request, 'MedTAG_sket_dock_App/registration.html', context)
        try:
            with transaction.atomic():

                password = hashlib.md5(password1.encode()).hexdigest()
                ns_robot = NameSpace.objects.get(ns_id = 'Robot')
                ns_human = NameSpace.objects.get(ns_id = 'Human')
                User.objects.create(username = username,profile=profile,password = password,ns_id=ns_robot)
                User.objects.create(username = username,profile=profile,password = password,ns_id=ns_human)

                request.session['username'] = username
                request.session['mode'] = 'Human'
                request.session['profile'] = profile

                return redirect('MedTAG_sket_dock_App:index')
        except (Exception) as error:
            print(error)
            context = {'errorMessage': "Something went wrong, probably you did not set any profile"}
            return render(request, 'MedTAG_sket_dock_App/registration.html', context)
    return render(request, 'MedTAG_sket_dock_App/registration.html')


def credits(request):

    """Credits page for app"""

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')


def configure(request):

    """Configuration page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')


def team_members_stats(request):
    """Team members' stats page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if (username):
        context = {'username': username, 'profile': profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')


def updateConfiguration(request):

    """Update Configuration page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')


def infoAboutConfiguration(request):

    """Information about Configuration page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')


def tutorial(request):

    """Tutorial page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')


def my_stats(request):

    """User's reports stats page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')

def reports_stats(request):

    """Reports' stats page for app """

    username = request.session.get('username', False)
    profile = request.session.get('profile', False)
    if(username):
        context = {'username': username,'profile':profile}
        return render(request, 'MedTAG_sket_dock_App/index.html', context)
    else:
        return redirect('MedTAG_sket_dock_App:login')



def get_session_params(request):

    """This view returns the current session parameters """

    json_resp = {}
    usecase = request.session.get('usecase',None)
    language = request.session.get('language',None)
    institute = request.session.get('institute',None)
    annotation = request.session.get('mode',None)
    if usecase is not None and language is not None and institute is not None and annotation is not None:
        json_resp['usecase'] = usecase
        json_resp['language'] = language
        json_resp['institute'] = institute
        if annotation == 'Human':
            json_resp['annotation'] = 'Manual'
        elif annotation == 'Robot':
            json_resp['annotation'] = 'Automatic'
    else:
        json_resp['usecase'] = ''
        json_resp['language'] = ''
        json_resp['institute'] = ''
        json_resp['annotation'] = ''
    return JsonResponse(json_resp)


def login(request):

    """Login page for app """

    print('login')
    if request.method == 'POST':
        md5_pwd = ''
        admin = False

        username = request.POST.get('username', False)
        mode1 = 'Human'
        mode = NameSpace.objects.get(ns_id=mode1)
        password = request.POST.get('password', False)
        if username:
            username = username.replace("\"", "").replace("'", "")
        if password:
            password = password.replace("\"", "").replace("'", "")
            md5_pwd = hashlib.md5(password.encode()).hexdigest()
        if (username != False and password != False):
            user = User.objects.filter(username = username,ns_id=mode, password = md5_pwd)


            if user.exists():
                # print('LOGGATO')
                mode1 = 'Human'
                mode = NameSpace.objects.get(ns_id=mode1)
                user = User.objects.get(username=username, password=md5_pwd,ns_id=mode)
                print("username: " + username)
                request.session['username'] = username
                request.session['mode'] = mode1
                request.session['profile'] = user.profile
                return redirect('MedTAG_sket_dock_App:index')
                #return redirect('MedTAG_sket_dock_App:select_options')

        profile_list = User.objects.values_list('profile', flat=True).distinct()
        if 'Admin' in profile_list:
            admin = True
        context = {'errorMessage': "Your username and password didn't match.","admin":admin}
        return render(request, 'MedTAG_sket_dock_App/login.html', context)

    else:
        username = request.session.get('username', False)
        admin = False
        profile_list = User.objects.values_list('profile', flat=True).distinct()
        if 'Admin' in profile_list:
            admin = True
        context = {'admin': admin}

        if username:
            return redirect('MedTAG_sket_dock_App:index')

        return render(request, 'MedTAG_sket_dock_App/login.html',context)


def annotationlabel(request,action=None):

    """This view handles the GET and POST requestes for LABELS ANNOTATION ACTION

    .js files: Baseindex.js Buttons.js SubmitButtons.js NextPrevButtons.js """

    username = request.session['username']
    mode1 = request.session['mode']
    auto_required = request.GET.get('ns_id', None)
    mode = NameSpace.objects.get(ns_id=mode1)

    print('mode',mode1)
    usecase = request.session['usecase']
    language = request.session['language']
    type = 'labels'

    if request.method == 'GET' and action.lower() == 'user_labels':

        """GET request: given the report, the labels annotated by the user are returned"""


        user_get = request.GET.get('username',username)
        report_id = request.GET.get('report_id')
        report1 = Report.objects.get(id_report = report_id,language = language)
        # if auto_required == 'Robot':
        #     mode = NameSpace.objects.get(ns_id=auto_required)
        if auto_required is not None:
            mode_1 = NameSpace.objects.get(ns_id=auto_required)
        else:
            mode_1 = mode
        json_dict = get_user_gt(user_get,mode_1,report1,language,'labels')

        return JsonResponse(json_dict)

    elif request.method == 'GET' and action.lower() == 'all_labels':

        """ GET request: given the usecase, all the labels associated to that usecase are returned. """

        labels = AnnotationLabel.objects.filter(name=usecase).values('seq_number','label')
        json_dict = {}
        count = get_labels_exa_count()
        if len(labels) > 0:
            json_dict['labels'] = []
            if mode1 == 'Human':
                for el in labels:
                    json_val = {}
                    if int(el['seq_number']) > count: # i primi 20 sono inseriti automaticamente
                        json_val['label'] = (el['label'])
                        json_val['seq_number'] = (el['seq_number'])
                        json_dict['labels'].append(json_val)
            elif mode1 == 'Robot' or auto_required == 'Robot':
                for el in labels:
                    json_val = {}
                    if int(el['seq_number']) <= count: # i primi 20 sono inseriti automaticamente
                        json_val['label'] = (el['label'])
                        json_val['seq_number'] = (el['seq_number'])
                        json_dict['labels'].append(json_val)

        else:
            json_dict['labels'] = []
        json_dict['labels'] = sorted(json_dict['labels'], key=lambda json: json['seq_number'])
        return JsonResponse(json_dict)

    elif request.method == 'POST' and action.lower() == 'delete':

        """PSOT request: given the report, the labels the user annotated are removed together with the
         associated groundtruth."""

        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username,ns_id=mode)
        language = request.session['language']
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting parameters.'}
            return json_response
        to_del = Associate.objects.filter(username=user, ns_id=mode, id_report=report1, language=language)
        if mode1 == 'Human':
            try:
                with transaction.atomic():

                    if to_del.exists():
                        json_response = delete_all_annotation(to_del, user, report1,language, type,mode)
                        # update_majority_vote_GT_labels(report_id,language,request.session['mode'])

                    else:
                        json_response = {'msg':'nothing to do'}

            except Exception as error:
                print(error)
                json_response = {'error': 'An error occurred saving the ground_truth and the labels'}
                return JsonResponse(json_response)
            else:
                return JsonResponse(json_response)
        else:
            to_del = Associate.objects.filter(id_report=report1, language=language, username=user, ns_id=mode)
            json_response = restore_robot_annotation(to_del, 'labels',user)
            return JsonResponse(json_response)

    if request.method == 'POST' and action.lower() == 'insert':

        """PSOT request: given the report, the labels the user annotated are added in the database and a new 
        JSON groundtruth is created. """

        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username,ns_id=mode)
        language = request.session['language']
        report1 = Report.objects.get(id_report=report_id,language = language)

        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response)

        labels_to_save = request_body_json['labels']
        # In this case the user manually deletes all the labels (NOT WITH CLEAR BUTTON) and saves.
        if len(labels_to_save) == 0 and  mode1 == 'Human':

            """If there are not labels to save, if there is a ground truth saved in the database, this is removed,
             otherwise no action is performed. """

            rows = Associate.objects.filter(username = user,ns_id=mode, id_report = report1, language = language)
            if rows.exists():
                try:
                    with transaction.atomic():
                        json_response = delete_all_annotation(rows,user,report1,language,type,mode)
                        # update_majority_vote_GT_labels(report_id,language,request.session['mode'])

                except Exception as error:
                    print(error)
                    json_response = {'error': 'An error occurred.'}
                    return JsonResponse(json_response, status=500)
                else:
                    return JsonResponse(json_response)
            else:
                json_response = {'message': 'Nothing to save.'}
                return JsonResponse(json_response)

        if len(labels_to_save) == 0 and mode1 == 'Robot':

            """ If there are not labels to save and the name space is Robot no action is performed and the already 
            existing ground-truth is kept """
            to_del = Associate.objects.filter(id_report=report1, language=language, username=user, ns_id=mode)
            json_response = restore_robot_annotation(to_del, 'labels',user)
            return JsonResponse(json_response)

        update = True

        """ Check if the user's labels she inserted are as many as the rows already present in the db: 
        if they are not: update the annotation: the old annotation is replaced with the new one
        if they are: check if the labels existing are those inserted, in this case nothing is done, otherwise 
        the current groundtruth is updated. """

        existing_rows = Associate.objects.filter(username = user,ns_id=mode, id_report =report1,language =language)
        if existing_rows.exists():
            if existing_rows.count() == len(labels_to_save):
                for label in labels_to_save:
                    label1 = AnnotationLabel.objects.get(name=usecase, label=label['label'], seq_number=label['seq_number'])
                    if not Associate.objects.filter(username=user,ns_id=mode, seq_number=label1.seq_number, label=label1,
                                                    id_report=report1, language=language).exists():
                        update = True
                        break
                    else:
                        update = False
        if update == True:
            try:
                with transaction.atomic():
    # Remove all the existing labels inserted by the user for that report. The existing ground truth is kept untile the deletion is successful
                    to_del = Associate.objects.filter(username=user,ns_id=mode, id_report=report1,language = language)
                    delete_all_annotation(to_del,user,report1,language,type,mode)

                    json_resp_labels = update_annotation_labels(labels_to_save,usecase,user,report1,language,mode)

                    jsonDict = serialize_gt(type, usecase, username, report_id,language,mode)
                    GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language = language,
                                                      gt_json=jsonDict, gt_type=type,insertion_time=Now())
                    # update_majority_vote_GT_labels(report_id,language,request.session['mode'])

            except (Exception) as error:
                print(error)
                print('rolled back')
                json_response = {'error': 'An error occurred saving the ground_truth '
                                          'and the labels, the transaction rolledback'}
                return JsonResponse(json_response)

            else:
                return JsonResponse(json_resp_labels)
        else:
            if mode1 == 'Human':
                json_response = {'message':'no changes detected'}
                return JsonResponse(json_response)

            elif mode1 == 'Robot':

                """ In this section the name space Robot is handled: If the user is in the AUTOMATIC MODE and the labels
                she inserts are those annotated by the algorithm, this means that she agrees with the annotation of the 
                Robot user. The annotation does not change, only the insertion time is changed."""

                try:
                    with transaction.atomic():
                        # in questa sezione solo se la gt è uguale a prima, l'utente acconsente alla gt della macchina
                        user_robot = User.objects.get(username='Robot_user', ns_id=mode)
                        gt_robot = GroundTruthLogFile.objects.filter(username=user_robot, ns_id=mode,
                                                                     id_report=report1, language=language,
                                                                     gt_type='labels')

                        gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report1,
                                                               language=language,
                                                               gt_type='labels')
                        if gt.count() == 1 and gt_robot.count() == 1:
                            if gt_robot[0].insertion_time == gt[0].insertion_time:
                                js = gt[0].gt_json
                                GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report1,
                                                                  language=language,
                                                                  gt_type='labels').delete()

                                GroundTruthLogFile.objects.create(gt_json=js, insertion_time=Now(), username=user,
                                                                  ns_id=mode, id_report=report1, language=language,
                                                                  gt_type='labels')

                                ass = Associate.objects.filter(username=user, id_report=report1, language=language,
                                                               ns_id=mode).values('label', 'seq_number')
                                for el in ass:
                                    lab = AnnotationLabel.objects.get(label=el['label'], seq_number=el['seq_number'])
                                    Associate.objects.filter(username=user, ns_id=mode, label=lab, seq_number=lab.seq_number,
                                                             id_report=report1, language=language).delete()
                                    Associate.objects.create(username=user, ns_id=mode, label=lab, seq_number=lab.seq_number,
                                                             insertion_time=Now(), id_report=report1, language=language)

                except Exception as error:
                    print(error)
                    print('rolled back')
                    json_response = {'error': 'An error occurred updating labels dates'}
                    return JsonResponse(json_response)
                else:
                    json_response = {'message': 'dates updated'}
                    return JsonResponse(json_response)


def mention_insertion(request,action=None):
    """
    This view handles the GET and POST requests concerning the mentions identification action

    .js files: Baseindex.js Buttons.js SubmitButtons.js NextPrevButtons.js Association.js"""

    username = request.session['username']
    mode1 = request.session['mode']
    mode = NameSpace.objects.get(ns_id=mode1)

    language = request.session['language']
    usecase = request.session['usecase']
    type = 'mentions'

    if request.method == 'GET':

        """ GET request: it returns the list of mentions associated to a specific report the user already inserted. """

        report_id = request.GET.get('report_id')
        report1 = Report.objects.get(id_report=report_id,language=language)
        user_get = request.GET.get('username',username)
        try:
            # if auto_required == 'Robot':
            #     mode = NameSpace.objects.get(ns_id=auto_required)
            auto_required = request.GET.get('ns_id', None)
            if auto_required is not None:
                mode_1 = NameSpace.objects.get(ns_id=auto_required)
            else:
                mode_1 = mode
            json_dict = get_user_gt(user_get,mode_1,report1,language,'mentions')
            return JsonResponse(json_dict)

        except Exception as error:
            print(error)
            json_response = {'error': 'Sorry, an error occurred during the GET request.'}
            return JsonResponse(json_response,status=500)

    elif request.method == 'POST' and action.lower() == 'delete':

        """POST request: it deletes all the mentions the user inserted for a specific report together with the 
        associated ground-truth."""

        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username,ns_id=mode)
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting parameters.'}
            return JsonResponse(json_response,status=500)

        ass = Annotate.objects.filter(username=user,ns_id=mode, id_report=report1.id_report,language = language).values('start', 'stop')
        if len(ass) == 0:
            json_response = {'message': 'Nothing to delete.'}
            return JsonResponse(json_response)

        if mode1 == 'Human':
            try:
                with transaction.atomic():
                    json_response = delete_all_mentions(user, report1,language, type,usecase,mode)
                    # update_majority_vote_GT_mentions(report_id,language,request.session['mode'])

            except (Exception) as error:
                print(error)
                json_response = {'error': 'An error occurred.'}
                return JsonResponse(json_response, status=500)
            else:
                return JsonResponse(json_response)
        else:

            """If the user chose AUTOMATIC MDOE it is impossible to delete the ground truth. If the user did not 
            modified the annotation created by the algorithm that one is kept, otherwise it is kept the one modified 
            by the user."""
            to_del = Annotate.objects.filter(username = user, ns_id = mode, id_report  = report1,language = language)
            json_response = restore_robot_annotation(to_del,'mentions',user)
            return JsonResponse(json_response)

    elif request.method == 'POST' and action.lower() == 'insert':

        """ POST request: the mentions found by the user (if any) are saved and a ground-truth is created. """

        json_response = {'message':'Mentions and Ground truth saved.'}
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username = username,ns_id=mode)
        report1 = Report.objects.get(id_report = report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response,status=500)

        mentions = request_body_json['mentions']
        # In this case the user manually deletes all the mentions (NOT WITH CLEAR BUTTON) and saves.
        if len(mentions) == 0 and mode1 == 'Human':

            """ If the annotation mode is MANUAL the ground-truth and the annotation of the report is removed. """

            if Annotate.objects.filter(username = user,ns_id=mode, id_report =report1,language =language).exists():
                try:
                    with transaction.atomic():
                        json_response = delete_all_mentions(user, report1,language, type,usecase,mode)
                        # update_majority_vote_GT_mentions(report_id,language,request.session['mode'])

                except Exception as error:
                    print(error)
                    json_response = {'error': 'An error occurred.'}
                    return JsonResponse(json_response, status=500)
                else:
                    return JsonResponse(json_response)

            else:
                json_response = {'message': 'Nothing to do'}
                return JsonResponse(json_response)

        if len(mentions) == 0 and mode1 == 'Robot':
            """ If the name space is ROBOT the ground-truth and the annotation cannot be removed """
            to_del = Annotate.objects.filter(username = user,language = language,id_report = report1,ns_id = mode)
            json_response = restore_robot_annotation(to_del,'mentions',user)
            # json_response = {'message': 'Nothing to do'}
            return JsonResponse(json_response)

        update = True

        """ Check if the user's mentions she inserted are as many as the rows already present in the db: 
        if they are not: update the annotation: the old annotation is replaced with the new one
        if they are: check if the existing mentions are those inserted, in this case nothing is done, otherwise 
        the current groundtruth is updated."""

        existing_rows = Annotate.objects.filter(username = user,ns_id=mode, id_report =report1,language =language)
        if existing_rows.exists():
            if existing_rows.count() == len(mentions):

                for ment in mentions:
                    mentionDB = Mention.objects.filter(start=int(ment['start']),stop=int(ment['stop']),mention_text=ment['mention_text'],
                                                       id_report = report1,language = language)

                    if mentionDB.exists():
                        if mentionDB.count() > 1:
                            json_response = {'error': 'something is wrong in mentions!'}
                            return JsonResponse(json_response, status=500)

                        mentionDB = mentionDB.first()
                        anno = Annotate.objects.filter(username = user,ns_id=mode, id_report =report1,language =language,
                                                        start = mentionDB,stop = mentionDB.stop)
                        if anno.exists():
                            if anno.count() > 1:
                                json_response = {'error': 'something is wrong in annotations!'}
                                return JsonResponse(json_response, status=500)

                            update = False
                        else:
                            update = True
                            break
                    else: # If at lest one mention is different the ground truth and the annotation have to be updated
                        update = True
                        break

        if update == True:
            try:
                with transaction.atomic():
                    json_response = update_mentions(mentions,report1,language,user,usecase,mode)
                    if GroundTruthLogFile.objects.filter(username = user,ns_id=mode, language = language, id_report = report1, gt_type = 'mentions').exists():
                        GroundTruthLogFile.objects.filter(username=user, ns_id=mode,language=language, id_report=report1,
                                                          gt_type='mentions').delete()
                    jsonDict = serialize_gt(type, usecase, username, report_id,language,mode)
                    GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1,language = language, gt_json=jsonDict, gt_type=type,
                                                          insertion_time=Now())
                    # update_majority_vote_GT_mentions(report_id,language,request.session['mode'])

            except Exception as error:
                print(error)
                json_response = {'error':'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response, status=500)
            else:
                return JsonResponse(json_response)

        else:
            if mode1 == 'Human':
                json_response = {'message':'no changes detected'}
                return JsonResponse(json_response)

            elif mode1 == 'Robot':
                try:
                    with transaction.atomic():
                        user_robot = User.objects.get(username='Robot_user', ns_id=mode)
                        gt_robot = GroundTruthLogFile.objects.filter(username=user_robot, ns_id=mode,
                                                                     id_report=report1, language=language,
                                                                     gt_type='mentions')
                        gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report1,
                                                               language=language,
                                                               gt_type='mentions')
                        if gt.count() == 1 and gt_robot.count() == 1:
                            if gt_robot[0].insertion_time == gt[0].insertion_time:
                                js = gt[0].gt_json
                                GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report1,
                                                                  language=language,
                                                                  gt_type='mentions').delete()
                                GroundTruthLogFile.objects.create(gt_json=js, insertion_time=Now(), username=user,
                                                                  ns_id=mode, id_report=report1, language=language,
                                                                  gt_type='mentions')

                                ass = Annotate.objects.filter(username=user, id_report=report1, language=language,
                                                              ns_id=mode).values('start', 'stop')
                                for el in ass:
                                    ment = Mention.objects.get(id_report=report1, language=language,start = el['start'],stop=el['stop'])

                                    Annotate.objects.filter(username=user, ns_id=mode, start=ment,stop=ment.stop,
                                                            id_report=report1, language=language).delete()
                                    Annotate.objects.create(username=user, ns_id=mode,start=ment,stop=ment.stop,
                                                            insertion_time=Now(), id_report=report1, language=language)
                except Exception as error:
                    print(error)
                    json_response = {'error': 'An error occurred trying to save your ground truth.'}
                    return JsonResponse(json_response, status=500)
                else:
                    json_response = {'message': 'dates updated'}
                    return JsonResponse(json_response)


def insert_link(request,action=None):

    """This view handles ENTITY LINKING action.

    .js files: SubmitButtons.js NextPrevButtons.js Baseindex.js AddAssociation.js Buttons.js"""

    username = request.session['username']
    mode1 = request.session['mode']
    mode = NameSpace.objects.get(ns_id=mode1)
    language = request.session['language']
    usecase = request.session['usecase']
    auto_required = request.GET.get('ns_id', None)
    type = 'concept-mention'

    if request.method == 'GET' and action.lower() == 'linked':

        """GET request: it returns the mention-concept associations found by the user for that report."""

        try:
            report_id = request.GET.get('report_id')

            user_get = request.GET.get('username',username)
            report1 = Report.objects.get(id_report=report_id,language = language )
            # if auto_required == 'Robot':
            #     mode = NameSpace.objects.get(ns_id=auto_required)
            if auto_required is not None:
                mode_1 = NameSpace.objects.get(ns_id=auto_required)
            else:
                mode_1 = mode
            json_dict = get_user_gt(user_get,mode_1,report1,language,'concept-mention')
            return JsonResponse(json_dict)
        except Exception as error:
            print(error)
            json_response = {'error': 'An error occurred during the GET request.'}
            return JsonResponse(json_response, status=500)

    if request.method == 'GET' and action.lower() == 'mentions':

        """This GET request returns the list fo mentions associated to the report """

        report_id = request.GET.get('report_id')
        if auto_required is not None:
            mode_1 = NameSpace.objects.get(ns_id=auto_required)
        else:
            mode_1 = mode
        report1 = Report.objects.get(id_report=report_id,language = language)
        try:
            a = Annotate.objects.filter(username=username,ns_id=mode_1, id_report=report1, language=language).values('start', 'stop')
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

        except Exception as error:
            print(error)
            json_response = {'error': 'Sorry, an erorr occurred during the GET request.'}
            return JsonResponse(json_response, status=500)

    elif request.method == 'POST' and action.lower() == 'insert_mention':

        """ POST request: insertion of a new mention """

        json_response = {'message': 'Your mentions were correctly inserted'}
        user = User.objects.get(username=username,ns_id=mode)
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
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
                    Annotate.objects.create(username = user,ns_id=mode, insertion_time = Now(),start = menti, stop = menti.stop, id_report = report1, language = language)
                    type = 'mentions'
                    if GroundTruthLogFile.objects.filter(username=user, ns_id=mode,id_report=report1, language=language,
                                                         gt_type=type).exists():
                        GroundTruthLogFile.objects.filter(username=user, ns_id=mode,id_report=report1, language=language,
                                                          gt_type=type).delete()

                    jsonDict = serialize_gt(type, usecase, username, report_id, language,mode)
                    GroundTruthLogFile.objects.create(username=user,ns_id=mode, id_report=report1, language=language,
                                                                    gt_json=jsonDict,
                                                                    gt_type=type, insertion_time=Now())
                    # update_majority_vote_GT_mentions(report_id,language,request.session['mode'])

            except Exception as error:
                print(error)
                json_response = {'error': 'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response, status=500)
            else:
                return JsonResponse(json_response)

        else:
            json_response = {'message': 'nothing to save'}
            return JsonResponse(json_response)

    elif request.method == 'POST' and action.lower() == 'delete':

        """ POST request: delete the mention-concept associations the user found for that report"""

        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username,ns_id=mode)
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting parameters.'}
            return json_response

        to_del = Linked.objects.filter(username=user,ns_id=mode, id_report=report1.id_report,language = language)
        if len(to_del) == 0:
            json_response = {'message': 'Nothing to delete.'}
            return JsonResponse(json_response)
        if mode1 == 'Human':
            try:
                with transaction.atomic():
                    json_response = delete_all_associations(user, report1, language, type,usecase,mode)
                    # update_majority_vote_GT_linking(report_id, language,request.session['mode'])
            except Exception as error:
                print(error)
                json_response = {'error': 'Sorry, an erorr occurred, rolled back.'}
                return JsonResponse(json_response,status=500)
            else:
                return JsonResponse(json_response)
        else:
            """ In Automatic mode a ground truth the robot ground-truth is restored and the changes made by the user 
             are lost """
            to_del = Linked.objects.filter(username=user, ns_id=mode, id_report=report1, language=language)
            json_response = restore_robot_annotation(to_del, 'concept-mention',user)
            return JsonResponse(json_response)

    elif request.method == 'POST' and action.lower() == 'insert':

        """ POST request: insert the associations in the db """

        json_response = {'message': 'Associations and Ground truth saved.'}
        request_body_json = json.loads(request.body)
        report_id = request_body_json['report_id']
        user = User.objects.get(username=username,ns_id=mode)
        report1 = Report.objects.get(id_report=report_id,language = language)
        if user is None or report1 is None:
            json_response = {'error': 'An error occurred getting the parameters.'}
            return JsonResponse(json_response)

        concepts = request_body_json['linked']
        # In this case the user manually deletes all the associations (NOT WITH CLEAR BUTTON) and saves.
        if len(concepts) == 0 and mode1 == 'Human':
            if Linked.objects.filter(username=user,ns_id=mode, id_report=report1, language=language).exists():
                try:
                    with transaction.atomic():
                        json_response = delete_all_associations(user, report1,language, type,usecase,mode)
                        # update_majority_vote_GT_linking(report_id,language,request.session['mode'])
                    return JsonResponse(json_response)
                except Exception as error:
                    print(error)
                    json_response = {'error': 'Sorry, an erorr occurred, rolled back.'}
                    return JsonResponse(json_response, status=500)

            else:
                json_response ={'message':'Nothing to do'}
                return JsonResponse(json_response)
        if len(concepts) == 0 and mode1 == 'Robot':
            """If the user sends 0 associations the robot's ground truth is restored"""
            to_del = Linked.objects.filter(username = user, ns_id = mode, id_report = report1,language = language)
            json_response = restore_robot_annotation(to_del, 'concept-mention',user)
            # json_response = {'message': 'Nothing to do'}
            return JsonResponse(json_response)

        update = True
        existing_rows = Linked.objects.filter(username=user,ns_id=mode, id_report=report1, language=language)
        if existing_rows.exists():
            if existing_rows.count() == len(concepts):

                for concept in concepts:
                    conc = concept
                    ment = Mention.objects.filter(start=conc['start'], stop=conc['stop'],
                                                       mention_text=conc['mention_text'],
                                                       id_report=report1, language=language)

                    if ment.exists():
                        ment = ment.first()
                        concept_model = Concept.objects.get(concept_url=conc['concept_url'])
                        area = SemanticArea.objects.get(name=conc['semantic_area'])
                        anno = Linked.objects.filter(username=user,ns_id = mode, id_report=report1, language=language,
                                                       start=ment, stop=ment.stop,concept_url = concept_model,name=area)
                        if anno.exists():
                            update = False
                        else:
                            update = True
                            break
                    else:  # update if at least one association is different
                        update = True
                        break
        if update == True:
            try:
                with transaction.atomic():

                    json_response = update_associations(concepts, user, report1,language,usecase,mode)
                    if GroundTruthLogFile.objects.filter(username=user,ns_id=mode, language = language,id_report=report1, gt_type='concept-mention').exists():
                        obj = GroundTruthLogFile.objects.filter(username=user, language = language,id_report=report1, gt_type='concept-mention')
                        obj.delete()
                    jsonDict = serialize_gt(type, usecase, username, report_id,language,mode)
                    GroundTruthLogFile.objects.create(username=user,ns_id=mode, language = language,id_report=report1, gt_json=jsonDict, gt_type=type,
                                                          insertion_time=Now())
                    # update_majority_vote_GT_linking(report_id, language,request.session['mode'])
                    return JsonResponse(json_response)

            except Exception as error:
                print(error)
                json_response = {'error': 'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response,status=500)
        else:
            try:
                with transaction.atomic():
                    if mode1 == 'Human':
                        json_response = {'message': 'no changes detected'}
                        return JsonResponse(json_response)
                    elif mode1 == 'Robot':
                        user_robot = User.objects.get(username='Robot_user',ns_id=mode)
                        gt_robot = GroundTruthLogFile.objects.filter(username=user_robot, ns_id=mode, id_report=report1, language=language,
                                                            gt_type='concept-mention')
                        # in questa sezione solo se la gt è uguale a prima, l'utente acconsente alla gt della macchina
                        gt = GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report1, language=language,
                                                            gt_type='concept-mention')
                        if gt.count() == 1 and gt_robot.count() == 1:
                            if gt_robot[0].insertion_time == gt[0].insertion_time:

                                js = gt[0].gt_json
                                GroundTruthLogFile.objects.filter(username=user, ns_id=mode, id_report=report1, language=language,
                                                            gt_type='concept-mention').delete()
                                GroundTruthLogFile.objects.create(gt_json=js,insertion_time=Now(),username=user,ns_id = mode,id_report = report1,language = language,gt_type='concept-mention')
                                ass = Linked.objects.filter(username=user, id_report=report1, language=language, ns_id=mode).values('start','stop','name','concept_url')
                                for el in ass:
                                    men_cur = Mention.objects.get(id_report = report1,language = language, start = el['start'],stop=el['stop'])
                                    sem = SemanticArea.objects.get(name=el['name'])
                                    concept_u = Concept.objects.get(concept_url=el['concept_url'])
                                    Linked.objects.filter(username = user,id_report=report1,language=language,ns_id=mode,name=sem,start=men_cur,stop=el['stop'],concept_url = concept_u).delete()
                                    Linked.objects.create(username=user,ns_id=mode,id_report = report1,language=language,name=sem,stop=el['stop'],start=men_cur,concept_url=concept_u,insertion_time=Now())

            except Exception as error:
                print(error)
                json_response = {'error': 'An error occurred trying to save your ground truth.'}
                return JsonResponse(json_response, status=500)
            else:
                json_response = {'message': 'dates updated'}
                return JsonResponse(json_response)


def contains(request, action=None):

    """This view handles the GET AND POST requests to insert, delete, get concepts.

    .js files: Baseindex.js Buttons.js SubmitButtons.js NextPrevButtons.js"""

    username = request.session.get('username', False)
    mode1 = request.session.get('mode', False)
    mode = NameSpace.objects.get(ns_id=mode1)
    language = request.session.get('language', False)
    error_json = {"Error": "No user authenticated"}

    if (username):
        response_json = {}
        if request.method == 'GET':

            """GET request: it returns a list of concepts the user inserted about that report """

            report = request.GET.get('report_id')
            user_get = request.GET.get('username',username)
            report1 = Report.objects.get(id_report=report, language = language)
            auto_required = request.GET.get('ns_id',None)
            # if auto_required == 'Robot':
            #     mode = NameSpace.objects.get(ns_id=auto_required)
            if auto_required is not None:
                mode_1 = NameSpace.objects.get(ns_id=auto_required)
            else:
                mode_1 = mode
            response_json = get_user_gt(user_get,mode_1,report1,language,'concepts')
            return JsonResponse(response_json)

        elif request.method == 'POST' and action.lower() == 'insert':

            """ POST request: insert new concepts in the database"""

            request_body_json = json.loads(request.body)
            concepts_list = request_body_json['concepts_list']
            report = request_body_json['report_id']
            report1 = Report.objects.get(id_report=report)

            username = request.session.get('username', False)
            user1 = User.objects.get(username=username,ns_id=mode)
            usecase = request.session.get('usecase',False)
            type = 'concepts'

            if report is not None and concepts_list is not None:
                user = username
                count = 0
                already_inserted_list = []
                try:
                    with transaction.atomic():
                        for concept in concepts_list:
                            concept = json.loads(concept)
                            concept_url = concept['concept_url']
                            semantic_area = concept['semantic_area']
                            if not check_concept_report_existance(report, concept_url, user,mode, semantic_area,language):
                                # Insert a new record
                                if populate_contains_table(report, concept_url, user,mode, semantic_area,language):
                                    count += 1
                                else:
                                    error_json = {"error message": "insert in table 'contains' failed"}
                                    return JsonResponse(error_json)
                            else:
                                already_inserted_list.append(concept)
                        jsonDict = serialize_gt(type, usecase, username, report,language,mode)
                        GroundTruthLogFile.objects.create(username=user1, id_report=report1,ns_id=mode,
                                                                        language = language, gt_json=jsonDict,
                                                                        gt_type=type, insertion_time=Now())
                        # update_majority_vote_GT_concepts(report,language,request.session['mode'])
                except Exception as error:
                     print(error)
                     print('rolled back')

                if count == len(concepts_list):
                    response_json = {"message": "All concepts inserted successfully"}
                else:
                    response_json = {"message": "Some concepts have been already inserted: ["+ ", ".join(already_inserted_list)+"]"}
            else:
                response_json = {"error": "Missing data"}

        elif request.method == 'POST' and action.lower() == 'update':

            """ POST request: update the concepts that already exist in the database, a new ground truth is created 
            if needed."""

            request_body_json = json.loads(request.body)
            concepts_list = request_body_json['concepts_list']
            report = request_body_json['report_id']
            report1 = Report.objects.get(id_report = report,language = language)
            username = request.session.get('username',False)
            user1 = User.objects.get(username = username,ns_id=mode)
            usecase = request.session.get('usecase',False)
            type = 'concepts'
            if report is not None and concepts_list is not None:
                user = username
                count = 0
                rows = Contains.objects.filter(username = user1,ns_id=mode, id_report = report1, language = language)
                if rows.exists() and len(concepts_list) == 0:
                    if mode1 == 'Human':
                        with transaction.atomic():
                            json_response=delete_contains_record(report1, language, None,mode, user, None)
                            # update_majority_vote_GT_concepts(report,language,request.session['mode'])
                            return JsonResponse(json_response,safe=False)
                    else:
                        # json_response = {'message': 'Robot mode, rows can not be deleted'}
                        json_response = restore_robot_annotation(rows,'concepts',user1)
                        return JsonResponse(json_response)
                elif not rows.exists() and len(concepts_list) == 0:
                    json_response = {'message':'nothing to do'}
                    return JsonResponse(json_response)
                if len(concepts_list) == 0:
                    json_response = {'message': 'Nothing to do'}
                    return JsonResponse(json_response)
                update = True
                if rows.exists():
                    if rows.count() == len(concepts_list):
                        for concept in concepts_list:
                            concept_url = concept['concept_url']
                            semantic_area = concept['semantic_area']
                            concept_model = Concept.objects.get(concept_url = concept_url)
                            concepts = Contains.objects.filter(name=semantic_area, username = user1,ns_id=mode, id_report = report1, language = language, concept_url = concept_model)
                            if concepts.exists():
                                update = False
                            else:
                                update = True
                                break

                # Delete previous data for the specified user and report
                if update == True:
                    try:
                        with transaction.atomic():
                            js = delete_contains_record(report1,language, None, mode,user, None)
                            # Insert new data
                            for concept in concepts_list:
                                    # Insert a new record
                                    concept_url = concept['concept_url']
                                    semantic_area = concept['semantic_area']
                                    if populate_contains_table(report, concept_url, user, mode,semantic_area,language):
                                        count += 1
                                    else:
                                        error_json = {"error message": "insert in table 'contains' failed"}
                                        return JsonResponse(error_json)
                            jsonDict = serialize_gt(type, usecase, username, report,language,mode)
                            if GroundTruthLogFile.objects.filter(username=user1, ns_id=mode,id_report=report1,language = language, gt_type=type).exists():
                                GroundTruthLogFile.objects.filter(username=user1,ns_id=mode, id_report=report1, language=language,gt_type=type).delete()

                            GroundTruthLogFile.objects.create(username=user1,ns_id=mode, id_report=report1,
                                                                            gt_json=jsonDict,language = language,
                                                                            gt_type=type, insertion_time=Now())
                            # update_majority_vote_GT_concepts(report,language,request.session['mode'])

                    except Exception as error:
                         print(error)
                         print('rolled back')

                    if count == len(concepts_list):
                        response_json = {"message": "Update successfull"}
                    else:
                        response_json = {"error": "Update unsuccessfull"}
            else:
                response_json = {"error": "Missing data"}

        elif request.method == 'POST' and action.lower() == 'delete':

            """ POST request: delete the concepts the user associated to a specific report """

            request_body_json = json.loads(request.body)
            report = request_body_json['report_id']
            username = request.session.get('username', False)
            user1 = User.objects.get(username=username,ns_id=mode)

            with transaction.atomic():
                if report is not None and language is not None:
                    if mode1 == 'Human':
                        response_json = delete_contains_record(report, language, None,mode, user1, None)
                        # update_majority_vote_GT_concepts(report,language,request.session['mode'])
                    elif mode1 == 'Robot':
                        # report1 = Report.objects.get(id_report = report,language = language)
                        rows = Contains.objects.filter(username = user1,ns_id = mode,id_report = report,language = language)
                        response_json = restore_robot_annotation(rows,'concepts',user1)
                else:
                    response_json = {"Error": "Missing data"}

        return JsonResponse(response_json)

    else:
        return JsonResponse(error_json)


def test(request, table):

    """ This view allows to test the four actions a user can perform."""

    username = request.session.get('username', False)
    error_json = {"Error": "No user authenticated"}

    if (username):
        context = {'username': username}
        if table == "contains":
            return render(request, 'MedTAG_sket_dock_App/test/test-contains.html', context)
        elif table == "associate":
            return render(request, 'MedTAG_sket_dock_App/test/test-annotation.html', context)
        elif table == "annotate":
            return render(request, 'MedTAG_sket_dock_App/test/test-mentions.html', context)
        elif table == 'linked':
            return render(request, 'MedTAG_sket_dock_App/test/test-linked.html', context)

    return JsonResponse(error_json)


def get_reports(request):

    """This view returns the list of reports associated to a single use_case, institute and language

    .js files: Baseindex.js ReportsStats.js ReportSelection.js OptionsModal.js StartingMenu.js ReportForModal.js
    ReportToText.js"""

    inst = request.GET.get('institute',None)
    use = request.GET.get('usec',None)
    lang = request.GET.get('lang',None)
    all = request.GET.get('all',None)

    if all == 'all':
        # All the reports are returned independently of the usecase, the language or institute.
        reps = Report.objects.all().values('id_report','report_json','language')
        json_resp = {}
        json_resp['report'] = []

        for report in reps:
            json_rep = {}
            json_rep['id_report'] = report['id_report']
            json_rep['language'] = report['language']
            json_rep['report_json'] = report['report_json']
            json_resp['report'].append(json_rep)
        return JsonResponse(json_resp)

    if(inst != None and use != None and lang != None):

        """ It is used in the options modal: if the reuqired combination of institute, language and usecase has 0 reports
         associated, a message is returned. In this case this view returns the number of reports associated to a specific 
         configuration required """

        rep = Report.objects.filter(institute = inst, name = use, language = lang)
        json_count = {'count':len(rep)}
        return JsonResponse(json_count)

    usecase = request.session.get('usecase',None)
    mode1 = request.session.get('mode',None)
    mode = NameSpace.objects.get(ns_id=mode1)
    language = request.session.get('language',None)
    institute = request.session.get('institute',None)
    username = request.session['username']
    token = request.GET.get('configure',None) # This parameter is set when

    jsonError = {'error':'something wrong with params!'}
    if usecase is not None and language is not None and institute is not None:
        # Get the reports associated to the usecase, language and institute of the SESSION
        reports1 = Report.objects.filter(name = usecase, language = language, institute = institute)
        json_resp = {}
        json_resp['report'] = []
        if reports1.exists():
            reports = reports1.values('id_report','report_json','language')
            for report in reports:
                json_rep = {}
                json_rep['id_report'] = report['id_report']
                json_rep['language'] = report['language']
                json_rep['report_json'] = report['report_json']
                json_resp['report'].append(json_rep)

            json_resp['report'].sort(key=lambda json: json['id_report'], reverse=False) # Reports are sorted by ID
            json_resp['index'] = 0

            if token is not None:
                # Get the last ground truth given the session parameters.
                gt = get_last_groundtruth(username, usecase, language, institute,mode)
            else:
                # Get the last ground truth of the user.
                gt = get_last_groundtruth(username,mode)

            if gt is not None:
                # The index is updated and it characterizes the first report of the list shown to the user.
                id_report = gt['id_report']
                use = gt['use_case']
                lang = gt['language']
                institute = gt['institute']
                report_json = Report.objects.get(id_report = id_report, name = use, language = lang, institute = institute)
                rep_json = report_json.report_json
                index = json_resp['report'].index({'id_report':id_report,'language':lang,'report_json':rep_json})
                json_resp['index'] = int(index)

        return JsonResponse(json_resp)
    else:
        return JsonResponse(jsonError,status=500)

def get_admin(request):

    """ This view returns the admin of MedTAG (if any)

    .js files: App.js"""

    jsonResp = {}
    jsonResp['admin'] = ''
    if User.objects.filter(profile = 'Admin').exists():
        mode = NameSpace.objects.get(ns_id='Human')
        name = User.objects.get(profile = 'Admin',ns_id=mode)
        admin = name.username
        jsonResp['admin'] = admin

    return JsonResponse(jsonResp)

def check_input_files(request):

    """ This view checks whether the configuration files the user inserted are well formed and returns the response

    .js files: Configure.js"""

    reports = []
    labels = []
    concepts = []
    type1 = request.POST.get('type',None)
    username = request.POST.get('username',None)
    password = request.POST.get('password',None)
    for filename, file in request.FILES.items():
        if filename.startswith('reports'):
            reports.append(file)
        elif filename.startswith('concepts'):
            concepts.append(file)
        elif filename.startswith('labels'):
            labels.append(file)
    jsonDisp = request.POST.get('json_disp','')
    jsonAnn = request.POST.get('json_ann','')
    load_concepts = request.POST.get('exa_concepts',None)
    load_labels = request.POST.get('exa_labels',None)
    jsonResp = check_file(reports,labels,concepts,jsonDisp,jsonAnn,username,password,load_concepts,load_labels)

    print(jsonResp)

    return JsonResponse(jsonResp)


def get_gt_list(request):

    """ This view returns the list of groundtruths associated to a user and a specific configuration of institute,
    usecase and language.

    .js files: InfoAboutConfiguration.js DownloadGT.js"""

    groundTruths = 0
    json_resp = {}
    ins = request.GET.get('inst',None)
    lang = request.GET.get('lang',None)
    use = request.GET.get('use',None)
    action = request.GET.get('action',None)
    token = request.GET.get('token',None)
    if ins == '':
        ins = None
    if use == '':
        use = None
    if lang == '':
        lang = None
    if token == 'all':
        list_gt = GroundTruthLogFile.objects.all().count()
        groundTruths = list_gt

    else:
        if ins is None and use is None and lang is None:
            list_gt = GroundTruthLogFile.objects.filter(username = request.session['username'],ns_id=request.session['mode'], gt_type = action).count()
            groundTruths = list_gt

        elif ins is not None and use is not None and lang is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND g.language = r.language WHERE r.institute = %s AND r.name = %s AND r.language = %s AND g.gt_type = %s",
                    [ins, use, lang,action])
                groundTruths = cursor.fetchone()[0]

        elif ins is not None and use is not None and lang is None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND g.language = r.language WHERE r.institute = %s AND r.name = %s AND g.gt_type = %s",
                    [ins, use,action])
                groundTruths = cursor.fetchone()[0]

        elif ins is not None and use is None and lang is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report WHERE r.institute = %s AND r.language = %s AND g.gt_type = %s",
                    [ins, lang,action])
                groundTruths = cursor.fetchone()[0]

        elif ins is None and use is not None and lang is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND r.language = g.language WHERE r.name = %s AND r.language = %s AND g.gt_type = %s",
                    [use, lang,action])
                groundTruths = cursor.fetchone()[0]

        elif ins is not None and use is None and lang is None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND r.language = g.language WHERE r.institute = %s AND g.gt_type = %s",
                    [ins,action])
                groundTruths = cursor.fetchone()[0]

        elif ins is None and use is not None and lang is None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND r.language = g.language WHERE r.name = %s AND g.gt_type = %s",
                    [use,action])
                groundTruths = cursor.fetchone()[0]

        elif ins is None and use is None and lang is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND r.language = g.language WHERE r.language = %s AND g.gt_type = %s",
                    [lang,action])
                groundTruths = cursor.fetchone()[0]

    json_resp['ground_truths'] = groundTruths
    return JsonResponse(json_resp)


def check_files_for_update(request):

    """ This view checks whether the files inserted by the user to update the configuration are well formed

    .js files: UpdateConfiguration.js"""

    reports = []
    usecase = []
    areas = []
    labels = []
    concepts = []
    type1 = request.POST.get('type',None)
    for filename, file in request.FILES.items():
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
    msg = check_for_update(type1,reports,labels,concepts,areas,usecase,jsonDisp,jsonAnn,jsonDispUp,jsonAnnUp)
    jsonResp = {'message':msg}
    return JsonResponse(jsonResp)


def update_db(request):

    """ This view handles the update of the database once the files check went well

     .js files: UpdateConfiguration.js"""

    reports = []
    labels = []
    concepts = []
    usecase = request.session['usecase']
    type1 = request.POST.get('type', None)
    load_concepts = request.POST.get('exa_concepts',None)
    load_labels = request.POST.get('exa_labels',None)

    for filename, file in request.FILES.items():
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
    jsonAll = request.POST.get('json_all_update', '')

    msg = update_db_util(reports,labels,concepts,jsonDisp,jsonAnn,jsonDispUp,jsonAnnUp,jsonAll,load_concepts,load_labels)
    if 'message' in list(msg.keys()):
        keys = get_fields_from_json()
        request.session['fields'] = keys['fields']
        request.session['fields_to_ann'] = keys['fields_to_ann']
        if type1 == 'reports':
            get_fields_extractable('update')

    if request.session['mode'] == 'Robot':
        workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
        with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json')) as out:
            data = json.load(out)
            request.session['fields_to_ann'] = data['extract_fields'][usecase]

    return JsonResponse(msg)


def configure_db(request):

    """ This view handles the initial configuration, the first the admin performs

    .js files: Configure.js"""

    reports = []
    usecase = []
    areas = []
    labels = []
    concepts = []
    type = request.POST.get('type',None)
    load_concepts = request.POST.get('exa_concepts',[])
    load_labels = request.POST.get('exa_labels',[])

    for filename, file in request.FILES.items():
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

    msg = configure_data(reports,labels,concepts,jsonDisp,jsonAnn,jsonAll,username,password,load_concepts,load_labels)
    if 'message' in list(msg.keys()):
        get_fields_extractable('configure')
    return JsonResponse(msg)


def get_keys(request):

    """ This view returns the list of all the distinct keys present in the json reports. This view is called
     during configuration

     .js files: Configure.js UpdateConfiguration.js """

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

    """This view returns the ground truths created by the user according to the configuration she required.

    .js files: DownloadGT.js """

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path1 = os.path.join(workpath, './static/temp/temp.csv')
    path2 = os.path.join(workpath, './static/BioC/temp_files/to_download.csv')
    if os.path.exists(path1):
        os.remove(path1)
    if os.path.exists(path2):
        os.remove(path2)
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
        response = HttpResponse(content_type='text/csv')
        resp = create_csv_to_download1(username,use,inst,lang,action,response)
        return resp

    elif format == 'biocxml':
        json_keys_to_display = request.session['fields']
        json_keys_to_ann = request.session['fields_to_ann']
        json_keys = json_keys_to_display + json_keys_to_ann
        resp = generate_bioc(json_keys,json_keys_to_ann,username,action,lang,use,inst,'xml')
        return HttpResponse(resp,content_type='application/xml')

    elif format == 'biocjson':
        json_keys_to_display = request.session['fields']
        json_keys_to_ann = request.session['fields_to_ann']
        json_keys = json_keys_to_display + json_keys_to_ann
        resp = generate_bioc(json_keys,json_keys_to_ann,username,action,lang,use,inst,'json')
        return HttpResponse(resp,content_type='application/xml')


def download_all_ground_truths(request):

    """This view returns ALL the ground truths to be downloaded. This view can be called only by the admin and the
    ground truths returned are those of ALL the users in the platform

    .js files: InfoAboutConfiguration.js UpdateConfiguration.js """

    json_resp = {}
    json_resp['ground_truth'] = []

    mode = request.GET.get('gt_mode',None)
    if mode is None:
        gt = GroundTruthLogFile.objects.all()

    if mode.lower() == 'automatic':
        ns_id = NameSpace.objects.get('Robot')
        gt = GroundTruthLogFile.objects.filter(ns_id=ns_id)

    for el in gt:
        gt_json = el.gt_json
        if gt_json['gt_type'] == 'concept-mention':
            gt_json['gt_type'] = 'linking'
        json_resp['ground_truth'].append(gt_json)
    return JsonResponse(json_resp)


def download_key_files(request):

    """This view returns the key files of BioC mentions and linking.

    .js files: DownloadGT.js DownloadForModal.js """

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    path = os.path.join(workpath, './static/BioC/linking.key')
    path1 = os.path.join(workpath, './static/BioC/mention.key')
    ment = request.GET.get('type_key',None)
    if ment == 'mentions':
        path = open(path1, 'r')
        return HttpResponse(path, content_type='text/plain')
    elif ment == 'linking':
        path1 = open(path, 'r')
        return HttpResponse(path1, content_type='text/plain')


def get_reports_from_action(request):

    """This view returns an array of tuples, where each tuple contains the id of the annotated report and the associated insertion time

     .js files: ReportSelection.js """

    username = request.session['username']
    mode1 = request.session['mode']
    mode = NameSpace.objects.get(ns_id=mode1)
    language = request.session['language']
    report_to_ret = []
    action = request.GET.get('action',None)
    user = User.objects.get(username = username,ns_id=mode)
    gt = GroundTruthLogFile.objects.filter(username = user,ns_id=mode, language = language, gt_type = action)
    if gt.exists():
        if mode1 == 'Human':
            for element in gt:
                val = (element.id_report_id,element.insertion_time.replace(tzinfo=timezone.utc).astimezone(tz=None))
                report_to_ret.append(val)

        elif mode1 == 'Robot':
            user_rob = User.objects.get(username = 'Robot_user',ns_id = mode)
            for el in gt:
                gt_rob = GroundTruthLogFile.objects.get(id_report = el.id_report, language = language, gt_type = el.gt_type,ns_id=mode, username=user_rob)
                if el.insertion_time != gt_rob.insertion_time:
                    val = (el.id_report_id, el.insertion_time.replace(tzinfo=timezone.utc).astimezone(tz=None))
                    report_to_ret.append(val)

    jsonDict = {}
    jsonDict['reports_presence'] = report_to_ret

    return JsonResponse(jsonDict)


def get_last_gt(request):

    """ This view returns the last ground truth created by the user for the session's parameters

    .js files: Baseindex.js """

    username = request.session['username']
    mode1 = request.session['mode']
    mode = NameSpace.objects.get(ns_id=mode1)
    language = request.session['language']
    usecase = request.session['usecase']
    institute = request.session['institute']
    jsonDict = {}
    token = request.GET.get('configure',None)
    if token is None:
        gt_json = get_last_groundtruth(username,mode)
    else:
        gt_json = get_last_groundtruth(username,usecase,language,institute,mode)

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


def conc_view(request):

    """ This view returns the concept_urls related to each semantic_area. The concepts can be those added by the admin
    (in the manual mode), those of EXAMODE added EXCLUSIVELY for automatic annotation (in the automatic mode) or those
    of EXAMODE added for automatic AND manual mode.

    .js files: SubmitButtons.js Baseindex.js """

    usecase = request.session['usecase']
    mode = request.session['mode']
    auto_required = request.GET.get('ns_id',None)
    jsonDict = {}
    concepts = {}
    notEmpty = False
    jsonDict['concepts'] = []
    if mode == 'Human' or auto_required == 'Human':
        areas = SemanticArea.objects.all()
        for area in areas:
            name = area.name
            concepts[name] = []
            description = {'provenance': 'admin', 'insertion_author': 'admin'}
            description_1 = {'provenance': 'EXAMODE', 'insertion_author': 'admin'}
            desc = json.dumps(description)
            desc_1 = json.dumps(description_1)
            concepts_list = get_concepts_by_usecase_area(usecase, name,desc)
            concepts_list_final = concepts_list + get_concepts_by_usecase_area(usecase, name,desc_1)
            for c in concepts_list_final:
                if c not in concepts[name]:
                    concepts[name].append(c)
                    notEmpty = True
        if notEmpty == True:
            jsonDict['concepts'] = concepts

    elif mode == 'Robot' or auto_required == 'Robot':
        with transaction.atomic():
            with connection.cursor() as cursor:
                description = {'provenance': 'EXAMODE','insertion_author':'admin'}
                description_1 = {'provenance': 'EXAMODE','insertion_author':'robot'}
                desc = json.dumps(description)
                desc1 = json.dumps(description_1)
                desc_tup = (desc,desc1)
                cursor.execute("SELECT DISTINCT(name) FROM belong_to WHERE concept_url IN (SELECT c.concept_url FROM concept AS c INNER JOIN concept_has_uc AS chu ON chu.concept_url = c.concept_url WHERE chu.name=%s AND c.json_concept IN %s)",[usecase,desc_tup])
                areas_arr = cursor.fetchall()
                areas = [el[0] for el in areas_arr]
                for area in areas:
                    concepts[area] = get_concepts_by_usecase_area(usecase, area, desc)
                    if len(concepts[area]) > 0:
                        notEmpty = True
                if notEmpty == True:
                    jsonDict['concepts'] = concepts

    return JsonResponse(jsonDict)


def get_semantic_area(request):

    """ This view returns the semantic areas: fi the session's mode is ROBOT (automatic annotation) we look for those
    concepts whose provenance is EXAMODE otherwise we look for those concepts whose insertion author is ADMIN.

    .js files: Baseindex.js SubmitButtons.js """

    json_dict = {}
    arr = []
    arr_sem = SemanticArea.objects.all().values('name')
    for area in arr_sem:
        arr.append(area['name'])
    description = {'provenance':'EXAMODE','insertion_author':'admin'}
    description1 = {'provenance': 'EXAMODE', 'insertion_author': 'robot'}
    description2 = {'provenance': 'admin', 'insertion_author': 'admin'}
    desc = json.dumps(description)
    desc1 = json.dumps(description1)
    desc2 = json.dumps(description2)
    tup = (desc,desc1)
    tup1 = (desc,desc2)
    areas = []
    auto_required = request.GET.get('ns_id',None)
    if request.session['mode'] == 'Robot' or auto_required == 'Robot':
        with connection.cursor() as cursor:
            cursor.execute('SELECT DISTINCT(b.name) FROM concept AS c INNER JOIN belong_to AS b ON c.concept_url = b.concept_url WHERE c.json_concept IN %s',[tup])
            rows = cursor.fetchall()
            for row in rows:
                areas.append(row[0])
    elif request.session['mode'] == 'Human' or auto_required == 'Human':
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT DISTINCT(b.name) FROM concept AS c INNER JOIN belong_to AS b ON c.concept_url = b.concept_url WHERE c.json_concept IN %s',
                [tup1])
            rows = cursor.fetchall()
            for row in rows:
                areas.append(row[0])
    json_dict['area'] = areas
    return JsonResponse(json_dict)


def report(request,report_id,language):

    """ This view returns the json report of the required report

    .js files: USED ONLY DURING DEBUG """

    json_resp = {}
    error_json = {'error':'the report does not exist!'}

    if Report.objects.filter(id_report = report_id, language = language).exists():
        report = Report.objects.get(id_report = report_id, language = language)
        json_resp['report_json'] = report.report_json
        return JsonResponse(json_resp['report_json'])

    return error_json


def report_start_end(request):

    """ This view returns for each key of the json report required its text, the indexes of the start and stop chars
    in the json report string and the number of words that compose the fields to annotate.

    .js files: Baseindex.js SubmitButtons.js ReportToText.js ReportForModal.js  """

    report = request.GET.get('report_id')
    usecase = request.session['usecase']
    json_keys_to_display = request.session['fields']
    json_keys_to_ann = request.session['fields_to_ann']
    print(json_keys_to_ann)
    language = request.session['language']
    request_auto = request.GET.get('ns_id',None)
    if request_auto is not None and request_auto == 'Robot':
        # In this case we require automatic annotation: the keys to annotate change
        workpath = os.path.dirname(
            os.path.abspath(__file__))  # Returns the Path your .py file is in
        with open(os.path.join(workpath,
                               './automatic_annotation/auto_fields/auto_fields.json')) as out:
            data = json.load(out)
            json_keys_to_ann = data['extract_fields'][usecase]
            for el in json_keys_to_ann:
                if el in json_keys_to_display:
                    json_keys_to_display.remove(el)

    json_keys = json_keys_to_display + json_keys_to_ann
    json_dict = report_get_start_end(json_keys,json_keys_to_ann,report,language)
    print(json_dict)
    return JsonResponse(json_dict)


def get_usecase_inst_lang(request):

    """ This view returns the list of all the possible: usecases, languages and institutes.

    .js files: App.js UpdateConfiguration.js Configure.js ReportsStats.js Credits.js MyStats.js Tutorial.js """

    jsonDict = get_distinct()
    return JsonResponse(jsonDict)


def get_fields(request):

    """This view returns the fields to display and annotate. If the annotation mode is automatic the fields to annotate
    are those the concepts and mentions have been extracted from. The fields are returned to give the user the chance to
    update the fields she wants to display/annotate in MANUAL CONFIGURATION.

    .js files: Baseindex.js SubmitButtons.js UpdateConfiguration.js ReportsStats.js ReportForModal.js ReportToText.js"""

    json_resp = {}
    json_resp['fields'] = []
    json_resp['fields_to_ann'] = []
    all = request.GET.get('all',None)
    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    auto_request = request.GET.get('ns_id', None)
    if all == 'all':
        #All the possible fields for every usecase (MANUAL CONFIGURATION)
        json_resp = get_fields_from_json()


    else:
        # Fileds related exclusively to a usecase
        json_resp = get_fields_from_json_configuration(request.session['usecase'],request.session['institute'],request.session['language'])
        if request.session['mode'] == 'Robot' or auto_request == 'Robot':
            with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json')) as out:
                data = json.load(out)
                json_resp['fields_to_ann'] = data['extract_fields'][request.session['usecase']]
                for el in json_resp['fields_to_ann']:
                    if el in json_resp['fields']:
                        json_resp['fields'].remove(el)

    return JsonResponse(json_resp)


def download_examples(request):

    """ This view creates the HttpResponse object with the CSV examples files, these are the examples the user can
    download.

    .js files: Cofnigure.js InfoAboutConfiguration.js UpdateConfiguration.js """

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

    """ This view creates the HttpResponse object with the appropriate CSV header, these are the templates the user can
    download.

    .js files: InfoAboutConfiguration.js """

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


def get_keys_and_uses_from_csv(request):

    """This view returns the list of all the keys found in report files (other than institute,usecase,id_report,language)
    and the list of usecases, this list contains the usecases where automatic annotation can be applied.

    .js files: Configure.js"""

    reports = []
    json_resp = {}
    for filename, file in request.FILES.items():
        if filename.startswith('reports'):
            reports.append(file)

    keys,uses = get_keys_and_uses_csv(reports)
    json_resp['keys'] = keys
    json_resp['usecases'] = uses
    return JsonResponse(json_resp)


def get_keys_from_csv_update(request):

    """This view returns the list of all the keys found in report files (other than institute,usecase,id_report,language)
    the admin has just inserted to update the database (only the keys that have never been detected before are returned).

    .js files: UpdateConfiguration.js"""

    reports = []
    json_resp = {}
    for filename, file in request.FILES.items():
        if filename.startswith('reports'):
            reports.append(file)

    keys,uses = get_keys_csv_update(reports)
    json_resp['keys'] = keys

    return JsonResponse(json_resp)


def get_presence_examode_concepts(request):

    """This view returns the list of usecases (colon,uterine cervix,lung) for which the examode concepts have not been added
    in the database.

    .js files: UpdateConfiguration.js"""

    json_resp = {}
    json_resp['concepts'] = get_presence_exa_concepts()
    return JsonResponse(json_resp)

#----------------------------------------------------------------------------------------------------------
# REPORT USER'S STATA
def get_stats_array_per_usecase(request):

    """This view returns for each usecase the statistics concerning the user's annotations

    .js files: MyStats.js"""

    mode = request.GET.get('mode',None)
    usern = request.GET.get('member',request.session['username'])
    username = User.objects.get(username=usern, ns_id=mode)
    json_rep = get_array_per_usecase(username,mode)
    return JsonResponse(json_rep)


# def get_number_annot_per_report(request):
#     json_resp = {}
#     report_id = request.GET.get('report',None)
#     language = request.GET.get('language',None)
#     report = Report.objects.get(id_report=report_id,language=language)
#     gt_lab = GroundTruthLogFile.objects.filter(id_report=report,language=language,gt_type='labels')
#     gt_ment = GroundTruthLogFile.objects.filter(id_report=report,language=language,gt_type='mentions')
#     gt_conc = GroundTruthLogFile.objects.filter(id_report=report,language=language,gt_type='concepts')
#     gt_link = GroundTruthLogFile.objects.filter(id_report=report,language=language,gt_type='concept-mention')
#     json_resp['total'] = gt_lab + gt_ment + gt_conc + gt_link
#     json_resp['labels'] = gt_lab
#     json_resp['mentions'] = gt_ment
#     json_resp['concepts'] = gt_conc
#     json_resp['linking'] = gt_link
#     return JsonResponse(json_resp)

def get_data1(request):

    """This view returns the rows to be inserted in the reports' table
    .js files: ReportsStats.js"""

    json_resp = {}
    reports = Report.objects.all()
    json_resp['reports'] = []
    for el in reports:

        report = Report.objects.get(id_report=el.id_report, language=el.language)
        language = el.language
        gt_lab = GroundTruthLogFile.objects.filter(id_report=report, language=language, gt_type='labels')
        gt_ment = GroundTruthLogFile.objects.filter(id_report=report, language=language, gt_type='mentions')
        gt_conc = GroundTruthLogFile.objects.filter(id_report=report, language=language, gt_type='concepts')
        gt_link = GroundTruthLogFile.objects.filter(id_report=report, language=language, gt_type='concept-mention')
        total = gt_lab.count() + gt_ment.count() + gt_conc.count() + gt_link.count()
        labels = gt_lab.count()
        mentions = gt_ment.count()
        concepts = gt_conc.count()
        linking = gt_link.count()
        rep = report.report_json
        new_rep = {}
        for key in rep.keys():
            nkey = key+ '_0'
            new_rep[nkey] = rep[key]

        new_rep['usecase'] = report.name_id
        new_rep['id_report'] = report.id_report
        new_rep['institute'] = report.institute
        new_rep['language'] = report.language
        json_resp['reports'].append({'total':total,'labels':labels,'mentions':mentions,'concepts':concepts,'linking':linking, 'report':new_rep,'id_report':el.id_report, 'language':el.language})

    return JsonResponse(json_resp)

def get_data(request):

    """This view returns the rows to be inserted in the reports' table

    .js files: ReportsStats.js"""

    json_resp = {}
    reports = Report.objects.all()
    json_resp['reports'] = []
    for el in reports:

        report = Report.objects.get(id_report=el.id_report, language=el.language)
        language = el.language
        ns_human = NameSpace.objects.get(ns_id='Human')
        ns_robot = NameSpace.objects.get(ns_id='Robot')
        gt_lab_human = GroundTruthLogFile.objects.filter(ns_id=ns_human,id_report=report, language=language, gt_type='labels').count()
        gt_ment_human = GroundTruthLogFile.objects.filter(ns_id=ns_human,id_report=report, language=language, gt_type='mentions').count()
        gt_conc_human = GroundTruthLogFile.objects.filter(ns_id=ns_human,id_report=report, language=language, gt_type='concepts').count()
        gt_link_human = GroundTruthLogFile.objects.filter(ns_id=ns_human,id_report=report, language=language, gt_type='concept-mention').count()

        user_rob = User.objects.get(username='Robot_user',ns_id=ns_robot)
        gt_lab_robot_user = GroundTruthLogFile.objects.filter(username=user_rob,ns_id=ns_robot, id_report=report, language=language,
                                                         gt_type='labels')
        if gt_lab_robot_user.count() == 1:
            gt = gt_lab_robot_user.first()
            ins_time_labels = gt.insertion_time
            gt_robot_labs = GroundTruthLogFile.objects.all().filter(ns_id=ns_robot, id_report=report, language=language,
                                                         gt_type='labels').exclude(insertion_time=ins_time_labels).count()
            gt_labels = gt_lab_human + gt_lab_robot_user.count() + gt_robot_labs
        else:
            gt_labels = gt_lab_human
        gt_ment_robot_user = GroundTruthLogFile.objects.filter(username=user_rob,ns_id=ns_robot, id_report=report, language=language,
                                                          gt_type='mentions')
        if gt_ment_robot_user.count() == 1:
            gt = gt_ment_robot_user.first()
            ins_time_mentions = gt.insertion_time
            gt_robot_ments = GroundTruthLogFile.objects.all().filter(ns_id=ns_robot, id_report=report, language=language,
                                                         gt_type='mentions').exclude(insertion_time=ins_time_mentions).count()
            gt_mentions = gt_ment_human + gt_ment_robot_user.count() + gt_robot_ments
        else:
            gt_mentions = gt_ment_human

        gt_conc_robot_user = GroundTruthLogFile.objects.filter(username=user_rob,ns_id=ns_robot, id_report=report, language=language,
                                                          gt_type='concepts')
        if gt_conc_robot_user.count() == 1:
            gt = gt_conc_robot_user.first()
            ins_time_concepts = gt.insertion_time
            gt_robot_concs = GroundTruthLogFile.objects.all().filter(ns_id=ns_robot, id_report=report, language=language,
                                                         gt_type='concepts').exclude(insertion_time=ins_time_concepts).count()
            gt_concepts = gt_conc_human + gt_conc_robot_user.count() + gt_robot_concs
        else:
            gt_concepts = gt_conc_human

        gt_link_robot_user = GroundTruthLogFile.objects.filter(username=user_rob,ns_id=ns_robot, id_report=report, language=language,
                                                          gt_type='concept-mention')
        if gt_link_robot_user.count() == 1:
            gt = gt_link_robot_user.first()
            ins_time_linking = gt.insertion_time
            gt_robot_links = GroundTruthLogFile.objects.all().filter(ns_id=ns_robot, id_report=report, language=language,
                                                         gt_type='concept-mention').exclude(insertion_time=ins_time_linking).count()
            gt_linking = gt_link_human + gt_link_robot_user.count() + gt_robot_links
        else:
            gt_linking = gt_link_human

        total = gt_labels + gt_mentions + gt_concepts + gt_linking
        labels = gt_labels
        mentions = gt_mentions
        concepts = gt_concepts
        linking = gt_linking
        rep = report.report_json
        new_rep = {}
        for key in rep.keys():
            nkey = key+ '_0'
            new_rep[nkey] = rep[key]

        new_rep['usecase'] = report.name_id
        new_rep['id_report'] = report.id_report
        new_rep['institute'] = report.institute
        new_rep['language'] = report.language
        json_resp['reports'].append({'total':total,'labels':labels,'mentions':mentions,'concepts':concepts,'linking':linking, 'report':new_rep,'id_report':el.id_report, 'language':el.language})

    return JsonResponse(json_resp)
#-----------------------------------------------------------------------------------------------------------

def report_missing_auto(request):

    """Check the number of reports annotated by the machine. It is needed by frontend to display how many reports
    have not been alg annotated yet if one or more reports have been inserted later.

    .js files: UpdateConfiguration.js"""

    usecases = UseCase.objects.all()
    json_resp = {}

    for el in usecases:
        use = el.name
        if use in ['Colon','Lung','cervix','uterine','Uterine cervix']:
            report = Report.objects.filter(name=el)
            count_rep = report.count()

            if count_rep > 0:
                json_resp[use] = {}
                json_resp[use]['tot'] = count_rep
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM report AS r INNER JOIN ground_truth_log_file AS g ON g.id_report = r.id_report AND r.language = g.language WHERE r.name = %s AND g.username = %s AND gt_type=%s;",
                        [str(use),'Robot_user','labels'])
                    groundTruths = cursor.fetchone()[0]
                    json_resp[use]['annotated'] = groundTruths
    print(json_resp)
    return JsonResponse(json_resp)


def get_post_fields_for_auto(request):

    """GET request: get the fields to automatically extract annotations from.
    POST request: post the fields to automatically extract annotations from.

    .js files: UpdateConfiguration.js SubmitButtons.js DownloadGT.js OptionsModal.js StartingMeny.js MyStats.js"""

    workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
    with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'r') as use_outfile:
        json_to_ret = json.load(use_outfile)
    if request.method == 'GET':
        return JsonResponse(json_to_ret)

    if request.method == 'POST':
        json_error = {'error': 'an error occurred'}
        json_resp = {'msg': 'ok'}

        try:
            request_body_json = json.loads(request.body)
            fields = request_body_json['fields']

            for k in fields.keys():
                array_use = fields[k]
                prev_arr = json_to_ret['extract_fields'][k]
                for el in array_use:
                    if el not in json_to_ret['extract_fields'][k]:
                        prev_arr.append(el)
                json_to_ret['extract_fields'][k] = prev_arr
            print(json_to_ret)
            with open(os.path.join(workpath, './automatic_annotation/auto_fields/auto_fields.json'), 'w') as use_outfile:
                json.dump(json_to_ret,use_outfile)
            return JsonResponse(json_resp)
        except Exception as e:
            print(e)
            return JsonResponse(json_error)


def create_auto_annotations(request): # post

    """This view handles the creation of automatic annotations

    .js files: UpdateConfiguration.js"""

    request_body_json = json.loads(request.body)
    usecase_list = request_body_json['usecase']
    fields_list = request_body_json['selected']

    for usecase in usecase_list:
        fields = fields_list[usecase]
        print(fields)
        error = ''
        bool_val = False

        bool_val,error = create_auto_gt(usecase,fields)
        if bool_val == False:
            json_resp = {'error': error}
            return JsonResponse(json_resp)

    json_resp = {'msg':'ok'}
    return JsonResponse(json_resp)


def annotation_all_stats(request):

    """It returns the statistics of all the annotations, depending on Automatic or Manual annotation mode.

    .js files: TableToShow.js  """

    id_report = request.GET.get('report',None)
    language = request.GET.get('language',None)
    human = NameSpace.objects.get(ns_id='Human')
    robot = NameSpace.objects.get(ns_id='Robot')
    json_dict = {}
    json_dict['Human'] = get_annotations_count(id_report,language,human)
    json_dict['Robot'] = get_annotations_count(id_report,language,robot)

    return JsonResponse(json_dict)


def delete_reports(request):

    """This view removes one or more entries from the reports table

        .js files: TableToShow.js"""

    report_list = request.POST.getlist('report_list',None)
    try:
        with transaction.atomic():
            json_resp = {'msg':'ok'}
            for report in report_list:
                rp = Report.objects.filter(id_report = report['id_report'],language = report['language'])
                if rp.count() == 1:
                    Annotate.objects.filter(id_report = rp,language=rp.language).delete()
                    Linked.objects.filter(id_report = rp,language=rp.language).delete()
                    Mention.objects.filter(id_report = rp,language=rp.language).delete()
                    Associate.objects.filter(id_report = rp,language=rp.language).delete()
                    Contains.objects.filter(id_report = rp,language=rp.language).delete()
                    GroundTruthLogFile.objects.filter(id_report = rp,language=rp.language).delete()
                    rp.delete()
            print('DONE')
            return JsonResponse(json_resp)

    except Exception as e:
        json_error={'error':e}
        return JsonResponse(json_error)


def download_for_report(request):

    """This view handles the download of one or more reports' groundtruths (including the GT majority vote based.

    .js files: DownloadForModal.js"""

    request_body_json = json.loads(request.body)
    report_list =request_body_json['report_list']
    mode = request_body_json['format']
    action = request_body_json['action']
    type_gts = request_body_json['type_gts']
    annot = request_body_json['annotation_mode']
    if annot == 'Manual':
        annot = 'Human'
    elif annot == 'Automatic':
        annot = 'Robot'
    else:
        annot = None
    try:
        response = HttpResponse(content_type='text/csv')
        resp = download_report_gt(report_list,action,annot,mode,response,type_gts)
        if mode == 'biocxml' or mode == 'biocjson':
            return HttpResponse(resp, content_type='application/xml')
        elif mode == 'csv':
            return resp
        elif mode == 'json':
            return JsonResponse(resp)

    except Exception as e:
        print(e)
        json_error = {'error': e}
        return JsonResponse(json_error)


def get_gt_action_based(request):

    """This view returns the number of ground truths for the required action.

    .js files: DownloadForModal.js"""

    action = request.GET.get('action',None)
    ns = request.GET.get('annotation_mode',None)

    if ns == 'Manual':
        ns = 'Human'
    elif ns == 'Automatic':
        ns = 'Robot'
    gts = GroundTruthLogFile.objects.filter(gt_type=action)

    if ns is not None:
        ns_id = NameSpace.objects.get(ns_id = ns)
        gts = GroundTruthLogFile.objects.filter(ns_id = ns_id, gt_type = action)

    json_resp = {'count':gts.count()}
    return JsonResponse(json_resp)


def get_insertion_time_record(request):

    """This view returns the insertion time of the ground truth of a specific report and action

    .js files: ReportListUpdated.js"""

    report = request.GET.get('rep',None)
    language = request.GET.get('language',None)
    user_obj = request.GET.get('username',request.session['username'])
    ns_id_str = request.GET.get('ns_id',None)
    action = request.GET.get('action',None)
    report1 = Report.objects.get(id_report = report, language = language)
    ns_id = NameSpace.objects.get(ns_id=ns_id_str)

    user = User.objects.get(username=user_obj,ns_id=ns_id)
    gt_user = GroundTruthLogFile.objects.filter(id_report = report1, language = language, ns_id = ns_id,username=user,gt_type=action)
    if gt_user.exists():
        gt_user =GroundTruthLogFile.objects.get(id_report = report1, language = language, ns_id = ns_id,username=user,gt_type=action)
        if user_obj == request.session['username'] and ns_id_str == 'Robot':
            ns_id_rob = NameSpace.objects.get(ns_id='Robot')
            user_rob = User.objects.get(username='Robot_user', ns_id=ns_id_rob)
            gt_rob = GroundTruthLogFile.objects.get(id_report = report1, language = language, ns_id = ns_id,username=user_rob,gt_type=action)
            if gt_user.insertion_time != gt_rob.insertion_time:
                json_resp = {'date':gt_user.insertion_time}
            else:
                json_resp = {'date': ''}
        else:
            json_resp = {'date': gt_user.insertion_time}
    else:
        json_resp = {'date': ''}

    return JsonResponse(json_resp)


def get_users_list(request):

    """This view returns the list of users"""

    users = User.objects.all().values('username')
    user_black_list = ['Robot_user','IAA','Test']
    lista = []
    for name in users:
        if name['username'] not in user_black_list and name['username'] not in lista:
            lista.append(name['username'])
    return JsonResponse(lista,safe=False)


def get_user_ground_truth(request):

    """This view returns the ground-truth associated to a specific user,action,report"""

    user = request.GET.get('user',None)
    action = request.GET.get('action',None)
    mode = request.GET.get('mode',None)
    report = request.GET.get('report',None)

    language = request.GET.get('language',request.session['language'])

    mode_obj = NameSpace.objects.get(ns_id=mode)
    report = Report.objects.get(id_report = report, language = language)
    gt = get_user_gt(user,mode_obj,report,language,action)
    return JsonResponse(gt)







