import sqlite3
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

def executar_query(query):
    try:
        conn = sqlite3.connect("morbilidade.db") 
        cursor = conn.cursor()
        cursor.execute(query)
        resultados = cursor.fetchall()  
        colunas = [desc[0] for desc in cursor.description]
        conn.close()
        return {"colunas": colunas, "dados": resultados}
    except sqlite3.Error as e:
        return {"erro": str(e)}

@app.route("/")
def index():
    conn = sqlite3.connect('morbilidade.db') 
    cursor = conn.cursor()

    query = """
    SELECT * FROM
    (SELECT COUNT(*) AS 'Nº de Perfis de Pacientes' FROM pacientes) AS a
    JOIN
    (SELECT COUNT(*) AS 'Nº Condições Médicas' FROM grupoDiagnostico) AS b
    JOIN
    (SELECT COUNT(*) AS 'Nº de Regioes' FROM regioes) AS c
    JOIN
    (SELECT COUNT(*) AS 'Nº de Instituições' FROM instituicoes) AS d
    """
    cursor.execute(query)
    results = cursor.fetchone()
    
    conn.close()
    
    headers = ['Nº de Perfis de Pacientes', 'Nº Condições Médicas', 'Nº de Regioes', 'Nº de Instituições']
    return render_template('index.html', headers=headers, data=results)
    return render_template("index.html")

@app.route("/base_dados")
def base_dados():
    return render_template("base_dados.html")

@app.route("/diagrama_classes")
def diagrama_classes():
    return render_template("diagrama_classes.html")

@app.route("/modelo_relacional")
def modelo_relacional():
    return render_template("modelo_relacional.html")

@app.route("/tipos_query")
def tipos_query():
    return render_template("tipos_query.html")

@app.route("/query_page/<tipo>")
def query_page(tipo):
    queries = {
    "regiao": {
        "1": {
            "descricao": "Quais as instituições localizadas na Região de Saúde do Norte? Liste-as por ordem alfabética do nome da instituição.",
            "query": "select i.instituicao from instituicoes i natural left join regioes r where r.regiao='Região de Saúde do Norte' order by i.instituicao;"
        },
        "2": {
            "descricao": "Quais são as três regiões com o menor número de óbitos? Indique apenas o nome das regiões.",
            "query": "select r.regiao, sum(i.obitos) as obitosReg from internamentos i natural join instituicoes itc natural join regioes r group by itc.regiaoId order by obitosReg limit 3;"
        },
        "3": {
            "descricao": "Quais são os diagnósticos mais comuns por região de saúde, entre 2017 e 2019? Liste a descrição do diagnóstico (GrupoDiagnóstico) e a respetiva região, organizados por ordem alfabética pelo nome da região.",
            "query": "select regiao, descricao from (select regiao, descricao, max(num) as max from (select r.regiao as regiao, gd.descricao as descricao, count(gd.codigoGD) as num from internamentos i natural join instituicoes itc natural join regioes r natural join grupodiagnostico gd where i.periodo like '%2017%' or i.periodo like '%2018%' or i.periodo like '%2019%' group by r.regiaoId, gd.codigoGD) group by regiao order by regiao, num desc) order by regiao;"
        },
        "4": {
            "descricao": "Quais são as regiões (regiao e regiaoID) onde o número de instituições é igual ou superior à média nacional de instituições por região? Liste as regiões, juntamente com o número de instituições em cada uma, ordenadas da região com mais instituições para a que tem menos.",
            "query": "select r.regiaoId, r.regiao, count(i.instituicaoId) as nInstituicoes from instituicoes i natural left join regioes r group by r.regiaoId having nInstituicoes >= (select avg(nInstituicao*1.0/nRegiao) as PseudoMedia from (select count(distinct i.instituicaoId) as nInstituicao, count(distinct i.regiaoId) as nRegiao from instituicoes i)) order by r.regiaoId desc;"
        },
        "5": {
            "descricao": "Qual é a distribuição percentual de internamentos por região em relação ao total nacional? Liste a região e a distribuição percentual, por ordem decrescente desta.",
            "query": "select r.regiao, (nrIntReg*100.0/nrIntNacional) as percReg from ((select itc.regiaoId as regiaoId, sum(i.nrInternamentos) as nrIntReg from internamentos i natural left join instituicoes itc group by itc.regiaoId) as reg left join (select sum(i.nrInternamentos) as nrIntNacional from internamentos i) as nac) natural join regioes r group by regiaoId order by percReg desc;"
        }
    },
    "doencas": {
        "1": {
            "descricao": "Qual a média de dias de internamento por faixa etária, excluindo “gravidez, parto e puerpério”. Liste a faixa etária e a média de dias, ordenados por faixa etária.",
            "query": """
            Select p.faixaEtaria, avg(i.nrInternamentos) as media
            from internamentos i
            natural join pacientes p
            natural join grupoDiagnostico gd
            where gd.descricao not in ('Gravidez, parto e puerpério')
            group by p.faixaEtaria
            """
        },
        "2": {
            "descricao": "Quais foram as 10 doenças mais letais no país entre 2017 e 2019 (maior número de óbitos)?",
            "query": "select descricao from (select gd.descricao as descricao, sum(i.obitos) as obitosDoenca from internamentos i natural join grupodiagnostico gd group by i.codigoGD order by obitosDoenca desc) limit 10;"
        },
        "3": {
            "descricao": "Qual é a média de dias de internamento para as 5 doenças mais comuns?",
            "query": "select gd.descricao, avg(i.diasInternamentos) as mediaDiasInt from internamentos i natural left join grupodiagnostico gd where i.codigoGD in (select codigoGD from (select i.codigoGD as codigoGD, count(i.codigoGD) as nDoenca from internamentos i group by i.codigoGD order by nDoenca desc limit 5)) group by i.codigoGD;"
        },
        "4": {
            "descricao": "Qual é o total de óbitos para pacientes na faixa etária de 0 a 1 ano, por região? Liste o nome da região e o total de óbitos, ordenados por ordem decrescente de número de óbitos.",
            "query": "select r.regiao, sum(i.obitos) as obitosBebes from internamentos i natural join pacientes p natural join instituicoes itc natural left join regioes r where p.faixaEtaria='[0-1[' group by itc.regiaoId order by obitosBebes desc;"
        },
        "5": {
            "descricao": "Qual foi a distribuição percentual de internamentos por 'Doenças do aparelho circulatório' entre 2016 e 2020? Liste os anos e a distribuição percentual de cada um, por ordem dos anos.",
            "query": "select ano, (ano.intAno*100.0/t.totalAno) as mediaIntAno from ((select SUBSTR(i.periodo, 1, 4) as ano, sum(i.nrInternamentos) as intAno from internamentos i natural join grupodiagnostico gd where gd.descricao='Doenças do aparelho circulatório' group by SUBSTR(i.periodo, 1, 4)) as ano join (select sum(i.nrInternamentos) as totalAno from internamentos i natural join grupodiagnostico gd where gd.descricao='Doenças do aparelho circulatório') as t) order by ano;"
        },
        "6": {
            "descricao": "Qual foi a faixa etária com o maior número de óbitos para cada diagnóstico no país? Indique a descrição do diagnóstico e a faixa etária, ordenados pelo código do diagnóstico.",
            "query": "select gd.descricao, z.faixaEtaria from (select fe.codigoGD as codigoGD, fe.faixaEtaria as faixaEtaria, fe.obitos as n, m.max as m from ((select i.codigoGD as codigoGD, p.faixaEtaria as faixaEtaria, sum(i.obitos) as obitos from internamentos i natural left join pacientes p group by i.codigoGD, p.faixaEtaria order by i.codigoGD, obitos desc) as fe natural join (select codigoGD, max(obitos) as max from (select i.codigoGD as codigoGD, p.faixaEtaria, sum(i.obitos) as obitos from internamentos i natural left join pacientes p group by i.codigoGD, p.faixaEtaria order by i.codigoGD, obitos desc) group by codigoGD) as m) where n=m) as z natural left join grupodiagnostico gd;"
        },
        "7": {
            "descricao": "Quais foram as 5 doenças que apresentaram o maior aumento no número de episódios de ambulatório entre 2 anos consecutivos? Liste os anos, a doença e essa diferença.",
            "query": "select a.ano as ano1, b.ano as ano2, gd.descricao, b.epAmbulatorio-a.epAmbulatorio as aumento from (select CAST(SUBSTR(i.periodo, 1, 4) AS INTEGER) as ano, i.codigoGD as codigoGD, sum(i.ambulatorio) as epAmbulatorio from internamentos i group by i.codigoGD, SUBSTR(i.periodo, 1, 4)) as a join (select CAST(SUBSTR(i.periodo, 1, 4) AS INTEGER) as ano, i.codigoGD as codigoGD, sum(i.ambulatorio) as epAmbulatorio from internamentos i group by i.codigoGD, SUBSTR(i.periodo, 1, 4)) as b on a.codigoGD=b.codigoGD and a.ano = b.ano-1 natural join grupodiagnostico gd order by aumento desc limit 5;"
        },
        "8": {
            "descricao": "Quais são os hospitais com óbitos para todos os tipos de doença? Liste apenas os hospitais por ordem do nome da instituição.",
            "query": """
            SELECT DISTINCT i.instituicao
            FROM Instituicoes i
            WHERE i.instituicaoid NOT IN (
                SELECT i2.instituicaoid
                FROM Instituicoes i2
                JOIN GrupoDiagnostico gd ON 1=1
                WHERE gd.codigoGD NOT IN (
                    SELECT it.codigoGD
                    FROM Internamentos it
                    WHERE it.instituicaoid = i2.instituicaoid
                    AND it.obitos > 0
                )
            )
            """
        },
        "9": {
            "descricao": "Existe uma diferença significativa no número de internamentos e óbitos entre os géneros para cada tipo de doença em Portugal? Liste, para cada doença, a diferença no número de internamentos e a diferença no número de óbitos entre homens e mulheres (ignore género 'I'), indicando qual dos dois (Homem ou Mulher) é mais afetados em cada um dos parâmetros analisados.",
            "query": """""
                        select a.descricao, (b.nInt-a.nInt) as diferençaInternamentos, (b.nObitos-a.nObitos) as diferençaObitos,
                -- Verificar quem foi mais afetado nos internamentos
                CASE 
                    WHEN (b.nInt - a.nInt) < 0 THEN 'Mulher'
                    WHEN (b.nInt - a.nInt) > 0 THEN 'Homem'
                    ELSE 'Igual'
                END AS maisAfetadoInternamentos,

                -- Verificar quem foi mais afetado nos óbitos
                CASE 
                    WHEN (b.nObitos - a.nObitos) < 0 THEN 'Mulher'
                    WHEN (b.nObitos - a.nObitos) > 0 THEN 'Homem'
                    ELSE 'Igual'
                END AS maisAfetadoObitos
            from

            (select gd.descricao as descricao, p.genero as genero, sum(i.nrInternamentos) as nInt, sum(i.obitos) as nObitos
            from internamentos i
            natural left join grupodiagnostico gd
            natural left join pacientes p
            where p.genero in ('F', 'M')
            group by i.codigoGD, p.genero) as a

            join

            (select gd.descricao as descricao, p.genero as genero, sum(i.nrInternamentos) as nInt, sum(i.obitos) as nObitos
            from internamentos i
            natural left join grupodiagnostico gd
            natural left join pacientes p
            where p.genero in ('F', 'M')
            group by i.codigoGD, p.genero) as b

            on a.descricao=b.descricao and a.genero<b.genero
                    
            """
        }
    },
    "covid19": {
        "1": {
            "descricao": "Quantos óbitos, por região, foram registados em 2020 devido a 'Doenças do aparelho respiratório', podendo estar associadas a casos de COVID-19? Liste o nome da região e o número de óbitos, organizados por ordem decrescente pelo total de óbitos.",
            "query": """
                select r.regiao, sum(i.obitos) as obitosReg
                from internamentos i
                natural left join grupodiagnostico gd
                natural join instituicoes itc
                natural join regioes r
                where i.periodo like '2020%' and gd.descricao='Doenças do aparelho respiratório'
                group by itc.regiaoId
                order by obitosReg desc
            """
        },
        "2": {
            "descricao": "Qual foi o número de internamentos por mês ao longo de 2020? Liste o período (mês) e o total de internamentos, ordenados por ordem decrescente do número de internamentos.",
            "query": """
                select i.periodo, sum(i.nrInternamentos) as nIntMes
                from internamentos i
                where periodo like '2020%'
                group by i.periodo
            """
        },
        "3": {
            "descricao": "Quais foram as 10 instituições mais sobrecarregadas durante a pandemia de COVID-19? Liste as instituições, e respetivas regiões, com o maior número de casos de 'Doenças do aparelho respiratório' registadas a partir de março 2020, ordenadas a partir da que teve mais casos, para a que teve menos.",
            "query": """
                select r.regiao, itc.instituicao, sum(i.nrInternamentos) as nIntInst
                from internamentos i
                natural left join instituicoes itc
                natural left join regioes r
                where periodo like '2020%' and periodo not like '2020-01' and periodo not like '2020-02'
                group by i.instituicaoId
                order by nIntInst desc
                limit 10;
            """
        },
        "4": {
            "descricao": "Qual foi a faixa etária e género mais afetados em 2020 pelo maior número de internamentos devido a 'Doenças do aparelho respiratório'?",
            "query": """
                select fe.faixaEtaria, g.genero
                from

                (select p.faixaEtaria, sum(i.nrInternamentos) as nIntFE
                from internamentos i
                natural left join grupodiagnostico gd
                natural join pacientes p
                where gd.descricao='Doenças do aparelho respiratório'
                group by p.faixaEtaria
                order by nIntFE desc
                limit 1) as fe

                join

                (select p.genero, sum(i.nrInternamentos) as nIntG
                from internamentos i
                natural left join grupodiagnostico gd
                natural left join pacientes p
                where gd.descricao='Doenças do aparelho respiratório'
                group by p.genero
                order by nIntG desc
                limit 1
                ) as g
            """
        },
        "5": {
            "descricao": "Compare a média anual de internamentos por 'Doenças do aparelho respiratório', entre março e novembro de 2016 a 2019, com o total de internamentos para as mesmas doenças no período de março a novembro de 2020 (pico da pandemia de COVID-19). Apresente uma coluna adicional chamada 'diferença', que mostre a diferença entre o total de 2020 e a média dos anos anteriores.",
            "query": """
                    select semCovid.mediaIntAnoSC, comCovid.mediaIntAnoCC
                    from

                    (select (sum(i.nrInternamentos)/4) as mediaIntAnoSC
                    from internamentos i
                    natural left join grupodiagnostico gd
                    where gd.descricao='Doenças do aparelho respiratório'
                        and i.periodo not like '2020%' and i.periodo not like '%01' 
                        and i.periodo not like '%02' and i.periodo not like '%12') as semCovid
                        
                    join

                    (select sum(i.nrInternamentos) as mediaIntAnoCC
                    from internamentos i
                    natural left join grupodiagnostico gd
                    where gd.descricao='Doenças do aparelho respiratório'
                        and i.periodo like '2020%' and i.periodo not like '%01' 
                        and i.periodo not like '%02' and i.periodo not like '%12') as comCovid
            """
        },
        "6": {
            "descricao": "Como variaram os óbitos por 'Doenças do aparelho respiratório' em 2020 em comparação com 2019, mês a mês, entre março e novembro? Liste os meses (nome e não número) e os correspondentes número de óbitos, em cada ano, ordenados pelo período.",
            "query": """
                select  CASE 
                        SUBSTR(semCovid.periodo, 6, 2)
                        WHEN '03' THEN 'Março'
                        WHEN '04' THEN 'Abril'
                        WHEN '05' THEN 'Maio'
                        WHEN '06' THEN 'Junho'
                        WHEN '07' THEN 'Julho'
                        WHEN '08' THEN 'Agosto'
                        WHEN '09' THEN 'Setembro'
                        WHEN '10' THEN 'Outubro'
                        WHEN '11' THEN 'Novembro'
                    END AS mês,

                    semCovid.obitos2019, comCovid.obitos2020
                from

                (select i.periodo as periodo, (sum(i.obitos)) as obitos2019
                from internamentos i
                natural left join grupodiagnostico gd
                where gd.descricao='Doenças do aparelho respiratório'
                     and i.periodo like '2019%' and i.periodo not like '%01' 
                     and i.periodo not like '%02' and i.periodo not like '%12'
                group by i.periodo) as semCovid

                left join

                (select i.periodo as periodo, sum(i.obitos) as obitos2020
                from internamentos i
                natural left join grupodiagnostico gd
                where gd.descricao='Doenças do aparelho respiratório'
                     and i.periodo like '2020%' and i.periodo not like '%01' 
                     and i.periodo not like '%02' and i.periodo not like '%12'
                group by i.periodo) as comCovid

                ON SUBSTR(semCovid.periodo, 6, 2) = SUBSTR(comCovid.periodo, 6, 2);
            """
        }
    }
}

    descriptions = {key: query["descricao"] for key, query in queries[tipo].items()}

    return render_template("query_page.html", tipo=tipo, queries=descriptions)



@app.route('/executar/<tipo>/<query_id>')
def executar(tipo, query_id):
    query_info = all_queries[tipo][query_id]
    query = query_info["query"]

    conn = sqlite3.connect("morbilidade.db")
    cursor = conn.cursor()
    cursor.execute(query)
    colunas = [desc[0] for desc in cursor.description]
    dados = cursor.fetchall()

    return render_template('resultado.html', colunas=colunas, dados=dados)

all_queries = {
    "regiao": {
        "1": {
            "query": "select i.instituicao from instituicoes i natural left join regioes r where r.regiao='Região de Saúde do Norte' order by i.instituicao;",
            "descricao": "Quais as instituições localizadas na Região de Saúde do Norte? Liste-as por ordem alfabética do nome da instituição."
        },
        "2": {
            "query": "select r.regiao, sum(i.obitos) as obitosReg from internamentos i natural join instituicoes itc natural join regioes r group by itc.regiaoId order by obitosReg limit 3;",
            "descricao": "Quais são as três regiões com o menor número de óbitos? Indique apenas o nome das regiões."
        },
        "3": {
            "query": "select regiao, descricao from (select regiao, descricao, max(num) as max from (select r.regiao as regiao, gd.descricao as descricao, count(gd.codigoGD) as num from internamentos i natural join instituicoes itc natural join regioes r natural join grupodiagnostico gd where i.periodo like '%2017%' or i.periodo like '%2018%'or i.periodo like '%2019%' group by r.regiaoId, gd.codigoGD) group by regiao order by regiao, num desc) order by regiao;",
            "descricao": "Quais são os diagnósticos mais comuns por região de saúde, entre 2017 e 2019? Liste a descrição do diagnóstico (GrupoDiagnóstico) e a respetiva região, organizados por ordem alfabética pelo nome da região."
        },
        "4": {
            "query": "select r.regiaoId, r.regiao, count(i.instituicaoId) as nInstituicoes from instituicoes i natural left join regioes r group by r.regiaoId having nInstituicoes >= (select avg(nInstituicao*1.0/nRegiao) as PseudoMedia from (select count(distinct i.instituicaoId) as nInstituicao, count(distinct i.regiaoId) as nRegiao from instituicoes i)) order by r.regiaoId desc;",
            "descricao": "Quais são as regiões (regiao e regiaoID) onde o número de instituições é igual ou superior à média nacional de instituições por região? Liste as regiões, juntamente com o número de instituições em cada uma, ordenadas da região com mais instituições para a que tem menos."
        },
        "5": {
            "query": "select r.regiao, (nrIntReg*100.0/nrIntNacional) as percReg from ((select itc.regiaoId as regiaoId, sum(i.nrInternamentos) as nrIntReg from internamentos i natural left join instituicoes itc group by itc.regiaoId) as reg left join (select sum(i.nrInternamentos) as nrIntNacional from internamentos i) as nac) natural join regioes r group by regiaoId order by percReg desc;",
            "descricao": "Qual é a distribuição percentual de internamentos por região em relação ao total nacional? Liste a região e a distribuição percentual, por ordem decrescente desta."
        }
    },
    "doencas": {
        "1": {
            "query": """
            Select p.faixaEtaria, avg(i.nrInternamentos) as media
            from internamentos i
            natural join pacientes p
            natural join grupoDiagnostico gd
            where gd.descricao not in ('Gravidez, parto e puerpério')
            group by p.faixaEtaria
            """,
            "descricao": "Qual a média de dias de internamento por faixa etária, excluindo “gravidez, parto e puerpério”. Liste a faixa etária e a média de dias, ordenados por faixa etária."
        },
        "2": {
            "query": "select descricao from (select gd.descricao as descricao, sum(i.obitos) as obitosDoenca from internamentos i natural join grupodiagnostico gd group by i.codigoGD order by obitosDoenca desc) limit 10;",
            "descricao": "Quais foram as 5 doenças mais letais no país entre 2017 e 2019 (maior número de óbitos)?"
        },
        "3": {
            "query": "select gd.descricao, avg(i.diasInternamentos) as mediaDiasInt from internamentos i natural left join grupodiagnostico gd where i.codigoGD in (select codigoGD from (select i.codigoGD as codigoGD, count(i.codigoGD) as nDoenca from internamentos i group by i.codigoGD order by nDoenca desc limit 5)) group by i.codigoGD;",
            "descricao": "Qual é a média de dias de internamento para as 5 doenças mais comuns?"
        },
        "4": {
            "query": "select r.regiao, sum(i.obitos) as obitosBebes from internamentos i natural join pacientes p natural join instituicoes itc natural left join regioes r where p.faixaEtaria='[0-1[' group by itc.regiaoId order by obitosBebes desc;",
            "descricao": "Qual é o total de óbitos para pacientes na faixa etária de 0 a 1 ano, por região? Liste o nome da região e o total de óbitos, ordenados por ordem decrescente de número de óbitos."
        },
        "5": {
            "query": "select ano, (ano.intAno*100.0/t.totalAno) as mediaIntAno from ((select SUBSTR(i.periodo, 1, 4) as ano, sum(i.nrInternamentos) as intAno from internamentos i natural join grupodiagnostico gd where gd.descricao='Doenças do aparelho circulatório' group by SUBSTR(i.periodo, 1, 4)) as ano join (select sum(i.nrInternamentos) as totalAno from internamentos i natural join grupodiagnostico gd where gd.descricao='Doenças do aparelho circulatório') as t) order by ano;",
            "descricao": "Qual foi a evolução do número de internamentos por Doenças do aparelho circulatório ao longo dos últimos 10 anos?"
        },
        "6": {
            "query": "select gd.descricao, z.faixaEtaria from (select fe.codigoGD as codigoGD, fe.faixaEtaria as faixaEtaria, fe.obitos as n, m.max as m from ((select i.codigoGD as codigoGD, p.faixaEtaria as faixaEtaria, sum(i.obitos) as obitos from internamentos i natural left join pacientes p group by i.codigoGD, p.faixaEtaria order by i.codigoGD, obitos desc) as fe natural join (select codigoGD, max(obitos) as max from (select i.codigoGD as codigoGD, p.faixaEtaria, sum(i.obitos) as obitos from internamentos i natural left join pacientes p group by i.codigoGD, p.faixaEtaria order by i.codigoGD, obitos desc) group by codigoGD) as m) where n=m) as z natural left join grupodiagnostico gd;",
            "descricao": "Qual foi a faixa etária com o maior número de óbitos para cada diagnóstico no país? Indique a descrição do diagnóstico e a faixa etária, ordenados pelo código do diagnóstico."
        },
        "7": {
            "query": "select a.ano as ano1, b.ano as ano2, gd.descricao, b.epAmbulatorio-a.epAmbulatorio as aumento from (select CAST(SUBSTR(i.periodo, 1, 4) AS INTEGER) as ano, i.codigoGD as codigoGD, sum(i.ambulatorio) as epAmbulatorio from internamentos i group by i.codigoGD, SUBSTR(i.periodo, 1, 4)) as a join (select CAST(SUBSTR(i.periodo, 1, 4) AS INTEGER) as ano, i.codigoGD as codigoGD, sum(i.ambulatorio) as epAmbulatorio from internamentos i group by i.codigoGD, SUBSTR(i.periodo, 1, 4)) as b on a.codigoGD=b.codigoGD and a.ano = b.ano-1 natural join grupodiagnostico gd order by aumento desc limit 5;",
            "descricao": "Qual foi a doença(s) que apresentou o maior aumento no número de episódios de ambulatório ao longo dos anos?"
        },
        "8": {
            "descricao": "Quais são os hospitais com óbitos para todos os tipos de doença? Liste apenas os hospitais por ordem do nome da instituição.",
            "query": """
            SELECT DISTINCT i.instituicao
            FROM Instituicoes i
            WHERE i.instituicaoid NOT IN (
                SELECT i2.instituicaoid
                FROM Instituicoes i2
                JOIN GrupoDiagnostico gd ON 1=1
                WHERE gd.codigoGD NOT IN (
                    SELECT it.codigoGD
                    FROM Internamentos it
                    WHERE it.instituicaoid = i2.instituicaoid
                    AND it.obitos > 0
                )
            )
            """
        },
        "9": {
            "query": """
                            select a.descricao, (b.nInt-a.nInt) as diferençaInternamentos, (b.nObitos-a.nObitos) as diferençaObitos,
                -- Verificar quem foi mais afetado nos internamentos
                CASE 
                    WHEN (b.nInt - a.nInt) < 0 THEN 'Mulher'
                    WHEN (b.nInt - a.nInt) > 0 THEN 'Homem'
                    ELSE 'Igual'
                END AS maisAfetadoInternamentos,

                -- Verificar quem foi mais afetado nos óbitos
                CASE 
                    WHEN (b.nObitos - a.nObitos) < 0 THEN 'Mulher'
                    WHEN (b.nObitos - a.nObitos) > 0 THEN 'Homem'
                    ELSE 'Igual'
                END AS maisAfetadoObitos
            from

            (select gd.descricao as descricao, p.genero as genero, sum(i.nrInternamentos) as nInt, sum(i.obitos) as nObitos
            from internamentos i
            natural left join grupodiagnostico gd
            natural left join pacientes p
            where p.genero in ('F', 'M')
            group by i.codigoGD, p.genero) as a

            join

            (select gd.descricao as descricao, p.genero as genero, sum(i.nrInternamentos) as nInt, sum(i.obitos) as nObitos
            from internamentos i
            natural left join grupodiagnostico gd
            natural left join pacientes p
            where p.genero in ('F', 'M')
            group by i.codigoGD, p.genero) as b

            on a.descricao=b.descricao and a.genero<b.genero
                """
            ,
            "descricao": "Existe uma diferença significativa no número de internamentos e óbitos entre os géneros para cada tipo de doença em Portugal? Liste, para cada doença, a diferença no número de internamentos e a diferença no número de óbitos entre homens e mulheres (ignore género 'I'), indicando qual dos dois (Homem ou Mulher) é mais afetados em cada um dos parâmetros analisados."
        }
    },
    "covid19": {
        "1": {
            "query": "select r.regiao, sum(i.obitos) as obitosReg from internamentos i natural left join grupodiagnostico gd natural join instituicoes itc natural join regioes r where i.periodo like '2020%' and gd.descricao='Doenças do aparelho respiratório' group by itc.regiaoId order by obitosReg desc;",
            "descricao": "Quantos óbitos, por região, foram registados em 2020 devido a 'Doenças do aparelho respiratório', podendo estar associadas a casos de COVID-19? Liste o nome da região e o número de óbitos, organizados por ordem decrescente pelo total de óbitos."
        },
        "2": {
            "query": "select i.periodo, sum(i.nrInternamentos) as nIntMes from internamentos i where periodo like '2020%' group by i.periodo;",
            "descricao": "Qual foi o número de internamentos por mês ao longo de 2020? Liste o período (mês) e o total de internamentos, ordenados por ordem decrescente do número de internamentos."
        },
        "3": {
            "query": "select r.regiao, itc.instituicao, sum(i.nrInternamentos) as nIntInst from internamentos i natural left join instituicoes itc natural left join regioes r where periodo like '2020%' and periodo not like '2020-01' and periodo not like '2020-02' group by i.instituicaoId order by nIntInst desc limit 10;",
            "descricao": "Quais foram as 10 instituições mais sobrecarregadas durante a pandemia de COVID-19? Liste as instituições, e respetivas regiões, com o maior número de casos de 'Doenças do aparelho respiratório' registadas a partir de março 2020, ordenadas a partir da que teve mais casos, para a que teve menos."
        },
        "4": {
            "query": """
                select fe.faixaEtaria, g.genero
                from

                (select p.faixaEtaria, sum(i.nrInternamentos) as nIntFE
                from internamentos i
                natural left join grupodiagnostico gd
                natural join pacientes p
                where gd.descricao='Doenças do aparelho respiratório'
                group by p.faixaEtaria
                order by nIntFE desc
                limit 1) as fe

                join

                (select p.genero, sum(i.nrInternamentos) as nIntG
                from internamentos i
                natural left join grupodiagnostico gd
                natural left join pacientes p
                where gd.descricao='Doenças do aparelho respiratório'
                group by p.genero
                order by nIntG desc
                limit 1
                ) as g
            """,
            "descricao": "Qual foi a faixa etária e género mais afetados em 2020 pelo maior número de internamentos devido a 'Doenças do aparelho respiratório'?"
        },
        "5": {
            "query":  """
                select semCovid.mediaIntAnoSC, comCovid.mediaIntAnoCC
                from

                (select (sum(i.nrInternamentos)/4) as mediaIntAnoSC
                from internamentos i
                natural left join grupodiagnostico gd
                where gd.descricao='Doenças do aparelho respiratório'
                    and i.periodo not like '2020%' and i.periodo not like '%01' 
                    and i.periodo not like '%02' and i.periodo not like '%12') as semCovid
                    
                join

                (select sum(i.nrInternamentos) as mediaIntAnoCC
                from internamentos i
                natural left join grupodiagnostico gd
                where gd.descricao='Doenças do aparelho respiratório'
                    and i.periodo like '2020%' and i.periodo not like '%01' 
                    and i.periodo not like '%02' and i.periodo not like '%12') as comCovid
            """,
            "descricao": "Compare a média anual de internamentos por 'Doenças do aparelho respiratório', entre março e novembro de 2016 a 2019, com o total  de internamentos para as mesmas doenças no período de março a novembro de 2020 (pico da pandemia de COVID-19). Apresente uma coluna adicional chamada 'diferença', que mostre a diferença entre o total de 2020 e a média dos anos anteriores."
        },
        "6": {
            "query": """
                select  CASE 
                        SUBSTR(semCovid.periodo, 6, 2)
                        WHEN '03' THEN 'Março'
                        WHEN '04' THEN 'Abril'
                        WHEN '05' THEN 'Maio'
                        WHEN '06' THEN 'Junho'
                        WHEN '07' THEN 'Julho'
                        WHEN '08' THEN 'Agosto'
                        WHEN '09' THEN 'Setembro'
                        WHEN '10' THEN 'Outubro'
                        WHEN '11' THEN 'Novembro'
                    END AS mês,

                    semCovid.obitos2019, comCovid.obitos2020
                from

                (select i.periodo as periodo, (sum(i.obitos)) as obitos2019
                from internamentos i
                natural left join grupodiagnostico gd
                where gd.descricao='Doenças do aparelho respiratório'
                     and i.periodo like '2019%' and i.periodo not like '%01' 
                     and i.periodo not like '%02' and i.periodo not like '%12'
                group by i.periodo) as semCovid

                left join

                (select i.periodo as periodo, sum(i.obitos) as obitos2020
                from internamentos i
                natural left join grupodiagnostico gd
                where gd.descricao='Doenças do aparelho respiratório'
                     and i.periodo like '2020%' and i.periodo not like '%01' 
                     and i.periodo not like '%02' and i.periodo not like '%12'
                group by i.periodo) as comCovid

                ON SUBSTR(semCovid.periodo, 6, 2) = SUBSTR(comCovid.periodo, 6, 2);
            """,
            "descricao": "Como variaram os óbitos por 'Doenças do aparelho respiratório' em 2020 em comparação com 2019, mês a mês, entre março e novembro? Liste os meses (nome e não número) e os correspondentes número de óbitos, em cada ano, ordenados pelo período."
        }
    }
}

DB_PATH = "morbilidade.db"

@app.route("/navegar_tabelas", methods=["GET", "POST"])
def navegar_tabelas():
    resultado = None
    tabela_selecionada = None
    id_selecionado = None
    erro = None

    if request.method == "POST":
        tabela_selecionada = request.form.get("tabela")
        id_selecionado = request.form.get("id")

        if not id_selecionado:
            erro = "Por favor, insira um ID válido."
        else:
            try:
                id_selecionado = int(id_selecionado)

                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()

                    tabelas_config = {
                        "regioes": {"chave": "regiaoID", "caracteristica": "regiao"},
                        "instituicoes": {"chave": "instituicaoID", "caracteristica": "instituicao"},
                        "grupodiagnostico": {"chave": "codigoGD", "caracteristica": "descricao"},
                        "pacientes": {"chave": "pacienteID", "caracteristica": ["faixaEtaria", "genero"]},
                    }

                    if tabela_selecionada in tabelas_config:
                        config = tabelas_config[tabela_selecionada]
                        chave = config["chave"]
                        coluna = config["caracteristica"]

                        if isinstance(coluna, list):
                            colunas_str = ", ".join(coluna)
                            query = f"SELECT {colunas_str} FROM {tabela_selecionada} WHERE {chave} = ?"
                        else:
                            query = f"SELECT {coluna} FROM {tabela_selecionada} WHERE {chave} = ?"

                        cursor.execute(query, (id_selecionado,))
                        resultado = cursor.fetchone()

                        if resultado:
                            if isinstance(coluna, list):
                                resultado_dict = dict(zip(coluna, resultado))
                                resultado = f"Faixa Etária: {resultado_dict['faixaEtaria']}, Gênero: {resultado_dict['genero']}"
                            else:
                                resultado = resultado[0]
                        else:
                            erro = f"ID {id_selecionado} não encontrado na tabela {tabela_selecionada}."
                    else:
                        erro = "Tabela inválida selecionada."
            except sqlite3.Error as e:
                erro = f"Erro ao acessar o banco de dados: {e}"
            except ValueError:
                erro = "Por favor, insira um ID numérico válido."

    return render_template(
        "navegar_tabelas.html",
        resultado=resultado,
        tabela_selecionada=tabela_selecionada,
        id_selecionado=id_selecionado,
        erro=erro,
    )



if __name__ == "__main__":
    app.run(debug=True)
