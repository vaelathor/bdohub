#!/bin/bash
# Script de backup periódico dos dados do BDO Tools Hub
# Executa backup completo e mantém os 100 backups mais recentes

PROJECT_DIR="/home/ubuntu/projects/bdohub"
cd "$PROJECT_DIR" || exit 1

# Ativa o venv e executa o backup
"$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/backup_utils.py" 2>&1 | logger -t bdohub-backup

# Git auto-commit e cleanup - tudo feito pelo Python para evitar problemas de escape
"$PROJECT_DIR/venv/bin/python3" "$PROJECT_DIR/backup_cron.py" 2>&1 | logger -t bdohub-backup

echo "Backup concluído em $(date)"
