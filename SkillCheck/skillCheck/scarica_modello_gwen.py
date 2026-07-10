from huggingface_hub import snapshot_download
import os

# Definiamo dove salvare il modello (nella tua cartella "modelli")
cartella_destinazione = os.path.join("modelli", "qwen_hr")

print("Inizio il download del modello IA (circa 3 GB)..")
print("Potrebbe volerci qualche minuto in base alla connessione.")

# Questo comando scarica tutti i file necessari e mostra una barra di caricamento
snapshot_download(
    repo_id="Qwen/Qwen2.5-1.5B-Instruct", 
    local_dir=cartella_destinazione
)

print("Download completato! Il modello è salvato nella cartella: modelli/qwen_hr")