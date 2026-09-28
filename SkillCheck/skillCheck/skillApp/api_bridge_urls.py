from django.urls import path, re_path
from .api_bridge_views import (
    jobs, job_detail,
    candidates, candidate_update, candidate_partial_update,
    register, login, logout,
    candidates_by_job,
    apply_for_job_api, mostra_domande_api, personality_test_api,
    select_questions_api, save_selected_questions_api,
    employees, employee_detail, nominate_candidate, employee_job_scores,
)

urlpatterns = [
    path('jobs/<str:code>/candidates/', candidates_by_job, name='api_job_candidates'),
    path('jobs/<int:job_description_id>/nominate/', nominate_candidate, name='api_nominate_candidate'),
    path('jobs/<int:job_description_id>/employee_scores/', employee_job_scores, name='api_employee_job_scores'),
    path('jobs/', jobs, name='api_jobs'),
    re_path(r'^jobs/(?P<code>[^/]+)/$', job_detail, name='api_job_detail'),
    path('employees/', employees, name='api_employees'),
    path('employees/<int:pk>/', employee_detail, name='api_employee_detail'),
    path('candidates/', candidates),
    path('candidates/<int:pk>/', candidate_update),
    path('candidates/<int:pk>/state/', candidate_partial_update),
    path('register/', register, name='api_register'),
    path('login/', login, name='api_login'),
    path('logout/', logout, name='api_logout'),
    path('apply/<int:job_description_id>/', apply_for_job_api, name='api_apply_for_job'),
    path('mostra_domande/<int:resume_id>/<int:job_description_id>/', mostra_domande_api, name='api_mostra_domande'),
    path('personality_test/<int:resume_id>/', personality_test_api, name='api_personality_test'),
    path('select_questions/<int:job_description_id>/', select_questions_api, name='api_select_questions'),
    path('select_questions/<int:job_description_id>/save/', save_selected_questions_api, name='api_save_selected_questions'),
]
