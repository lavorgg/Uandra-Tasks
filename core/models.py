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
    ('expirada', 'Expirada'),
]

DIAS_SEMANA = [
    (0, 'Segunda-feira'),
    (1, 'Terça-feira'),
    (2, 'Quarta-feira'),
    (3, 'Quinta-feira'),
    (4, 'Sexta-feira'),
    (5, 'Sábado'),
    (6, 'Domingo'),
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
    # Guarda o mês/ano em que os pontos atuais foram contabilizados (ex: "2026-06")
    mes_referencia = models.CharField(max_length=7, blank=True, null=True)

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
    recorrente = models.ForeignKey(
        'TarefaRecorrente', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tarefas_geradas'
    )

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['-criado_em']


class TarefaRecorrente(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    pontos = models.IntegerField(default=10)
    dias_semana = models.CharField(max_length=20)
    horario_limite = models.TimeField()
    criado_por = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL, null=True,
        related_name='tarefas_recorrentes_criadas'
    )
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def get_dias_lista(self):
        return [int(d) for d in self.dias_semana.split(',') if d.strip()]

    def get_dias_nomes(self):
        nomes = dict(DIAS_SEMANA)
        return ', '.join(nomes[d] for d in self.get_dias_lista())

    def __str__(self):
        return f"{self.titulo} ({self.get_dias_nomes()})"

    class Meta:
        verbose_name = 'Tarefa Recorrente'
        verbose_name_plural = 'Tarefas Recorrentes'
        ordering = ['titulo']


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


class AdicaoPontos(models.Model):
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, related_name='adicoes'
    )
    pontos_adicionados = models.IntegerField()
    motivo = models.TextField()
    adicionado_por = models.ForeignKey(
        Funcionario, on_delete=models.SET_NULL, null=True,
        related_name='adicoes_realizadas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Adição de Pontos'
        verbose_name_plural = 'Adições de Pontos'
        ordering = ['-criado_em']


class HistoricoMensal(models.Model):
    """Guarda o resultado final de cada funcionário ao virar o mês."""
    funcionario = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, related_name='historico'
    )
    mes_ano = models.CharField(max_length=7)  # formato "2026-06"
    pontos_finais = models.IntegerField()
    meta = models.IntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico Mensal'
        verbose_name_plural = 'Históricos Mensais'
        ordering = ['-mes_ano']