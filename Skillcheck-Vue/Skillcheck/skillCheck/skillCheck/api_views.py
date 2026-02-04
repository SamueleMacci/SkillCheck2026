from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from urllib.parse import unquote
from collections import Counter
import uuid 
import re
try:
    from skillApp.models import Candidate
except Exception:
    Candidate = None
    
# cache volatile: { candidate_id: {status, status_cv, status_hr, status_tech} }
STATUS_CACHE = {}

@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    return Response({'status': 'ok'})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    raw_username = (request.data.get('username') or '').strip()
    password     = (request.data.get('password') or '')
    email        = (request.data.get('email') or '').strip().lower()
    if not email or not password:
        return Response({'detail': 'username, email e password sono obbligatori'}, status=400)
    if not raw_username:
        base = (email.split('@')[0] or '').lower()
        base = re.sub(r'[^a-z0-9_]', '_', base)[:30]
        if not base:
            base = 'user'
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

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    if email and not username:
        try:
            u = User.objects.get(email__iexact=email)
            username = u.username
        except User.DoesNotExist:
            return Response({'detail': 'credenziali non valide'}, status=400)
    if not username or not password:
        return Response({'detail': 'email/username e password richiesti'}, status=400)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'detail': 'credenziali non valide'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})

JOBS = [
    {"code": "#xx024x", "name": "Programmatore Software",
     "deadline": "2025-12-10",
     "content": "La figura ricercata dovrà occuparsi della progettazione, sviluppo e manutenzione di applicazioni software in linguaggio C."},
    {"code": "#xx025x", "name": "Ingegnere Informatico",
     "deadline": "2025-10-11",
     "content": "Progettazione, sviluppo e manutenzione di applicazioni web."},
    {"code": "#xx026x", "name": "Programmatore Java",
     "deadline": "2025-09-11",
     "content": "Sviluppo applicazioni Java e utilizzo dei principali framework."},
    {"code": "#xx027x", "name": "Software Architect",
     "deadline": "2025-10-01",
     "content": "Architetture cloud, performance e sicurezza."},
]

def normalize_status(value):
    v = str(value or '').strip().lower()
    if v in ('ok', 'idoneo', 'idonei', 'eligible'):
        return 'ok'
    if v in ('pending', 'attesa', 'in attesa'):
        return 'pending'
    if v in ('rejected', 'scartato', 'non idoneo'):
        return 'rejected'
    if v in ('contact', 'contattare', 'da contattare'):
        return 'contact'
    return ''

def compute_counts_for(code: str):
    counts = {"contact": 0, "ok": 0, "pending": 0, "rejected": 0}
    if not Candidate:
        return counts
    code = str(code or "").strip()
    if not code:
        return counts
    try:
        if hasattr(Candidate, "job_code"):
            qs = Candidate.objects.filter(job_code__iexact=code)
        elif hasattr(Candidate, "code"):
            qs = Candidate.objects.filter(code__iexact=code)
        else:
            return counts
    except Exception as e:
        return counts
    for c in qs:
        ov = STATUS_CACHE.get(c.id, {})
        overall = normalize_status(ov.get("status"))
        if not overall:
            phases = [
                normalize_status(ov.get("status_cv")),
                normalize_status(ov.get("status_hr")),
                normalize_status(ov.get("status_tech")),
            ]
            phases = [p for p in phases if p]
            if phases:
                overall = Counter(phases).most_common(1)[0][0]
        if not overall:
            overall = normalize_status(getattr(c, "status", ""))
        if overall:
            counts[overall] += 1
    return counts

@api_view(['GET'])
@permission_classes([AllowAny])
def candidates(request):
    job = (request.query_params.get('job') or '').strip()
    job = unquote(job)
    qs = Candidate.objects.all()
    if job:
        qs = qs.filter(job_code__iexact=job)
    def serialize(c):
        base = {
            'id': c.id,
            'first_name': getattr(c, 'first_name', ''),
            'last_name': getattr(c, 'last_name', ''),
            'email': getattr(c, 'email', ''),
            'phone': getattr(c, 'phone', ''),
            'status': getattr(c, 'status', ''),
            'job': getattr(c, 'job_code', ''),
        }
        ov = STATUS_CACHE.get(c.id, {})
        if 'status' in ov:
            base['status'] = ov['status']
        base.update({
            'status_cv': ov.get('status_cv', base['status']),
            'status_hr': ov.get('status_hr', base['status']),
            'status_tech': ov.get('status_tech', base['status']),
        })
        return base

    data = [serialize(c) for c in qs[:500]]
    return Response(data)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def jobs(request):
    if request.method == 'GET':
        out = []
        for it in JOBS:
            out.append({**it, "counts": compute_counts_for(it["code"])})
        return Response(out)
    data = request.data or {}
    name = (data.get("name") or data.get("title") or "").strip() or "Annuncio"
    content = (data.get("content") or data.get("description") or "").strip()
    deadline = (data.get("deadline") or data.get("scadenza") or "").strip()
    code = (data.get("code") or f"#{uuid.uuid4().hex[:6]}").strip()
    if any(j["code"].lower() == code.lower() for j in JOBS):
        return Response({"detail": "code già esistente"}, status=status.HTTP_400_BAD_REQUEST)
    job = {"code": code, "name": name, "deadline": deadline, "content": content}
    JOBS.append(job)
    return Response(job, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def job_detail(request, code):
    code = unquote(code)
    job = next((j for j in JOBS if j["code"].lower() == code.lower()), None)
    if not job:
        return Response({"detail": "Not found"}, status=404)
    return Response({**job, "counts": compute_counts_for(job["code"])})

@api_view(['PATCH'])
@permission_classes([AllowAny])
def candidate_update(request, pk: int):
    if Candidate is None:
        return Response({'detail': 'Candidate model not available'}, status=501)
    try:
        c = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    payload = request.data or {}
    changed = False
    def set_if_exists(obj, field, value):
        nonlocal changed
        if hasattr(obj, field) and value is not None:
            setattr(obj, field, value)
            changed = True
    set_if_exists(c, 'status', payload.get('status'))
    set_if_exists(c, 'comment', payload.get('comment'))
    set_if_exists(c, 'phone', payload.get('phone'))
    set_if_exists(c, 'email', payload.get('email'))
    if changed:
        c.save()
    cur = STATUS_CACHE.get(c.id, {})
    if 'status' in payload and payload['status'] is not None:
        cur['status'] = str(payload['status']).lower()
    STATUS_CACHE[c.id] = cur
    return Response({'ok': True, 'id': c.id, **cur})

@api_view(['PATCH'])
@permission_classes([AllowAny])
def candidate_partial_update(request, pk):
    current = STATUS_CACHE.get(pk, {}).copy()
    changed = False
    for key in ('status', 'status_cv', 'status_hr', 'status_tech'):
        if key in request.data:
            current[key] = str(request.data[key]).lower()
            changed = True
    overall = (
        normalize_status(current.get('status')) or
        normalize_status(current.get('status_tech')) or
        normalize_status(current.get('status_hr')) or
        normalize_status(current.get('status_cv'))
    )
    if overall:
        current['status'] = overall
    STATUS_CACHE[pk] = current
    return Response({'id': pk, **current})
