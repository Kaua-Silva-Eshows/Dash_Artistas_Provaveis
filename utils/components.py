import streamlit as st
from st_aggrid import GridUpdateMode
from st_aggrid import AgGrid, GridOptionsBuilder

def component_hide_sidebar():
    st.markdown(""" 
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
                }
    </style>
    """, unsafe_allow_html=True)

def component_fix_tab_echarts():
    streamlit_style = """
    <style>
    iframe[title="streamlit_echarts.st_echarts"]{ height: 450px; width: 750px;} 
   </style>
    """

    return st.markdown(streamlit_style, unsafe_allow_html=True)

def component_effect_underline():
    st.markdown("""
    <style>
        .full-width-line-white {
            width: 100%;
            border-bottom: 1px solid #ffffff;
            margin-bottom: 0.5em;
        }
        .full-width-line-black {
            width: 100%;
            border-bottom: 1px solid #000000;
            margin-bottom: 0.5em;
        }
    </style>
    """, unsafe_allow_html=True)

def component_plotDataframe(df, name):
    st.markdown(f"<h5 style='text-align: center; background-color: #ffb131; padding: 0.1em;'>{name}</h5>", unsafe_allow_html=True)
    keywords = ['VER DETALHES', 'VER CANDIDATOS', 'DISPARAR WPP', 'PERFIL ARTISTA']  # usado para procurar colunas que contenham links
    columns_with_link = [col_name for col_name in df.columns if any(keyword in col_name.upper() for keyword in keywords)]
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True)  # Habilitar filtro para todas as colunas
    
    # Configurar a seleção de linhas (opcional)
    gb.configure_selection(
        selection_mode='multiple',  # 'single' ou 'multiple'
        use_checkbox=False,         # Habilitar caixas de seleção
        pre_selected_rows=[],
        suppressRowClickSelection=False  # Permite selecionar ao clicar em qualquer célula
    )
    
    grid_options = gb.build()

    # Adicionar configurações adicionais para seleção de células
    grid_options.update({
        "enableRangeSelection": True,
        "suppressRowClickSelection": True,
        "cellSelection": True,
        "defaultColDef": {
            "flex": 1,
            "minWidth": 100,
            "autoHeight": True,
            "filter": True  # Habilitar filtro para cada coluna
        }
    })

    # Exibir o DataFrame usando AgGrid com filtros
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,  # Ajusta as colunas automaticamente ao carregar
        key=f"aggrid_{name}"
        
    )

    # Recupera o DataFrame filtrado
    filtered_df = grid_response['data']

    return filtered_df, len(filtered_df)