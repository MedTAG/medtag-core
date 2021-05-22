""" Define URLs pattern for groundtruth_app """
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import views as auth_views


app_name='MedTag_app'
urlpatterns = [

    path('', views.login, name='login'),
    path('index', views.index, name='index'),
    path('get_session_params',views.get_session_params,name='get_session_params'),
    path('login', views.login, name='login'),
    path('tutorial', views.tutorial, name='tutorial'),
    # path('about', views.about, name='about'),
    path('credits', views.credits, name='credits'),
    path('download_ground_truths', views.download_ground_truths, name='download_ground_truths'),
    path('download_key_files', views.download_key_files, name='download_key_files'),
    path('download_all_ground_truths', views.download_all_ground_truths, name='download_all_ground_truths'),
    path('infoAboutConfiguration', views.infoAboutConfiguration, name='infoAboutConfiguration'),
    path('configure', views.configure, name='configure'),
    path('get_admin', views.get_admin, name='get_admin'),
    path('get_fields', views.get_fields, name='get_fields'),
    path('registration', views.registration, name='registration'),
    path('logout', views.logout, name='logout'),
    path('select_options', views.select_options, name='select_options'),
    # path('signals_malfunctions', views.signals_malfunctions, name='signals_malfunctions'),
    path('check_input_files', views.check_input_files, name='check_input_files'),
    path('check_files_for_update', views.check_files_for_update, name='check_files_for_update'),
    path('configure_db', views.configure_db, name='configure_db'),
    path('mentions', views.mentions, name='mentions'),
    path('mention_insertion/<slug:action>', views.mention_insertion, name='mention_insertion'),
    path('mention_insertion', views.mention_insertion, name='mention_insertion'),
    path('annotation', views.annotation, name='annotation'),
    path('annotationlabel/<slug:action>', views.annotationlabel, name='annotationlabel'),
    path('annotationlabel', views.annotationlabel, name='annotationlabel'),
    path('link', views.link, name='link'),
    path('insert_link/<slug:action>', views.insert_link, name='insert_link'),
    path('get_reports', views.get_reports, name='get_reports'),
    path('new_credentials', views.new_credentials, name='new_credentials'),
    path('get_usecase_inst_lang', views.get_usecase_inst_lang, name='get_usecase_inst_lang'),
    path('report_start_end', views.report_start_end, name='report_start_end'),
    path('get_reports_from_action', views.get_reports_from_action, name='get_reports_from_action'),
    path('updateConfiguration', views.updateConfiguration, name='updateConfiguration'),
    path('update_db', views.update_db, name='update_db'),
    path('get_keys', views.get_keys, name='get_keys'),
    path('get_keys_from_csv', views.get_keys_from_csv, name='get_keys_from_csv'),
    path('get_keys_from_csv_update', views.get_keys_from_csv_update, name='get_keys_from_csv_update'),
    path('download_examples', views.download_examples, name='download_examples'),
    path('download_templates', views.download_templates, name='download_templates'),
    path('get_gt_list', views.get_gt_list, name='get_gt_list'),

    path('report/<report_id>/<language>', views.report, name='report'),

    path('contains', views.contains, name='contains'),
    path('contains/<slug:action>', views.contains, name='contains'),
    path('test/<slug:table>', views.test, name='test'),


    path('conc_view',views.conc_view,name='conc_view'),
    path('get_semantic_area',views.get_semantic_area,name='get_semantic_area'),
    path('get_last_gt', views.get_last_gt, name='get_last_gt'),

]


