import streamlit as st
import pandas as pd
from io import BytesIO


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Nassau Candy | BI Dashboard",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PROFESSIONAL DARK DASHBOARD CSS
# =========================================================

st.markdown(
    """
    <style>

    /* Main application */
    .stApp {
        background-color: #0e1117;
        color: #f5f5f5;
    }

    /* Main content */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Headings */
    h1 {
        font-size: 42px !important;
        font-weight: 800 !important;
    }

    h2 {
        font-size: 30px !important;
        font-weight: 750 !important;
        margin-top: 30px !important;
    }

    h3 {
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #171a21;
        border-right: 1px solid #30343d;
    }

    section[data-testid="stSidebar"] * {
        color: #f5f5f5 !important;
    }

    /* KPI cards */
    div[data-testid="stMetric"] {
        background: #171a21;
        border: 1px solid #30343d;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 750;
    }

    /* Download button */
    .stDownloadButton button {
        width: 100%;
        border-radius: 9px;
        font-weight: 700;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Info / success boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD DATASET
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv("Data/Nassau Candy Distributor.csv")


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "CSV file nahi mila. Make sure file is here: "
        "Data/Nassau Candy Distributor.csv"
    )
    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================

df.columns = df.columns.str.strip()

# Numeric columns
numeric_columns = [
    "Sales",
    "Units",
    "Gross Profit",
    "Cost"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# Date conversion
df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True,
    errors="coerce"
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🔎 Dashboard Filters")

st.sidebar.markdown("---")


# Region
regions = ["All"] + sorted(
    df["Region"].dropna().astype(str).unique().tolist()
)

selected_region = st.sidebar.selectbox(
    "🌎 Select Region",
    regions
)


# Division
divisions = ["All"] + sorted(
    df["Division"].dropna().astype(str).unique().tolist()
)

selected_division = st.sidebar.selectbox(
    "🏢 Select Division",
    divisions
)


# Product
products = ["All"] + sorted(
    df["Product Name"].dropna().astype(str).unique().tolist()
)

selected_product = st.sidebar.selectbox(
    "🍫 Select Product",
    products
)


# =========================================================
# DATE FILTER
# =========================================================

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Date Filter")

valid_dates = df["Order Date"].dropna()

if len(valid_dates) > 0:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:
    selected_dates = None


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()


if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]


if selected_division != "All":
    filtered_df = filtered_df[
        filtered_df["Division"] == selected_division
    ]


if selected_product != "All":
    filtered_df = filtered_df[
        filtered_df["Product Name"] == selected_product
    ]


# Date filter
if selected_dates is not None:

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[1])

        filtered_df = filtered_df[
            (filtered_df["Order Date"] >= start_date)
            &
            (filtered_df["Order Date"] <= end_date)
        ]


st.sidebar.markdown("---")

st.sidebar.write(
    f"📌 Showing **{len(filtered_df):,} records**"
)


# =========================================================
# HEADER
# =========================================================

st.title("🍬 Nassau Candy Distributor")

st.subheader(
    "Product Line Profitability & Margin Performance Analysis"
)

st.write(
    "Interactive Business Intelligence Dashboard"
)


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Gross Profit"].sum()

total_cost = filtered_df["Cost"].sum()

total_orders = filtered_df["Order ID"].nunique()

total_customers = filtered_df["Customer ID"].nunique()

if total_sales != 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0


# =========================================================
# KPI SECTION
# =========================================================

st.header("📊 Key Performance Indicators")


kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        "💰 Total Sales",
        f"${total_sales:,.2f}"
    )

with kpi2:
    st.metric(
        "📈 Total Profit",
        f"${total_profit:,.2f}"
    )

with kpi3:
    st.metric(
        "💸 Total Cost",
        f"${total_cost:,.2f}"
    )


kpi4, kpi5, kpi6 = st.columns(3)

with kpi4:
    st.metric(
        "📦 Total Orders",
        f"{total_orders:,}"
    )

with kpi5:
    st.metric(
        "👥 Total Customers",
        f"{total_customers:,}"
    )

with kpi6:
    st.metric(
        "📊 Profit Margin",
        f"{profit_margin:.2f}%"
    )


# =========================================================
# MONTHLY SALES ANALYSIS
# =========================================================

st.header("📈 Sales Performance")


chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    st.subheader("📈 Monthly Sales Trend")

    if not filtered_df.empty:

        monthly_sales = (
            filtered_df
            .dropna(subset=["Order Date"])
            .assign(
                Month=lambda x:
                x["Order Date"].dt.to_period("M").astype(str)
            )
            .groupby("Month")["Sales"]
            .sum()
            .sort_index()
        )

        if not monthly_sales.empty:
            st.line_chart(
                monthly_sales,
                width="stretch"
            )

    else:
        st.info("No sales data available.")


# =========================================================
# SALES BY REGION
# =========================================================

with chart_col2:

    st.subheader("🌎 Sales by Region")

    if not filtered_df.empty:

        region_sales = (
            filtered_df
            .groupby("Region")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        if not region_sales.empty:
            st.bar_chart(
                region_sales,
                width="stretch"
            )

    else:
        st.info("No regional data available.")


# =========================================================
# TOP PRODUCTS + DIVISION PROFIT
# =========================================================

chart_col3, chart_col4 = st.columns(2)


with chart_col3:

    st.subheader("🍫 Top 10 Products by Sales")

    if not filtered_df.empty:

        top_products = (
            filtered_df
            .groupby("Product Name")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.bar_chart(
            top_products,
            width="stretch"
        )


with chart_col4:

    st.subheader("🏢 Division-wise Profit")

    if not filtered_df.empty:

        division_profit = (
            filtered_df
            .groupby("Division")["Gross Profit"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            division_profit,
            width="stretch"
        )


# =========================================================
# TOP CUSTOMERS
# =========================================================

st.header("👥 Top 10 Customers by Sales")


if not filtered_df.empty:

    customer_sales = (
        filtered_df
        .groupby("Customer ID")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(
        customer_sales,
        width="stretch"
    )


# =========================================================
# EXECUTIVE BUSINESS INSIGHTS
# =========================================================

st.header("💡 Executive Business Insights")


if not filtered_df.empty:

    # Top region
    region_summary = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    if not region_summary.empty:
        top_region = region_summary.index[0]
        top_region_sales = region_summary.iloc[0]
    else:
        top_region = "N/A"
        top_region_sales = 0


    # Top product
    product_summary = (
        filtered_df
        .groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    if not product_summary.empty:
        top_product = product_summary.index[0]
        top_product_sales = product_summary.iloc[0]
    else:
        top_product = "N/A"
        top_product_sales = 0


    # Top division
    division_summary = (
        filtered_df
        .groupby("Division")["Gross Profit"]
        .sum()
        .sort_values(ascending=False)
    )

    if not division_summary.empty:
        top_division = division_summary.index[0]
        top_division_profit = division_summary.iloc[0]
    else:
        top_division = "N/A"
        top_division_profit = 0


    insight1, insight2, insight3 = st.columns(3)


    with insight1:

        st.info(
            f"🌎 **Top Region**\n\n"
            f"### {top_region}\n\n"
            f"Sales: **${top_region_sales:,.2f}**"
        )


    with insight2:

        st.success(
            f"🍫 **Top Product**\n\n"
            f"### {top_product}\n\n"
            f"Sales: **${top_product_sales:,.2f}**"
        )


    with insight3:

        st.warning(
            f"🏢 **Top Division**\n\n"
            f"### {top_division}\n\n"
            f"Profit: **${top_division_profit:,.2f}**"
        )


# =========================================================
# MANAGEMENT SUMMARY
# =========================================================

st.subheader("📌 Management Summary")


if not filtered_df.empty:

    st.write(
        f"The dashboard currently contains "
        f"**{len(filtered_df):,} records** based on the selected filters."
    )

    st.write(
        f"Total sales are **${total_sales:,.2f}** "
        f"with total gross profit of **${total_profit:,.2f}**."
    )

    st.write(
        f"The overall profit margin is **{profit_margin:.2f}%**."
    )

    st.write(
        f"The strongest region by sales is **{top_region}**, "
        f"while the leading product is **{top_product}**."
    )

    st.write(
        f"The division generating the highest gross profit is "
        f"**{top_division}**."
    )

else:

    st.warning(
        "No records match the selected filters."
    )


# =========================================================
# PRODUCT PROFITABILITY ANALYSIS
# =========================================================

st.header("🍫 Product Profitability Analysis")


if not filtered_df.empty:

    product_analysis = (
        filtered_df
        .groupby("Product Name")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Units=("Units", "sum")
        )
        .reset_index()
    )


    # Margin calculation
    product_analysis["Margin %"] = (
        product_analysis["Profit"]
        /
        product_analysis["Sales"].replace(0, pd.NA)
        * 100
    )

    product_analysis["Margin %"] = (
        product_analysis["Margin %"]
        .fillna(0)
    )


    # Sort by profit
    product_analysis = (
        product_analysis
        .sort_values(
            "Profit",
            ascending=False
        )
        .reset_index(drop=True)
    )


    # Most profitable product
    if not product_analysis.empty:

        most_profitable_product = (
            product_analysis.iloc[0]["Product Name"]
        )

        top_profit = (
            product_analysis.iloc[0]["Profit"]
        )

        highest_margin_row = (
            product_analysis
            .sort_values("Margin %", ascending=False)
            .iloc[0]
        )

        highest_margin_product = (
            highest_margin_row["Product Name"]
        )

        highest_margin = (
            highest_margin_row["Margin %"]
        )

        average_margin = (
            product_analysis["Margin %"].mean()
        )


        # Product KPI cards
        pa1, pa2, pa3, pa4 = st.columns(4)


        with pa1:
            st.metric(
                "🏆 Most Profitable Product",
                most_profitable_product
            )


        with pa2:
            st.metric(
                "💰 Highest Product Profit",
                f"${top_profit:,.2f}"
            )


        with pa3:
            st.metric(
                "📊 Highest Margin Product",
                highest_margin_product
            )


        with pa4:
            st.metric(
                "📈 Average Product Margin",
                f"{average_margin:.2f}%"
            )


        # Product profit chart
        st.subheader(
            "💰 Top 10 Products by Gross Profit"
        )


        top_product_profit = (
            product_analysis
            .set_index("Product Name")["Profit"]
            .head(10)
        )


        st.bar_chart(
            top_product_profit,
            width="stretch"
        )


        # Product table
        st.subheader(
            "📋 Product Profitability Table"
        )


        display_product = product_analysis.copy()


        display_product["Sales"] = (
            display_product["Sales"]
            .map(lambda x: f"${x:,.2f}")
        )


        display_product["Profit"] = (
            display_product["Profit"]
            .map(lambda x: f"${x:,.2f}")
        )


        display_product["Cost"] = (
            display_product["Cost"]
            .map(lambda x: f"${x:,.2f}")
        )


        display_product["Units"] = (
            display_product["Units"]
            .map(lambda x: f"{x:,.0f}")
        )


        display_product["Margin %"] = (
            display_product["Margin %"]
            .map(lambda x: f"{x:.2f}%")
        )


        st.dataframe(
            display_product,
            width="stretch",
            hide_index=True
        )


else:

    st.info(
        "No product profitability data available."
    )


# =========================================================
# BUSINESS RECOMMENDATIONS
# =========================================================

st.header("🎯 Business Recommendations")


if not filtered_df.empty:

    recommendation_col1, recommendation_col2 = st.columns(2)


    with recommendation_col1:

        st.success(
            f"""
            **📈 Growth Opportunity**

            Focus on the **{top_region}** region because it
            currently generates the highest sales among the
            selected records.
            """
        )


    with recommendation_col2:

        st.info(
            f"""
            **🍫 Product Opportunity**

            **{top_product}** is currently the leading product
            by sales. Consider maintaining inventory availability
            and promotional support for this product.
            """
        )


    if profit_margin >= 50:

        st.success(
            f"💰 Current overall margin of "
            f"**{profit_margin:.2f}%** indicates strong profitability."
        )

    else:

        st.warning(
            f"⚠️ Current overall margin is "
            f"**{profit_margin:.2f}%**. Review product costs and pricing."
        )


# =========================================================
# DOWNLOAD SECTION
# =========================================================

st.header("📥 Download Filtered Data")


if not filtered_df.empty:

    download_col1, download_col2 = st.columns(2)


    # CSV
    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")


    with download_col1:

        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name="nassau_candy_filtered_data.csv",
            mime="text/csv"
        )


    # Excel
    excel_buffer = BytesIO()


    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        filtered_df.to_excel(
            writer,
            index=False,
            sheet_name="Filtered Data"
        )


    excel_buffer.seek(0)


    with download_col2:

        st.download_button(
            label="📊 Download Excel",
            data=excel_buffer,
            file_name="nassau_candy_filtered_data.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )


# =========================================================
# FILTERED DATASET PREVIEW
# =========================================================

st.header("📋 Filtered Dataset Preview")


if not filtered_df.empty:

    st.dataframe(
        filtered_df.head(100),
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No filtered records available for preview."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "🍬 Nassau Candy Distributor | "
    "Interactive Business Intelligence Dashboard"
)