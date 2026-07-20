# BDO Tools Hub

Centralizador de ferramentas para **Black Desert Online** — um único servidor Flask que reúne módulos de Bartering, Hunting, Contribution Points e um Dashboard pessoal.

## Módulos

### Bartering Tracker
- Calculadora de custos de Moedas Corvo com descontos (Pacote Econômico, Vice-Capitã Cleia, Barganha)
- Tabela de experiência por nível com registro de medições e projeção de permutas para 100%
- Configuração salva automaticamente

### Hunting Calculator
- Calculadora de drops e experiência para caça
- Histórico de sessões
- Geração de dados de teste

### CP (Contribution Points)
- Calculadora de CP com projeção de avanço
- OCR via API para extrair níveis de profissão de screenshots do jogo
- Simulação de avanço por profissão de Life Skill

### Dashboard
- Lista de tarefas diárias/semanais com reset automático
- Notas
- Exibição de prata do dia

## Stack

- **Backend:** Python 3.12 + Flask
- **Frontend:** HTML/CSS/JS vanilla (templates Jinja2)
- **OCR:** OCR.space API (módulo CP)
- **Ícones:** Lucide Icons
- **Fonte:** Web Pearl (BDO style)

## Como rodar

```bash
# Criar e ativar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar
python app.py
```

O servidor inicia em `http://0.0.0.0:5000`.

Acesse os módulos:
- `/bartering/`
- `/hunting/`
- `/cp/`
- `/dashboard/`

## Deploy com Nginx

O app roda atrás do Nginx com proxy reverso e HTTPS via Let's Encrypt. Exemplo de configuração:

```nginx
location /bdohub/ {
    proxy_pass http://127.0.0.1:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /bdohub;
}
```

## Estrutura

```
bdohub/
├── app.py                    # Entrypoint Flask
├── requirements.txt
├── data/                     # Dados persistentes (dashboard.json)
├── static/                   # Assets globais (fontes, SVG)
├── templates/                # Template base (index)
└── modules/
    ├── bartering/            # Módulo de Bartering
    ├── hunting/              # Módulo de Hunting
    ├── cp/                   # Módulo de CP
    └── dashboard/            # Módulo de Dashboard
```

## Licença

Uso pessoal.
