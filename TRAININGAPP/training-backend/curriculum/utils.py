from pdfminer.high_level import extract_text

def estrai_testo_da_pdf(percorso_file):
    """
    Estrae il testo da un file PDF dato il suo percorso.
    Restituisce il testo come stringa.
    """
    try:
        testo = extract_text(percorso_file)
        return testo
    except Exception as e:
        print("Errore durante l'estrazione del testo dal PDF:", e)
        return ""
