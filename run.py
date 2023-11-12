import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# PREPARATION START
st.set_page_config(
    layout="wide",
    page_title="DICODING-AIR QUALITY DASHBOARD",
    # theme="light"
)
df = pd.read_csv("Air-Quality-Final.csv", sep=";", index_col=False)
df = df[["datetime", "station", 'PM2.5', 'PM10', 'SO2', 'NO2', 'CO', "RAIN"]]
df["datetime"] = pd.to_datetime(df["datetime"])
pollutant = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO']
# PREPARATION END

# FUNCTION START


def main_df():
    filtered_df = df[(df["datetime"] > pd.to_datetime(start_date)) & (
        df["datetime"] < pd.to_datetime(end_date))].reset_index(drop=True)
    return filtered_df


def st_grouping():
    st_condition = main_df().groupby("station").mean(
        numeric_only=True).sort_values(by=["RAIN"], ascending=False)
    return st_condition


def filtered_st():
    data = main_df()
    station_name = st_grouping().index[0]
    station_df = data[data["station"] == station_name]
    return station_df


def monthly_rain_df():
    rainest_df = filtered_st()
    monthly_rainest_df = rainest_df.groupby(
        rainest_df['datetime'].dt.to_period("M")).mean(numeric_only=True)
    return monthly_rainest_df


def convert_date():
    before = monthly_rain_df().index
    after = before.to_timestamp()
    return after


def rain_df():
    rainest_df = filtered_st()
    is_rain = []
    for x in rainest_df["RAIN"]:
        if x != 0:
            is_rain.append("Rain")
        else:
            is_rain.append("Not Rain")
    rainest_df["is_rain"] = is_rain
    return rainest_df
# FUNCTION END


# SIDEBAR START
max_filter = df["datetime"].max()
min_filter = df["datetime"].min()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_filter,
        max_value=max_filter,
        value=[min_filter, max_filter]
    )
# SIDEBAR END

# BODY START
st.title("AIR QUALITY DASHBOARD")

with st.container():
    st.subheader("Stasiun Dengan Curah Hujan Paling Tinggi", anchor=False)
    fig, ax = plt.subplots(figsize=(9, 3))
    ax = sns.barplot(
        y=st_grouping().index,
        x='RAIN',
        palette="crest_r",
        data=st_grouping()
    )
    sns.despine()
    plt.ylabel('Stasiun')
    plt.xlabel('Rata-Rata Curah Hujan')
    plt.title(f'{start_date.strftime("%B %Y")} - {end_date.strftime("%B %Y")}')
    st.pyplot(fig)

st.subheader(
    f"Tingkat Curah Hujan Dan Polusi Stasiun {st_grouping().index[0]}")
col1, col2 = st.columns(2)


with col1:
    with st.container():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax = sns.lineplot(
            y="RAIN",
            x=[x.strftime("%B-%Y") for x in convert_date()],
            # palette="crest_r",
            marker="o",
            data=monthly_rain_df())
        sns.despine(
        )
        plt.title(
            f'Curah Hujan Stasiun {st_grouping().index[0]}\n{convert_date()[0].strftime("%B %Y")} - {convert_date()[-1].strftime("%B %Y")}')
        if len(convert_date()) > 12:
            plt.xticks([])
            plt.xlabel("Month-Year")
        else:
            plt.xticks(rotation=45, fontsize=10)

        # ax.set_xticks([])
        plt.ylabel("Curah Hujan")
        st.pyplot(fig)


with col2:
    # st.subheader(f"Keadaan Polusi Di Stasiun {st_grouping().index[0]}")
    col2_1, col2_2 = st.columns(2, )
    with col2_1:

        st.markdown(
            f"""
            **Hujan**  
            ### {np.round(filtered_st().groupby("station").mean()["RAIN"].iloc[0],3)}
            
            **PM2.5**  
            ### {np.round(filtered_st().groupby("station").mean()["PM2.5"].iloc[0],3)}
            
            **PM10**  
            ### {np.round(filtered_st().groupby("station").mean()["PM10"].iloc[0],3)}
            """
        )
    with col2_2:
        f"""
            **SO2**
            ### {np.round(filtered_st().groupby("station").mean()["SO2"].iloc[0],3)}
            **NO2**  
            ### {np.round(filtered_st().groupby("station").mean()["NO2"].iloc[0],3)}
            **CO**  
            ### {np.round(filtered_st().groupby("station").mean()["CO"].iloc[0],3)}
"""


st.header(
    f"Perbandingan Polusi pada Stasiun {st_grouping().index[0]}")
fig, axes = plt.subplots(
    ncols=5,
    nrows=1,
    figsize=(17, 5),

)
for x in range(len(axes)):

    axes[x] = sns.boxenplot(
        data=rain_df(),
        y=pollutant[x],
        hue="is_rain",
        ax=axes[x],
    )

plt.subplots_adjust(hspace=0.3, wspace=.6)
st.pyplot(fig)
