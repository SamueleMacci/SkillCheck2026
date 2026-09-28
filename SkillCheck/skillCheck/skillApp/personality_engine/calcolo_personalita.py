import json
import os
from django.conf import settings
from skillApp.models import PersonalityQuestion

SCALA_MIN=1
SCALA_MAX=7
TRATTI=("O","C","E","A","N")


def calcola_personalita(risposte_utente):
    # risposte_utente: {"1": 3, "2": 5, ...}  (posizioni dal form)
    punto_medio = (SCALA_MIN + SCALA_MAX) / 2
    punteggi = {t: 0 for t in TRATTI}
    conteggio = {t:0 for t in TRATTI}

    #ordine domande
    domande = PersonalityQuestion.objects.all().order_by("id")

    for idx, domanda in enumerate(domande, start=1):
        tratto = (domanda.tratto or "").strip().upper()
        if tratto not in punteggi:
            continue #ignora item con tratto non valido
        risposta = int(risposte_utente.get(str(idx),punto_medio))
        conteggio[tratto]+=1

        if domanda.direzione == "+":
            punteggi[tratto] += risposta
        else:
            punteggi[tratto]+=(SCALA_MIN + SCALA_MAX - risposta)

    def alto(tratto):
        if conteggio[tratto]==0:
            return False
        return punteggi[tratto]>= conteggio[tratto]*punto_medio

    let_1 = "E" if alto("E") else "I"
    let_2 = "N" if alto("O") else "S"
    let_3 = "F" if alto("A") else "T"
    let_4 = "J" if alto("C") else "P"
    let_5 = "A" if alto("N") else "T"

    profilo_16p= f"{let_1}{let_2}{let_3}{let_4}-{let_5}"

    return profilo_16p, punteggi
