import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import os
sns.set_theme(style='dark')

st.set_page_config(page_title="Bike Sharing Dashboard",
                   page_icon="📈",
                   layout="wide")

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_monthly_share_df(df):
    monthly_share_df = df.resample(rule='ME', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    monthly_share_df.index = monthly_share_df.index.strftime('%b 20%y')
    monthly_share_df = monthly_share_df.reset_index()
    monthly_share_df.rename(columns={
        "dteday": "bulan_tahun",
        "cnt": "semua_pengguna",
        "casual": "pengguna_lepas",
        "registered": "pengguna_terdaftar"
    }, inplace=True)
    return monthly_share_df

def create_hourly_mean_df(df):
    hourly_mean_df = df.groupby(by="hr").agg({
        "casual": "mean",
        "registered": "mean",
        "cnt": "mean"
    })
    hourly_mean_df = hourly_mean_df.reset_index()
    hourly_mean_df.rename(columns={
        "hr": "jam",
        "cnt": "semua_pengguna",
        "casual": "pengguna_lepas",
        "registered": "pengguna_terdaftar"
    }, inplace=True)
    return hourly_mean_df

def create_daily_mean_df(df):
    daily_mean_df = df.groupby(by="weekday").agg({
    "casual": "mean",
    "registered": "mean",
    "cnt": "mean"
    })
    daily_mean_df = daily_mean_df.reset_index()
    daily_mean_df.rename(columns={
        "weekday": "hari",
        "cnt": "semua_pengguna",
        "casual": "pengguna_lepas",
        "registered": "pengguna_terdaftar"
    }, inplace=True)
    # Mengurutkan berdasarkan nama hari
    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    daily_mean_df['hari'] = pd.Categorical(daily_mean_df['hari'], categories=ordered_days, ordered=True)
    daily_mean_df = daily_mean_df.sort_values('hari')
    return daily_mean_df

def create_workingday_group_df(df):
    workingday_group = df.groupby(by="workingday").agg({
        "casual": "mean",
        "registered": "mean",
        "cnt": "mean"
    })
    workingday_group = workingday_group.reset_index()
    workingday_group['workingday'] = workingday_group['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})
    workingday_group.rename(columns={
        "workingday": "day",
        "cnt": "semua_pengguna",
        "casual": "pengguna_lepas",
        "registered": "pengguna_terdaftar"
    }, inplace=True)
    return workingday_group

def create_seasonly_share_df(df):
    seasonly_share_df = df.groupby('season').cnt.sum().reset_index()
    return seasonly_share_df


# Load cleaned data
script_dir = os.path.dirname(os.path.realpath(__file__))
day_df = pd.read_csv(f"{script_dir}/cleaned_day.csv")
hour_df = pd.read_csv(f"{script_dir}/cleaned_hour.csv")

hour_df.sort_values(by="dteday", inplace=True)
hour_df.reset_index(inplace=True)
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

# Filter data
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(f"{script_dir}/bike_icon.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value = max_date,
        value = [min_date, max_date]
    )


main_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
mainhour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]

# Menyiapkan berbagai dataframe
monthly_share_df = create_monthly_share_df(main_df)
hourly_mean_df = create_hourly_mean_df(mainhour_df)
daily_mean_df = create_daily_mean_df(main_df)
workingday_group = create_workingday_group_df(main_df)
seasonly_share_df = create_seasonly_share_df(main_df)

st.title('Bike Sharing Dashboard 📊🚲')

col1, col2, col3 = st.columns(3)
with col1:
    total_share = main_df.cnt.sum()
    st.metric("Total Peminjam Sepeda", value=total_share)
with col2:
    total_registered = main_df.registered.sum()
    st.metric("Total Peminjam Sepeda Terdaftar", value=total_registered)
with col3:
    total_casual = main_df.casual.sum() 
    st.metric("Total Peminjam Sepeda Lepas", value=total_casual)


fig1 = px.line(monthly_share_df,
              x='bulan_tahun',
              y=['pengguna_lepas', 'pengguna_terdaftar', 'semua_pengguna'],
              color_discrete_sequence=["#f70a8d", "#00d26a", "#00a6ed"],
              markers=True,
              title="Total Peminjaman Sepeda Setiap Bulan").update_layout(xaxis_title='', yaxis_title='')
fig1.update_xaxes(tickangle = 45)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(hourly_mean_df,
              x='jam',
              y=['pengguna_lepas', 'pengguna_terdaftar', 'semua_pengguna'],
              color_discrete_sequence=["#f70a8d", "#00d26a", "#00a6ed"],
              markers=True,
              title="Rata-rata Peminjaman Sepeda Berdasarkan Waktu").update_layout(xaxis_title='', yaxis_title='', xaxis=dict(tickmode='array', tickvals=[i for i in range(24)]))
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(daily_mean_df,
              x='hari',
              y=['pengguna_terdaftar', 'pengguna_lepas'],
              color_discrete_sequence=["#00d26a", "#f70a8d"],
              title="Rata-rata Peminjaman Sepeda Berdasarkan Hari").update_layout(xaxis_title='', yaxis_title='')
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.bar(workingday_group,
              x='day',
              y=['pengguna_terdaftar', 'pengguna_lepas'],
              color_discrete_sequence=["#00d26a", "#f70a8d"],
              title="Rata-rata Peminjaman Sepeda pada Hari Kerja dan Hari Libur").update_layout(xaxis_title='', yaxis_title='')
st.plotly_chart(fig4, use_container_width=True)

fig8 = px.bar(seasonly_share_df,
              x='season',
              y='cnt',
              color='season',
              color_discrete_sequence=["#e44e16", "#00d26a", "#f70a8d", "#00a6ed"],
              title="Total Peminjaman Sepeda Setiap Musim").update_layout(xaxis_title='', yaxis_title='')
st.plotly_chart(fig8, use_container_width=True)


st.subheader("Pengaruh Kondisi Cuaca terhadap Jumlah Peminjaman Sepeda")
tab1, tab2, tab3= st.tabs(["Temperatur", "Kelembapan", "Kecepatan Angin"])

with tab1:
    st.markdown("**Hubungan Temperatur dengan Jumlah Peminjaman Sepeda**")
    fig5 = px.scatter(main_df,
              x='atemp',
              y='cnt',
              color="weathersit",
              color_discrete_sequence=["#f70a8d", "#00d26a", "#00a6ed"]).update_layout(xaxis_title='Temperatur', yaxis_title='Total Peminjaman Sepeda')
    fig5.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
    ))
    st.plotly_chart(fig5, use_container_width=True)

    with st.expander("Lihat penjelasaan"):
        st.write(
            """Grafik ini menunjukkan hubungan antara temperatur dan jumlah peminjaman sepeda, 
            dengan titik-titik berwarna yang mewakili kondisi cuaca berbeda. Secara umum, grafik 
            memperlihatkan bahwa peminjaman sepeda cenderung meningkat seiring dengan naiknya 
            temperatur, terutama dalam cuaca cerah atau sedikit berawan (hijau). Sebaliknya, pada 
            kondisi cuaca seperti kabut, hujan ringan, atau badai petir (merah muda dan biru), 
            jumlah peminjaman sepeda cenderung lebih rendah, khususnya pada temperatur yang lebih 
            rendah. Cuaca yang lebih baik tampaknya mendorong lebih banyak peminjaman sepeda.
            """
        )
with tab2:
    st.markdown("**Hubungan Kelembapan dengan Jumlah Peminjaman Sepeda**")
    fig6 = px.scatter(main_df,
              x='hum',
              y='cnt',
              color="weathersit",
              color_discrete_sequence=["#f70a8d", "#00d26a", "#00a6ed"]).update_layout(xaxis_title='Kelembapan', yaxis_title='Total Peminjaman Sepeda')
    fig6.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
    ))
    st.plotly_chart(fig6, use_container_width=True)

    with st.expander("Lihat penjelasaan"):
        st.write(
            """Grafik ini menunjukkan hubungan antara kelembapan dan jumlah peminjaman sepeda, dengan 
            titik-titik berwarna mewakili kondisi cuaca yang berbeda. Secara umum, peminjaman sepeda 
            cenderung lebih tinggi pada tingkat kelembapan menengah (sekitar 0.4 hingga 0.6), terutama 
            pada kondisi cuaca cerah atau sedikit berawan (hijau). Pada kelembapan yang sangat rendah 
            atau sangat tinggi, jumlah peminjaman sepeda cenderung lebih sedikit, terutama dalam kondisi 
            cuaca hujan ringan atau badai petir (biru) dan cuaca berkabut atau mendung (merah muda). 
            Secara keseluruhan, grafik ini menunjukkan bahwa kelembapan mempengaruhi peminjaman sepeda, 
            di mana kondisi kelembapan sedang dan cuaca yang lebih cerah cenderung mendorong lebih banyak 
            peminjaman sepeda, sementara kelembapan ekstrem dengan cuaca buruk mengurangi minat peminjaman.
            """
        )
with tab3:
    st.markdown("**Hubungan Kecepatan Angin dengan Jumlah Peminjaman Sepeda**")
    fig7 = px.scatter(main_df,
              x='windspeed',
              y='cnt',
              color="weathersit",
              color_discrete_sequence=["#f70a8d", "#00d26a", "#00a6ed"]).update_layout(xaxis_title='Kecepatan Angin', yaxis_title='Total Peminjaman Sepeda')
    fig7.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
    ))
    st.plotly_chart(fig7, use_container_width=True)

    with st.expander("Lihat penjelasaan"):
        st.write(
            """Grafik ini menunjukkan hubungan antara kecepatan angin dan jumlah peminjaman sepeda, 
            dengan titik-titik berwarna yang mewakili kondisi cuaca berbeda. Secara umum, grafik 
            memperlihatkan bahwa kecepatan angin tidak memiliki pengaruh yang signifikan terhadap 
            jumlah peminjaman sepeda, karena peminjaman tetap tersebar di berbagai tingkat kecepatan 
            angin. Namun, peminjaman cenderung lebih banyak terjadi pada kecepatan angin rendah hingga 
            sedang (sekitar 0 hingga 0.2), terutama pada cuaca cerah atau berawan sebagian (hijau).
            Jumlah peminjaman sepeda lebih sedikit pada kondisi cuaca hujan atau badai petir (biru) di 
            berbagai tingkat kecepatan angin. Secara keseluruhan, grafik ini menunjukkan bahwa kecepatan 
            angin tidak secara jelas memengaruhi jumlah peminjaman sepeda, meskipun cuaca cerah dan 
            berawan sebagian tampaknya mendorong lebih banyak peminjaman dibandingkan kondisi cuaca buruk.
            """
        )


mean_cnt = main_df['cnt'].mean()
std_cnt = main_df['cnt'].std()

# Membuat kolom baru berdasarkan kolom cnt (rendah, sedang, tinggi)
main_df['cnt_category'] = pd.cut(main_df['cnt'],
                                bins=[0, mean_cnt - std_cnt, mean_cnt + std_cnt, main_df['cnt'].max()],
                                labels=['Rendah', 'Sedang', 'Tinggi'])

category_counts = main_df['cnt_category'].value_counts()
fig9 = px.pie(values=category_counts.values, 
             names=category_counts.index, 
             title='Distribusi Kategori Jumlah Peminjaman Sepeda',
             color_discrete_sequence=["#f70a8d", "#00d26a", "#00a6ed"])

st.plotly_chart(fig9, use_container_width=True)

st.caption("Copyright (c) Febriana Nur Syifa Rizqi 2024")