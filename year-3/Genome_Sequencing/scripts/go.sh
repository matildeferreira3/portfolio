#!/usr/bin/env bash
# shellcheck disable=SC1091

set -e # Parar em caso de Erro

#---------------------------------
# Ambiente genomica_tp1
#---------------------------------
NOME_AMBIENTE="genomica_tp1"
ENV_FILE="env/environment.yml"

echo "Verificar se o ambiente '$NOME_AMBIENTE' existe"
if conda env list | grep -q "$NOME_AMBIENTE"; then
	echo "Ambiente já existe"
else
	echo "Criar ambiente"
	conda env create -f "$ENV_FILE"
fi
echo ""


echo "Ativar ambiente Conda"

# Inicializar conda dentro de scripts
source "$(conda info --base)/etc/profile.d/conda.sh"
# Ativar o ambiente
conda activate genomica_tp1
echo "Ambiente ativo: genomica_tp1"

echo "Executar Makefile"
make all
#make all_verificacao
#make all_download
#make qc
#make all_assembly
