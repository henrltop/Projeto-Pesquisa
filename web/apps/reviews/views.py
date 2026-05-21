from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.documents.models import Classification, Document

from .forms import ReviewForm
from .models import Review


def _fila_qs():
    ultima_classe = (
        Classification.objects
        .filter(document=OuterRef("pk"))
        .order_by("-created_at")
        .values("classificacao")[:1]
    )
    tem_review = Review.objects.filter(document=OuterRef("pk"))
    return (
        Document.objects
        .annotate(ultima_classe=Subquery(ultima_classe), tem_review=Exists(tem_review))
        .filter(ultima_classe=Classification.Classificacao.DUVIDOSO, tem_review=False)
        .order_by("ano", "pagina")
    )


@login_required
def review_queue(request):
    qs = _fila_qs().prefetch_related("classificacoes")
    total = qs.count()
    return render(request, "reviews/queue.html", {"fila": qs[:50], "total": total})


@login_required
@require_http_methods(["GET", "POST"])
def review_document(request, document_id: int):
    doc = get_object_or_404(Document, pk=document_id)
    instance = Review.objects.filter(document=doc).first()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=instance)
        if form.is_valid():
            review = form.save(commit=False)
            review.document = doc
            review.revisor = request.user
            review.save()
            messages.success(request, f"Documento marcado como {review.get_decisao_display().lower()}.")
            proximo = _fila_qs().exclude(pk=doc.pk).first()
            if proximo:
                return redirect("reviews:review", document_id=proximo.pk)
            messages.info(request, "Fila de revisao zerada. Bom trabalho!")
            return redirect("reviews:queue")
    else:
        form = ReviewForm(instance=instance)

    return render(
        request,
        "reviews/review.html",
        {
            "doc": doc,
            "form": form,
            "classificacao_atual": doc.classificacao_atual,
            "existente": instance,
        },
    )
