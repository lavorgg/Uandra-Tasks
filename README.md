# ⚡ Uandra Tasks

Sistema de gerenciamento de tarefas com pontuação para equipes.
Desenvolvido com **Django + SQLite** no backend e **HTML/CSS/JS** no frontend, com suporte a **PWA** para uso como aplicativo no celular.

---

## ⚠️ IMPORTANTE — Como abrir o sistema

> **NÃO abra os arquivos .html diretamente no navegador.**
> O sistema usa templates Django que só funcionam rodando pelo servidor Python.
> Se abrir direto, verá as tags `{% ... %}` cruas e receberá erros.

---

## ✅ Como rodar (jeito mais fácil)

### Windows
1. Abra a pasta `backend/`
2. Clique duas vezes em **`iniciar_windows.bat`**
3. Aguarde instalar e o navegador abrirá automaticamente em `http://localhost:8000`

### Linux / Mac
```bash
cd backend
./iniciar_linux_mac.sh
```

---

## 🔧 Passo a passo manual

```bash
# Abra o terminal DENTRO da pasta backend/
cd backend

# Instale o Django (somente na primeira vez)
pip install django

# Crie o banco de dados (somente na primeira vez)
python manage.py migrate

# Popule com usuários e tarefas de exemplo (somente na primeira vez)
python seed.py

# Inicie o servidor
python manage.py runserver

# Acesse no navegador:
# http://localhost:8000
```

---

## 👤 Usuários de Exemplo

| Nome         | Código | Senha    | Cargo       |
|--------------|--------|----------|-------------|
| Carlos Dono  | 0      | 01011980 | Dono        |
| Ana Gerente  | 1      | 15031985 | Gerente     |
| João Silva   | 2      | 20051995 | Funcionário |
| Maria Souza  | 3      | 10101992 | Funcionário |

> A senha é a data de nascimento no formato **DDMMAAAA** (sem barras).

---

## 🗂 Estrutura

```
uandra_zip/
├── backend/                    ← RODE DAQUI
│   ├── iniciar_windows.bat     ← Duplo clique (Windows)
│   ├── iniciar_linux_mac.sh    ← Terminal (Linux/Mac)
│   ├── manage.py
│   ├── seed.py                 ← Cria usuários e tarefas de exemplo
│   ├── templates/              ← HTMLs processados pelo Django
│   │   ├── login.html
│   │   ├── tarefas.html
│   │   ├── pendentes.html
│   │   ├── relatorio.html
│   │   └── gerente/
│   ├── static/                 ← CSS, PWA, ícones
│   │   ├── estilo.css
│   │   ├── manifest.json
│   │   ├── sw.js
│   │   └── icons/
│   ├── uandra_tasks/           ← Configurações Django
│   └── core/                   ← Models, views, rotas
│
└── README.md
```

---

## 📱 Usar como App no Celular (PWA)

1. Com o servidor rodando, descubra o IP do computador:
   - Windows: abra o CMD e digite `ipconfig` → procure "Endereço IPv4"
2. No celular (mesma rede Wi-Fi), abra: `http://SEU_IP:8000`
3. **Android (Chrome):** menu ⋮ → "Adicionar à tela inicial"
4. **iPhone (Safari):** botão compartilhar → "Adicionar à Tela de Início"

---

## ⚙️ Configurações importantes (settings.py)

Para usar em produção, edite `backend/uandra_tasks/settings.py`:

```python
DEBUG = False                         # Desativa mensagens de erro detalhadas
ALLOWED_HOSTS = ['seu-dominio.com']   # Coloque o domínio real
SECRET_KEY = 'troque-por-chave-segura'
```

---

*Uandra Tasks © 2024 — Todos os direitos reservados*
