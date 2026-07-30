import json
from pathlib import Path

from django.core.management.base import BaseCommand

from skillApp.models import PersonalityQuestion

QUESTIONS_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "personality_engine"
    / "domande_personalità.json"
)


class Command(BaseCommand):
    help = "Importa le domande del test di personalità da domande_personalità.json nel database"
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Svuota la tabella PersonalityQuestion e reimporta da zero",
        )

    def handle(self, *args, **options):
        if PersonalityQuestion.objects.exists():
            if not options["force"]:
                self.stdout.write(self.style.WARNING(
                    "PersonalityQuestion contiene già dati: nessuna azione. Usa --force per reimportare."
                ))
                return
            PersonalityQuestion.objects.all().delete()

        with open(QUESTIONS_FILE, encoding="utf-8") as f:
            domande = json.load(f)

        PersonalityQuestion.objects.bulk_create(
            PersonalityQuestion(testo=d["testo"], tratto=d["tratto"], direzione=d["direzione"])
            for d in domande
        )

        self.stdout.write(self.style.SUCCESS(
            f"Importate {len(domande)} domande di personalità."
        ))
