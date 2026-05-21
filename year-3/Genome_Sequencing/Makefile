# Makefile

# --------------------------------------------------------------
# Configuarações
# --------------------------------------------------------------

.PHONY: all
all: all_verificacao all_download all_qc all_assembly all_polishing all_evaluation all_annotation sumario

DIR_SCRIPTS := scripts

# Illumina paired-out
ILLUMINA_RUN := ERR2767971

# Nanopore single-end
NANOPORE_RUN := ERR4352271

REFERENCE_ID := GCA_903989475

THREADS := 11


# --------------------------------------------------------------
# Análise da qualidade dos scripts
# --------------------------------------------------------------

# Econtrar dinamicamente todos os scripts
SCRIPTS_A_ANALISAR := $(wildcard $(DIR_SCRIPTS)/*.sh)
# Ficheiro de saída que irá guardar o resultado da análise
FICHEIRO_RESULTADO := logs/analise_qualidade.log

# Regra Default
all_verificacao: $(FICHEIRO_RESULTADO)
# Regra Principal
$(FICHEIRO_RESULTADO): $(SCRIPTS_A_ANALISAR) # verificar se algum script é mais recente
	@echo "Um ou mais scripts foram modificados. A executar a análise de qualidade"
	@mkdir -p logs
	@./$(DIR_SCRIPTS)/analisar_scripts.sh > $(FICHEIRO_RESULTADO)
	@echo "Análise concluída. Resultados guardados em $(FICHEIRO_RESULTADO)"

# --------------------------------------------------------------
# Download
# --------------------------------------------------------------

# Default target
all_download: bootstrap download_data download_reference check_data stage0 stage1

bootstrap: data/raw data/reference results/qc data/clean results/assemblies

data/raw:
	mkdir -p $@
data/reference:
	mkdir -p $@
results/qc:
	mkdir -p $@
data/clean:
	mkdir -p $@
results/assemblies:
	mkdir -p $@


# Download the fastq files
download_data: data/raw/$(ILLUMINA_RUN)_1.fastq.gz data/raw/$(ILLUMINA_RUN)_2.fastq.gz data/raw/$(NANOPORE_RUN)_1.fastq.gz
data/raw/$(ILLUMINA_RUN)_1.fastq.gz:
	wget -O $@.tmp ftp.sra.ebi.ac.uk/vol1/fastq/ERR276/001/ERR2767971/ERR2767971_1.fastq.gz && mv $@.tmp $@
data/raw/$(ILLUMINA_RUN)_2.fastq.gz:
	wget -O $@.tmp ftp.sra.ebi.ac.uk/vol1/fastq/ERR276/001/ERR2767971/ERR2767971_2.fastq.gz && mv $@.tmp $@
data/raw/$(NANOPORE_RUN)_1.fastq.gz:
	wget -O $@.tmp ftp.sra.ebi.ac.uk/vol1/fastq/ERR435/001/ERR4352271/ERR4352271_1.fastq.gz && mv $@.tmp $@

# Stage 0
stage0: check_data

%.checked: %_1.fastq.gz %_2.fastq.gz
	fastqc -o results/qc $^ && touch $@
%.checked: %_1.fastq.gz
	fastqc -o results/qc $^ && touch $@
%.checked: %_subreads.fastq.gz
	fastqc -o results/qc $^ && touch $@

check_data: data/raw/$(ILLUMINA_RUN).checked data/raw/$(NANOPORE_RUN).checked

# Stage 1
stage1: results/qc/qc.html
results/qc/qc.html:
	mkdir -p $(dir $@) && \
	fastqc -t 2 -o $(dir $@) data/raw/*.fastq.gz
	#multiqc --force -o $(dir $@) -n qc $(dir $@)


download_reference: \
	data/reference/$(REFERENCE_ID).fna.gz \
	data/reference/$(REFERENCE_ID).gff.gz
data/reference/$(REFERENCE_ID).fna.gz:
	wget -O $@ \
		https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/903/989/475/GCF_903989475.2_X_arboricola_CPBF_427_hybrid_assembly/GCF_903989475.2_X_arboricola_CPBF_427_hybrid_assembly_genomic.fna.gz && \
	gunzip -c data/reference/GCA_903989475.fna.gz > data/reference/GCA_903989475.fna
	rm data/reference/GCA_903989475.fna.gz

data/reference/$(REFERENCE_ID).gff.gz:
	wget -O $@ \
		https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/903/989/475/GCF_903989475.2_X_arboricola_CPBF_427_hybrid_assembly/GCF_903989475.2_X_arboricola_CPBF_427_hybrid_assembly_genomic.gff.gz && \
	gunzip -c data/reference/GCA_903989475.gff.gz > data/reference/GCA_903989475.gff
	rm data/reference/GCA_903989475.gff.gz


# --------------------------------------------------------------
# QC - para Illumina
# --------------------------------------------------------------
all_qc: qc_standard qc_pilon

qc_standard:
	fastp \
		-i data/raw/$(ILLUMINA_RUN)_1.fastq.gz \
		-I data/raw/$(ILLUMINA_RUN)_2.fastq.gz \
		-o data/clean/$(ILLUMINA_RUN)_1.clean.fastq.gz \
		-O data/clean/$(ILLUMINA_RUN)_2.clean.fastq.gz \
		-h results/qc/$(ILLUMINA_RUN)_fastp_report.html \
		-j results/qc/$(ILLUMINA_RUN)_fastp_report.json \
		-q 20 \
		-l 100 \
		--cut_right --cut_right_mean_quality 10

qc_pilon:
	fastp \
		-i data/raw/$(ILLUMINA_RUN)_1.fastq.gz \
		-I data/raw/$(ILLUMINA_RUN)_2.fastq.gz \
		-o data/clean/$(ILLUMINA_RUN)_1.pilon.fastq.gz \
		-O data/clean/$(ILLUMINA_RUN)_2.pilon.fastq.gz \
		-h results/qc/$(ILLUMINA_RUN)_fastp_report_pilon.html \
		-j results/qc/$(ILLUMINA_RUN)_fastp_report_pilon.json \
		-q 28 \
		-l 100 \
		--cut_right --cut_right_mean_quality 20

# --------------------------------------------------------------
# Montagem do Genoma
# --------------------------------------------------------------
all_assembly: assembly_illumina assembly_nanopore assembly_hybrid results/assemblies/illumina results/assemblies/nanopore results/assemblies/hybrid

results/assemblies/illumina:
	mkdir -p $@
results/assemblies/nanopore:
	mkdir -p $@
results/assemblies/hybrid:
	mkdir -p $@

assembly_illumina: results/assemblies/illumina
	spades.py \
		--pe1-1 data/clean/$(ILLUMINA_RUN)_1.clean.fastq.gz \
		--pe1-2 data/clean/$(ILLUMINA_RUN)_2.clean.fastq.gz \
		-o results/assemblies/illumina \
		-t $(THREADS)

assembly_nanopore: results/assemblies/nanopore
	flye --nano-raw data/raw/$(NANOPORE_RUN)_1.fastq.gz \
		--out-dir results/assemblies/nanopore \
		--genome-size 5.1m \
		--threads $(THREADS)

assembly_hybrid: results/assemblies/hybrid
	spades.py \
		--pe1-1 data/clean/$(ILLUMINA_RUN)_1.clean.fastq.gz \
		--pe1-2 data/clean/$(ILLUMINA_RUN)_2.clean.fastq.gz \
		--nanopore data/raw/$(NANOPORE_RUN)_1.fastq.gz \
		-o results/assemblies/hybrid \
		-t $(THREADS)

# --------------------------------------------------------------
# Polimento da montagem de Long Reads
# --------------------------------------------------------------
all_polishing: polishing_inicial polishing_pilon results/alignments results/assemblies/flye_polished

results/assemblies/flye_polished:
	mkdir -p $@
results/alignments:
	mkdir -p $@

polishing_inicial: results/alignments
	bwa-mem2 index results/assemblies/nanopore/assembly.fasta
	bwa-mem2 mem -t 8 results/assemblies/nanopore/assembly.fasta \
    		data/clean/$(ILLUMINA_RUN)_1.pilon.fastq.gz \
		data/clean/$(ILLUMINA_RUN)_2.pilon.fastq.gz \
		> results/alignments/illumina_vs_flye.sam
	samtools view -bS results/alignments/illumina_vs_flye.sam > results/alignments/illumina_vs_flye.bam
	samtools sort results/alignments/illumina_vs_flye.bam -o results/alignments/illumina_vs_flye.sorted.bam
	samtools index results/alignments/illumina_vs_flye.sorted.bam

polishing_pilon: polishing_inicial results/assemblies/flye_polished
	_JAVA_OPTIONS="-Xms4g -Xmx16g" pilon \
		--genome results/assemblies/nanopore/assembly.fasta \
		--frags results/alignments/illumina_vs_flye.sorted.bam \
		--outdir results/assemblies/flye_polished \
		--output flye_polished

# --------------------------------------------------------------
# Avaliação
# --------------------------------------------------------------
all_evaluation: evaluation_data results/evaluation/busco results/evaluation/quast results/evaluation/busco_ref results/evaluation/quast_ref

results/evaluation/busco:
	mkdir -p $@
results/evaluation/quast:
	mkdir -p $@
results/evaluation/busco_ref:
	mkdir -p $@
results/evaluation/quast_ref:
	mkdir -p $@


evaluation_data: download_busco eval_quast eval_busco_ill eval_busco_nano eval_busco_nano_pol eval_busco_hybrid eval_quast_ref eval_busco_ref

eval_quast: results/evaluation/quast
	conda run -n genomica_tp1 quast.py -o results/evaluation/quast \
		-t $(THREADS) \
		--label "SPAdes_Illumina, Flye, Flye_Polished, Hybrid" \
		results/assemblies/illumina/scaffolds.fasta \
		results/assemblies/nanopore/assembly.fasta \
		results/assemblies/flye_polished/flye_polished.fasta \
		results/assemblies/hybrid/scaffolds.fasta

eval_quast_ref: results/evaluation/quast_ref
	conda run -n genomica_tp1 quast.py -o results/evaluation/quast_ref \
		-t $(THREADS) \
		data/reference/$(REFERENCE_ID).fna

create_env:
	conda create -y -n temporary && \
	conda run -n temporary conda install -y -c conda-forge mamba && \
	conda run -n temporary mamba install -y -c conda-forge -c bioconda busco=6.0.0 sepp=4.5.5


download_busco: create_env
	conda run -n temporary busco --download bacteria_odb10

eval_busco_ill: download_busco results/evaluation/busco
	conda run -n temporary busco -f \
		-i results/assemblies/illumina/scaffolds.fasta \
		-o results/evaluation/busco/ill \
		-l bacteria_odb10 \
		-m genome \
		-c 11
eval_busco_nano: download_busco results/evaluation/busco
	conda run -n temporary busco -f \
		-i results/assemblies/nanopore/assembly.fasta \
		-o results/evaluation/busco/nano \
		-l bacteria_odb10 \
		-m genome \
		-c 11
eval_busco_nano_pol: download_busco results/evaluation/busco
	conda run -n temporary busco -f \
		-i results/assemblies/flye_polished/flye_polished.fasta \
		-o results/evaluation/busco/nanoPol \
		-l bacteria_odb10 \
		-m genome \
		-c 11
eval_busco_hybrid: download_busco results/evaluation/busco
	conda run -n temporary busco -f \
		-i results/assemblies/hybrid/scaffolds.fasta \
		-o results/evaluation/busco/hybrid \
		-l bacteria_odb10 \
		-m genome \
		-c 11

eval_busco_ref: download_busco results/evaluation/busco_ref
	conda run -n temporary busco -f \
		-i data/reference/$(REFERENCE_ID).fna \
		-o results/evaluation/busco_ref \
		-l bacteria_odb10 \
		-m genome \
		-c $(THREADS)

# --------------------------------------------------------------
# Annotation
# --------------------------------------------------------------
create_env_prokka:
	conda create -y -n temporary2 -c conda-forge -c bioconda prokka && \
	conda run -n temporary2 prokka --help

results/annotation:
	mkdir -p results/annotation

run_prokka: create_env_prokka results/annotation
	conda run -n temporary2 prokka \
		--outdir results/annotation \
		--prefix annotated_genome \
		--locustag SAMPLE \
		--genus Xanthomonas \
		--species arboricola \
		--strain CPBF427 \
		--cpus 11 \
		--force \
		results/assemblies/hybrid/scaffolds.fasta

all_annotation: run_prokka



# --------------------------------------------------------------
# sumario.txt (adicionado Num_CDSs)
# --------------------------------------------------------------
sumario:
	@echo "Gerando sumário..."
	@rm -f results/evaluation/sumario.tsv
	@echo -e "Parâmetro\tIllumina-only\tNanopore-only\tHybrid\tReferencia" > results/evaluation/sumario.tsv
	@ref_genome=$$(grep -m1 "Total length" results/evaluation/quast_ref/report.tsv | cut -f2); \
	ref_contigs=$$(grep -m1 "# contigs (>= 0 bp)" results/evaluation/quast_ref/report.tsv | cut -f2); \
	ref_n50=$$(grep -m1 "^N50" results/evaluation/quast_ref/report.tsv | cut -f2); \
	ref_gc=$$(grep -m1 "^GC" results/evaluation/quast_ref/report.tsv | cut -f2); \
	ref_busco=$$(grep -m1 "C:" results/evaluation/busco_ref/short_summary*.txt | sed -E 's/.*C:([0-9.]+)%.*/\1/'); \
	new_cds=$$(awk -F'\t' '$$2=="CDS" {count++} END {print count}' results/annotation/annotated_genome.tsv); \
	echo $$new_cds; \
	cds_ref=$$(awk -F'\t' '$$3=="CDS" {count++} END {print count}' data/reference/GCA_903989475.gff); \
	\
	echo -n "Tamanho_Genoma_bp\t" >> results/evaluation/sumario.tsv; \
	awk -F'\t' '/Total length/ {print $$2"\t"$$3"\t"$$4; exit}' results/evaluation/quast/report.tsv | \
	awk -v ref="$$ref_genome" '{print $$0"\t"ref}' >> results/evaluation/sumario.tsv; \
	\
	echo -n "Num_Contigs\t" >> results/evaluation/sumario.tsv; \
	awk -F'\t' '/# contigs/ {print $$2"\t"$$3"\t"$$4; exit}' results/evaluation/quast/report.tsv | \
	awk -v ref="$$ref_contigs" '{print $$0"\t"ref}' >> results/evaluation/sumario.tsv; \
	\
	echo -n "N50_bp\t" >> results/evaluation/sumario.tsv; \
	awk -F'\t' '/^N50/ {print $$2"\t"$$3"\t"$$4; exit}' results/evaluation/quast/report.tsv | \
	awk -v ref="$$ref_n50" '{print $$0"\t"ref}' >> results/evaluation/sumario.tsv; \
	\
	echo -n "GC_percent\t" >> results/evaluation/sumario.tsv; \
	awk -F'\t' '/^GC/ {print $$2"\t"$$3"\t"$$4; exit}' results/evaluation/quast/report.tsv | \
	awk -v ref="$$ref_gc" '{print $$0"\t"ref}' >> results/evaluation/sumario.tsv; \
	\
	echo -n "BUSCO_Completo_percent\t" >> results/evaluation/sumario.tsv; \
	awk '/C:/ {gsub(/.*C:|%.*/,""); print}' results/evaluation/busco/ill/short_summary*.txt > tmp1; \
	awk '/C:/ {gsub(/.*C:|%.*/,""); print}' results/evaluation/busco/nano/short_summary*.txt > tmp2; \
	awk '/C:/ {gsub(/.*C:|%.*/,""); print}' results/evaluation/busco/hybrid/short_summary*.txt > tmp3; \
	paste -d '\t' tmp1 tmp2 tmp3 | awk -v ref="$$ref_busco" '{print $$0"\t"ref}' >> results/evaluation/sumario.tsv; \
	rm tmp1 tmp2 tmp3; \
	\
	# Adicionar Num_CDSs do Prokka \
	echo -e "Num_CDSs\tNA\tNA\t$$new_cds\t$$cds_ref" >> results/evaluation/sumario.tsv;
	@echo "Sumário finalizado."



# Limpeza
# --------------------------------------------------------------
.PHONY: clean
clean:
	@rm -rf logs/* data/raw/* results/qc/* data/clean/* results/assemblies/*
