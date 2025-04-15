from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cavalier, Participation, Cheval, Cours
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count


def accueil(request):
    return render(request, 'accueil.html')


@login_required
def dashboard(request):
    user = request.user
    try:
        cavalier = Cavalier.objects.get(user=user)
        participations = Participation.objects.filter(cavalier=cavalier)
    except Cavalier.DoesNotExist:
        cavalier = None
        participations = None

    return render(request, 'dashboard.html', {
        'cavalier': cavalier,
        'participations': participations,
    })


@login_required
def statut(request):
    try:
        cavalier = Cavalier.objects.get(user=request.user)
        participations = Participation.objects.filter(cavalier=cavalier)
    except Cavalier.DoesNotExist:
        participations = []

    return render(request, 'statut.html', {
        'participations': participations
    })


@login_required
def inscription(request):
    message = ""
    try:
        cavalier = Cavalier.objects.get(user=request.user)
        participations = Participation.objects.filter(cavalier=cavalier)
        nb_actuel = participations.count()

        if request.method == "POST" and nb_actuel < 3:
            cours_id = request.POST.get("cours_id")
            cours = Cours.objects.get(id=cours_id)
            deja = Participation.objects.filter(cavalier=cavalier, cours=cours).exists()
            if not deja:
                cheval_dispo = Cheval.objects.filter(disponible=True).first()
                if cheval_dispo:
                    Participation.objects.create(cavalier=cavalier, cours=cours, cheval=cheval_dispo)
                    message = "Inscription réussie ✅"
                else:
                    message = "Aucun cheval disponible 😥"
            else:
                message = "Tu es déjà inscrit à ce cours."
        cours_dispo = Cours.objects.exclude(participations__cavalier=cavalier)
        if nb_actuel >= 3:
            cours_dispo = []

    except Cavalier.DoesNotExist:
        cours_dispo = []
        message = "Cavalier introuvable"

    return render(request, "inscription.html", {
        "cours_dispo": cours_dispo,
        "message": message
    })


@login_required
def concours(request):
    message = ""
    try:
        cavalier = Cavalier.objects.get(user=request.user)
        concours = Cours.objects.filter(niveau__iexact="concours")
        if request.method == "POST":
            cours_id = request.POST.get("cours_id")
            cours = Cours.objects.get(id=cours_id)
            deja = Participation.objects.filter(cavalier=cavalier, cours=cours).exists()
            if not deja:
                cheval_dispo = Cheval.objects.filter(disponible=True).first()
                if cheval_dispo:
                    try:
                        Participation.objects.create(cavalier=cavalier, cours=cours, cheval=cheval_dispo)
                        message = "Inscription au concours réussie ✅"
                    except Exception as e:
                        message = f"Erreur : {e}"
                else:
                    message = "Aucun cheval disponible pour ce concours 😥"
            else:
                message = "Tu es déjà inscrit à ce concours."
    except Cavalier.DoesNotExist:
        concours = []
        message = "Cavalier non trouvé."

    return render(request, "concours.html", {
        "concours": concours,
        "message": message
    })


@login_required
def chevaux(request):
    chevaux = Cheval.objects.all()
    return render(request, "chevaux.html", {
        "chevaux": chevaux
    })


@login_required
def inscription_cavalier(request):
    cavalier = Cavalier.objects.get(email=request.user.email)
    cours_disponibles = Cours.objects.annotate(nb=Count('participations')).filter(nb__lt=5)
    today = now().strftime('%A').lower()
    chevaux_disponibles = Cheval.objects.filter(
        disponible=True
    ).annotate(nb=Count('participation')).filter(nb__lt=2)

    if request.method == "POST":
        cours_id = request.POST.get("cours_id")
        cheval_id = request.POST.get("cheval_id")

        cours = Cours.objects.get(id=cours_id)
        cheval = Cheval.objects.get(id=cheval_id)
        semaine = now().date() - timedelta(days=7)
        total = Participation.objects.filter(cavalier=cavalier, cours__jour__gte=semaine).count()

        if total >= 4:
            messages.error(request, "❌ Tu as atteint la limite de 4 cours par semaine.")
            return redirect("inscription_cavalier")

        if cours.participations.count() >= 5:
            messages.error(request, "❌ Ce cours est déjà complet.")
            return redirect("inscription_cavalier")

        today_count = Participation.objects.filter(cheval=cheval, cours__jour=cours.jour).count()
        if today_count >= 2:
            messages.error(request, f"❌ {cheval.nom} est déjà monté 2 fois aujourd’hui.")
            return redirect("inscription_cavalier")

        Participation.objects.create(cavalier=cavalier, cheval=cheval, cours=cours)
        messages.success(request, f"✅ Tu es inscrit à {cours} avec {cheval.nom} !")
        return redirect("inscription_cavalier")

    return render(request, "club/inscription_cavalier.html", {
        "cours_disponibles": cours_disponibles,
        "chevaux_disponibles": chevaux_disponibles
    })
