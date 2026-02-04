# forms.py
from django import forms
from .models import Resume, JobDescription


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['title', 'description']
        labels = {
            'title': 'Titolo',
            'description': 'Descrizione',
        }

class JobDescriptionAdminForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = '__all__'

    # Sovrascrivi il campo 'description' con un widget di testo
    description = forms.CharField(widget=forms.Textarea)

class ResumeForm(forms.ModelForm):
    pdf_file_upload = forms.FileField(label='Upload Curriculum PDF')

    class Meta:
        model = Resume
        fields = '__all__'

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'email', 'pdf_file_upload']


class QuestionSelectionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['domande_esperienze', 'domande_competenze', 'domande_titoli_di_studio']
        labels = {
            'domande_esperienze': 'Domande Esperienze',
            'domande_competenze': 'Domande Competenze',
            'domande_titoli_di_studio': 'Domande Titoli di Studio',
        }
        widgets = {
            'domande_esperienze': forms.Textarea(attrs={'rows': 4}),
            'domande_competenze': forms.Textarea(attrs={'rows': 4}),
            'domande_titoli_di_studio': forms.Textarea(attrs={'rows': 4}),
        }
