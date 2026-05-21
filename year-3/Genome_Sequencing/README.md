# TP1-Sequenciacao-de-Genomas

### Trabalho realizado por:
- Ana Matilde Ferreira (up202307802@up.pt)
- Maria Leonor Carvalho (up202307522@up.pt)

### Estrutura de diretórios
├── Makefile

├── README.md

├── env

	├── environment.yml

└── scripts

	├── analisar_scripts.sh

	└── go.sh

### Ferramentas utilizadas
name: genomica_tp1

channels:
  - bioconda
  - conda-forge

dependencies:
  - python
  - fastqc
  - spades
  - flye
  - unicycler
  - quast
  - busco
  - prokka
  - samtools
  - pandas
  - shellcheck
  - wget
  - sra-tools

### Reprodutibilidade e Execução
Todo o pipeline é totalmente automatizado através do ficheiro go.sh.

Para executar a análise completa:
 - bash scripts/go.sh

O script:
1. Cria o ambiente Conda e instala todas as dependências.
2. Ativa o ambiente.
3. Chama o Makefile.
4. O Makefile executa, por ordem:
	- Download dos dados (Illumina e Nanopore)
	- QC (FastQC)
	- Montagens (Illumina / Nanopore / Híbrida)
	- Polimento da montagem de Long Reads
	- Avaliação (QUAST + BUSCO)
	- Anotação (melhor montagem - híbrida)
	- Geração automática da tabela final sumario.tsv na raiz do repositório

### Resultados

Após a execução de go.sh, os principais resultados são guardados em:
- results/evaluation/sumario.tsv: Tabela com os parâmetros comparativos das montagens
- results/evaluation/quast: Relatórios QUAST
- results/evaluation/busco/: Relatórios BUSCO
- esults/annotation/: Ficheiros da anotação Prokka
