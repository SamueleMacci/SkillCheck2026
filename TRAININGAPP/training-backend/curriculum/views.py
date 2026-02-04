from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils import estrai_testo_da_pdf
import os
import json
from django.conf import settings
from rest_framework import status
from pathlib import Path
from rest_framework.decorators import api_view
from backend.settings import BASE_DIR
from django.views.decorators.csrf import ensure_csrf_cookie

BASE_DIR = settings.BASE_DIR

def parse_pdf_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        pdf_file = request.FILES['file']
        text = estrai_testo_da_pdf(pdf_file)
        return JsonResponse({'text': text})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ParsePDFView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({'error': 'Nessun file fornito'}, status=400)

        temp_path = os.path.join(settings.BASE_DIR, 'temp_uploaded_file.pdf')
    
        with open(temp_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        try:
            text = estrai_testo_da_pdf(temp_path)
            return Response({'text': text})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
def normalize_text(text):
    return ' '.join(sorted(text.lower().split()))


class TrainDataView(APIView):
    def get(self, request):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'trainCompare.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return JsonResponse(data, safe=False)
        except FileNotFoundError:
            return JsonResponse({'error': 'File non trovato'}, status=404)

    def post(self, request):
        print("Raw body:", request.body)
        entries = request.data
        print("Dati ricevuti dal frontend:", entries)

        if not isinstance(entries, list):
            print("I dati ricevuti non sono una lista!")
            return Response({"error": "I dati devono essere una lista di comparazioni."}, status=400)

        json_path = Path("data/trainCompare.json")
        print("Percorso file:", json_path.resolve())

        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "competenze": [],
                "esperienze": [],
                "titoli": []
            }

        count = 0
        for entry in entries:
            categoria = entry.get("categoria")
            if categoria not in data:
             continue

            new_text1 = entry.get("text1", "")
            new_text2 = entry.get("text2", "")
            new_score = round(float(entry.get("score", 0.0)) / 10 + 1e-8, 1)

            existing = data[categoria]
            updated = False

            for comp in existing:
                if (
                    normalize_text(comp["text1"]) == normalize_text(new_text1) and
                    normalize_text(comp["text2"]) == normalize_text(new_text2)
                    ):
                    media = round((comp["score"] + new_score) / 2 + 1e-8, 1)
                    comp["score"] = media
                    print(f"Media aggiornata: {comp}")
                    updated = True
                    break

            if not updated:
                nuovo_elemento = {
                    "text1": new_text1,
                    "text2": new_text2,
                    "score": new_score
                }
                data[categoria].append(nuovo_elemento)
                print(f"Aggiunta comparazione a {categoria}: {nuovo_elemento}")
                count += 1

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Salvate {count} nuove comparazioni (le altre sono state aggiornate).")
        return Response({"status": "ok", "inserite": count}, status=200)
    
@api_view(['GET'])
def get_custom_fields(request, tipologia):
    import os
    import json

    path = os.path.join(BASE_DIR, 'data', 'campi_personalizzati.json')

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return JsonResponse(data.get(tipologia, {
        "competenze": [],
        "esperienze": [],
        "titoli": []
    }))


@api_view(['POST'])
def add_custom_field(request, tipologia):
    categoria = request.data.get('categoria')
    nuovo_campo = request.data.get('campo')
    if not categoria or not nuovo_campo:
        return JsonResponse({'error': 'Dati mancanti'}, status=400)

    path = os.path.join(BASE_DIR, 'data', 'campi_personalizzati.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    data.setdefault(tipologia, {
        "competenze": [],
        "esperienze": [],
        "titoli": []
    })

    if nuovo_campo not in data[tipologia][categoria]:
        data[tipologia][categoria].append(nuovo_campo)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'success': True})

@api_view(['POST'])
def remove_custom_field(request, tipologia):
    categoria = request.data.get('categoria')
    campo = request.data.get('campo')

    if not categoria or not campo:
        return JsonResponse({'error': 'Dati mancanti'}, status=400)

    path = os.path.join(BASE_DIR, 'data', 'campi_personalizzati.json')

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if tipologia in data and campo in data[tipologia].get(categoria, []):
        data[tipologia][categoria].remove(campo)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Campo non trovato'}, status=404)


@api_view(['GET'])
def list_curriculum_types(request):
    path = os.path.join(BASE_DIR, 'data', 'campi_personalizzati.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JsonResponse({'types': list(data.keys())})
    else:
        return JsonResponse({'types': []})

@api_view(['POST'])
def add_curriculum_type(request):
    tipo = request.data.get('tipo')
    if not tipo:
        return JsonResponse({'error': 'Tipo mancante'}, status=400)

    path = os.path.join(BASE_DIR, 'data', 'campi_personalizzati.json')

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    if tipo not in data:
        data[tipo] = {
            "titoli": [],
            "competenze": [],
            "esperienze": []
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'status': 'success'})

@api_view(['GET'])
def get_all_custom_fields(request):
    path = os.path.join(BASE_DIR, 'data', 'campi_personalizzati.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

class TrainRecognizeView(APIView):
    def post(self, request):
        try:
            entries = request.data
            print("Ricevuti dati recognize:", entries)

            json_path = Path(settings.BASE_DIR) / "data" / "trainRecognize.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            else:
                existing_data = []

            nuovi = 0
            for entry in entries:
                frase = entry["frase"]
                start = entry["start"]
                end = entry["end"]
                label = entry["categoria"]

                esistente = next((e for e in existing_data if e[0] == frase), None)

                if esistente:
                    entità_corrente = (start, end, label)
                    if entità_corrente not in esistente[1]["entities"]:
                        esistente[1]["entities"].append(entità_corrente)
                        nuovi += 1
                else:
                    nuovo_esempio = (
                        frase,
                        {"entities": [(start, end, label)]}
                    )
                    existing_data.append(nuovo_esempio)
                    nuovi += 1

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

            print(f"Salvati {nuovi} nuovi esempi in trainRecognize.json")
            return Response({"status": "ok", "nuovi": nuovi}, status=200)

        except Exception as e:
            print("Errore nel salvataggio recognize:", e)
            return JsonResponse({"error": str(e)}, status=500)
        
class TrainQuestionsView(APIView):
    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "I dati devono essere una lista"}, status=400)

        file_path = Path("data/trainQuestions.json")
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []

        existing_set = {
            (item["categoria"].lower(), item["testo"].strip().lower())
            for item in existing
        }

        aggiunti = 0

        for entry in data:
            categoria = entry.get("categoria", "").strip().lower()
            testo = entry.get("testo", "").strip()
            domanda = entry.get("domanda", "").strip()

            if (categoria, testo.lower()) in existing_set:
                print(f"Duplicato ignorato: {testo}")
                continue

            if categoria == "titoli" and not domanda:
                testo_lower = testo.lower()

                if "laurea" in testo_lower:
                    domanda = f"Hai una {testo}?"
                elif "diploma" in testo_lower:
                    domanda = f"Hai un {testo}?"
                else:
                    domanda = f"Hai un titolo di studio in {testo}?"

            existing.append({
                "categoria": categoria,
                "testo": testo,
                "domanda": domanda
            })
            existing_set.add((categoria, testo.lower()))
            aggiunti += 1

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        return Response({"status": "ok", "aggiunti": aggiunti})

