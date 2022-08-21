from email.policy import default
import imp
#from msilib import schema
from socket import inet_aton
from tokenize import group
from turtle import color, down, width
import matplotlib
#from matplotlib.cbook import safe_masked_invalid
#from matplotlib.pyplot import title
#from matplotlib.style import use
from requests import head
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from PIL import Image
import plotly.express as px
from chart_studio import plotly
import sqlalchemy
from sqlalchemy import column, create_engine, true, values
import streamlit.components.v1 as components
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from tenacity import retry_unless_exception_type
import plotly.express as px 
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import altair as alt
import seaborn as sns

st.set_page_config(layout='wide',
                   page_title='DASHTEAM', page_icon='logo_djo.png')
padding = 0
st.markdown(f""" <style>.reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {0}rem;
        padding-left: {0}rem;
        padding-bottom: {padding}rem;}} </style> """, unsafe_allow_html=True)

alt.themes.enable('urbaninstitute')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)    

cm = sns.light_palette('green', as_cmap=True)
def milyar(x):
    x = (x/1000000000)
    x =  '{}M'.format(str(x)[:5])
    return x
#MENU
selected = option_menu(None, ["Home","Eksplor Data Penerimaan","Bank Data", "Tools"], 
    icons=['house',"bi bi-bar-chart", 'bi bi-bar-chart-line-fill', "list-task"], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "3!important", "background-color": "#018da2","max-width":'1320px'},
        "icon": {"color": "orange", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "orange"},
        "menu-title" :{"background-color":"#018da2"},
    }
)

#db_conn = mysql.connect(host = '10.4.19.215', user = 'sugengw07', password= 'sgwi2341',
        #database = 'mpninfo',port = '3306')
db_conn = create_engine('mysql://sugengw07:sgwi2341@10.4.19.215/mpninfo')

psql_conn = create_engine('postgresql://postgres:sgwi2341@10.4.19.215/penerimaan')
mon_conn = create_engine('postgresql://postgres:sgwi2341@10.4.19.215/monitoring')


@st.cache(hash_funcs={sqlalchemy.engine.base.Engine: id})
def ppmpkm2022(x):
    data = pd.read_sql(x,con=psql_conn)
    return data

@st.cache(hash_funcs={sqlalchemy.engine.base.Engine: id})
def mpn2020_2022(x):
    data = pd.read_sql(x,con=psql_conn)
    return data

@st.cache()
def monitoring(x):
    data = pd.read_sql(x,con=mon_conn)
    return data

#SQL KPI
#bruto2022 = ppmpkm2022("select sum(p.nominal) from ppmpkm2022 p where p.ket != 'SPMKP'")['nominal'].sum()
bruto2022 = pd.read_sql("select sum(p.nominal) as nominal from ppmpkm2022 p where p.ket != 'SPMKP'",con=psql_conn)['nominal'].sum()
bruto2022 = bruto2022/1000000000000
spmkp2022 = pd.read_sql("select sum(p.nominal) as nominal from ppmpkm2022 p where p.ket = 'SPMKP'",con=psql_conn)['nominal'].sum()
netto2022 = pd.read_sql("select sum(p.nominal) as nominal from ppmpkm2022 p",con=psql_conn)['nominal'].sum()
capaian = (netto2022/8411473360000)*100

#BULAN INI
bruto_bulanini = ppmpkm2022('''select sum(nominal) as jumlah from ppmpkm2022
        where ket  <> 'SPMKP' and extract(month from datebayar) = extract(month from current_date) ''')['jumlah'].sum()
netto_bulanini =ppmpkm2022('select sum(nominal)as netto from ppmpkm2022 where extract(month from datebayar) = extract(month from current_date)')['netto'].sum()
spmkp_bulanini =ppmpkm2022(''' select sum(nominal) as jumlah from ppmpkm2022 where ket='SPMKP' and extract(month from datebayar) = extract(month from current_date) ''')['jumlah'].sum()*-1

tgl_mpn = pd.read_sql("SELECT  MAX(datebayar) as Tanggal_update FROM ppmpkm2022 where ket ='MPN'",con=psql_conn)
tgl_spm = pd.read_sql("SELECT  MAX(datebayar) as Tanggal_update FROM ppmpkm2022 where ket ='SPM'",con=psql_conn)

@st.cache
def convert_csv(df):
    return df.to_csv()


#FRONTED
if selected == "Home":
    #KPI
    colkpi1,colkpi2,colkpi3,colkpi4 = st.columns([2,2,2,1])
    with colkpi1:
        st.subheader('Bruto')
        st.metric(label='s.d Sekarang', value='{:,.2f} T'.format(bruto2022)
        )
        st.metric(label = 'Bulan ini', value= '{:,.2f} M'.format(bruto_bulanini/1000000000))
    with colkpi2:
        st.subheader('SPMKP')
        st.metric(label='s.d Sekarang', value='{:,.2f} T'.format(spmkp2022/1000000000000))
        st.metric(label= 'Bulan ini', value= '{:,.2f} M'.format(spmkp_bulanini/1000000000))
    with colkpi3:
        st.subheader('NETTO')
        st.metric(label='s.d Sekarang', value='{:,.2f} T'.format(netto2022/1000000000000))
        st.metric(label='Bulan ini', value='{:,.2f} M'.format(netto_bulanini/1000000000))
    with colkpi4:
        #st.write(capaian)
        #st.write(tgl_mpn)
        st.metric(label='Capaian',value="%.2f" %capaian)
        st.write('MPN:{}'.format(tgl_mpn.iloc[0,0]))
        st.write('SPM:{}'.format(tgl_spm.iloc[0,0]))

    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
    col1, col2 = st.columns([4,2])
    datapie = ppmpkm2022('select "SEKSI","NAMA_AR", nominal from public.ppmpkm2022 where extract (month from datebayar) = extract(month from current_date)').groupby(
        ['SEKSI','NAMA_AR']).sum().reset_index()
    seksi_pie = px.pie(datapie, names= 'SEKSI', values='nominal',color_discrete_sequence=px.colors.qualitative.Pastel)
    seksi_pie.update_layout(showlegend=False)
    with col2:
        st.plotly_chart(seksi_pie, use_container_width=True)
        
    databar = px.bar(datapie, x='NAMA_AR', y='nominal',color='SEKSI', width=960,color_discrete_sequence=px.colors.qualitative.Pastel)   
    databar.update_layout({'plot_bgcolor':'rgba(0,0,0,0)'})
    databar.update_layout(showlegend=False)
    databar.update_yaxes(title=None)
    databar.update_xaxes(title=None)
    with col1:
        st.plotly_chart(databar,use_container_width=True)
    
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
    
    # PPM PKM & PERSEKSI    
    perseksi = ppmpkm2022('select "SEKSI", nominal from public.ppmpkm2022').groupby('SEKSI').sum().reset_index()
    perseksi_bar = px.bar(perseksi,y='nominal',x='SEKSI',text_auto=',.0f')
    perseksi_bar.update_layout(
        {'showlegend' : False,'plot_bgcolor':'rgba(0, 0, 0,0)','paper_bgcolor': 'rgba(0, 0, 0,0)',
         'margin_t':1 ,'margin_l':1, 'xaxis_title':None, 'yaxis_title':None
         })
    perseksi_bar.update_traces(textposition='inside')
    #st.markdown("<h1 style='text-align:center'>Bulan Ini</h1>", unsafe_allow_html=True)
    st.plotly_chart(perseksi_bar, use_container_width=True)
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)

    #PER JENIS PAJAK
    perjenis = ppmpkm2022('''select "MAP" , nominal from ppmpkm2022''').groupby('MAP').sum().reset_index().sort_values(by='nominal',ascending=False)
    perjenis_copy = perjenis.copy()
    perjenis_copy.nominal = perjenis_copy.nominal.apply(milyar)
    perjenis_tabel = ff.create_table(perjenis_copy)
    perjenis_tree = px.treemap(perjenis,path=['MAP'],values='nominal',color='MAP',height=680,
    color_discrete_sequence=px.colors.qualitative.Pastel)
    perjenis_tree.update_layout({'margin_t':1 ,'margin_l':1})
    coljenistree,coljenistabel = st.columns([3,2])
    with coljenistree:
        st.plotly_chart(perjenis_tree, use_container_width=True)
    with coljenistabel:
        st.title('Per MAP(Netto)')
        st.plotly_chart(perjenis_tabel, use_container_width=True)

   
    
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
    sfsp_top10 = pd.read_sql('select * from upthismonth.sfsp_top',con=mon_conn)
    sfsp_top10.loc[:,'2022':'SHORTFALL/SURPPLUS'] = sfsp_top10.loc[:,'2022':'SHORTFALL/SURPPLUS'].applymap(milyar)
    #sfsp_top10 = sfsp_top10.style.background_gradient(cmap=cm)
    
    #sfsp_top10 = ff.create_table(sfsp_top10)
    sfsp_bot10 = pd.read_sql('select * from upthismonth.sfsp_bot',con=mon_conn)
    sfsp_bot10.loc[:,'2022':'SHORTFALL/SURPPLUS'] = sfsp_bot10.loc[:,'2022':'SHORTFALL/SURPPLUS'].applymap(milyar)
    
    #sfsp_bot10 = ff.create_table(sfsp_bot10)
    
    st.markdown("<h1 style='text-align:center'>10 Surplus Terbesar</h1>", unsafe_allow_html=True)
    
    st.table(sfsp_top10)
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center'>10 Shortfall Terbesar</h1>", unsafe_allow_html=True)
    st.table(sfsp_bot10)
    
    # permap = '''<div class='tableauPlaceholder' id='viz1653306419960' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;01&#47;010422&#47;MAP&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='010422&#47;MAP' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;01&#47;010422&#47;MAP&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>var divElement = document.getElementById('viz1653306419960');var vizElement = divElement.getElementsByTagName('object')[0];if ( divElement.offsetWidth > 800 ) { vizElement.style.minWidth='1169px';vizElement.style.maxWidth='100%';vizElement.style.minHeight='877px';vizElement.style.maxHeight=(divElement.offsetWidth*0.75)+'px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.minWidth='1169px';vizElement.style.maxWidth='100%';vizElement.style.minHeight='877px';vizElement.style.maxHeight=(divElement.offsetWidth*0.75)+'px';} else { vizElement.style.width='100%';vizElement.style.minHeight='1000px';vizElement.style.maxHeight=(divElement.offsetWidth*1.77)+'px';} var scriptElement = document.createElement('script');scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';vizElement.parentNode.insertBefore(scriptElement, vizElement);</script>
    # '''
    # components.html(permap, width=1366, height=650)

elif selected=='Bank Data':
    jenis_data = ['Penerimaan', 'Monitoring/Sanding Data']
    data_menu = st.selectbox('Jenis Data',jenis_data,index=0)
    if data_menu =='Penerimaan':
        
        tabel = ['ppmpkm2022','laporan.existing_ppmpkm2022','laporan.mpn2021']
        
        tabel_selected = st.selectbox('Pilih Tabel yang akan dilihat',tabel)
        
        kolom = pd.read_sql(f'select * from {tabel_selected} limit 1',con=psql_conn)
        kolom_list = st.multiselect('Pilih Kolom',kolom.columns)
        kolom_list = ','.join(['"'+x+'"' for x in kolom_list])
        #st.write(kolom_list)
        if  kolom_list:
            data = pd.read_sql(f'select {kolom_list} from {tabel_selected}',con=psql_conn)
            
            #Aggrid
            gb = GridOptionsBuilder.from_dataframe(data)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            gb.configure_default_column(groupable= True, sorteable= True, enableRowGroup=True, aggFunc='sum', editable=True)
            gridOptions = gb.build()    
            AgGrid(data, gridOptions=gridOptions, enable_enterprise_modules=True)
            
            #Convert
            csv = convert_csv(data)
            st.download_button(
                label=' Download Data',
                data= csv,
                file_name='{}.csv'.format(tabel_selected),
                mime='text/csv'
            )
            
    elif data_menu == "Monitoring/Sanding Data":
        monitoring = pd.read_sql("select table_name as tabel from information_schema.tables where table_schema ='upthismonth'",
                                    con=mon_conn).tabel.tolist()
        tabel_selected = st.selectbox('Pilih Tabel yang akan dilihat',monitoring)
        kolom = pd.read_sql(f'select * from upthismonth.{tabel_selected} limit 1',con=mon_conn)
        kolom_list = st.multiselect('Pilih Kolom',kolom.columns)
        kolom_list = ','.join(['"'+x+'"' for x in kolom_list])
        #st.write(kolom_list)
        if  kolom_list:
            data = pd.read_sql(f'select {kolom_list} from upthismonth.{tabel_selected}',con=mon_conn)
            
            #Aggrid
            gb = GridOptionsBuilder.from_dataframe(data)
            gb.configure_pagination()
            gb.configure_side_bar()
            gb.configure_default_column(groupable= True, value= True, enableRowGroup=True, aggFunc='sum', editable=True)
            gridOptions = gb.build()
            AgGrid(data, gridOptions=gridOptions, enable_enterprise_modules=True)
            
            csv = convert_csv(data)
            st.download_button(
                label=' Download Data',
                data= csv,
                file_name='{}.csv'.format(tabel_selected),
                mime='text/csv'
            )
            
elif selected == 'Eksplor Data Penerimaan':
    
    kuerimpn2020_2022 = '''select * from laporan.explor '''
        
    ppmpkm2022 = mpn2020_2022(kuerimpn2020_2022)
    now = datetime.now()
    #awaltahun = datetime(now.year,1,1)

    colseksi,colar,coltgl1,coltgl2 = st.columns([1,1,1,1])
    #seksi
    with colseksi:
        seksi = ppmpkm2022['SEKSI'].unique()
        opt_seksi = st.selectbox('Seksi', np.insert(seksi,0,'Semua'),index=0)
        if opt_seksi != 'Semua':
            ppmpkm2022 = ppmpkm2022[ppmpkm2022['SEKSI']==opt_seksi]
        else:
            ppmpkm2022 =ppmpkm2022[ppmpkm2022['SEKSI'].isin(seksi)]
    #ar
    with colar:
        ar = ppmpkm2022['NAMA_AR'].unique()
        opt_ar = st.selectbox('AR',np.insert(ar,0,'Semua'),index=0 )
        if opt_ar != 'Semua':
            ppmpkm2022 = ppmpkm2022[ppmpkm2022['NAMA_AR']==opt_ar]
        else:
            ppmpkm2022 =ppmpkm2022[ppmpkm2022['NAMA_AR'].isin(ar)]
    
        
    #waktu
    with coltgl1:
        awaltahun = ppmpkm2022['datebayar'].min()
        mulai = st.date_input('Tanggal Mulai Bayar',awaltahun)
    with coltgl2:
        akhir = st.date_input('Tanggal Akhir Bayar',datetime.now())
    if (mulai is not None) & (akhir is not None):
        mulai = pd.to_datetime(mulai)
        akhir = pd.to_datetime(akhir)
        ppmpkm2022 = ppmpkm2022[ppmpkm2022['datebayar'].isin(pd.date_range(mulai,akhir))] 
    
    #map
    colwp, colmap, colkjs = st.columns([2,1,1])
    #wp
    with colwp:
        wp = ppmpkm2022['NAMA_WP'].unique()
        opt_wp = st.selectbox('WAJIB PAJAK',np.insert(wp,0,'Semua'),index=0)
        if opt_wp != 'Semua':
            ppmpkm2022 = ppmpkm2022[ppmpkm2022['NAMA_WP']==opt_wp]
        else:
            ppmpkm2022 =ppmpkm2022[ppmpkm2022['NAMA_WP'].isin(wp)]
            
    with colmap:
        kdmap = ppmpkm2022['MAP'].unique()
        opt_map = st.selectbox('Jenis Pajak',np.insert(kdmap,0,'Semua'),index=0)
        if opt_map !='Semua':
            ppmpkm2022 = ppmpkm2022[ppmpkm2022['MAP']==opt_map]
        else:
            ppmpkm2022 =ppmpkm2022[ppmpkm2022['MAP'].isin(kdmap)]
    #kjs
    with colkjs:
        kjs = ppmpkm2022['kdbayar'].unique()
        opt_kjs = st.selectbox('Kode Bayar',np.insert(kjs,0,'Semua'),index=0)
        if opt_kjs != "Semua":
            ppmpkm2022 = ppmpkm2022[ppmpkm2022['kdbayar']==opt_kjs]
        else:
            ppmpkm2022 =ppmpkm2022[ppmpkm2022['kdbayar'].isin(kjs)]                                       
    
    
    # ppmpkm2022 = ppmpkm2022[ppmpkm2022['tahun']=='2022']
    total = ppmpkm2022['jumlah'].sum()/1000000000
    # maks = ppmpkm2022['jumlah'].max()/1000000000
    # minim = ppmpkm2022['jumlah'].min()/1000000000
    per_ntpn = ppmpkm2022[['ntpn','jumlah']].groupby('ntpn').sum().reset_index()
    median = per_ntpn['jumlah'].median()/1000000
    rata_rata= per_ntpn['jumlah'].mean()/1000000000
    bruto = ppmpkm2022[~ ppmpkm2022['ket'].isin(['SPMKP','SPMKP dari SIDJP'])]
    bruto = bruto['jumlah'].sum()/1000000000
    spmkp = ppmpkm2022[ppmpkm2022['ket'].isin(['SPMKP','SPMKP dari SIDJP'])]
    spmkp = spmkp['jumlah'].sum()/1000000000
    
    colbruto, colspmkp, colnetto = st.columns(3)
    with colbruto:
        st.metric(label='Bruto',value='{:,.0f}M'.format(bruto))
    with colspmkp:
        st.metric(label='SPMKP', value='{:,.0f}M'.format(spmkp))
    with colnetto:
        st.metric(label='Netto', value='{:,.0f}M'.format(total))
    # with colratarata:
    #     st.metric(label='Rata-Rata',value= '{:,.0f}M'.format(rata_rata))
    # with colmedian:
    #     st.metric(label='Median', value='{:,.0f}Jt'.format(median))
    
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)

    # Multiyears
    datatren = ppmpkm2022[['tahun','bulan','jumlah']].groupby(['tahun','bulan']).sum().reset_index()
    datatren = datatren.sort_values('bulan',ascending=True)
    trendline = px.line(datatren, x='bulan', y='jumlah' ,color='tahun',height=640)
    trendline.update_layout(plot_bgcolor='#3F4E4F')
    trendline.update_xaxes(showgrid=False,nticks=12)
    trendline.update_yaxes(showgrid = True, gridwidth =1, gridcolor='white', title=None)
    
    st.plotly_chart(trendline, use_container_width=True)
        
    #TRENDLINE
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
    dataline = ppmpkm2022[['datebayar','jumlah']].groupby('datebayar').sum().reset_index()
    line = alt.Chart(dataline).mark_bar(
        color= 'white'
    ).encode(
        x= 'datebayar',
        y = 'jumlah',
        tooltip = ['datebayar','jumlah']
    )
    rule = alt.Chart(dataline).mark_rule(color='red').encode(
        y = 'mean(jumlah):Q'
    )
    tren = (line+rule).properties(height = 480).interactive()
    
    st.altair_chart(tren,use_container_width=True)
    
    #TREEMAP
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True) 
    datatree = ppmpkm2022[ppmpkm2022['ket']=='MPN'].filter(['MAP','kdbayar','jumlah']).groupby(['MAP','kdbayar']).sum().reset_index()
    datatree.dropna(inplace=True)
    tree = px.treemap(datatree, path=['MAP','kdbayar'],values='jumlah', width=1280, color_discrete_sequence=px.colors.qualitative.Pastel)
    tree.data[0].textinfo= 'label+percent entry+text'
    st.plotly_chart(tree,use_container_width=True)
    
    data_map = datatree[['MAP','jumlah']].groupby('MAP').sum().reset_index().sort_values(by='jumlah',ascending=False)
    data_kjs = datatree[['kdbayar','jumlah']].groupby('kdbayar').sum().reset_index().sort_values(by='jumlah',ascending=False)
    data_map['jumlah'] = data_map['jumlah'].astype('int64')
    data_map['jumlah'] = data_map['jumlah'].apply(milyar)
    data_kjs['jumlah'] = data_kjs['jumlah'].apply(milyar)
    # tabel_map = ff.create_table(data_map)
    # tabel_kjs = ff.create_table(data_kjs)
   
        
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
    
    #MATRIX
    data_matrix = dataline
    data_matrix['hari'] = data_matrix['datebayar'].dt.day
    data_matrix['bulan'] = data_matrix['datebayar'].dt.month
    data_matrix.drop('datebayar', axis=1, inplace = True)
    data_matrix = pd.pivot_table(data_matrix, index='hari', columns='bulan', aggfunc='sum')
    data_matrix.fillna(0,inplace=True)
    data_matrix['jumlah'] = data_matrix['jumlah'].astype('int64')
    bulandict = {'jumlah_1':'Januari','jumlah_2':'Februari','jumlah_3':'Maret','jumlah_4':'April','jumlah_5':'Mei','jumlah_6':'Juni',
                 'jumlah_7':'Juli','jumlah_8':'Agustus','jumlah_9':'September','jumlah_10':'Oktober','jumlah_11':'November','jumlah_12':'Desember'}
    data_matrix.columns = ['_'.join(str(s).strip() for s in col if s )for col in data_matrix.columns]
    data_matrix.reset_index(inplace=True)
    data_matrix.rename(columns=bulandict, inplace=True)
    data_matrix.set_index('hari', inplace=True)
    heatmap = px.imshow(data_matrix,color_continuous_scale=px.colors.sequential.Blues, height=640)
    heatmap.update_xaxes(side='top')
    st.plotly_chart(heatmap, use_container_width=True)
    for col in data_matrix.columns:
        data_matrix[col] = data_matrix[col].apply(lambda x:"{:,}".format(x))
    #data_matrix = ff.create_table(data_matrix)
    #data_matrix.loc[:,data_matrix.columns[0]:data_matrix.columns[-1]] = data_matrix['jumlah'].map('{:,.0f}'.format)
    st.table(data_matrix)
    
    st.markdown("""<hr style="height:3px;border:none;color:#FFFFFF;background-color:#ffc91b;" /> """, unsafe_allow_html=True)
   
    colkdmap, colkdbayar = st.columns([1,1])
    with colkdmap:
        st.table(data_map)  
    with colkdbayar:
        st.table(data_kjs)
elif selected == 'Tools':
    st.markdown("<h1 style='text-align:center'>Laporan Penerimaan Januari s.d. Mei 2022</h1>", unsafe_allow_html=True)

    st.markdown('<iframe title="UPTHISMONTH" width="1280" height="720" src="https://app.powerbi.com/reportEmbed?reportId=fc51c849-218c-4843-a7f7-5cf8b5ce5e1b&autoAuth=true&ctid=b2e7bf22-070a-4364-b049-4d31669854c4&config=eyJjbHVzdGVyVXJsIjoiaHR0cHM6Ly93YWJpLXNvdXRoLWVhc3QtYXNpYS1iLXByaW1hcnktcmVkaXJlY3QuYW5hbHlzaXMud2luZG93cy5uZXQvIn0%3D" frameborder="0" allowFullScreen="true"></iframe>',
                unsafe_allow_html=True)