"""Popula dados falsos para demonstracao visual sem rodar pipeline real.

Uso:
    python manage.py seed_demo --limpar
"""
from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.documents.models import Classification, Document
from apps.reviews.models import Review
from apps.searches.models import SearchJob

User = get_user_model()

TERMOS_DEMO = [
    "ensino superior tecnologico",
    "UNEMAT",
    "curso de tecnologia",
    "conselho estadual de educacao",
    "escola tecnica federal",
    "SEDUC convenio",
]
TIPOS_RELEVANTES = ["Lei", "Decreto", "Portaria", "Resolucao", "Convenio"]
TIPOS_IRRELEVANTES = ["Licitacao", "Nomeacao", "Mencao Casual", "Pregao"]

JUSTIFICATIVAS_RELEVANTE = [
    "Autoriza a criacao de curso superior de tecnologia junto a UNEMAT.",
    "Regulamenta convenio entre o Estado e o MEC para educacao profissional.",
    "Reconhece curso tecnologico ofertado pela Escola Tecnica Federal.",
    "Dispoe sobre estrutura do Conselho Estadual de Educacao (CEE/MT).",
]
JUSTIFICATIVAS_DUVIDOSO = [
    "Mencao a curso tecnico sem ato legal explicito no excerto.",
    "Portaria trata de educacao mas o escopo esta ambiguo.",
    "Convenio citado sem detalhamento do objeto - merece revisao humana.",
]
JUSTIFICATIVAS_IRRELEVANTE = [
    "Aviso de licitacao sem relacao com ensino superior.",
    "Nomeacao de servidor comum - sem peso legal educacional.",
    "Mencao casual sem ato legal associado.",
]


class Command(BaseCommand):
    help = "Popula dados de demonstracao (usuarios, buscas, documentos, classificacoes, revisoes)."

    def add_arguments(self, parser):
        parser.add_argument("--limpar", action="store_true", help="Apaga os dados demo existentes antes.")
        parser.add_argument("--docs", type=int, default=60, help="Quantidade de documentos a gerar.")

    def handle(self, *args, **opts):
        if opts["limpar"]:
            self.stdout.write("Limpando dados antigos...")
            Review.objects.all().delete()
            Classification.objects.all().delete()
            Document.objects.all().delete()
            SearchJob.objects.all().delete()

        equipe = [
            self._ensure_user("henrique", "Henrique", "henrique@example.com", "demo12345"),
            self._ensure_user("beatriz", "Beatriz", "beatriz@example.com", "demo12345"),
        ]

        # cria 3 buscas historicas
        buscas = []
        for i, termo in enumerate(TERMOS_DEMO[:3]):
            criador = random.choice(equipe)
            job = SearchJob.objects.create(
                criado_por=criador,
                termo=termo,
                busca_exata=True,
                ano_inicio=2000 + i * 2,
                ano_fim=2005 + i * 2,
                status=SearchJob.Status.CONCLUIDO,
                started_at=timezone.now() - timedelta(hours=i + 1),
                finished_at=timezone.now() - timedelta(hours=i, minutes=30),
            )
            buscas.append(job)

        total_docs = opts["docs"]
        self.stdout.write(f"Gerando {total_docs} documentos...")
        relevantes = duvidosos = descartados = 0

        for idx in range(total_docs):
            ano = random.randint(2000, 2008)
            edicao_id = str(10000 + idx)
            doc = Document.objects.create(
                edicao_id=edicao_id,
                pagina=random.randint(1, 30),
                ano=ano,
                tipo_edicao=1,
                nome_edicao=f"Edicao {edicao_id}",
                data_pub=f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{ano}",
                link_oficial=f"https://iomat.mt.gov.br/portal/visualizacoes/pdf/{edicao_id}",
                texto_bruto=(
                    f"Excerto fictício do Diario Oficial de Mato Grosso. Ano {ano}. "
                    f"Lorem ipsum dolor sit amet, ensino superior tecnologico, convenio educacional, "
                    f"portaria conjunta MEC/SEDUC, UNEMAT. Texto gerado automaticamente para demonstracao."
                ),
            )

            # distribuicao: ~40% relevante, ~25% duvidoso, ~35% irrelevante
            rnd = random.random()
            if rnd < 0.40:
                classif = Classification.Classificacao.RELEVANTE
                tipo = random.choice(TIPOS_RELEVANTES)
                just = random.choice(JUSTIFICATIVAS_RELEVANTE)
                relevantes += 1
            elif rnd < 0.65:
                classif = Classification.Classificacao.DUVIDOSO
                tipo = random.choice(TIPOS_RELEVANTES + ["Ato"])
                just = random.choice(JUSTIFICATIVAS_DUVIDOSO)
                duvidosos += 1
            else:
                classif = Classification.Classificacao.IRRELEVANTE
                tipo = random.choice(TIPOS_IRRELEVANTES)
                just = random.choice(JUSTIFICATIVAS_IRRELEVANTE)
                descartados += 1

            job = random.choice(buscas)
            Classification.objects.create(
                document=doc, search_job=job, termo_buscado=job.termo,
                classificacao=classif, tipo_ato=tipo, justificativa=just,
                prompt_enviado="(demo)", resposta_crua="{}", modelo_ia="gpt-4o-mini",
                tokens_input=random.randint(300, 1500),
                tokens_output=random.randint(40, 120),
            )

            # revisa ~metade dos duvidosos
            if classif == Classification.Classificacao.DUVIDOSO and random.random() < 0.5:
                Review.objects.create(
                    document=doc,
                    revisor=random.choice(equipe),
                    decisao=random.choice([Review.Decisao.APROVADO, Review.Decisao.REJEITADO]),
                    comentario="Revisao de demonstracao.",
                )

        # atualiza contadores dos jobs
        for job in buscas:
            qs = Classification.objects.filter(search_job=job)
            job.total_extraidos = qs.values("document").distinct().count()
            job.total_relevantes = qs.filter(classificacao="relevante").count()
            job.total_duvidosos = qs.filter(classificacao="duvidoso").count()
            job.total_descartados = qs.filter(classificacao="irrelevante").count()
            job.save()

        self.stdout.write(self.style.SUCCESS(
            f"OK. Docs: {total_docs} ({relevantes} relevantes, {duvidosos} duvidosos, {descartados} descartados)."
        ))
        self.stdout.write("Usuarios demo (senha: demo12345): henrique, beatriz")

    def _ensure_user(self, username, first_name, email, password):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"first_name": first_name, "email": email, "is_staff": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"  usuario criado: {username}")
        return user
