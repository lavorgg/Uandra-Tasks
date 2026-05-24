import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uandra_tasks.settings')
django.setup()

from core.models import Funcionario

# Só cria se ainda não existir — nunca sobrescreve
if not Funcionario.objects.filter(cargo='dono').exists():
    dono = Funcionario(
        nome='Dono',
        codigo='0',
        cargo='dono',
        meta_mensal=200,
    )
    dono.definir_senha('01011980')
    dono.save()
    print('Dono criado com sucesso.')
else:
    print('Dono já existe, nada foi alterado.')