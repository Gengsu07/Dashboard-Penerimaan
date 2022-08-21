 kueri_ppmpkm2022 = '''
    select  p."FULL",p."NAMA_WP" ,p."MAP" ,p.kdbayar , p.datebayar , sum(p.nominal) as jumlah , p.ket,
    p."Kategori" ,p."NAMA_AR" , p."SEKSI" 
    from 
    ppmpkm2022 p 
    group by p."FULL",p."NAMA_WP" ,p."MAP" ,p.kdbayar , p.datebayar , p.ket,
    p."Kategori" ,p."NAMA_AR" , p."SEKSI" 
    '''
    
#EDA
    col1, col2 = st.columns([4,2])
    datapie = ppmpkm2022[['SEKSI','NAMA_AR','jumlah']].groupby(['SEKSI','NAMA_AR']).sum().reset_index()
    seksi_pie = px.pie(datapie, names= 'SEKSI', values='jumlah',color_discrete_sequence=px.colors.qualitative.Pastel)
    with col2:
        st.plotly_chart(seksi_pie, use_container_width=True)
        
    databar = px.bar(datapie, x='NAMA_AR', y='jumlah',color='SEKSI', width=960,color_discrete_sequence=px.colors.qualitative.Pastel)   
    databar.update_layout({'plot_bgcolor':'rgba(0,0,0,0)'})
    with col1:
        st.plotly_chart(databar,use_container_width=True)
        
    #where extract (month from datebayar) = extract(month from current_date
    # where extract(month from datebayar)=extract(month from current_date
    
     klu = pd.read_sql('''
                      select "Kategori", sum(2022) as setor 
                        from laporan.perklu_netto 
                        group by "Kategori" order by sum(2022) asc''',con=psql_conn)
    klu_replace = {'Perdagangan Besar dan Eceran; Reparasi dan Perawatan Mobil dan Sepeda Motor':'Perdagangan Besar dan Eceran<br>Reparasi dan Perawatan<br>Mobil dan Sepeda Motor',
    'Penyediaan Akomodasi dan Penyediaan Makan Minum':'Penyediaan Akomodasi dan<br>Penyediaan Makan Minum',
    'Pengadaan Listrik, Gas, Uap/Air Panas dan Udara Dingin.':'Pengadaan Listrik, Gas<br>Uap/Air Panas dan Udara Dingin',
    'Jasa Persewaan, Ketenagakerjaan, Agen Perjalanan dan Penunjang Usaha lainnya':'Jasa Persewaan, Ketenagakerjaan,<br>Agen Perjalanan dan Penunjang Usaha lainnya',
    'Pengadaan Air, Pengelolaan Sampah dan Daur Ulang, Pembuangan dan Pembersihan Limbah dan Sampah':'Pengadaan Air, Pengelolaan Sampah dan <br> Daur Ulang, Pembuangan dan Pembersihan<br>Limbah dan Sampah'}
    klu.replace({'Kategori':klu_replace},inplace=True)
    klu_bar = px.bar(klu, x='Kategori',y= 'setor',text_auto=',.0f',width=1366, height=640)
    klu_bar.update_traces(textposition='inside')
    st.plotly_chart(klu_bar,use_container_width=True)