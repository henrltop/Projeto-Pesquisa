from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, CharField, F, OuterRef, Q, Subquery, Value, When
from django.shortcuts import get_object_or_404, render

from apps.reviews.models import Review

from .models import Classification, Document


@login_required
def document_list(request):
    ultima_classe = (
        Classification.objects
        .filter(document=OuterRef("pk"))
        .order_by("-created_at")
        .values("classificacao")[:1]
    )
    ultima_review = (
        Review.objects
        .filter(document=OuterRef("pk"))
        .order_by("-created_at")
        .values("decisao")[:1]
    )
    qs = Document.objects.all().annotate(
        ultima_classe=Subquery(ultima_classe),
        ultima_review=Subquery(ultima_review),
    ).annotate(
        estado_efetivo=Case(
            When(ultima_review="super_relevante", then=Value("super_relevante")),
            When(ultima_review="aprovado", then=Value("relevante")),
            When(ultima_review="ressalva", then=Value("relevante")),
            When(ultima_review="rejeitado", then=Value("irrelevante")),
            default=F("ultima_classe"),
            output_field=CharField(),
        ),
    )

    ano = request.GET.get("ano", "").strip()
    termo = request.GET.get("q", "").strip()
    classe = request.GET.get("classe", "").strip()

    if ano.isdigit():
        qs = qs.filter(ano=int(ano))
    if termo:
        qs = qs.filter(
            Q(texto_bruto__icontains=termo)
            | Q(classificacoes__termo_buscado__icontains=termo)
        ).distinct()
    if classe in dict(Classification.Classificacao.choices):
        qs = qs.filter(estado_efetivo=classe)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page", 1))

    return render(
        request,
        "documents/list.html",
        {
            "page": page,
            "filtros": {"ano": ano, "q": termo, "classe": classe},
            "classes": Classification.Classificacao.choices,
        },
    )


@login_required
def document_detail(request, pk: int):
    doc = get_object_or_404(Document, pk=pk)
    return render(
        request,
        "documents/detail.html",
        {
            "doc": doc,
            "classificacoes": doc.classificacoes.all().order_by("-created_at"),
            "reviews": doc.reviews.all().order_by("-created_at"),
        },
    )
