from django.urls import path
from .views import (
    ParsePDFView,
    get_custom_fields,
    add_custom_field,
    list_curriculum_types,
    add_curriculum_type,
    remove_custom_field,
    get_csrf_token,
    TrainDataView,
    TrainRecognizeView,
    TrainQuestionsView
)

urlpatterns = [
    path('parse-pdf/', ParsePDFView.as_view(), name='parse-pdf'),
    path('train-data/', TrainDataView.as_view(), name='train-data'),
    path('custom-fields/add-type', add_curriculum_type, name='add_curriculum_type'),
    path('custom-fields/<str:tipologia>/add', add_custom_field, name='add_custom_field'),
    path('custom-fields/<str:tipologia>/', get_custom_fields, name='get_custom_fields'),
    path('custom-fields/', list_curriculum_types, name='list_curriculum_types'),
    path('custom-fields/<str:tipologia>/remove', remove_custom_field, name='remove_custom_field'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path("train-recognize/", TrainRecognizeView.as_view(), name="train-recognize"),
    path('train-questions/', TrainQuestionsView.as_view(), name='train-questions'),
]
