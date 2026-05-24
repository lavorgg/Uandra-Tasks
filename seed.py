import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uandra_tasks.settings')
django.setup()

from core.models import Funcionario, Tarefa
from django.utils import timezone
import datetime

print('Populando banco de dados...')

Funcionario.objects.all().delete()
Tarefa.objects.all().delete()

dono = Funcionario(nome='Carlos Dono', codigo='0', cargo='dono', meta_mensal=200)
dono.definir_senha('01011980')
dono.save()

gerente = Funcionario(nome='Ana Gerente', codigo='1', cargo='gerente', meta_mensal=150)
gerente.definir_senha('15031985')
gerente.save()

f1 = Funcionario(nome='João Silva', codigo='2', cargo='funcionario', meta_mensal=100)
f1.definir_senha('20051995')
f1.save()

f2 = Funcionario(nome='Maria Souza', codigo='3', cargo='funcionario', meta_mensal=100)
f2.definir_senha('10101992')
f2.save()

prazo1 = timezone.now() + datetime.timedelta(days=2)
prazo2 = timezone.now() + datetime.timedelta(days=1)
prazo3 = timezone.now() + datetime.timedelta(hours=5)

Tarefa.objects.create(
    titulo='Organizar o estoque',
    descricao='Verificar e reorganizar os produtos do estoque, registrar itens com baixo estoque e separar itens danificados.',
    pontos=20, prazo=prazo1, criado_por=gerente
)
Tarefa.objects.create(
    titulo='Atendimento ao cliente VIP',
    descricao='Realizar o atendimento personalizado para clientes VIP agendados para esta semana e registrar feedback.',
    pontos=30, prazo=prazo2, criado_por=gerente
)
Tarefa.objects.create(
    titulo='Relatório diário de vendas',
    descricao='Compilar os dados de vendas do dia e enviar para a gerência até o final do expediente.',
    pontos=15, prazo=prazo3, criado_por=gerente
)

print('Banco populado com sucesso!')
print('Dono:     código=0 / senha=01011980')
print('Gerente:  código=1 / senha=15031985')
print('Func 1:   código=2 / senha=20051995')
print('Func 2:   código=3 / senha=10101992')
