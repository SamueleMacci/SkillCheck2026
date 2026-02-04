import json
from trainCompare import COMPARAZIONI

with open("trainCompare.json", "w", encoding="utf-8") as f:
    json.dump(COMPARAZIONI, f, ensure_ascii=False, indent=2)

print("trainCompare.py → trainCompare.json salvato con successo.")
