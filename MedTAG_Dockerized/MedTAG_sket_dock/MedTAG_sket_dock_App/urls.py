from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import views as auth_views


app_name='MedTAG_sket_dock_App'
urlpatterns = [

    path('', views.login, name='login'),
    path('index', views.index, name='index'),
    path('get_session_params',views.get_session_params,name='get_session_params'),
    path('login', views.login, name='login'),
    path('tutorial', views.tutorial, name='tutorial'),
    path('my_stats', views.my_stats, name='my_stats'),
    path('reports_stats', views.reports_stats, name='reports_stats'),
    path('credits', views.credits, name='credits'),
    path('get_users_list', views.get_users_list, name='get_users_list'),
    path('team_members_stats', views.team_members_stats, name='team_members_stats'),
    path('download_ground_truths', views.download_ground_truths, name='download_ground_truths'),
    path('download_key_files', views.download_key_files, name='download_key_files'),
    path('download_all_ground_truths', views.download_all_ground_truths, name='download_all_ground_truths'),
    path('infoAboutConfiguration', views.infoAboutConfiguration, name='infoAboutConfiguration'),
    path('configure', views.configure, name='configure'),
    path('get_admin', views.get_admin, name='get_admin'),
    path('get_fields', views.get_fields, name='get_fields'),
    path('registration', views.registration, name='registration'),
    path('logout', views.logout, name='logout'),
    # path('select_options', views.select_options, name='select_options'),
    # path('signals_malfunctions', views.signals_malfunctions, name='signals_malfunctions'),
    path('check_input_files', views.check_input_files, name='check_input_files'),
    path('check_files_for_update', views.check_files_for_update, name='check_files_for_update'),
    path('configure_db', views.configure_db, name='configure_db'),
    # path('mentions', views.mentions, name='mentions'),
    path('mention_insertion/<slug:action>', views.mention_insertion, name='mention_insertion'),
    path('mention_insertion', views.mention_insertion, name='mention_insertion'),
    # path('annotation', views.annotation, name='annotation'),
    path('annotationlabel/<slug:action>', views.annotationlabel, name='annotationlabel'),
    path('annotationlabel', views.annotationlabel, name='annotationlabel'),
    # path('link', views.link, name='link'),
    path('insert_link/<slug:action>', views.insert_link, name='insert_link'),
    path('get_reports', views.get_reports, name='get_reports'),
    path('new_credentials', views.new_credentials, name='new_credentials'),
    path('get_usecase_inst_lang', views.get_usecase_inst_lang, name='get_usecase_inst_lang'),
    path('report_start_end', views.report_start_end, name='report_start_end'),
    path('get_reports_from_action', views.get_reports_from_action, name='get_reports_from_action'),
    path('updateConfiguration', views.updateConfiguration, name='updateConfiguration'),
    path('update_db', views.update_db, name='update_db'),
    path('get_keys', views.get_keys, name='get_keys'),
    path('get_keys_and_uses_from_csv', views.get_keys_and_uses_from_csv, name='get_keys_and_uses_from_csv'),
    path('get_keys_from_csv_update', views.get_keys_from_csv_update, name='get_keys_from_csv_update'),
    path('download_examples', views.download_examples, name='download_examples'),
    path('download_templates', views.download_templates, name='download_templates'),
    path('get_gt_list', views.get_gt_list, name='get_gt_list'),
    # path('get_number_annot_per_report', views.get_number_annot_per_report, name='get_number_annot_per_report'),
    path('get_data', views.get_data, name='get_data'),
    path('create_auto_annotations', views.create_auto_annotations, name='create_auto_annotations'),
    # path('check_agent_presence', views.check_agent_presence, name='check_agent_presence'),
    path('get_insertion_time_record',views.get_insertion_time_record,name='get_insertion_time_record'),
    path('get_presence_examode_concepts', views.get_presence_examode_concepts, name='get_presence_examode_concepts'),
    path('report/<report_id>/<language>', views.report, name='report'),

    path('contains', views.contains, name='contains'),
    path('contains/<slug:action>', views.contains, name='contains'),
    path('test/<slug:table>', views.test, name='test'),


    # path('check_for_EXAMODE_context',views.check_for_EXAMODE_context,name='check_for_EXAMODE_context'),
    # path('get_all_mentions',views.get_all_mentions,name='get_all_mentions'),
    path('delete_reports',views.delete_reports,name='delete_reports'),
    # path('check_concepts_provenance',views.check_concepts_provenance,name='check_concepts_provenance'),
    path('conc_view',views.conc_view,name='conc_view'),
    path('get_semantic_area',views.get_semantic_area,name='get_semantic_area'),
    path('get_last_gt', views.get_last_gt, name='get_last_gt'),
    # path('get_missing_usecase_auto', views.get_missing_usecase_auto, name='get_missing_usecase_auto'),
    path('report_missing_auto', views.report_missing_auto, name='report_missing_auto'),
    path('get_post_fields_for_auto', views.get_post_fields_for_auto, name='get_post_fields_for_auto'),
    # path('delete_table_entries', views.delete_table_entries, name='delete_table_entries'),
    path('annotation_all_stats',views.annotation_all_stats,name='annotation_all_stats'),
    #CERT
    path('get_gt_action_based',views.get_gt_action_based,name='get_gt_action_based'),
    # path('get_robot_gt',views.get_robot_gt,name='get_robot_gt'),
    path('download_for_report',views.download_for_report,name='download_for_report'),
    # path('alg_extracted_concepts', views.alg_extracted_concepts, name='alg_extracted_concepts'),
    # path('copy_rows', views.copy_rows, name='copy_rows'),
    # path('is_alg_annotated', views.is_alg_annotated, name='is_alg_annotated'),
    path('get_stats_array_per_usecase', views.get_stats_array_per_usecase, name='get_stats_array_per_usecase'),
    # path('get_stats_array_per_usecase_percent', views.get_stats_array_per_usecase_percent, name='get_stats_array_per_usecase_percent'),

]


