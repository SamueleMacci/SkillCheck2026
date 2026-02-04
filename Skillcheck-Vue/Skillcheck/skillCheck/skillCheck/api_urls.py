from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ping, register, login,
    candidates, jobs,
    candidate_update, candidate_partial_update, job_detail,
)

router = DefaultRouter()

urlpatterns = [
    path('ping/', ping, name='ping'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('candidates/', candidates, name='candidates'),
    path('candidates/<int:pk>/', candidate_update, name='candidate_update'),
    path('candidates/<int:pk>/state/', candidate_partial_update, name='candidate_partial_update'),
    path('jobs/', jobs, name='jobs'),
    path('jobs/<str:code>/', job_detail, name='job-detail'),
    path('', include(router.urls)),
]
