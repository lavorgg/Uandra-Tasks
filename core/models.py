from django.db import models
from django.contrib.auth.hashers import make_password, check_password


CARGO_CHOICES = [
    ('dono', 'Dono'),
    ('gerente', 'Gerente'),
    ('funcionario', 'Funcionário'),
]

STATUS_TAREFA = [
    ('disponivel', 'Disponível'),
    ('aceita', 'Aceita'),
    ('pendente_finalizacao', 'Aguardando Aprovação'),
    ('finalizada', 'Finalizada'),
]


class Funcionario(models.Model):
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=20, unique=True)
    senha_hash = models.CharField(max_length=256)
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES, default='funcionario')
    pontos = models.IntegerField(default=0)
    meta_mensal = models.IntegerField(default=100)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def definir_senha(self, senha):
        self.senha_hash = make_password(senha)

    def verificar_senha(self, senha):
        return check_password(senha, self.senha_hash)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']


class Tarefa(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    pontos = models.IntegerField(default=10)
    prazo = models.DateTimeField()
    criado_por = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL, null=True,
        related_name='tarefas_criadas'
    )
    aceita_por = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tarefas_aceitas'
    )
    status = models.CharField(max_length=30, choices=STATUS_TAREFA, default='disponivel')
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['-criado_em']


class RemocaoPontos(models.Model):
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, related_name='remocoes'
    )
    pontos_removidos = models.IntegerField()
    motivo = models.TextField()
    removido_por = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL, null=True,
        related_name='remocoes_realizadas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Remoção de Pontos'
        verbose_name_plural = 'Remoções de Pontos'
        ordering = ['-criado_em']
