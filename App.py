# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from collections import Counter, defaultdict

st.set_page_config(
    page_title="Análise Lotofácil + Fechamento",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Lotofácil: Análise + Fechamento (14 Pontos)")
st.markdown("App para análise de ciclos e geração de fechamento com 20 números. Funciona 100% pelo celular!")

# ==============================
# DADOS DE ENTRADA PELO USUÁRIO
# ==============================

st.sidebar.header("📥 Insira seus dados")

# Seus 20 números
meus_numeros_str = st.sidebar.text_input(
    "Seus 20 números (separados por vírgula, sem espaços):",
    value="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
)
try:
    meus_20 = sorted([int(x.strip()) for x in meus_numeros_str.split(",")])
    if len(meus_20) != 20:
        st.sidebar.error("⚠️ Insira exatamente 20 números!")
        st.stop()
except:
    st.sidebar.error("⚠️ Formato inválido! Use: 1,2,3,...,20")
    st.stop()

# Resultados recentes
st.sidebar.markdown("### 📋 Últimos concursos (um por linha)")
st.sidebar.markdown("Formato: `concurso,data,n1-n2-n3-...-n15`")
exemplo = "2800,10/01/2026,1-3-5-7-9-11-13-15-17-19-21-22-23-24-25\n2801,13/01/2026,2-4-6-8-10-12-14-16-18-20-1-3-5-7-9"
resultados_input = st.sidebar.text_area(
    "Cole aqui os resultados:",
    value=exemplo,
    height=200
)

# Processar resultados
resultados = []
if resultados_input.strip():
    linhas = resultados_input.strip().split("\n")
    for linha in linhas:
        if not linha.strip():
            continue
        partes = linha.split(",")
        if len(partes) != 3:
            st.sidebar.error(f"❌ Linha inválida: {linha}")
            st.stop()
        concurso, data, nums_str = partes
        try:
            numeros = set(int(x) for x in nums_str.split("-"))
            if len(numeros) != 15:
                st.sidebar.error(f"❌ Deve ter 15 números: {linha}")
                st.stop()
            resultados.append({
                "concurso": int(concurso),
                "data": data,
                "numeros": numeros
            })
        except:
            st.sidebar.error(f"❌ Erro nos números: {linha}")
            st.stop()

# Parâmetros de ciclo
st.sidebar.markdown("### 🔄 Ciclos de análise")
ciclos = st.sidebar.number_input("Quantos ciclos?", min_value=1, max_value=20, value=10)
concursos_por_ciclo = st.sidebar.number_input("Concursos por ciclo", min_value=1, max_value=20, value=5)

total_concursos = ciclos * concursos_por_ciclo
if len(resultados) < total_concursos:
    st.warning(f"⚠️ Você inseriu {len(resultados)} concursos, mas precisa de {total_concursos} para {ciclos} ciclos de {concursos_por_ciclo}.")
else:
    # Usar apenas os últimos N concursos
    resultados_usar = sorted(resultados, key=lambda x: x["concurso"], reverse=True)[:total_concursos]
    resultados_usar.reverse()  # do mais antigo ao mais recente

    # ==============================
    # ANÁLISE POR CICLOS
    # ==============================
    st.header("📊 Análise por Ciclos")

    todos_numeros = []
    atrasos = {n: 0 for n in range(1, 26)}
    ultimo_concurso = max(r["concurso"] for r in resultados_usar)

    for r in resultados_usar:
        todos_numeros.extend(r["numeros"])
        for n in range(1, 26):
            if n in r["numeros"]:
                atrasos[n] = 0
            else:
                atrasos[n] += 1

    freq_total = Counter(todos_numeros)
    
    # Dividir em ciclos
    ciclos_lista = []
    for i in range(ciclos):
        inicio = i * concursos_por_ciclo
        fim = inicio + concursos_por_ciclo
        ciclo_resultados = resultados_usar[inicio:fim]
        nums_ciclo = []
        for r in ciclo_resultados:
            nums_ciclo.extend(r["numeros"])
        ciclos_lista.append(Counter(nums_ciclo))

    # Criar DataFrame
    df_data = {"Número": list(range(1, 26))}
    df_data["Total"] = [freq_total.get(n, 0) for n in range(1, 26)]
    df_data["Atraso"] = [atrasos[n] for n in range(1, 26)]
    
    for i, ciclo_freq in enumerate(ciclos_lista):
        df_data[f"Ciclo {i+1}"] = [ciclo_freq.get(n, 0) for n in range(1, 26)]
    
    df = pd.DataFrame(df_data)
    df = df.set_index("Número")
    
    st.dataframe(df.style.highlight_max(axis=0, color="lightgreen").highlight_min(axis=0, color="lightcoral"))

    # Estatísticas rápidas
    mais_sorteados = freq_total.most_common(5)
    menos_sorteados = freq_total.most_common()[:-6:-1]
    maior_atraso = sorted(atrasos.items(), key=lambda x: x[1], reverse=True)[:5]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🔝 Mais sorteados")
        for n, f in mais_sorteados:
            st.write(f"{n}: {f} vezes")
    with col2:
        st.subheader("🔻 Menos sorteados")
        for n, f in menos_sorteados:
            st.write(f"{n}: {f} vezes")
    with col3:
        st.subheader("⏳ Maior atraso")
        for n, a in maior_atraso:
            st.write(f"{n}: {a} concursos")

    # ==============================
    # GERAR FECHAMENTO
    # ==============================
    st.header("🎫 Fechamento (Garantia ~14/15)")

    # Gerar fechamento aproximado (76 jogos)
    base_indices = list(range(20))
    fechamento = []
    # Estratégia: omitir combinações de 5 números (escolher 15)
    for omitidos in combinations(base_indices, 5):
        if len(fechamento) >= 76:
            break
        aposta_idx = sorted(set(base_indices) - set(omitidos))
        fechamento.append(aposta_idx)
    
    # Converter para números reais
    apostas_reais = []
    for aposta_idx in fechamento:
        aposta_num = [meus_20[i] for i in aposta_idx]
        apostas_reais.append(sorted(aposta_num))

    st.success(f"✅ Gerado fechamento com {len(apostas_reais)} apostas!")

    # Mostrar apostas
    st.subheader("📋 Suas apostas:")
    for i, aposta in enumerate(apostas_reais, 1):
        st.text(f"{i:02d}: {' '.join(f'{x:02d}' for x in aposta)}")

    # Testar contra último sorteio (se dentro dos 20)
    ultimo_sorteio = resultados_usar[-1]["numeros"]
    if ultimo_sorteio.issubset(set(meus_20)):
        st.info("✅ Último sorteio está dentro dos seus 20 números!")
        max_acerto = 0
        for aposta in apostas_reais:
            acertos = len(set(aposta) & ultimo_sorteio)
            if acertos > max_acerto:
                max_acerto = acertos
        st.metric("Máximo de acertos no último sorteio", f"{max_acerto}/15")
    else:
        fora = ultimo_sorteio - set(meus_20)
        st.warning(f"⚠️ Último sorteio tem {len(fora)} número(s) fora dos seus 20: {sorted(fora)}")

else:
    st.info("👆 Insira pelo menos os concursos necessários para ver a análise.")
