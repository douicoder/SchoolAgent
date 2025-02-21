import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.title("Student Data")

file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "userdatabase",
    "Updated_Student_Data_Extended.csv",
)


df = pd.read_csv(file_path)


gender_counts = df["Gender"].value_counts()
fig1 = px.pie(
    names=gender_counts.index, values=gender_counts.values, title="Gender Distribution"
)
st.plotly_chart(fig1)


class_counts = df["Class"].value_counts().sort_index()
fig2 = px.bar(
    x=class_counts.index,
    y=class_counts.values,
    labels={"x": "Class", "y": "Number of Students"},
    title="Number of Students in Each Class",
)
st.plotly_chart(fig2)


pass_threshold = 50
df["Status"] = df["Results"].apply(lambda x: "Pass" if x >= pass_threshold else "Fail")
pass_fail_counts = df["Status"].value_counts()
fig3 = px.pie(
    names=pass_fail_counts.index,
    values=pass_fail_counts.values,
    title="Pass vs. Fail Percentage",
)
st.plotly_chart(fig3)


area_avg = df.groupby("Area Type")["Results"].mean().reset_index()
fig4 = px.bar(
    area_avg,
    x="Area Type",
    y="Results",
    title="Average Scores: Urban vs. Rural",
    color="Area Type",
)
st.plotly_chart(fig4)
