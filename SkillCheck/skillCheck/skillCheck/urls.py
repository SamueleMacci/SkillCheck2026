"""
URL configuration for skillCheck project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views. home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView
from skillApp.views import (
    index, job_description_list, create_job_description, job_description_details,
    apply_for_job, view_applied_resumes, select_questions_for_job_description,
    save_selected_questions, mostra_domande, mostra_risposte, view_pdf
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('job_descriptions/', job_description_list, name='job_description_list'),
    path('create/', create_job_description, name='create_job_description'),
    path('<int:pk>/', job_description_details, name='job_description_details'),
    path('<int:job_description_id>/apply/', apply_for_job, name='apply_for_job'),
    path('<int:pk>/applied_resumes/', view_applied_resumes, name='view_applied_resumes'),
    path('<int:job_description_id>/select_questions/', select_questions_for_job_description,
         name='select_questions_for_job_description'),
    path('<int:pk>/save_selected_questions/', save_selected_questions, name='save_selected_questions'),
    path('mostra_domande/<int:resume_id>/<int:job_description_id>/', mostra_domande, name='mostra_domande'),
    path('risposte_domande/<int:resume_id>/', mostra_risposte, name='risposte_domande'),
    path('view_pdf/<int:resume_id>/', view_pdf, name='view_pdf'),
    path('api/', include('skillApp.api_bridge_urls')),
]
urlpatterns += [
    re_path(r'^skillcheck(?:/.*)?$',
            TemplateView.as_view(template_name='skillcheck/index.html'),
            name='skillcheck_spa'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/skillcheck/(?P<path>.*)$',
                serve, {'document_root': settings.BASE_DIR / 'static' / 'skillcheck'}),
    ]