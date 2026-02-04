import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent
input_path = base_dir / "trainCompare.json"
output_path = base_dir / "trainCompare_converted.py"

def convert_traincompare_to_python():
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = ["COMPARAZIONI = [\n"]

    sezioni = [
        ("competenze", "##competenze"),
        ("esperienze", "#esperienze"),
        ("titoli", "#titolidistudio")
    ]

    for key, commento in sezioni:
        lines.append(f"    {commento}")
        for voce in data.get(key, []):
            riga = f'    {{"text1": "{voce["text1"]}", "text2": "{voce["text2"]}", "score": {voce["score"]}}},'
            lines.append(riga)
        lines.append("")

    lines.append("]")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Conversione completata: {output_path.name}")

if __name__ == "__main__":
    convert_traincompare_to_python()
