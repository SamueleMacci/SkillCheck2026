from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from skillApp.employee_import import import_employees_from_csv


class Command(BaseCommand):
    help = (
        "Importa in blocco i dipendenti/candidati da un file CSV (colonne: "
        "nome, email, reparto opzionale, cv_path opzionale). "
        "Se cv_path è presente, il PDF viene cercato in --cv-dir (o accanto al CSV) "
        "e collegato come CV del dipendente."
    )
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Percorso del file CSV da importare")
        parser.add_argument(
            "--cv-dir",
            type=str,
            default=None,
            help="Cartella in cui cercare i PDF indicati nella colonna cv_path "
                 "(default: la cartella del CSV stesso)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Se un dipendente con la stessa email esiste già, aggiorna i suoi dati "
                 "invece di saltarlo",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"]).expanduser().resolve()
        if not csv_path.exists():
            raise CommandError(f"File non trovato: {csv_path}")

        cv_dir = Path(options["cv_dir"]).expanduser().resolve() if options["cv_dir"] else csv_path.parent

        def resolve_cv(rel_path):
            cv_file_path = (cv_dir / rel_path).resolve()
            if not cv_file_path.exists():
                return None
            with open(cv_file_path, "rb") as f:
                return ContentFile(f.read(), name=cv_file_path.name)

        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            try:
                stats, messages = import_employees_from_csv(f, resolve_cv, update_existing=options["update"])
            except ValueError as exc:
                raise CommandError(str(exc))

        for msg in messages:
            style = self.style.ERROR if "errore" in msg.lower() else self.style.WARNING
            self.stdout.write(style(msg))

        self.stdout.write(self.style.SUCCESS(
            f"Import completato: {stats['created']} creati, {stats['updated']} aggiornati, "
            f"{stats['skipped']} saltati, {stats['errors']} errori."
        ))
