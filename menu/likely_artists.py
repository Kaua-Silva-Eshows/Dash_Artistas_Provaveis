from datetime import date, datetime, timedelta
import streamlit as st
from data.querys_eshows import *
from menu.page import Page
from utils.components import *
from utils.functions import *

def BuildLikelyArtists(rankliKelyArtists):

    row = st.columns(6)
    global day, day2

    with row[2]:
        day = st.date_input('Data Inicio:',value=date.today(),format='DD/MM/YYYY',key='day')
    
    with row[3]:
        day2 = st.date_input('Data Fim:',value=date.today(),format='DD/MM/YYYY',key='day2')
    
    rankliKelyArtists = rank_likely_artists(day, day2, filters='', id_group='')

    if day2 < day:        
        st.warning("Data Inicio deve ser menor que Data Fim")
    
    elif rankliKelyArtists.empty:
        st.warning("Nenhuma Oportunidade Encontrada")
    
    else:
        
        row1 = st.columns(3)
        with row1[1]:
            opportunity = len(rankliKelyArtists['ID_OPORTUNIDADE'].unique())
            tile = row1[1].container(border=True)
            tile.write(f"""<p style='text-align: center; font-size: 15px;'>Oportunidades em Aberto<br><span style='font-size: 17px;'>{opportunity}</span></p>""",unsafe_allow_html=True)

            companie = st.selectbox ("Estabelecimento", rankliKelyArtists['Estabelecimento'].unique())
        rankliKelyArtists = rankliKelyArtists[rankliKelyArtists['Estabelecimento'] == companie]
        id_group = rankliKelyArtists['ID GRUPO'].unique()
        id_companie = rankliKelyArtists['ID Estabelecimento'].unique()
        filters = f"AND O.FK_CONTRATANTE = '{id_companie[0]}'"

        if rankliKelyArtists['ID GRUPO'].isnull().any():
            rankliKelyArtists = rank_likely_artists(day, day2, filters)

        else:
            rankliKelyArtists = rank_likely_artists(day, day2, filters, id_group[0])
        
        rankliKelyArtists = rankliKelyArtists.drop(columns=['ID Estabelecimento', 'Estabelecimento', 'ID GRUPO', 'RN', 'PONTUACAO'])

        if len(rankliKelyArtists) > 0:
            filtered_copy, count = component_plotDataframe(rankliKelyArtists, 'Artistas Mais Provaveis')
            function_box_lenDf(count, rankliKelyArtists, y=0, x=540, box_id='box1', item='Artistas')
            function_copy_dataframe_as_tsv(filtered_copy)
        
        else:
            st.error("Nenhuma Oportunidade Encontrada")

        st.markdown("---")

class LikelyArtists(Page):
    def render(self):
        self.data = {}
        day = date.today() 
        day2 = date.today()
        self.data['rankliKelyArtists'] = rank_likely_artists(day, day2, filters='', id_group='')
        
        BuildLikelyArtists(self.data['rankliKelyArtists'])