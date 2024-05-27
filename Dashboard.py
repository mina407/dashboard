import streamlit as st
import pandas as pd
import numpy as np
import os 
import plotly.express as px
import plotly.figure_factory as ff
import warnings
warnings.filterwarnings('ignore')



st.set_page_config(page_title='Super Store' , page_icon=":bar_chart:" , layout="wide")
st.title(":bar_chart: Sample Superstore EDA")

st.markdown('<style>div.block-container{padding-top:2rem;}</style>' , unsafe_allow_html=True)
@st.cache_data
def load_data(file):
    return pd.read_csv(file , encoding="ISO-8859-1")
    
### Uploading the file
file = st.file_uploader(":file_folder: Upload The File" , type=(['csv']))
if file is not None:
    df = load_data(file)
    del (df['Row ID'])
    ##1- number of rows to show 
    #num_rows = st.slider("Number Of Rows",min_value=1 , max_value=len(df))
    ## controling the columns to show 
    #num_colm = st.multiselect("Select Columns To Show" , df.columns.to_list(),
                              #default=df.columns.to_list())
    ##2- numerical and categorical features    
    num_features = df.select_dtypes(exclude="O").columns.tolist()
    cat_features = df.select_dtypes(include='O').columns.tolist()

    col1 , col2 , = st.columns((2))
    
    ##3- Converting date type into date time
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    start_date = df['Order Date'].min()
    end_date = df['Order Date'].max()
    
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date" , start_date))
    with col2 :
        date2 = pd.to_datetime(st.date_input("End Date" , end_date))

    df = df[(df['Order Date'] >= date1)& (df['Order Date']<=date2)].copy()
    ##4- printing the data
    # st.write(df[:num_rows][num_colm])

    ##5- Filter based on Region
    st.sidebar.header("Choose Your Filter")
    region = st.sidebar.multiselect("Select The Region" , df['Region'].unique())
    if not region:
        df2 = df.copy()
    else :
        df2 = df[df['Region'].isin(region)]
    
    ##6- Create filter based on state 
    state = st.sidebar.multiselect("Select The State" , df2['State'].unique())
    if not state :
        df3 = df2.copy()
    else :
        df3 = df2[df['State'].isin(state)]

    ## 7- Filter based of City
    city = st.sidebar.multiselect("Select The City" , df3['City'].unique())
    if not city :
        df4 = df3.copy()
    else :
        df4 = df3[df3['City'].isin(city)]

    ## 8- Filter based on 
    category = st.sidebar.multiselect("Select The Category" , df4['Category'].unique())
    if not category:
        df5 = df4.copy()
    else : 
        df5 = df4[df4['Category'].isin(category)]
    ##st.write(df5[:num_rows][num_colm])

    ## comparing Categories using bar chart
    with col1 :
        st.subheader("Categories Average Sales" ,) 
        category_avg = df5.groupby('Category' , as_index = False)['Sales'].mean()
        fig_cate = px.bar(data_frame=category_avg , x = "Category" , y = "Sales" , template='plotly' , text = ['${:,.2f}'.format(x) for x in category_avg["Sales"]])
        st.plotly_chart(fig_cate , use_container_width=True ,height = 100)

    ## Comparing region using pie chart
    with col2:
        st.subheader('contribution Of Region')
        region = df5.groupby('Region' , as_index = False)['Sales'].mean()
        fig_region = px.pie(data_frame=region , values="Sales" , names="Region" ,hole = 0.5 ,color_discrete_sequence=px.colors.sequential.RdBu)
        fig_region.update_traces(text =region['Region'] , textposition = 'outside' )
        st.plotly_chart(fig_region , use_container_width=True )
    ## to dwonload the data based on filter
    cl1 , cl2 = st.columns((2))
    with cl1 :
        with st.expander("Category View Data"):
            st.write(category_avg.style.background_gradient(cmap = 'Blues'))
            csv = category_avg.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data" , data= csv , file_name= 'category.csv' , mime='txt/csv' , help='Click Here To Download the Data as csv file') 

    with cl2:
        with st.expander("Region View Data"):
            st.write(region.style.background_gradient(cmap = "Oranges"))
            csv = region.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data" , data=csv , file_name="region.csv" , mime="csv/txt" , help='Click Here To Download the Data as csv file')

    ## Create time series analysis
    st.subheader('Time Series Analysis')
    ## Extract year and month from order data column 
    df5['Year Month'] = df5['Order Date'].dt.to_period("M") 
    line_chart = pd.DataFrame(np.round(df5.groupby(df5['Year Month'].dt.strftime("%Y:%b"))['Sales'].mean(),1)).reset_index()
    fig_line = px.line(line_chart , x = "Year Month" , y="Sales" ,height=500 )
    st.plotly_chart(fig_line , use_container_width=True)      

    ## to download the data :
    with st.expander("View Time Series Data"):
        st.write(line_chart.T.style.background_gradient(cmap="Green"))
        csv = line_chart.to_csv(index = False).encode("utf-8")
        st.download_button("Download Time Series Data" , data = csv , file_name='line_chart.csv' , )

    ## create tree map for region Category and sub_category
    st.subheader("Hierarchical View Of Sales using Treemap")
    fig_treemap = px.treemap(df5 , path=['Region' , 'Category' , 'Sub-Category'] , values='Sales' , hover_data=['Sales' ], 
               color='Sub-Category')
    fig_treemap.update_layout(width = 800 , height = 650)
    st.plotly_chart(fig_treemap , use_container_width=True)

    chart1 , chart2 = st.columns((2))

    with chart1 : 
       fig_cate_pie =  px.pie(df5 , values="Sales" , names='Category' , template='plotly')
       fig_cate_pie.update_traces(text = df5['Category'] , textposition = 'inside')
       st.plotly_chart(fig_cate_pie , use_container_width=True)
    with chart2 :
        fig_seg = px.pie(df5 , values='Sales' , names='Segment' , template='plotly_dark')
        fig_seg.update_traces(text =df5['Segment'] , textposition = 'inside')
        st.plotly_chart(fig_seg)

    ## making tabel to show data 
    st.subheader(":point_right: Show The Data")
    with st.expander("Summary Data"):
        num_rows = st.slider("Number Of Rows",min_value=1 , max_value=len(df))
        df_sample = df5[:num_rows][['Region' , 'State' , 'City' , "Category" ,  'Quantity','Sales' , 'Profit' ]]
        fig_data = ff.create_table(df_sample , colorscale= 'Cividis')
        st.plotly_chart(fig_data , use_container_width=True)

    ## make tabel for sales and sub_categorey
    st.markdown("Month Sales And Sub_Category")
    df5['month'] = df5['Order Date'].dt.month_name()

    sub_categiry_df = pd.pivot_table(data=df5 , index = 'Sub-Category' , columns='month' , values='Sales' , aggfunc='mean')
    st.write(sub_categiry_df.style.background_gradient('RdYlGn_r'))

    ## Relationship between sales and profit 
    data = px.scatter(data_frame=df5 , x = 'Sales' , y = 'Profit')
    data.update_layout(title = "RelationShip Between Sales And Profit" , titlefont = dict(size = 17))
    st.plotly_chart(data  , use_container_width=True)

    ## make button to download after applying filters 
    csv = df5.to_csv(index = False).encode('utf-8')
    st.download_button("Download The Data" , data = csv , file_name="Data.csv" , mime=("csv/txt"))

