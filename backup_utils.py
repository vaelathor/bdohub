"""
Módulo de backup automático dos dados do BDO Tools Hub.

Cria snapshots com timestamp de todos os arquivos de dados do usuário
em /home/ubuntu/projects/bdohub/data_backups/<timestamp>/

Uso:
    from backup_utils import backup_data, backup_single_file
    
    # Backup completo de todos os dados
    backup_data()
    
    # Backup de um arquivo específico
    backup_single_file('modules/cp/config.json')
"""

import os
import shutil
import json
import time
from datetime import datetime

# Diretório raiz dos backups (dentro do projeto)
BACKUP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_backups')

# Lista de arquivos de dados que devem ser sempre preservados
# (caminhos relativos ao diretório do projeto)
DATA_FILES = [
    'modules/bartering/config.json',
    'modules/bartering/exp_table.json',
    'modules/hunting/config.json',
    'modules/hunting/historico.json',
    'modules/cp/config.json',
    'data/dashboard.json',
]


def _get_timestamp():
    """Retorna timestamp no formato YYYY-MM-DD_HH-MM-SS para usar como nome do backup."""
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def _get_project_root():
    """Retorna o caminho absoluto do diretório raiz do projeto."""
    return os.path.dirname(os.path.abspath(__file__))


def _get_latest_symlink():
    """Retorna o caminho do symlink 'latest'."""
    return os.path.join(BACKUP_ROOT, 'latest')


def _update_latest_symlink(backup_dir):
    """Atualiza o symlink 'latest' para apontar para o backup mais recente."""
    latest = _get_latest_symlink()
    # Remove o symlink antigo se existir
    if os.path.islink(latest) or os.path.exists(latest):
        try:
            os.unlink(latest)
        except OSError:
            pass
    # Cria o novo symlink
    try:
        os.symlink(backup_dir, latest)
    except OSError:
        pass  # Se falhar (ex: permissão), não é crítico


def backup_data(backup_root=None):
    """
    Faz backup de todos os arquivos de dados do projeto.
    
    Args:
        backup_root: Diretório alternativo para os backups (opcional).
                     Se não informado, usa o diretório padrão 'data_backups'.
    
    Returns:
        dict com informações do backup realizado, ou None se nada foi copiado.
    """
    if backup_root is None:
        backup_root = BACKUP_ROOT
    
    project_root = _get_project_root()
    timestamp = _get_timestamp()
    backup_dir = os.path.join(backup_root, timestamp)
    
    os.makedirs(backup_dir, exist_ok=True)
    
    backed_up = []
    errors = []
    
    for rel_path in DATA_FILES:
        src = os.path.join(project_root, rel_path)
        if os.path.exists(src):
            try:
                # Cria os subdiretórios necessários no destino
                dst_path = os.path.join(backup_dir, rel_path)
                dst_dir = os.path.dirname(dst_path)
                os.makedirs(dst_dir, exist_ok=True)
                
                # Copia o arquivo mantendo metadados
                shutil.copy2(src, dst_path)
                backed_up.append(rel_path)
            except Exception as e:
                errors.append({'file': rel_path, 'error': str(e)})
    
    if backed_up:
        _update_latest_symlink(backup_dir)
        return {
            'timestamp': timestamp,
            'backup_dir': backup_dir,
            'files': backed_up,
            'errors': errors if errors else None
        }
    
    return None


def backup_single_file(rel_path, backup_root=None):
    """
    Faz backup de um único arquivo de dados.
    
    Args:
        rel_path: Caminho relativo do arquivo (ex: 'modules/cp/config.json')
        backup_root: Diretório alternativo para os backups (opcional)
    
    Returns:
        dict com informações do backup, ou None se o arquivo não existir.
    """
    if backup_root is None:
        backup_root = BACKUP_ROOT
    
    project_root = _get_project_root()
    src = os.path.join(project_root, rel_path)
    
    if not os.path.exists(src):
        return None
    
    timestamp = _get_timestamp()
    backup_dir = os.path.join(backup_root, timestamp)
    
    dst_path = os.path.join(backup_dir, rel_path)
    dst_dir = os.path.dirname(dst_path)
    os.makedirs(dst_dir, exist_ok=True)
    
    shutil.copy2(src, dst_path)
    
    _update_latest_symlink(backup_dir)
    
    return {
        'timestamp': timestamp,
        'backup_dir': backup_dir,
        'file': rel_path
    }


def list_backups(backup_root=None):
    """
    Lista todos os backups disponíveis, ordenados do mais novo ao mais antigo.
    
    Args:
        backup_root: Diretório de backups (opcional)
    
    Returns:
        lista de dicts com timestamp e caminho de cada backup.
    """
    if backup_root is None:
        backup_root = BACKUP_ROOT
    
    if not os.path.exists(backup_root):
        return []
    
    backups = []
    for entry in os.listdir(backup_root):
        entry_path = os.path.join(backup_root, entry)
        # Filtra apenas diretórios com formato timestamp (YYYY-MM-DD_HH-MM-SS)
        # Exclui .git, latest e qualquer outro diretório que não seja snapshot
        if os.path.isdir(entry_path) and entry != 'latest' and not entry.startswith('.'):
            backups.append({
                'timestamp': entry,
                'path': entry_path
            })
    
    # Ordena do mais novo para o mais antigo
    backups.sort(key=lambda x: x['timestamp'], reverse=True)
    return backups


def cleanup_old_backups(max_backups=50, backup_root=None):
    """
    Remove backups antigos, mantendo apenas os N mais recentes.
    
    Args:
        max_backups: Número máximo de backups para manter
        backup_root: Diretório de backups (opcional)
    """
    if backup_root is None:
        backup_root = BACKUP_ROOT
    
    backups = list_backups(backup_root)
    
    if len(backups) <= max_backups:
        return
    
    # Remove os backups mais antigos (final da lista)
    to_remove = backups[max_backups:]
    for backup in to_remove:
        try:
            shutil.rmtree(backup['path'])
        except OSError:
            pass


def restore_from(backup_timestamp, backup_root=None):
    """
    Restaura os dados de um backup específico.
    AVISO: Isso sobrescreve os dados atuais!
    
    Args:
        backup_timestamp: Timestamp do backup (ex: '2026-07-28_17-00-00')
        backup_root: Diretório de backups (opcional)
    
    Returns:
        dict com informações da restauração.
    """
    if backup_root is None:
        backup_root = BACKUP_ROOT
    
    project_root = _get_project_root()
    backup_dir = os.path.join(backup_root, backup_timestamp)
    
    if not os.path.exists(backup_dir):
        return {'error': f'Backup {backup_timestamp} não encontrado.'}
    
    restored = []
    errors = []
    
    for rel_path in DATA_FILES:
        src = os.path.join(backup_dir, rel_path)
        dst = os.path.join(project_root, rel_path)
        
        if os.path.exists(src):
            try:
                dst_dir = os.path.dirname(dst)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src, dst)
                restored.append(rel_path)
            except Exception as e:
                errors.append({'file': rel_path, 'error': str(e)})
    
    return {
        'backup': backup_timestamp,
        'restored': restored,
        'errors': errors if errors else None
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        backups = list_backups()
        if backups:
            print(f"Backups disponíveis ({len(backups)}):")
            for b in backups:
                print(f"  {b['timestamp']}")
        else:
            print("Nenhum backup encontrado.")
    
    elif len(sys.argv) > 2 and sys.argv[1] == 'restore':
        result = restore_from(sys.argv[2])
        if 'error' in result:
            print(f"Erro: {result['error']}")
        else:
            print(f"Restaurado do backup {result['backup']}:")
            for f in result['restored']:
                print(f"  + {f}")
            if result['errors']:
                for e in result['errors']:
                    print(f"  ! {e['file']}: {e['error']}")
    
    else:
        result = backup_data()
        if result:
            print(f"Backup realizado em {result['timestamp']}:")
            for f in result['files']:
                print(f"  ✓ {f}")
        else:
            print("Nenhum arquivo para fazer backup.")
