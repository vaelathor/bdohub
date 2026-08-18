"""
Script auxiliar executado pelo cron para:
- Limpar backups antigos (mantém os 100 mais recentes)
- Git auto-commit no diretório de backups (versionamento extra)
"""
import os
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import backup_utils


def main():
    # 1. Limpa backups antigos (mantém os 100 mais recentes)
    backup_utils.cleanup_old_backups(max_backups=100)

    # 2. Git auto-commit no diretório de backups
    git_dir = os.path.join(PROJECT_DIR, 'data_backups')
    os.chdir(git_dir)

    # Inicializa git se necessário
    if not os.path.exists(os.path.join(git_dir, '.git')):
        os.system('git init')
        os.system('git add -A')
        os.system('git commit -m "backup: snapshot inicial"')
    else:
        os.system('git add -A')
        # Só commit se houver mudanças
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        result = os.system(f'git diff --cached --quiet || git commit -m "backup: {now}"')

    print(f"Git auto-commit concluído em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
