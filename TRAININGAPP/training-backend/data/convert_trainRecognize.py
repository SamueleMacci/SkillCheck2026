import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent
input_path = base_dir / "trainRecognize.json"
output_path = base_dir / "trainRecognize_converted.py"

def convert_to_python_format():
    if not input_path.exists():
        print(f"File non trovato: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    lines = []
    lines.append("TRAIN_DATA = [\n")

    for sentence, annotation in raw_data:
        entities = annotation.get("entities", [])

        corrected_entities = []
        for start, end, label in entities:
            if label == "titoli":
                label = "titoli_di_studio"
            corrected_entities.append((start, end, label))

        entity_str = ", ".join(f"({start}, {end}, \"{label}\")" for start, end, label in corrected_entities)
        line = f"    (\"{sentence}\", {{\"entities\": [{entity_str}]}}),"
        lines.append(line)

    lines.append("]\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Conversione completata. File salvato in: {output_path.resolve()}")

if __name__ == "__main__":
    convert_to_python_format()
