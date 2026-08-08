# --- LIBRERIE STANDARD PYTHON ---
import re
from urllib.parse import unquote
from collections import defaultdict
from decimal import Decimal

# --- LIBRERIE DJANGO ---
from django.apps import apps
from django.db.models import Q
from django.utils.timezone import now
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.core.files.storage import Storage
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
#from django.core.mail import send_mail beckend mail import
from django.core.mail import EmailMessage

# --- LIBRERIE REST FRAMEWORK ---
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

# --- IMPORT LOCALI ---
from .models import EmailTemplate, PersonalityCounter, PersonalityQuestion  # <--- models for mail
from .personality_engine.calcolo_personalita import calcola_personalita
from .utils import genera_consiglio_ia# <--- local ai
from .forms import ResumeForm
from .views import (
    _get_domande_job_desc_resume,
    save_domande_risposte,
    build_mostra_domande_context,
    parse_generated_questions,
)

from .utils import hash_personality
# ------------ Model access (robusto a differenze di nomi) ------------
JD = apps.get_model('skillApp', 'JobDescription')
# Prova a risolvere il modello dei candidati/applied resumes
Resume = (apps.get_model('skillApp', 'Resume')
          or apps.get_model('skillApp', 'AppliedResume')
          or apps.get_model('skillApp', 'Candidate'))

# Field names probabili / fallback
def _get(obj, *names, default=None):
    """Ritorna il primo attributo esistente tra *names*.
    Se l'attributo è callable, lo chiama senza argomenti.
    """
    for n in names:
        if hasattr(obj, n):
            try:
                val = getattr(obj, n)
                return val() if callable(val) else val
            except Exception:
                continue
    return default

def _abs_url(request: HttpRequest, value):
    """
    Restituisce un URL assoluto se 'value' è:
    - una stringa (già url o path relativo),
    - un FileField / FieldFile (usa .url),
    altrimenti None.
    """
    if not value:
        return None
    try:
        url = getattr(value, "url", None) or str(value)
    except Exception:
        url = str(value)
    if url.startswith("http://") or url.startswith("https://"):
        return url
    try:
        return request.build_absolute_uri(url)
    except Exception:
        return url

def _set(obj, name, value):
    if hasattr(obj, name):
        setattr(obj, name, value)
        return True
    return False

# mappa inversa per FK dai resume alla JD
def _fk_name_to_jd():
    # prova i nomi comuni usati nel repo
    for field in getattr(Resume, '_meta').get_fields():
        if getattr(field, 'related_model', None) is JD:
            return field.name
    for guess in ('job_description', 'job', 'jd'):
        if hasattr(Resume, guess):
            return guess
    return None

RESUME_FK_TO_JD = _fk_name_to_jd()

def _job_code_for_resume(r):
    """
    Ritorna il pk della JD associata a r, gestendo sia FK singola che relazioni many.
    Fallback a eventuali campi flat (job_code/job/code).
    """
    if RESUME_FK_TO_JD and hasattr(r, RESUME_FK_TO_JD):
        rel = getattr(r, RESUME_FK_TO_JD)
        if hasattr(rel, 'pk'):
            return str(rel.pk)
        try:
            first = rel.first()
            if first:
                return str(first.pk)
        except Exception:
            pass

    # Fallback su campi flat
    jc = _get(r, 'job_code', 'job', 'code', default='')
    return str(jc or '')

# ------------ Cache stati ------------
STATUS_CACHE = defaultdict(dict)

def normalize_status(value):
    if not value:
        return None
    v = str(value).strip().lower()
    mapping = {
        'ok': 'ok', 'eligible': 'ok', 'idoneo': 'ok', 'assunto': 'ok',
        'rejected': 'rejected', 'scartato': 'rejected', 'non idoneo': 'rejected',
        'pending': 'pending', 'attesa': 'pending',
        'contact': 'contact', 'da contattare': 'contact',
    }
    return mapping.get(v, v)

def _resume_queryset_for_code(code):
    # nel FE usiamo "code" = id JD in stringa
    try:
        jd = JD.objects.get(pk=int(code))
    except Exception:
        return JD.objects.none(), Resume.objects.none()

    if not RESUME_FK_TO_JD:
        return jd, Resume.objects.none()

    return jd, Resume.objects.filter(**{f"{RESUME_FK_TO_JD}__pk": jd.pk})

def compute_counts_for(code):
    jd, qs = _resume_queryset_for_code(code)
    if not jd:
        return {"total": 0, "ok": 0, "rejected": 0, "pending": 0, "contact": 0}

    total = qs.count()
    counts = {"total": total, "ok": 0, "rejected": 0, "pending": 0, "contact": 0}
    # conteggi solo da cache se non esiste campo status nel DB
    for r in qs:
        st = STATUS_CACHE.get(r.pk, {}).get("status") or normalize_status(_get(r, 'status', 'state'))
        st = normalize_status(st) or 'pending'
        if st in counts:
            counts[st] += 1
        else:
            counts['pending'] += 1
    return counts

def _to_num(x):
    try:
        if x is None or x == '':
            return None
        return float(x)
    except Exception:
        try:
            return float(Decimal(str(x)))
        except Exception:
            return None

def _resume_to_row(request, r, job_code):
    first = _get(r, 'first_name', 'name', default='').strip()
    last  = _get(r, 'last_name', default='').strip()
    email = _get(r, 'email', 'mail', default='')
    phone = _get(r, 'phone', 'telefono', default='')
    cache = STATUS_CACHE.get(r.pk, {})
    status_db = normalize_status(_get(r, 'status', 'state'))
    overall   = cache.get("status") or status_db or "pending"
    score_title = _get(
        r, 'titoli_di_studio_similarity',
        'score_title', 'title_score', 'voto_titolo', 'voto_titoli', 'voto_titolo_studio'
    )
    score_skills = _get(
        r, 'competenze_similarity',
        'score_skills', 'skills_score', 'voto_competenze', 'voti_competenze', 'score_competenze'
    )
    score_experience = _get(
        r, 'esperienze_similarity',
        'score_experience', 'experience_score', 'voto_esperienze', 'voto_esperienza', 'score_esperienze'
    )
    score_similarity = _get(
        r, 'score_similarity_avg', 'similarity_avg',
        'media_voti', 'media_similarita', 'media_voti_similarita'
    )
    score_questions = _get(
        r, 'domande_affinity',
        'score_questions', 'questions_score', 'punteggio_domande'
    )
    score_avg = _get(
        r, 'score_avg', 'final_score', 'total_score',
        'media_tot', 'media_totale', 'media'
    )
    if score_similarity in (None, ''):
        parts = [_to_num(score_title), _to_num(score_skills), _to_num(score_experience)]
        parts = [p for p in parts if p is not None]
        if parts:
            score_similarity = sum(parts) / len(parts)
    if score_avg in (None, ''):
        ms = _to_num(score_similarity)
        q  = _to_num(score_questions)
        comps = [v for v in (ms, q) if v is not None]
        if comps:
            score_avg = sum(comps) / len(comps)
    pdf_url     = request.build_absolute_uri(f"/view_pdf/{r.pk}/")
    answers_url = request.build_absolute_uri(f"/risposte_domande/{r.pk}/")
    return {
        "id": r.pk,
        "first_name": first,
        "last_name": last,
        "email": email,
        "phone": phone,
        "status": overall,
        "status_cv":   cache.get("status_cv"),
        "status_hr":   cache.get("status_hr"),
        "status_tech": cache.get("status_tech"),
        "job_code": str(job_code),
        "score_title":          score_title,
        "score_skills":         score_skills,
        "score_experience":     score_experience,
        "score_similarity_avg": score_similarity,
        "score_questions":      score_questions,
        "score_avg":            score_avg,

        "comment": _get(r, 'comment', default=''),

        "pdf_url":     pdf_url,
        "answers_url": answers_url,
    }

# ------------------------ Endpoints ------------------------

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def jobs(request):
    if request.method == 'GET':
        data = []
        for jd in JD.objects.all().order_by('-id'):
            code = str(jd.pk)
            data.append({
                "name": _get(jd, 'title', 'name', default=f"JD {jd.pk}"),
                "content": _get(jd, 'description', 'content', default=''),
                "deadline": _get(jd, 'deadline', 'scadenza', default=None),
                "code": code,
                "is_public": _get(jd, 'is_public', default=True),
                "counts": compute_counts_for(code),
            })
        return Response(data)

    # POST create
    payload = request.data or {}
    title = payload.get('name') or payload.get('title') or "Senza titolo"
    description = payload.get('content') or payload.get('description') or ""
    deadline = payload.get('deadline', None)
    is_public = payload.get('is_public', True)

    jd = JD()
    _set(jd, 'title', title) or _set(jd, 'name', title)
    _set(jd, 'description', description) or _set(jd, 'content', description)
    _set(jd, 'deadline', deadline)
    _set(jd, 'is_public', is_public)
    jd.save()

    code = str(jd.pk)
    return Response({
        "id": jd.pk,
        "name": title,
        "content": description,
        "deadline": deadline,
        "code": code,
        "is_public": is_public,
        "counts": compute_counts_for(code),
    }, status=http_status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def job_detail(request, code):
    code = unquote(code)
    try:
        jd = JD.objects.get(pk=int(code))
    except Exception:
        return Response(status=http_status.HTTP_404_NOT_FOUND)

    return Response({
        "name": _get(jd, 'title', 'name', default=f"JD {jd.pk}"),
        "content": _get(jd, 'description', 'content', default=''),
        "deadline": _get(jd, 'deadline', 'scadenza', default=None),
        "code": str(jd.pk),
        "is_public": _get(jd, 'is_public', default=True),
        "counts": compute_counts_for(str(jd.pk)),
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def candidates(request):
    job = request.query_params.get('job', '')
    job = unquote(job or '')
    jd, qs = _resume_queryset_for_code(job)
    rows = [_resume_to_row(request, r, job) for r in qs]
    return Response(rows)

@api_view(['GET'])
@permission_classes([AllowAny])
def candidates_by_job(request, code):
    code = unquote(str(code or ''))
    jd, qs = _resume_queryset_for_code(code)
    rows = [_resume_to_row(request, r, code) for r in qs]
    return Response(rows)

@api_view(['PATCH'])
@permission_classes([AllowAny])
def candidate_update(request, pk):
    try:
        r = Resume.objects.get(pk=pk)
    except Resume.DoesNotExist:
        return Response(status=http_status.HTTP_404_NOT_FOUND)
    
    payload = request.data or {}
    st = normalize_status(payload.get('status'))
    
    if st:
        saved = False
        if _set(r, 'status', st):
            try:
                r.save(update_fields=['status'])
                saved = True
            except Exception:
                pass
        if not saved and _set(r, 'state', st):
            try:
                r.save(update_fields=['state'])
            except Exception:
                try:
                    r.save()
                except Exception:
                    pass
        STATUS_CACHE[pk]['status'] = st

        # ---  IN CASE PERSON WENT REJECTED ---
        if st == 'rejected':
            if hasattr(r, 'risposte_personalita_raw') and r.risposte_personalita_raw:
                
                # 1.  find skill gaps and generate advice with AI
                #gaps = getattr(r, 'domande_e_risposte', {}).get("skill_gaps", []) if hasattr(r, 'domande_e_risposte') and isinstance(getattr(r, 'domande_e_risposte'), dict) else []
                #gap_skills = [g.get("jd_skill") for g in gaps if isinstance(g, dict) and g.get("jd_skill")]
                #skills_str = ", ".join(gap_skills) if gap_skills else ""
                
               # print(f"Richiesta frase all'IA per le skill: {skills_str}")
                #commento_ia = genera_consiglio_ia(skills_str)
                #print(f"Risposta IA: {commento_ia}")
                #NEW FIND SKILL GAPS 
                domande_risposte = getattr(r,'domande_e_risposte', {})
                gap_skills = []
                if isinstance(domande_risposte, dict):
                    for chiave, valore in domande_risposte.items():
                        if isinstance(valore, str) and valore.strip().lower()== "no":
                            skill_pulita =  chiave.replace("?","").strip()
                            gap_skills.append(skill_pulita)
                skills_str = ", ".join(gap_skills) if gap_skills else ""
                commento_ia = genera_consiglio_ia(skills_str)
                        

                # 2. Calculate personality profile from raw answers 
                risposte = r.risposte_personalita_raw
                profilo_completo, _ = calcola_personalita(risposte)
                profilo_base = profilo_completo[:4]
               
                
                # Check all MAIUSC letters and strip whitespace
                profilo_base = str(profilo_completo[:4]).strip().upper()
                
                #print(f"Sto cercando nel database il template per la personalità: '{profilo_base}'")
                
                # 3. base date for compilation 
                jd_title = 'la posizione'
                if RESUME_FK_TO_JD and hasattr(r, RESUME_FK_TO_JD):
                    rel = getattr(r, RESUME_FK_TO_JD)
                    if rel:
                        if hasattr(rel, 'title'):
                            jd_title = rel.title
                        elif hasattr(rel, 'first') and rel.first():
                            jd_title = rel.first().title

                dati_frontend = _resume_to_row(request, r, _job_code_for_resume(r))
                score_avg = dati_frontend.get("score_avg")
                
                # *10 is a %
                percentuale = int(float(score_avg) * 10) if score_avg else 0
                nome_candidato = _get(r, 'first_name', 'name', default='Candidato').strip()
                email_destinatario = _get(r, 'email', 'mail')

                # 4. Rotation email 1->10 for each personality type
                profilo_hash = hash_personality(profilo_base)
                counter, _ = PersonalityCounter.objects.get_or_create(personality_type=profilo_hash)
                next_sequence = (counter.last_used_sequence % 10) + 1
                
                try:
                    template = EmailTemplate.objects.get(personality_type=profilo_base, sequence_number=next_sequence)
                    email_finale = template.body_text
                    
                    lignes = email_finale.split('\n')
                    subject = "Aggiornamento sulla tua candidatura"
                    if "Oggetto:" in lignes[0]:
                        subject = lignes[0].replace("Oggetto:", "").replace("**", "").strip()
                        email_finale = '\n'.join(lignes[1:]).strip()
                        
                except EmailTemplate.DoesNotExist:
                    email_finale = "Gentile [Nome del Candidato], grazie per aver presentato la tua candidatura. [commento] Cordiali saluti, Il Team HR."
                    subject = "Esito della tua candidatura"

                # 5. COMPILE MAIL 
                email_finale = email_finale.replace("[Nome del Candidato]", nome_candidato)
                email_finale = email_finale.replace("[Posizione]", jd_title)
                email_finale = email_finale.replace("[Azienda]", "SkillCheck")
                email_finale = email_finale.replace("[C]%", f"{percentuale}%")
                email_finale = email_finale.replace("[commento]", commento_ia) 
                subject = subject.replace("[Posizione]", jd_title).replace("[Azienda]", "SkillCheck")
                # 6. send email to candidate
                # email_destinatario:
                    #try:
                        #send_mail(
                            #subject=subject,
                            #message=email_finale,
                            #from_email='recruiting@tuosito.com', # insert here your real email address
                            #recipient_list=[email_destinatario],
                            #fail_silently=False, 
                        #) beckend mail block
                        #print(f"Email inviata con successo a {email_destinatario} (Template {next_sequence} per {profilo_base})")
                        
                        # save counter if the email is sent successfully
                if email_destinatario:
                    try:
                        # Recupera l'email del recruiter se è loggato
                        recruiter_email = None
                        if request.user and request.user.is_authenticated:
                            recruiter_email = request.user.email
                        # Imposta a chi deve andare la risposta (Reply-To)
                        reply_to_list = [recruiter_email] if recruiter_email else []

                        # Crea l'oggetto EmailMessage
                        email_msg = EmailMessage(
                            subject=subject,
                            body=email_finale,
                            from_email='avvisi.skillcheck@gmail.com',  # <-- site/server mail address
                            to=[email_destinatario],
                            reply_to=reply_to_list                # <-- will be recruiter mail address
                        )
                                    
                        # Invia l'email
                        email_msg.send(fail_silently=False)        
                        
                        counter.last_used_sequence = next_sequence
                        counter.save()
                    except Exception as e:
                        print(f"Errore invio email: {e}")

                # 7. DELETE PERSONALITY DATA
                try:
                    r.risposte_personalita_raw = None
                    r.save(update_fields=['risposte_personalita_raw'])
                except Exception:
                    pass
        # --- END AI BLOCK---
        
        #--IN CASE OF REJECTED CANDIDATE WITHOUT PERSONALITY DATA, SEND A GENERIC EMAIL WITH AI COMMENT--    
            else:
                
                # 1. SKILL GAPS
                domande_risposte = getattr(r, 'domande_e_risposte', {})
                gap_skills = []
                if isinstance(domande_risposte, dict):
                    for chiave, valore in domande_risposte.items():
                        if isinstance(valore, str) and valore.strip().lower() == "no":
                            skill_pulita = chiave.replace("?", "").strip()
                            gap_skills.append(skill_pulita)
                            
                skills_str = ", ".join(gap_skills) if gap_skills else ""
                commento_ia = genera_consiglio_ia(skills_str)

                # 2. BASE DATA FOR EMAIL
                nome_candidato = _get(r, 'first_name', 'name', default='Candidato').strip()
                email_destinatario = _get(r, 'email', 'mail')
                
                # 3. GENERIC EMAIL TEMPLATE
                subject = "Aggiornamento esito candidatura"
                email_finale = f"Gentile {nome_candidato},\n\nTi confermiamo che in questa fase abbiamo deciso di non procedere con la tua candidatura. {commento_ia}\n\nTi auguriamo il meglio per le tue future opportunità professionali.\n\nCordiali saluti,\nIl Team HR."

                # 4. SEND EMAIL
                if email_destinatario:
                    try:
                        recruiter_email = None
                        if request.user and request.user.is_authenticated:
                            recruiter_email = request.user.email
                        reply_to_list = [recruiter_email] if recruiter_email else []

                        email_msg = EmailMessage(
                            subject=subject,
                            body=email_finale,
                            from_email='avvisi.skillcheck@gmail.com',
                            to=[email_destinatario],
                            reply_to=reply_to_list
                        )
                        email_msg.send(fail_silently=False)
                    except Exception as e:
                        print(f"Errore invio email di fallback: {e}")
                        
    for k in ('email', 'phone', 'comment'):
        if k in payload and _set(r, k, payload[k]):
            try:
                r.save(update_fields=[k])
            except Exception:
                try:
                    r.save()
                except Exception:
                    pass
                    
    job_code = _job_code_for_resume(r)
    return Response(_resume_to_row(request, r, job_code))

@api_view(['PATCH'])
@permission_classes([AllowAny])
def candidate_partial_update(request, pk):
    # aggiorna solo cache per fasi
    cache = STATUS_CACHE[pk]
    for k in ('status_cv', 'status_hr', 'status_tech', 'status'):
        if k in request.data:
            val = request.data.get(k)
            cache[k] = normalize_status(val) if k == 'status' else val
    STATUS_CACHE[pk] = cache
    return Response({"id": pk, **cache})

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def register(request):
    """
    Compatibile con la tua SPA:
    body: { "email": ..., "password": ..., "username": (opzionale) }
    """
    raw_username = (request.data.get('username') or '').strip()
    password     = (request.data.get('password') or '').strip()
    email        = (request.data.get('email') or '').strip().lower()

    if not email or not password:
        return Response({'detail': 'username, email e password sono obbligatori'}, status=400)

    # username auto-derivato se non fornito
    if not raw_username:
        base = (email.split('@')[0] or '').lower()
        base = re.sub(r'[^a-z0-9_]', '_', base)[:30] or 'user'
        candidate = base
        i = 1
        while User.objects.filter(username=candidate).exists():
            suffix = f"_{i}"
            candidate = (base[:max(1, 30 - len(suffix))]) + suffix
            i += 1
        username = candidate
    else:
        username = raw_username

    if User.objects.filter(email__iexact=email).exists():
        return Response({'detail': 'email già registrata'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'username già esistente'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'username': username}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Compatibile con la tua SPA:
    body: { "email": ..., "password": ... }  (oppure "username" al posto di email)
    """
    email    = (request.data.get('email') or '').strip().lower()
    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()

    if email and not username:
        try:
            u = User.objects.get(email__iexact=email)
            username = u.get_username()
        except User.DoesNotExist:
            return Response({'detail': 'credenziali non valide'}, status=400)

    if not username or not password:
        return Response({'detail': 'email/username e password richiesti'}, status=400)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'detail': 'credenziali non valide'}, status=400)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Invalida il token dell’utente corrente.
    """
    Token.objects.filter(user=request.user).delete()
    return Response({'detail': 'logout ok'})


# ------------ Flusso candidato (pubblico, senza login) ------------

@api_view(['POST'])
@permission_classes([AllowAny])
def apply_for_job_api(request, job_description_id):
    """
    Candidatura di un candidato anonimo a una JD.
    body multipart: name, email, pdf_file_upload (file PDF)
    """
    job_description = get_object_or_404(JD, pk=job_description_id)

    form = ResumeForm(request.POST, request.FILES)
    if not form.is_valid():
        return Response({'errors': form.errors}, status=http_status.HTTP_400_BAD_REQUEST)

    resume = form.save(commit=False)
    resume.job_description = job_description
    resume.save()
    job_description.resumes.add(resume)

    return Response(
        {'resume_id': resume.id, 'job_description_id': job_description.id},
        status=http_status.HTTP_201_CREATED,
    )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def mostra_domande_api(request, resume_id, job_description_id):
    """
    GET: restituisce le domande (JD + resume + gap generati dall'IA) per il candidato.
    POST: salva le risposte (stessa convenzione di nomi campo della form Django:
          domanda_job_desc_<n>, domanda_resume_<n>, gap_yesno_<i>, gap_short_<j>, gap_short_skill_<j>).
    """
    resume = get_object_or_404(Resume, pk=resume_id)
    job_description = get_object_or_404(JD, pk=job_description_id)

    domande_job_desc, domande_resume = _get_domande_job_desc_resume(resume, job_description)

    if request.method == 'POST':
        save_domande_risposte(resume, domande_job_desc, domande_resume, request.data)
        return Response({'next': 'personality_test', 'resume_id': resume.id})

    context = build_mostra_domande_context(resume, job_description, domande_job_desc, domande_resume)
    return Response(context)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def personality_test_api(request, resume_id):
    """
    GET: restituisce le domande del test di personalità.
    POST: salva le risposte (body: {"domanda_1": 1..7, "domanda_2": ..., ...}).
    """
    resume = get_object_or_404(Resume, pk=resume_id)

    if request.method == 'GET':
        domande = PersonalityQuestion.objects.all().order_by('id')
        return Response([{'id': d.id, 'testo': d.testo} for d in domande])

    total = PersonalityQuestion.objects.count()
    risposte = {}
    for i in range(1, total + 1):
        campo = f"domanda_{i}"
        if campo in request.data:
            try:
                risposte[str(i)] = int(request.data.get(campo))
            except (TypeError, ValueError):
                continue

    resume.risposte_personalita_raw = risposte
    resume.save()

    return Response({
        'message': 'Grazie per aver completato il test di personalità! '
                    'Le tue risposte sono state salvate in modo sicuro.',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def select_questions_api(request, job_description_id):
    """Restituisce le domande auto-generate (esperienze/competenze/titoli) per una JD."""
    job_description = get_object_or_404(JD, pk=job_description_id)
    return Response(parse_generated_questions(job_description))


@api_view(['POST'])
@permission_classes([AllowAny])
def save_selected_questions_api(request, job_description_id):
    """
    Salva le domande selezionate (+ eventuali nuove aggiunte) per una JD.
    body: { selected_esperienze: [...], selected_competenze: [...], selected_titoli_di_studio: [...] }
    """
    job_description = get_object_or_404(JD, pk=job_description_id)
    payload = request.data or {}

    esperienze = payload.get('selected_esperienze') or []
    competenze = payload.get('selected_competenze') or []
    titoli = payload.get('selected_titoli_di_studio') or []

    job_description.save_selected_questions(esperienze, competenze, titoli)

    next_page = 'dashboard' if getattr(job_description, 'is_public', True) else 'SkillPath'
    return Response({'next': next_page})