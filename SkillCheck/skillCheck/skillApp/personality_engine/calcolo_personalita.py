import json
import os
from django.conf import settings
from skillApp.models import PersonalityQuestion


def calcola_personalita(risposte_utente):
    # risposte_utente: {"1": 3, "2": 5, ...}  (posizioni dal form)

    punteggi = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}

    # Carica le domande dal DATABASE in ordine ID
    domande = PersonalityQuestion.objects.all().order_by("id")

    for idx, domanda in enumerate(domande, start=1):
        posizione = str(idx)
        risposta = int(risposte_utente.get(posizione, 3))

        tratto = domanda.tratto
        if domanda.direzione == "+":
            punteggi[tratto] += risposta
        else:
            punteggi[tratto] += (6 - risposta)

    let_1 = "E" if punteggi["E"] >= 30 else "I"
    let_2 = "N" if punteggi["O"] >= 30 else "S"
    let_3 = "F" if punteggi["A"] >= 30 else "T"
    let_4 = "J" if punteggi["C"] >= 30 else "P"
    let_5 = "T" if punteggi["N"] >= 30 else "A"

    profilo_16p = f"{let_1}{let_2}{let_3}{let_4}-{let_5}"

    return profilo_16p, punteggi
    
    