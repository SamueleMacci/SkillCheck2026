from django.urls import path, re_path
from .api_bridge_views import (
    jobs, job_detail,
    candidates, candidate_update, candidate_partial_update,
    register, login, logout,
    candidates_by_job,
)

urlpatterns = [
    path('jobs/<str:code>/candidates/', candidates_by_job, name='api_job_candidates'),
    path('jobs/', jobs, name='api_jobs'),
    re_path(r'^jobs/(?P<code>[^/]+)/$', job_detail, name='api_job_detail'),
    path('candidates/', candidates),
    path('candidates/<int:pk>/', candidate_update),
    path('candidates/<int:pk>/state/', candidate_partial_update),
    path('register/', register, name='api_register'),
    path('login/', login, name='api_login'),
    path('logout/', logout, name='api_logout'),
]
