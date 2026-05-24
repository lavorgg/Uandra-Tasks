import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Funcionario, Tarefa, RemocaoPontos


# ─── Sessão ───────────────────────────────────────────────────────────────────

def login_view(request):
    if request.session.get('funcionario_id'):
        return _redirecionar_por_cargo(request)
    erro = None
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        senha = request.POST.get('senha', '').strip()
        try:
            funcionario = Funcionario.objects.get(codigo=codigo, ativo=True)
            if funcionario.verificar_senha(senha):
                request.session['funcionario_id'] = funcionario.id
                request.session['cargo'] = funcionario.cargo
                return _redirecionar_por_cargo(request)
            else:
                erro = 'Código ou senha inválidos.'
        except Funcionario.DoesNotExist:
            erro = 'Código ou senha inválidos.'
    return render(request, 'login.html', {'erro': erro})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def _redirecionar_por_cargo(request):
    cargo = request.session.get('cargo')
    if cargo in ('dono', 'gerente'):
        return redirect('gerente_tarefas')
    return redirect('tarefas')


def _funcionario_logado(request):
    fid = request.session.get('funcionario_id')
    if not fid:
        return None
    try:
        return Funcionario.objects.get(id=fid, ativo=True)
    except Funcionario.DoesNotExist:
        return None


def _requer_login(request):
    f = _funcionario_logado(request)
    if not f:
        return None, redirect('login')
    return f, None


def _requer_gerente(request):
    f, r = _requer_login(request)
    if not f:
        return None, r
    if f.cargo not in ('dono', 'gerente'):
        return None, redirect('tarefas')
    return f, None


def _pode_gerenciar(gerente, alvo):
    """Verifica se um gerente pode gerenciar determinado funcionário.
    Gerentes não podem tocar em donos nem em outros gerentes acima deles."""
    if gerente.cargo == 'dono':
        return True
    # Gerente só pode gerenciar funcionários comuns
    if alvo.cargo in ('dono', 'gerente'):
        return False
    return True


# ─── Funcionário ──────────────────────────────────────────────────────────────

def tarefas_view(request):
    f, r = _requer_login(request)
    if not f:
        return r
    if f.cargo in ('dono', 'gerente'):
        return redirect('gerente_tarefas')
    tarefas = Tarefa.objects.filter(status='disponivel').select_related('criado_por')
    return render(request, 'tarefas.html', {'funcionario': f, 'tarefas': tarefas})


@require_POST
def aceitar_tarefa(request, tarefa_id):
    f, r = _requer_login(request)
    if not f:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, status='disponivel')
    tarefa.aceita_por = f
    tarefa.status = 'aceita'
    tarefa.save()
    return JsonResponse({'ok': True})


def pendentes_view(request):
    f, r = _requer_login(request)
    if not f:
        return r
    if f.cargo in ('dono', 'gerente'):
        return redirect('gerente_pendentes')
    tarefas = Tarefa.objects.filter(aceita_por=f, status__in=['aceita', 'pendente_finalizacao'])
    return render(request, 'pendentes.html', {'funcionario': f, 'tarefas': tarefas})


@require_POST
def solicitar_finalizacao(request, tarefa_id):
    f, r = _requer_login(request)
    if not f:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, aceita_por=f, status='aceita')
    tarefa.status = 'pendente_finalizacao'
    tarefa.save()
    return JsonResponse({'ok': True})


def relatorio_view(request):
    f, r = _requer_login(request)
    if not f:
        return r
    if f.cargo in ('dono', 'gerente'):
        return redirect('gerente_relatorio')
    hoje = timezone.now()
    tarefas_mes = Tarefa.objects.filter(
        aceita_por=f, status='finalizada',
        finalizado_em__year=hoje.year, finalizado_em__month=hoje.month
    )
    pontos_removidos = RemocaoPontos.objects.filter(funcionario=f)
    total_removido = sum(r.pontos_removidos for r in pontos_removidos)
    return render(request, 'relatorio.html', {
        'funcionario': f,
        'tarefas_mes': tarefas_mes,
        'total_removido': total_removido,
        'remocoes': pontos_removidos,
    })


# ─── Gerente ──────────────────────────────────────────────────────────────────

def gerente_tarefas_view(request):
    g, r = _requer_gerente(request)
    if not g:
        return r
    tarefas = Tarefa.objects.filter(status='disponivel').select_related('criado_por')
    return render(request, 'gerente/tarefas.html', {'funcionario': g, 'tarefas': tarefas})


@require_POST
def criar_tarefa(request):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    dados = json.loads(request.body)
    tarefa = Tarefa.objects.create(
        titulo=dados['titulo'],
        descricao=dados['descricao'],
        pontos=int(dados['pontos']),
        prazo=dados['prazo'],
        criado_por=g,
        status='disponivel',
    )
    return JsonResponse({'ok': True, 'id': tarefa.id})


@require_POST
def excluir_tarefa(request, tarefa_id):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    tarefa = get_object_or_404(Tarefa, id=tarefa_id)
    tarefa.delete()
    return JsonResponse({'ok': True})


def gerente_pendentes_view(request):
    g, r = _requer_gerente(request)
    if not g:
        return r
    tarefas = Tarefa.objects.filter(status='pendente_finalizacao').select_related('aceita_por', 'criado_por')
    return render(request, 'gerente/pendentes.html', {'funcionario': g, 'tarefas': tarefas})


@require_POST
def finalizar_tarefa(request, tarefa_id):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    tarefa = get_object_or_404(Tarefa, id=tarefa_id, status='pendente_finalizacao')
    tarefa.status = 'finalizada'
    tarefa.finalizado_em = timezone.now()
    tarefa.save()
    if tarefa.aceita_por:
        tarefa.aceita_por.pontos += tarefa.pontos
        tarefa.aceita_por.save()
    return JsonResponse({'ok': True})


def gerente_funcionarios_view(request):
    g, r = _requer_gerente(request)
    if not g:
        return r
    # Dono vê todos; gerente vê apenas funcionários comuns
    if g.cargo == 'dono':
        funcionarios = Funcionario.objects.filter(ativo=True).exclude(id=g.id)
    else:
        funcionarios = Funcionario.objects.filter(ativo=True, cargo='funcionario')
    return render(request, 'gerente/funcionarios.html', {
        'funcionario': g,
        'funcionarios': funcionarios,
        'eh_dono': g.cargo == 'dono',
    })


@require_POST
def adicionar_funcionario(request):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    dados = json.loads(request.body)
    cargo_solicitado = dados.get('cargo', 'funcionario')
    # Gerente não pode criar dono nem outro gerente
    if g.cargo == 'gerente' and cargo_solicitado in ('dono', 'gerente'):
        return JsonResponse({'erro': 'Sem permissão para criar este cargo.'}, status=403)
    if Funcionario.objects.filter(codigo=dados['codigo']).exists():
        return JsonResponse({'erro': 'Código já cadastrado.'}, status=400)
    f = Funcionario(
        nome=dados['nome'],
        codigo=dados['codigo'],
        cargo=cargo_solicitado,
        meta_mensal=int(dados.get('meta_mensal', 100)),
    )
    f.definir_senha(dados['senha'])
    f.save()
    return JsonResponse({'ok': True, 'id': f.id, 'nome': f.nome, 'codigo': f.codigo})


@require_POST
def editar_funcionario(request, func_id):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    f = get_object_or_404(Funcionario, id=func_id)
    # Gerente não pode editar donos nem outros gerentes
    if not _pode_gerenciar(g, f):
        return JsonResponse({'erro': 'Sem permissão para editar este usuário.'}, status=403)
    dados = json.loads(request.body)
    cargo_novo = dados.get('cargo', f.cargo)
    # Gerente não pode promover para dono ou gerente
    if g.cargo == 'gerente' and cargo_novo in ('dono', 'gerente'):
        return JsonResponse({'erro': 'Sem permissão para atribuir este cargo.'}, status=403)
    f.nome = dados.get('nome', f.nome)
    f.codigo = dados.get('codigo', f.codigo)
    f.cargo = cargo_novo
    f.meta_mensal = int(dados.get('meta_mensal', f.meta_mensal))
    if dados.get('senha'):
        f.definir_senha(dados['senha'])
    f.save()
    return JsonResponse({'ok': True})


@require_POST
def remover_funcionario(request, func_id):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    f = get_object_or_404(Funcionario, id=func_id)
    # Gerente não pode remover donos nem outros gerentes
    if not _pode_gerenciar(g, f):
        return JsonResponse({'erro': 'Sem permissão para remover este usuário.'}, status=403)
    f.ativo = False
    f.save()
    return JsonResponse({'ok': True})


def gerente_relatorio_view(request):
    g, r = _requer_gerente(request)
    if not g:
        return r
    funcionarios = Funcionario.objects.filter(ativo=True, cargo='funcionario')
    hoje = timezone.now()
    dados = []
    for f in funcionarios:
        tarefas_mes = Tarefa.objects.filter(
            aceita_por=f, status='finalizada',
            finalizado_em__year=hoje.year, finalizado_em__month=hoje.month
        ).count()
        dados.append({
            'id': f.id,
            'nome': f.nome,
            'pontos': f.pontos,
            'meta': f.meta_mensal,
            'tarefas': tarefas_mes,
        })
    return render(request, 'gerente/relatorio.html', {
        'funcionario': g,
        'dados_funcionarios': json.dumps(dados),
        'funcionarios': funcionarios,
    })


@require_POST
def remover_pontos(request):
    g, r = _requer_gerente(request)
    if not g:
        return JsonResponse({'erro': 'Sem permissão'}, status=403)
    dados = json.loads(request.body)
    f = get_object_or_404(Funcionario, id=dados['funcionario_id'])
    qtd = int(dados['pontos'])
    motivo = dados['motivo']
    RemocaoPontos.objects.create(
        funcionario=f,
        pontos_removidos=qtd,
        motivo=motivo,
        removido_por=g,
    )
    f.pontos = max(0, f.pontos - qtd)
    f.save()
    return JsonResponse({'ok': True, 'pontos_atuais': f.pontos})


# ─── Perfil (todos os cargos) ─────────────────────────────────────────────────

def perfil_view(request):
    f, r = _requer_login(request)
    if not f:
        return r
    return render(request, 'perfil.html', {'funcionario': f})


@require_POST
def salvar_perfil(request):
    f, r = _requer_login(request)
    if not f:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)
    dados = json.loads(request.body)
    nome = dados.get('nome', '').strip()
    senha_atual = dados.get('senha_atual', '').strip()
    nova_senha = dados.get('nova_senha', '').strip()

    if not nome:
        return JsonResponse({'erro': 'O nome não pode ficar vazio.'}, status=400)

    # Valida senha atual antes de qualquer alteração
    if not f.verificar_senha(senha_atual):
        return JsonResponse({'erro': 'Senha atual incorreta.'}, status=400)

    f.nome = nome

    if nova_senha:
        if len(nova_senha) < 6:
            return JsonResponse({'erro': 'A nova senha precisa ter ao menos 6 caracteres.'}, status=400)
        f.definir_senha(nova_senha)

    f.save()
    # Atualiza o nome na sessão não é necessário, mas garante consistência
    return JsonResponse({'ok': True, 'nome': f.nome})
