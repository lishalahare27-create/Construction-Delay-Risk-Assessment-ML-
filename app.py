from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Construction Delay Risk Prediction",
    page_icon="🏗️",
    layout="wide"
)


# -----------------------------
# File paths
# -----------------------------
DATA_PATH = Path("data/synthetic_construction_projects.csv")
MODEL_RESULTS_PATH = Path("model_results.csv")
FEATURE_IMPORTANCE_PATH = Path("feature_importance_final.csv")


# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    return data


@st.cache_data
def load_model_results():
    if MODEL_RESULTS_PATH.exists():
        return pd.read_csv(MODEL_RESULTS_PATH)
    return None


@st.cache_data
def load_feature_importance():
    if FEATURE_IMPORTANCE_PATH.exists():
        return pd.read_csv(FEATURE_IMPORTANCE_PATH)
    return None


data = load_data()
model_results = load_model_results()
feature_importance = load_feature_importance()


# -----------------------------
# Title
# -----------------------------
st.title("Construction Project Delay Risk Prediction")
st.subheader("Interactive dashboard for construction project delay risk monitoring")

st.write(
    """
    This application presents an interactive analysis of construction project delay risk.
    
    The project uses a synthetic dataset inspired by real-world construction and public works project management challenges.
    The objective is to help identify projects that may require closer monitoring and preventive actions.
    """
)


# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.title("Filters")

project_types = sorted(data["Project_Type"].unique())
regions = sorted(data["Region"].unique())
material_levels = sorted(data["Material_Availability"].unique())
equipment_levels = sorted(data["Equipment_Availability"].unique())

selected_project_types = st.sidebar.multiselect(
    "Select project type",
    project_types,
    default=project_types
)

selected_regions = st.sidebar.multiselect(
    "Select region",
    regions,
    default=regions
)

selected_material = st.sidebar.multiselect(
    "Select material availability",
    material_levels,
    default=material_levels
)

selected_equipment = st.sidebar.multiselect(
    "Select equipment availability",
    equipment_levels,
    default=equipment_levels
)


filtered_data = data[
    (data["Project_Type"].isin(selected_project_types)) &
    (data["Region"].isin(selected_regions)) &
    (data["Material_Availability"].isin(selected_material)) &
    (data["Equipment_Availability"].isin(selected_equipment))
]


# -----------------------------
# KPI section
# -----------------------------
st.header("Project Monitoring Overview")

total_projects = len(filtered_data)
delay_risk_projects = (filtered_data["Delay_Risk"] == "Yes").sum()
delay_risk_rate = delay_risk_projects / total_projects * 100 if total_projects > 0 else 0
average_budget = filtered_data["Budget_Million_DZD"].mean() if total_projects > 0 else 0
average_duration = filtered_data["Planned_Duration_Months"].mean() if total_projects > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total projects", total_projects)
col2.metric("Delay-risk projects", delay_risk_projects)
col3.metric("Delay risk rate", f"{delay_risk_rate:.1f}%")
col4.metric("Average duration", f"{average_duration:.1f} months")

st.metric("Average budget", f"{average_budget:.1f} million DZD")


# -----------------------------
# Visual analysis
# -----------------------------
st.header("Interactive Visual Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Delay Risk Distribution")
    fig, ax = plt.subplots(figsize=(6, 4))
    filtered_data["Delay_Risk"].value_counts().plot(kind="bar", ax=ax)
    ax.set_xlabel("Delay Risk")
    ax.set_ylabel("Number of Projects")
    ax.set_title("Distribution of Delay Risk")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)

with col2:
    st.subheader("Delay Risk Rate by Project Type")
    delay_by_type = filtered_data.groupby("Project_Type")["Delay_Risk"].apply(
        lambda x: (x == "Yes").mean()
    ).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 4))
    delay_by_type.plot(kind="bar", ax=ax)
    ax.set_xlabel("Project Type")
    ax.set_ylabel("Delay Risk Rate")
    ax.set_title("Delay Risk Rate by Project Type")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)


col3, col4 = st.columns(2)

with col3:
    st.subheader("Delay Risk by Material Availability")
    delay_by_material = filtered_data.groupby("Material_Availability")["Delay_Risk"].apply(
        lambda x: (x == "Yes").mean()
    ).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    delay_by_material.plot(kind="bar", ax=ax)
    ax.set_xlabel("Material Availability")
    ax.set_ylabel("Delay Risk Rate")
    ax.set_title("Material Availability Impact")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)

with col4:
    st.subheader("Delay Risk by Equipment Availability")
    delay_by_equipment = filtered_data.groupby("Equipment_Availability")["Delay_Risk"].apply(
        lambda x: (x == "Yes").mean()
    ).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    delay_by_equipment.plot(kind="bar", ax=ax)
    ax.set_xlabel("Equipment Availability")
    ax.set_ylabel("Delay Risk Rate")
    ax.set_title("Equipment Availability Impact")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)


# -----------------------------
# Model results
# -----------------------------
st.header("Machine Learning Model Results")

if model_results is not None:
    st.subheader("Model Comparison")
    st.dataframe(model_results, use_container_width=True)
else:
    st.warning("model_results.csv not found.")


# -----------------------------
# Feature importance
# -----------------------------
st.header("Feature Importance")

if feature_importance is not None:
    top_features = feature_importance.head(15)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top_features["Feature"], top_features["Coefficient"])
    ax.set_xlabel("Coefficient")
    ax.set_ylabel("Feature")
    ax.set_title("Top 15 Important Features")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("Top Feature Importance Table")
    st.dataframe(top_features, use_container_width=True)
else:
    st.warning("feature_importance_final.csv not found.")


# -----------------------------
# Business recommendations
# -----------------------------
st.header("Business Recommendations")

st.markdown(
    """
    Based on the analysis and model interpretation, the main recommendations are:

    - Monitor material availability closely.
    - Improve equipment allocation and maintenance planning.
    - Strengthen supplier monitoring.
    - Give closer supervision to complex projects.
    - Use cost overrun and low progress as early-warning indicators.
    - Track safety incidents because they may increase delay risk.
    - Use the model as a decision-support tool, not as a replacement for project managers.
    """
)


# -----------------------------
# Detailed data
# -----------------------------
st.header("Filtered Project Data")

st.dataframe(filtered_data, use_container_width=True)

csv = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="filtered_construction_projects.csv",
    mime="text/csv"
)