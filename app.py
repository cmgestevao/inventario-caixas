import streamlit as st
import pandas as pd
import os

# Configuração da página ideal para telemóvel e PC
st.set_page_config(page_title="Inventário caixas", page_icon="📦", layout="centered")

st.title("📦 Inventário")
st.write("Consultar e pesquisar os materiais em tempo real.")

# Nome exato do ficheiro Excel guardado no vosso GitHub
FICHEIRO_LOCAL = "inventario_caixas_organizacao.xlsx"

# Função de leitura local rápida e sem intermediários de rede
@st.cache_data(ttl=5)  # Atualiza a cache rapidamente
def carregar_dados_locais():
    try:
        if not os.path.exists(FICHEIRO_LOCAL):
            st.error(f"⚠️ O ficheiro '{FICHEIRO_LOCAL}' não foi encontrado no GitHub. Por favor, faça o upload do ficheiro com este nome exato.")
            return pd.DataFrame()
            
        # Lemos o Excel local usando o motor openpyxl (que está nos requisitos)
        df_excel = pd.read_excel(FICHEIRO_LOCAL, sheet_name=0, engine="openpyxl")
        
        # Limpar colunas fantasma (Unnamed) criadas pelo Excel
        df_excel = df_excel.loc[:, ~df_excel.columns.str.contains('^Unnamed', case=False, na=False)]
        
        # Deitar fora as linhas vazias do modelo do Excel
        return df_excel.dropna(how="all")
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro Excel: {e}")
        return pd.DataFrame()

df = carregar_dados_locais()

if df.empty:
    st.stop()

# Garantir que removemos linhas em branco se existirem no fim do modelo
if 'Item' in df.columns:
    df = df.dropna(subset=['Item'])
    df = df[df['Item'].astype(str).str.strip() != '']

opcao = st.radio("Menu de Ações:", ["🔍 Pesquisar Itens"], horizontal=True)

if opcao == "🔍 Pesquisar Itens":
    st.subheader("Procurar no Stock")
    search_query = st.text_input("Escrever o nome do item ou categoria:", "").strip()
    
    # Tratamento da coluna 'Caixa'
    if 'Caixa' in df.columns:
        df['Caixa'] = df['Caixa'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
        caixas_disponiveis = ["Todas"] + sorted(list(df['Caixa'].dropna().unique()), key=lambda x: float(x) if str(x).replace('.','',1).isdigit() else 0)
        caixa_selecionada = st.selectbox("Filtrar por Nº da Caixa:", caixas_disponiveis)
    else:
        caixa_selecionada = "Todas"
        
    df_filtrado = df.copy()
    
    if search_query:
        mascara = df_filtrado.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        df_filtrado = df_filtrado[mascara]
        
    if caixa_selecionada != "Todas" and 'Caixa' in df.columns:
        df_filtrado = df_filtrado[df_filtrado['Caixa'] == caixa_selecionada]
        
    st.metric(label="Itens Ativos no Stock", value=len(df_filtrado))
    
    # Mostrar a tabela com o alinhamento central nas 3 primeiras colunas
    st.dataframe(
        df_filtrado, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Caixa": st.column_config.Column(alignment="center"),
            "Vert": st.column_config.Column(alignment="center"),
            "Horiz": st.column_config.Column(alignment="center")
        }
    )
