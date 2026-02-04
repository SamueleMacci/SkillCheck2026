import json
from collections import defaultdict

json_path = "trainQuestions.json"
py_path = "trainQuestions.py"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

categorie = defaultdict(list)
for entry in data:
    categoria = entry["categoria"]
    if categoria == "titoli":
        categoria_key = "titoli_di_studio"
        entry = entry.copy()
        entry["categoria"] = "titoli_di_studio"
    else:
        categoria_key = categoria

    categorie[categoria_key].append(entry)

with open(py_path, "w", encoding="utf-8") as f:
    f.write("dataset = [\n")

    for categoria in ["titoli_di_studio", "competenze", "esperienze"]:
        if categoria in categorie:
            f.write(f"  # {categoria}\n")
            for entry in categorie[categoria]:
                f.write(f"  {json.dumps(entry, ensure_ascii=False)},\n")

    f.write("]\n")
