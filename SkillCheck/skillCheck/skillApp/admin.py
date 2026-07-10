# admin.py
from django.contrib import admin
from .models import JobDescription, Resume, PersonalityCounter, EmailTemplate
from .forms import JobDescriptionAdminForm, ResumeForm

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)


    form = JobDescriptionAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Parameters', {
            'fields': ('esperienze', 'competenze', 'titoli_di_studio', 'domande_titoli_di_studio',
                       'domande_competenze', 'domande_esperienze'),
            'classes': ('collapse',),
        }),
    )

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'esperienze_short', 'competenze_short', 'titoli_di_studio_short',
                    'titoli_di_studio_similarity', 'competenze_similarity', 'esperienze_similarity')

    search_fields = ('name', 'email')
    readonly_fields = ('esperienze', 'competenze', 'titoli_di_studio', 'titoli_di_studio_similarity',
                       'competenze_similarity', 'esperienze_similarity')

    form = ResumeForm
    # Opzioni aggiuntive per gestire il caricamento del file PDF
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'pdf_file_upload', 'job_description')
        }),
        ('Calculated Similarities', {
            'fields': ('esperienze', 'competenze','titoli_di_studio', 'titoli_di_studio_similarity', 'competenze_similarity', 'esperienze_similarity'),
            'classes': ('collapse',),
        }),
    )

    def esperienze_short(self, obj):
        # Restituisci i primi 30 caratteri delle esperienze
        return obj.esperienze[:30] if obj.esperienze else ''

    esperienze_short.short_description = 'Esperienze'

    def competenze_short(self, obj):
        # Restituisci i primi 30 caratteri delle competenze
        return obj.competenze[:30] if obj.competenze else ''

    competenze_short.short_description = 'Competenze'

    def titoli_di_studio_short(self, obj):
        # Restituisci i primi 30 caratteri dei titoli di studio
        return obj.titoli_di_studio[:30] if obj.titoli_di_studio else ''

    titoli_di_studio_short.short_description = 'Titoli di studio'
    
admin.site.register(PersonalityCounter)
admin.site.register(EmailTemplate)