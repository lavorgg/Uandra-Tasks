import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uandra_tasks.settings')
django.setup()

from django.utils.timezone import localtime, now
from core.models import TarefaRecorrente, Tarefa
import datetime

agora_local = localtime(now())
hoje = agora_local.date()
dia_semana = hoje.weekday()

criadas = 0
for recorrente in TarefaRecorrente.objects.filter(ativa=True):
    if dia_semana not in recorrente.get_dias_lista():
        continue

    ja_existe = Tarefa.objects.filter(
        recorrente=recorrente,
        criado_em__date=hoje
    ).exists()

    if ja_existe:
        continue

    from django.utils import timezone
    prazo_naive = datetime.datetime.combine(hoje, recorrente.horario_limite)
    prazo = timezone.make_aware(prazo_naive)

    if prazo > now():
        Tarefa.objects.create(
            titulo=recorrente.titulo,
            descricao=recorrente.descricao,
            pontos=recorrente.pontos,
            prazo=prazo,
            criado_por=recorrente.criado_por,
            recorrente=recorrente,
            status='disponivel',
        )
        criadas += 1

print(f'{criadas} tarefa(s) recorrente(s) criada(s) para {hoje}')