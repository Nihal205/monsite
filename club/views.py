from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cavalier, Participation, Cheval, Cours

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

        # Gestion de l’inscription
        if request.method == "POST" and nb_actuel < 3:
            cours_id = request.POST.get("cours_id")
            cours = Cours.objects.get(id=cours_id)

            # Vérifier qu’il n’est pas déjà inscrit à ce cours
            deja = Participation.objects.filter(cavalier=cavalier, cours=cours).exists()
            if not deja:
                # Choisir automatiquement un cheval dispo
                cheval_dispo = Cheval.objects.filter(disponible=True).first()
                if cheval_dispo:
                    Participation.objects.create(cavalier=cavalier, cours=cours, cheval=cheval_dispo)
                    message = "Inscription réussie ✅"
                else:
                    message = "Aucun cheval disponible 😥"
            else:
                message = "Tu es déjà inscrit à ce cours."

        # Récupérer tous les cours pas encore choisis par ce cavalier
        cours_dispo = Cours.objects.exclude(participations__cavalier=cavalier)

        # Si déjà 3 cours → on bloque
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

            # éviter la double inscription
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

