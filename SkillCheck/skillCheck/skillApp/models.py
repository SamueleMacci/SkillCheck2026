# app/models.py
from django.db import models
from .utils import compute_satisfaction_percentage, extract_entities_from_text, \
    generate_questions, extract_text_from_pdf_content, filter_new_questions, extract_entities_resume
from django_cryptography.fields import encrypt

class PersonalityQuestion(models.Model):
    testo = models.TextField()
    tratto = models.CharField(max_length=1)  # E, A, C, O, N
    direzione = models.CharField(max_length=1)  # + o -  

class JobDescription(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    resumes = models.ManyToManyField('Resume', related_name='job_descriptions')
    esperienze = models.TextField(blank=True)  # Campo per memorizzare la lista di esperienze
    competenze = models.TextField(blank=True)  # Campo per memorizzare la lista di competenze
    titoli_di_studio = models.TextField(blank=True)  # Campo per memorizzare la lista di titoli di studio
    domande_esperienze = models.TextField(
        blank=True)  # Aggiunto campo per memorizzare la domanda selezionata per le esperienze
    domande_competenze = models.TextField(
        blank=True)  # Aggiunto campo per memorizzare la domanda selezionata per le competenze
    domande_titoli_di_studio = models.TextField(
        blank=True)  # Aggiunto campo per memorizzare la domanda selezionata per i titoli di studio
    domande_selezionate = models.TextField(blank=True)  # Campo per memorizzare le domande selezionate
    domande_con_data = models.TextField(blank=True)  # Campo per le domande selezionabili dai curriculum

    def save(self, *args, **kwargs):
        if self.pk is None:  # Se l'oggetto non esiste ancora nel database
            # Estrai le entità dal testo del curriculum
            self.esperienze, self.competenze, self.titoli_di_studio = extract_entities_from_text(self.description)

            # Genera le domande per le liste
            self.domande_esperienze, self.domande_competenze, self.domande_titoli_di_studio, self.domande_con_data = generate_questions(
                self.esperienze, self.competenze, self.titoli_di_studio)

        # Chiamare il metodo save() della classe padre per eseguire il salvataggio effettivo
        super(JobDescription, self).save(*args, **kwargs)

    def save_selected_questions(self, selected_esperienze, selected_competenze, selected_titoli_di_studio):
        self.domande_selezionate = "\n".join(selected_esperienze + selected_competenze + selected_titoli_di_studio)
        # Salva solo le domande senza ricalcolare altre proprietà
        self._update_fields(['domande_selezionate', 'domande_con_data'])

    def _update_fields(self, fields):
        # Salva solo i campi specificati senza chiamare il metodo save predefinito
        self.__class__.objects.filter(pk=self.pk).update(**{field: getattr(self, field) for field in fields})


class Resume(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    pdf_file = models.BinaryField()

    esperienze = models.TextField(blank=True)
    competenze = models.TextField(blank=True)
    titoli_di_studio = models.TextField(blank=True)

    titoli_di_studio_similarity = models.FloatField(null=True, blank=True)
    competenze_similarity = models.FloatField(null=True, blank=True)
    esperienze_similarity = models.FloatField(null=True, blank=True)

    domande_personali = models.TextField(blank=True)
    domande_affinity = models.FloatField(null=True, blank=True)
    domande_e_risposte = models.JSONField(default=dict)  # Campo per memorizzare domande e risposte come dizionario JSON
    risposte_personalita_raw = encrypt(models.JSONField(null=True, blank=True))
    job_description = models.ForeignKey(JobDescription, on_delete=models.CASCADE, default=1)
    resume_text = models.TextField(blank=True)
    pdf_file_upload = models.FileField(upload_to='pdf_resumes/', null=True, blank=True)
    comment = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        if self.pdf_file_upload:
            with self.pdf_file_upload.open('rb') as f:
                # Leggi il contenuto del file
                pdf_content = f.read()

                print("save")

                # Estrai il testo dal PDF
                text = extract_text_from_pdf_content(pdf_content)

                # Assegna il testo estratto al campo resume_text
                self.resume_text = text
                self.pdf_file = pdf_content

                # Estrai le entità dal testo del curriculum
                self.esperienze, self.competenze, self.titoli_di_studio = extract_entities_resume(text)

                self.titoli_di_studio_similarity, elem_titoli = compute_satisfaction_percentage(
                    self.job_description.titoli_di_studio, self.titoli_di_studio)
                self.competenze_similarity, elem_competenze = compute_satisfaction_percentage(
                    self.job_description.competenze, self.competenze)
                self.esperienze_similarity, elem_esperienze = compute_satisfaction_percentage(
                    self.job_description.esperienze, self.esperienze)

                # Unisci le tre liste in un'unica lista
                lowest_elements = elem_titoli + elem_competenze + elem_esperienze

                # Seleziona fino a 3 nuove domande e il relativo dato tra i lowest elements
                self.domande_personali = filter_new_questions(self.job_description, lowest_elements)

                super().save(*args, **kwargs)
        else:
            print("no pdf")
            super().save(*args, **kwargs)

    def save_affinity(self, *args, **kwargs):
        self._update_fields(['domande_affinity', 'domande_e_risposte'])

    def _update_fields(self, fields):
        # Salva solo i campi specificati senza chiamare il metodo save predefinito
        self.__class__.objects.filter(pk=self.pk).update(**{field: getattr(self, field) for field in fields})
        
class PersonalityCounter(models.Model):
    personality_type = models.CharField(max_length=64, unique=True)
    last_used_sequence = models.IntegerField(default=0)

    def __str__(self):
        return f"Hash {self.personality_type[:8]} - Ultimo: {self.last_used_sequence}"

class EmailTemplate(models.Model):
    personality_type = models.CharField(max_length=10)
    sequence_number = models.IntegerField()
    body_text = models.TextField()

    class Meta:
        unique_together = ('personality_type', 'sequence_number')

    def __str__(self):
        return f"Template {self.sequence_number} per {self.personality_type}"
