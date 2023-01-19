import streamlit as st
import pandas as pd
import numpy as np
import base64 
from io import StringIO, BytesIO  




st.set_page_config(page_title='Movement to Production')
st.title('Movement to Production App')
st.markdown("""---""")


def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Move to Production Results.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

st.write("1.Download Current Stock [link](https://pisang.sayurbox.tech/question/2404-inventory-summary-warehouse-area-inventory-management-system?warehouse=Sentul&inventory_system_category=Fruits&inventory_system_category=Vegetables), lalu upload langsung hasil download ke box dibawah")
read_stock = st.file_uploader('Upload Current Stock', type='xlsx')
if read_stock:
	st.markdown('Upload Current Stock Success')
st.markdown("""---""")

st.write("2.Download EPC Same Day [link](https://pisang.sayurbox.tech/question/7220-epc-real-time-parent-ingredients-virtual-bundling?slot=slot-sameday&warehouse=JK01&inventory_system_category=Fruits&inventory_system_category=Vegetables&order_status=COMPLETED&order_status=CONFIRMED&order_status=CREATED&order_status=DELIVERED&order_status=PAID&order_status=SHIPPED), input delivery date yang dibutuhkan lalu upload")
read_epcsd = st.file_uploader('Upload EPC Same Day', type='xlsx')
if read_epcsd:
	st.markdown('Upload EPC Same Day Success')
st.markdown("""---""")

st.write("3.Download EPC Next Day [link](https://pisang.sayurbox.tech/question/7220-epc-real-time-parent-ingredients-virtual-bundling?slot=slot-0&slot=slot-1&slot=slot-12&warehouse=JK01&inventory_system_category=Fruits&inventory_system_category=Vegetables&order_status=COMPLETED&order_status=CONFIRMED&order_status=CREATED&order_status=DELIVERED&order_status=PAID&order_status=SHIPPED), input delivery date yang dibutuhkan lalu upload")
read_epcnd = st.file_uploader('Upload EPC Next Day', type='xlsx')
if read_epcnd:
	st.markdown('Upload EPC Next Day Success')
st.markdown("""---""")

st.write("4.Download Parent Child Relationships [link](https://pisang.sayurbox.tech/question/2125-sku-parent-child-relationship-list), langsung tanpa input filter")
pcr = st.file_uploader('Upload Parent Child Relationships', type='xlsx')
if pcr:
	st.markdown('Upload Parent Child Relationships Success')
st.markdown("""---""")

st.write("5.Download SKU Master [link](https://pisang.sayurbox.tech/question/5853-sku-master), langsung tanpa input filter")
sku_master = st.file_uploader('Upload SKU Master', type='xlsx')
if sku_master:
	st.markdown('Upload SKU Master Success')
st.markdown("""---""")

st.write("6.Download History [link](https://pisang.sayurbox.tech/question/2290-inventory-history-realtime-inventory-management-system?warehouse=Sentul&inventory_system_category=Fruits&inventory_system_category=Vegetables), input created_at")
history_data = st.file_uploader('Upload History', type='xlsx')
if history_data:
	st.markdown('Upload History Success')
st.markdown("""---""")

st.write("7.Pilih apakah akan takeout EPC sameday")
sameday_takeout = st.selectbox('Takeout EPC Sameday',('NO', 'YES'))
st.markdown("""---""")

st.write("8.Jika cek diatas jam 12 malam, set buffer menjai OFF")
buffer = st.selectbox('Buffer',('ON', 'OFF'))
st.markdown("""---""")

buffer1 = 2
buffer2 = 1.3

process = st.button("Process")
if process:
	if buffer == 'OFF':
		buffer1 = 1
		buffer2 = 1

	data_raw = pd.read_excel(read_stock)
	data_raw = data_raw.loc[(data_raw['inventory_system_category'] == "Fruits") | (data_raw['inventory_system_category'] == "Vegetables")]
	data = data_raw[['sku_number','sku_description','inventory_system_category','Finished_Goods_Storage','Storage_Ambient_WH07','Storage_Chiller_Fresh']]
	base = pd.read_excel(sku_master)
	base = base[['sku_code','uom_unit','uom_qty']]
	base['converter']=sku['uom_qty']
	base.loc[(base['uom_unit'] =='gram'), 'converter'] = base['uom_qty']/1000
	base.columns = ['sku_number','unit','converter']
	data = pd.merge(
	        left=data,
	        right=base,
	        left_on='sku_number',
	        right_on='sku_number',
	        how='left')

	parent = pd.read_excel(pcr)
	parent = parent.loc[(parent['is_active'] == True)]
	promo_r = parent.loc[(parent['Relation_Type'] == "Promo")]
	promo_r = promo_r[['Child_SKU_Number','Parent_SKU_Desc']]

	data = pd.merge(
	                left=data,
	                right=promo_r,
	                left_on='sku_number',
	                right_on='Child_SKU_Number',
	                how='left')
	data = data.drop(columns=['Child_SKU_Number'])
	data.loc[(data['Parent_SKU_Desc'].isna()) , 'Parent_SKU_Desc'] = data['sku_description']

	data['varian_name'] = data['Parent_SKU_Desc'].str.replace(r'\s*\w+(?:\W+\w+)?\s*(?![^,])', '')
	data = data.replace({'varian_name': 'Impor Impor'},
			    {'varian_name': 'Impor'}, regex=True)
	data = data.replace({'varian_name': 'Import'},
			    {'varian_name': 'Impor'}, regex=True)
	data = data.replace({'varian_name': 'Organik Organik'}, 
	                        {'varian_name': 'Organik'}, regex=True)
	data = data.replace({'varian_name': 'Imperfect Imperfect'}, 
	                        {'varian_name': 'Imperfect'}, regex=True)
	data = data.replace({'varian_name': 'Konvensional Konvensional'}, 
	                        {'varian_name': 'Konvensional'}, regex=True)
	data = data.replace({'varian_name': 'Conventional'}, 
	                        {'varian_name': 'Konvensional'}, regex=True)
	data = data.replace({'varian_name': 'Premium Premium'}, 
	                        {'varian_name': 'Premium'}, regex=True)
	data = data.replace({'varian_name': 'Hidroponik Hidroponik'}, 
	                        {'varian_name': 'Hidroponik'}, regex=True)
	data = data.replace({'varian_name': 'Dummy'}, 
	                        {'varian_name': 'Konvensional'}, regex=True)
	data = data.replace({'varian_name': ' B2B'}, 
	                        {'varian_name': ''}, regex=True)
	data = data.replace({'varian_name': ' Konvensional'}, 
	                        {'varian_name': ''}, regex=True)

	data.loc[(data['unit'] == 'gram'), 'unit'] = 'kg'
	data['varian_name']=data['varian_name']+' '+data['unit']
	fg = data[['sku_number','sku_description','varian_name','inventory_system_category','unit','converter','Finished_Goods_Storage']]
	raw_mat = data[['varian_name','Storage_Ambient_WH07','Storage_Chiller_Fresh']]
	raw_mat['raw_mat']=raw_mat['Storage_Ambient_WH07']+raw_mat['Storage_Chiller_Fresh']
	raw_mat = raw_mat[['varian_name','raw_mat']]
	raw_mat = pd.DataFrame(raw_mat.groupby(['varian_name'], as_index = False).sum())
	join = pd.merge(
	                left=fg,
	                right=raw_mat,
	                left_on='varian_name',
	                right_on='varian_name',
	                how='left')
	epc_sd = pd.read_excel(read_epcsd)
	epc_sd = epc_sd[['Ingredients_SKU_CODE','UOS_TOTAL_QUANTITY']]
	epc_sd.columns = ['sku_number','epc_sameday']
	epc_sd = pd.DataFrame(epc_sd.groupby(['sku_number'], as_index = False).sum())
	epc_nd = pd.read_excel(read_epcnd)
	epc_nd = epc_nd[['Ingredients_SKU_CODE','UOS_TOTAL_QUANTITY']]
	epc_nd.columns = ['sku_number','epc_nextday']
	epc_nd = pd.DataFrame(epc_nd.groupby(['sku_number'], as_index = False).sum())
	join = pd.merge(
	        left=join,
	        right=epc_sd,
	        left_on='sku_number',
	        right_on='sku_number',
	        how='left')

	join = pd.merge(
	        left=join,
	        right=epc_nd,
	        left_on='sku_number',
	        right_on='sku_number',
	        how='left')
	join = join.fillna(0)
	join['sameday_takeout']=sameday_takeout
	join.loc[(join['sameday_takeout'] == 'YES'), 'epc_sameday'] = 0
	join['total_epc']=join['epc_sameday']+join['epc_nextday']
	join['minus_fg']=join['total_epc']-join['Finished_Goods_Storage']
	join = join.loc[(join['minus_fg'] > 0)]
	join.loc[(join['minus_fg'] <= 10), 'minus_fg_plus_buffer'] = (join['minus_fg']*buffer1).apply(np.ceil)
	join.loc[(join['minus_fg'] > 10), 'minus_fg_plus_buffer'] = (join['minus_fg']*buffer2).apply(np.ceil)
	
	history = pd.read_excel(history_data)
	history = history.loc[(history['activity_type'] == "stock_movement")]
	history = history.loc[(history['area_source'] == "Storage Chiller Fresh") | (history['area_source'] == "Storage Ambient WH07")
			      |(history['area_source'] == "Production")|(history['area_source'] == "Finished Goods Storage")]
	history = history.loc[(history['area_destination'] == "Production")|(history['area_destination'] == "Finished Goods Storage")]
	history = history[['created_time','sku_number','sku_description','qty','area_source','area_destination']]
	history = pd.DataFrame(history.groupby(['created_time','sku_number','sku_description','area_source','area_destination'], as_index = False).sum())
	history = history.drop_duplicates(subset='sku_number', keep="last")
	history = history.loc[(history['area_destination'] == "Production")]
	history = pd.merge(
		left=history,
		right=base,
		left_on='sku_number',
		right_on='sku_number',
		how='left')
	history['varian_name'] = history['sku_description'].str.replace(r'\s*\w+(?:\W+\w+)?\s*(?![^,])', '')
	history = history.replace({'varian_name': 'Impor Impor'}, 
                        {'varian_name': 'Impor'}, regex=True)
	history = history.replace({'varian_name': 'Import'}, 
                        {'varian_name': 'Impor'}, regex=True)
	history = history.replace({'varian_name': 'Organik Organik'}, 
				{'varian_name': 'Organik'}, regex=True)
	history = history.replace({'varian_name': 'Imperfect Imperfect'}, 
				{'varian_name': 'Imperfect'}, regex=True)
	history = history.replace({'varian_name': 'Konvensional Konvensional'}, 
				{'varian_name': 'Konvensional'}, regex=True)
	history = history.replace({'varian_name': 'Conventional'}, 
				{'varian_name': 'Konvensional'}, regex=True)
	history = history.replace({'varian_name': 'Premium Premium'}, 
				{'varian_name': 'Premium'}, regex=True)
	history = history.replace({'varian_name': 'Hidroponik Hidroponik'}, 
				{'varian_name': 'Hidroponik'}, regex=True)
	history = history.replace({'varian_name': 'Dummy'}, 
				{'varian_name': 'Konvensional'}, regex=True)
	history = history.replace({'varian_name': ' B2B'}, 
				{'varian_name': ''}, regex=True)
	history = history.replace({'varian_name': ' Konvensional'}, 
				{'varian_name': ''}, regex=True)
	history.loc[(history['unit'] == 'gram'), 'unit'] = 'kg'

	history['varian_name']=history['varian_name']+' '+history['unit']

	history = history[['varian_name','qty']]

	history.columns = ['varian_name','last_move_to_production']

	history = history.drop_duplicates(subset='varian_name', keep="last")

	join = pd.merge(
        	left=join,
        	right=history,
        	left_on='varian_name',
        	right_on='varian_name',
        	how='left')
	join = join.fillna(0)
	join = join.sort_values(by=['varian_name'])
	join['minus_fg_plus_buffer'] = (join['minus_fg_plus_buffer']/join['converter']).apply(np.floor)
	join['minus_fg_plus_buffer'] = join['minus_fg_plus_buffer']*join['converter']
		    
	
	to_phl = join[['varian_name','minus_fg_plus_buffer']]
	to_phl.columns = ['item_name','total_ambil_di_raw_mat']
	to_phl = pd.DataFrame(to_phl.groupby(['item_name], as_index = False).sum())

	st.markdown('Process Completed')
	st.dataframe(join)

	st.subheader('Downloads dan Print Untuk PHL:')
	generate_excel_download_link(to_phl)
					      
	st.subheader('Downloads dan Print Untuk Produksi:')
	generate_excel_download_link(join)				    
