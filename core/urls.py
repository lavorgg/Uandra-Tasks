from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),

    # Perfil (todos os cargos)
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/salvar/', views.salvar_perfil, name='salvar_perfil'),

    # Funcionário
    path('tarefas/', views.tarefas_view, name='tarefas'),
    path('tarefas/<int:tarefa_id>/aceitar/', views.aceitar_tarefa, name='aceitar_tarefa'),
    path('pendentes/', views.pendentes_view, name='pendentes'),
    path('pendentes/<int:tarefa_id>/solicitar/', views.solicitar_finalizacao, name='solicitar_finalizacao'),
    path('relatorio/', views.relatorio_view, name='relatorio'),

    # Gerente
    path('gerente/tarefas/', views.gerente_tarefas_view, name='gerente_tarefas'),
    path('gerente/tarefas/criar/', views.criar_tarefa, name='criar_tarefa'),
    path('gerente/tarefas/<int:tarefa_id>/excluir/', views.excluir_tarefa, name='excluir_tarefa'),
    path('gerente/pendentes/', views.gerente_pendentes_view, name='gerente_pendentes'),
    path('gerente/pendentes/<int:tarefa_id>/finalizar/', views.finalizar_tarefa, name='finalizar_tarefa'),
    path('gerente/funcionarios/', views.gerente_funcionarios_view, name='gerente_funcionarios'),
    path('gerente/funcionarios/adicionar/', views.adicionar_funcionario, name='adicionar_funcionario'),
    path('gerente/funcionarios/<int:func_id>/editar/', views.editar_funcionario, name='editar_funcionario'),
    path('gerente/funcionarios/<int:func_id>/remover/', views.remover_funcionario, name='remover_funcionario'),
    path('gerente/relatorio/', views.gerente_relatorio_view, name='gerente_relatorio'),
    path('gerente/relatorio/remover-pontos/', views.remover_pontos, name='remover_pontos'),
]
