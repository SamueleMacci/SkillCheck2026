import csv
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from skillApp.models import Employee

# Alias accettati per ogni colonna, case-insensitive (per tollerare intestazioni
# in italiano/inglese diverse a seconda di come è stato esportato il CSV).
COLUMN_ALIASES = {
    "nome": {"nome", "name", "nome e cognome", "nome completo"},
    "email": {"email", "e-mail", "mail"},
    "reparto": {"reparto", "dipartimento", "department", "team"},
    "cv_path": {"cv", "cv_path", "curriculum", "cv_file", "percorso_cv"},
}


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
        update_existing = options["update"]

        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise CommandError("Il CSV sembra vuoto o senza intestazioni.")
            column_map = self._resolve_columns(reader.fieldnames)
            if "nome" not in column_map or "email" not in column_map:
                raise CommandError(
                    "Il CSV deve avere almeno una colonna per il nome e una per l'email "
                    f"(intestazioni trovate: {reader.fieldnames})"
                )

            created = updated = skipped = errors = 0
            for i, row in enumerate(reader, start=2):  # riga 1 = intestazioni
                nome = (row.get(column_map.get("nome"), "") or "").strip()
                email = (row.get(column_map.get("email"), "") or "").strip()
                reparto = (row.get(column_map.get("reparto"), "") or "").strip() if "reparto" in column_map else ""
                cv_rel_path = (row.get(column_map.get("cv_path"), "") or "").strip() if "cv_path" in column_map else ""

                if not nome or not email:
                    self.stdout.write(self.style.WARNING(f"Riga {i}: nome o email mancanti, saltata."))
                    skipped += 1
                    continue

                existing = Employee.objects.filter(email=email).first()
                if existing and not update_existing:
                    self.stdout.write(self.style.WARNING(f"Riga {i}: {email} già presente, saltata (usa --update per sovrascrivere)."))
                    skipped += 1
                    continue

                employee = existing or Employee(email=email)
                employee.nome = nome
                employee.reparto = reparto

                try:
                    if cv_rel_path:
                        cv_file_path = (cv_dir / cv_rel_path).resolve()
                        if not cv_file_path.exists():
                            self.stdout.write(self.style.WARNING(
                                f"Riga {i}: CV non trovato ({cv_file_path}), dipendente salvato senza CV."
                            ))
                            employee.save()
                        else:
                            with open(cv_file_path, "rb") as cv_f:
                                employee.cv_file.save(cv_file_path.name, File(cv_f), save=True)
                    else:
                        employee.save()
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"Riga {i}: errore su {email}: {exc}"))
                    errors += 1
                    continue

                if existing:
                    updated += 1
                else:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import completato: {created} creati, {updated} aggiornati, {skipped} saltati, {errors} errori."
        ))

    @staticmethod
    def _resolve_columns(fieldnames):
        normalized = {name.strip().lower(): name for name in fieldnames}
        column_map = {}
        for target, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in normalized:
                    column_map[target] = normalized[alias]
                    break
        return column_map
