#!/usr/bin/env bash

# Script para analisar a qualidade de outros scripts com shellcheck

NOME_AMBIENTE="genomica_tp1"
DIR_SCRIPTS="scripts"

echo "Análise dos scripts com Shellcheck"
echo "Diretório dos scripts: $DIR_SCRIPTS"
echo "Ambiente conda: $NOME_AMBIENTE"

# Flag para verificar se foram encontrados problemas
HOUVE_ERROS=0

# Loop por todos os scripts (.sh)
for script_file in "$DIR_SCRIPTS"/*.sh; do
	echo ""
	echo "A analisar o ficheiro: $(basename "$script_file")"

	# Executar o shellcheck dentro do ambiente conda e se encontar algum problema o código de saída é >0
	if ! conda run -n "$NOME_AMBIENTE" shellcheck "$script_file"; then
		HOUVE_ERROS=1
	fi

	echo ""
done


# Resumo final
echo "Análise concluída"
if [ $HOUVE_ERROS -eq 1 ]; then
	echo "Foram encontrados problemas. Por favor reveja o output acima"
else
	echo "Todos os scripts passaram na verificação do shellcheck."
fi
