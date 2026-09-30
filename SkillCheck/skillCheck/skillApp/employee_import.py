import csv

from .models import Employee

# Alias accettati per ogni colonna, case-insensitive (per tollerare intestazioni
# in italiano/inglese diverse a seconda di come è stato esportato il CSV).
COLUMN_ALIASES = {
    "nome": {"nome", "name", "nome e cognome", "nome completo"},
    "email": {"email", "e-mail", "mail"},
    "reparto": {"reparto", "dipartimento", "department", "team"},
    "cv_path": {"cv", "cv_path", "curriculum", "cv_file", "percorso_cv"},
}


def resolve_columns(fieldnames):
    normalized = {name.strip().lower(): name for name in fieldnames}
    column_map = {}
    for target, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                column_map[target] = normalized[alias]
                break
    return column_map


def import_employees_from_csv(csv_lines, resolve_cv, update_existing=False):
    """
    Logica di import condivisa tra il comando da terminale (import_employees)
    e l'endpoint web (import_employees_api).

    csv_lines: iterabile di stringhe (righe del CSV già decodificate).
    resolve_cv: funzione che, dato il valore della colonna cv_path, restituisce
        un django.core.files.File da collegare come CV, o None se non
        trovato/assente. Il comando da terminale lo cerca su disco, l'endpoint
        web lo cerca tra i file caricati insieme al CSV.
    Ritorna (stats, messages): stats è un dict con i contatori, messages una
    lista di stringhe (una per riga con esito non banale).
    """
    reader = csv.DictReader(csv_lines)
    if not reader.fieldnames:
        raise ValueError("Il CSV sembra vuoto o senza intestazioni.")

    column_map = resolve_columns(reader.fieldnames)
    if "nome" not in column_map or "email" not in column_map:
        raise ValueError(
            "Il CSV deve avere almeno una colonna per il nome e una per l'email "
            f"(intestazioni trovate: {reader.fieldnames})"
        )

    messages = []
    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

    for i, row in enumerate(reader, start=2):  # riga 1 = intestazioni
        nome = (row.get(column_map.get("nome"), "") or "").strip()
        email = (row.get(column_map.get("email"), "") or "").strip()
        reparto = (row.get(column_map.get("reparto"), "") or "").strip() if "reparto" in column_map else ""
        cv_rel_path = (row.get(column_map.get("cv_path"), "") or "").strip() if "cv_path" in column_map else ""

        if not nome or not email:
            messages.append(f"Riga {i}: nome o email mancanti, saltata.")
            stats["skipped"] += 1
            continue

        existing = Employee.objects.filter(email=email).first()
        if existing and not update_existing:
            messages.append(f"Riga {i}: {email} già presente, saltata (attiva \"Aggiorna esistenti\" per sovrascrivere).")
            stats["skipped"] += 1
            continue

        employee = existing or Employee(email=email)
        employee.nome = nome
        employee.reparto = reparto

        try:
            cv_file = resolve_cv(cv_rel_path) if cv_rel_path else None
            if cv_rel_path and cv_file is None:
                messages.append(f"Riga {i}: CV '{cv_rel_path}' non trovato, dipendente salvato senza CV.")
                employee.save()
            elif cv_file is not None:
                employee.cv_file.save(cv_file.name, cv_file, save=True)
            else:
                employee.save()
        except Exception as exc:
            messages.append(f"Riga {i}: errore su {email}: {exc}")
            stats["errors"] += 1
            continue

        if existing:
            stats["updated"] += 1
        else:
            stats["created"] += 1

    return stats, messages
