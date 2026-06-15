from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, CharField, F, OuterRef, Q, Subquery, Value, When
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.reviews.models import Review
from apps.searches.models import SearchJob

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
    busca = request.GET.get("busca", "").strip()

    if ano.isdigit():
        qs = qs.filter(ano=int(ano))
    if termo:
        qs = qs.filter(
            Q(texto_bruto__icontains=termo)
            | Q(classificacoes__termo_buscado__icontains=termo)
        ).distinct()
    if classe in dict(Classification.Classificacao.choices):
        qs = qs.filter(estado_efetivo=classe)

    busca_obj = None
    if busca.isdigit():
        busca_obj = SearchJob.objects.filter(pk=int(busca)).first()
        # documentos que tiveram alguma classificacao vinculada a essa busca
        qs = qs.filter(classificacoes__search_job_id=int(busca)).distinct()

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page", 1))

    # lista de buscas para o seletor (so as que tem documentos classificados)
    buscas = (
        SearchJob.objects
        .filter(classificacoes__isnull=False)
        .distinct()
        .order_by("-created_at")
        .values("id", "termo", "ano_inicio", "ano_fim")
    )

    return render(
        request,
        "documents/list.html",
        {
            "page": page,
            "filtros": {"ano": ano, "q": termo, "classe": classe, "busca": busca},
            "classes": Classification.Classificacao.choices,
            "buscas": buscas,
            "busca_obj": busca_obj,
        },
    )


def _paginas_contexto(doc, classificacoes) -> list[int]:
    """Reune todas as paginas de contexto registradas nas classificacoes do doc.

    Retorna a lista de paginas VIZINHAS (exclui a propria pagina-alvo), ordenada.
    """
    paginas: set[int] = set()
    for c in classificacoes:
        if not c.paginas_contexto:
            continue
        for parte in c.paginas_contexto.split(","):
            parte = parte.strip()
            if parte.isdigit():
                paginas.add(int(parte))
    paginas.discard(doc.pagina)
    return sorted(paginas)


def _paginas_do_ato(doc, classificacoes) -> list[int]:
    """Paginas que formam o ato (alvo + contexto da classificacao mais recente)."""
    for c in classificacoes:  # ja ordenadas por -created_at
        if c.paginas_contexto:
            ps = [int(x) for x in c.paginas_contexto.split(",") if x.strip().isdigit()]
            if ps:
                return sorted(set(ps) | {doc.pagina})
    return [doc.pagina]


def _texto_completo(doc, classificacoes) -> str:
    """Concatena o texto OCR de TODAS as paginas do ato num texto unico continuo."""
    from apps.core.pdf_text import texto_da_pagina

    paginas = _paginas_do_ato(doc, classificacoes)
    partes: list[str] = []
    for p in paginas:
        if p == doc.pagina:
            txt = doc.texto_bruto or ""
        else:
            txt = texto_da_pagina(doc.tipo_edicao, doc.edicao_id, p) or ""
        txt = txt.strip()
        if not txt:
            continue
        if len(paginas) > 1:
            partes.append(f"────────── página {p} ──────────\n{txt}")
        else:
            partes.append(txt)
    return "\n\n".join(partes)


@login_required
def document_detail(request, pk: int):
    doc = get_object_or_404(Document, pk=pk)
    classificacoes = list(doc.classificacoes.all().order_by("-created_at"))
    paginas_ctx = _paginas_contexto(doc, classificacoes)

    # termo buscado para o "marcar palavra" (da classificacao mais recente que tiver)
    termo_buscado = ""
    for c in classificacoes:
        if c.termo_buscado:
            termo_buscado = c.termo_buscado
            break

    return render(
        request,
        "documents/detail.html",
        {
            "doc": doc,
            "classificacoes": classificacoes,
            "reviews": doc.reviews.all().order_by("-created_at"),
            "paginas_contexto": paginas_ctx,
            "paginas_ato": _paginas_do_ato(doc, classificacoes),
            "texto_completo": _texto_completo(doc, classificacoes),
            "termo_buscado": termo_buscado,
        },
    )


@login_required
def document_contexto_pdf(request, pk: int, pagina: int):
    """Baixa sob demanda o PDF de uma pagina de contexto (vizinha) e o serve.

    Salva em media/pdfs com o mesmo padrao de nome para reuso; se ja existir,
    apenas redireciona. Retorna JSON com a URL do PDF (consumido via fetch no front).
    """
    from pathlib import Path

    from django.conf import settings

    from apps.core.iomat_client import baixar_pdf

    doc = get_object_or_404(Document, pk=pk)
    if pagina < 1:
        raise Http404("pagina invalida")

    nome = f"DOE_MT_{doc.ano}_Edicao_{doc.edicao_id}_Pagina_{pagina}.pdf"
    pdf_dir = Path(settings.MEDIA_ROOT) / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    destino = pdf_dir / nome
    rel = f"pdfs/{nome}"

    if not destino.exists():
        try:
            baixar_pdf(doc.tipo_edicao, doc.edicao_id, pagina, str(destino))
        except Exception:  # noqa: BLE001
            return JsonResponse({"ok": False, "erro": "falha ao baixar"}, status=502)

    if not destino.exists():
        return JsonResponse({"ok": False, "erro": "pagina nao encontrada"}, status=404)

    # Retencao para auditoria: renova o mtime a cada visualizacao, reiniciando a
    # janela de "pelo menos 2 dias". A limpeza (limpar_pdfs_antigos) so remove
    # PDFs nao-corpus que ficaram 2+ dias sem serem abertos.
    import os
    try:
        os.utime(destino, None)
    except OSError:
        pass

    return JsonResponse({"ok": True, "url": f"/media/{rel}", "pagina": pagina})
