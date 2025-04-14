from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cours, Cheval, Cavalier, Participation
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count


@login_required
def inscription_cavalier(request):
    cavalier = Cavalier.objects.get(email=request.user.email)

    # 📅 Cours non pleins
    cours_disponibles = Cours.objects.annotate(nb=Count('participations')).filter(nb__lt=5)

    # 🐴 Chevaux disponibles (pas plus de 2 montées aujourd'hui)
    today = now().strftime('%A').lower()
    chevaux_disponibles = Cheval.objects.filter(
        disponible=True
    ).annotate(nb=Count('participation')).filter(nb__lt=2)

    if request.method == "POST":
        cours_id = request.POST.get("cours_id")
        cheval_id = request.POST.get("cheval_id")

        cours = Cours.objects.get(id=cours_id)
        cheval = Cheval.objects.get(id=cheval_id)

        # ⚠️Vérif 1 : limite 4 cours par semaine
        semaine = now().date() - timedelta(days=7)
        total = Participation.objects.filter(cavalier=cavalier, cours__jour__gte=semaine).count()
        if total >= 4:
            messages.error(request, "❌ Tu as atteint la limite de 4 cours par semaine.")
            return redirect("inscription_cavalier")

        # Vérif 2 : cours complet
        if cours.participations.count() >= 5:
            messages.error(request, "❌ Ce cours est déjà complet.")
            return redirect("inscription_cavalier")

        #  Vérif 3 : cheval monté plus de 2 fois aujourd’hui ?
        today_count = Participation.objects.filter(cheval=cheval, cours__jour=cours.jour).count()
        if today_count >= 2:
            messages.error(request, f"❌ {cheval.nom} est déjà monté 2 fois aujourd’hui.")
            return redirect("inscription_cavalier")

        # Sinon, on crée la participation
        Participation.objects.create(cavalier=cavalier, cheval=cheval, cours=cours)
        messages.success(request, f"✅ Tu es inscrit à {cours} avec {cheval.nom} !")
        return redirect("inscription_cavalier")

    return render(request, "club/inscription_cavalier.html", {
        "cours_disponibles": cours_disponibles,
        "chevaux_disponibles": chevaux_disponibles,
    })

