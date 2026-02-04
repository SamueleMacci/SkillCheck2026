from django.db import models

class Candidate(models.Model):
    first_name = models.CharField(max_length=80)
    last_name  = models.CharField(max_length=80)
    email      = models.EmailField(unique=True)
    skills     = models.TextField(blank=True)
    job_code   = models.CharField(max_length=20, blank=True, db_index=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
