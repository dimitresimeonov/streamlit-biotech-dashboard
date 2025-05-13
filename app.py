import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#initiate
newQ = "Q1 2025"
oldQ = "Q4 2024"

# === Load Excel Data ===
file_path = "Quarterly_Biotech_Holdings_Comparison.xlsx"
sheets = pd.read_excel(file_path, sheet_name=None)

st.set_page_config(page_title="Biotech Fund Dashboard", layout="wide")
st.title("Biotech Fund Ownership Dashboard")

# === Sidebar navigation ===
page_options = [
    "Overview",
    "Newly Owned",
    "Increased Ownership",
    "Reduced Ownership",
    "Quarter Summary"
]
page = st.sidebar.radio("Select Analysis Section", page_options)

# === Overview ===
if page == "Overview":
    st.markdown("""
        ### **Overview**

        **Goal: Access "smart money" investor data to identify compelling investments in biotech.**

        **My Process:** This project democratizes institutional biotech fund activity by systematically tracking quarterly trends. 
        We parse and analyze 13F-HR filings once per quarter to identify newly-owned companies, shifts in fund participation, 
        and macro trends in biotech investment.

        **Defining Biotech "Smart Money":** Investment funds with 60%+ biotech exposure, 5–100 biotech positions, and more than $50M in AUM.

        **The Key Insights:**
        - Newly owned companies by biotech funds
        - Changes in fund participation
        - Trends in public biotech investment        

        ### **About the Author**
        - PhD scientist, entrepreneur, and investor
        - 4 years in venture capital and early-stage drug discovery
        - 15 years investing in public biotech companies

        **Follow BiotechPicks** on Twitter (https://x.com/BiotechPicks) and Substack (https://substack.com/@biotechpicks)

        *This is not investment advice. Do your own due diligence. The data may have inaccuracies, if so, my apologies in advance!
        For fixes and additional analyses, please email sime8n@gmail.com.*
    """)

# === Newly Owned ===
elif page == "Newly Owned":
    df = sheets["Newly Owned"].copy()
    df = df.loc[:, ~df.columns.duplicated()]
    st.subheader("Newly Owned Biotechs")
    st.markdown("*Biotechs companies with new positions in %s, not previously owned in %s. Hover over data points to see tickers and additional information.*" % (newQ, oldQ))


        # First scatter plot styled to match second (transparent, white border)
    df_plot = df.dropna(subset=["MktCap", "num_funds_new"])
    fig1 = px.scatter(
        df_plot,
        x="MktCap",
        y="num_funds_new",
        hover_name="ticker",
        title="Market Cap vs # of New Funds",
        labels={"MktCap": "Market Cap (USD)", "num_funds_new": "# of Funds"},
        log_x=True,
        color_discrete_sequence=["#5B9BD5"]
    )
    fig1.update_traces(
        marker=dict(
            size=20,
            opacity=0.6,
            line=dict(width=1, color="white")
        ),
        selector=dict(mode="markers")
    )
    fig1.update_layout(template="plotly")
    st.plotly_chart(fig1, use_container_width=True)

        # New scatter plot with avg investment (in millions) as circle size
    if all(col in df.columns for col in ["total_val_new", "num_funds_new"]):
        df_plot2 = df.copy()
        df_plot2["avg_investment_new"] = df_plot2["total_val_new"] / df_plot2["num_funds_new"]
        df_plot2["avg_investment_mil"] = df_plot2["avg_investment_new"] / 1e6  # convert to millions
        df_plot2 = df_plot2.dropna(subset=["MktCap", "num_funds_new", "avg_investment_mil"])

        fig2 = px.scatter(
            df_plot2,
            x="MktCap",
            y="num_funds_new",
            size="avg_investment_mil",
            hover_name="ticker",
            title="Market Cap vs # of New Funds (Circle Size = Avg Investment $M)",
            labels={
                "MktCap": "Market Cap (USD)",
                "num_funds_new": "# of Funds",
                "avg_investment_mil": "Avg Investment ($M)"
            },
            log_x=True,
            size_max=60,
            color_discrete_sequence=["#5B9BD5"]
        )
        fig2.update_layout(template="plotly")
        st.plotly_chart(fig2, use_container_width=True)


# === Increased Ownership ===
elif page == "Increased Ownership":
    df = sheets["Increased Ownership"]
    df = df.loc[:, ~df.columns.duplicated()]
    st.subheader("Increased Ownership Biotechs")
    st.markdown("*Biotech companies owned by more funds in %s as compared to %s.*" % (newQ, oldQ))

    # First plot: stacked bar chart of total ownership (old + new)
    df_plot = df.sort_values("num_funds_new", ascending=False).head(25)
    fig1 = px.bar(
        df_plot,
        x="ticker",
        y=["num_funds_old", "delta_funds"],
        title="Top 25 Stocks with Increased Ownership (Total Funds)",
        labels={
            "value": "# of Funds",
            "ticker": "Ticker",
            "num_funds_old": "Old Funds",
            "delta_funds": "New Funds"
        },
        barmode="stack",
        color_discrete_sequence=["#C8C8C8", "#5B9BD5"],
        template="plotly"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Second plot: bar chart of just the new funds (delta_funds), sorted descending
    df_delta_only = df[df["delta_funds"] > 0].sort_values("delta_funds", ascending=False).head(25)
    fig2 = px.bar(
        df_delta_only,
        x="ticker",
        y="delta_funds",
        title="Top 25 Stocks by Increase in Fund Ownership (New Funds Only)",
        labels={"delta_funds": "# of New Funds", "ticker": "Ticker"},
        color_discrete_sequence=["#5B9BD5"],
        template="plotly"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Breakdown by Market Cap")
    st.markdown("*Subset companies based on their market capitalization to better highlight fund interest across all biotechs.*")
    if "MktCap" in df.columns:
        bins = [(1e9, float('inf')), (1e8, 1e9), (0, 1e8)]
        labels = ["> $1B", "$100M - $1B", "< $100M"]
        for (low, high), label in zip(bins, labels):
            df_filtered = df[(df["MktCap"] >= low) & (df["MktCap"] < high)].sort_values("num_funds_new", ascending=False).head(25)
            fig = px.bar(
                df_filtered,
                x="ticker",
                y="num_funds_new",
                title=f"{label} Market Cap - Fund Ownership",
                labels={"num_funds_new": "# of Funds", "ticker": "Ticker"},
                color_discrete_sequence=["#5B9BD5"],
                template="plotly"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Market cap data ('MktCap') not found in the dataset.")




# === Reduced Ownership ===
elif page == "Reduced Ownership":
    df = sheets["Reduced Ownership"]
    df = df.loc[:, ~df.columns.duplicated()]
    st.subheader("Reduced Ownership Biotechs")
    st.markdown("*Biotech companies owned by fewer funds in %s as compared to %s.*" % (newQ, oldQ))
    df = df.sort_values("num_funds_old", ascending=False)

    # First chart: overlay of old and new fund counts
    df_plot = df.head(25)
    fig = px.bar(
        df_plot,
        x="ticker",
        y=["num_funds_old", "num_funds_new"],
        title="Top 25 Decreases in Fund Ownership",
        labels={
            "value": "# of Funds",
            "ticker": "Ticker",
            "num_funds_old": "Old Funds",
            "num_funds_new": "New Funds"
        },
        barmode="overlay",
        opacity=0.85,
        color_discrete_sequence=["#C8C8C8", "#5B9BD5"],
        template="plotly"
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
    st.plotly_chart(fig, use_container_width=True)

    # Second chart: # of funds that completely sold out (owned before, now zero)
    df_sold_out = df[(df["num_funds_old"] > 0) & (df["num_funds_new"] == 0)].copy()
    df_sold_out = df_sold_out.sort_values("num_funds_old", ascending=False).head(25)

    fig2 = px.bar(
        df_sold_out,
        x="ticker",
        y="num_funds_old",
        title="Top 25 Stocks by Number of Funds That Sold Out",
        labels={"num_funds_old": "# of Funds That Sold Out", "ticker": "Ticker"},
        color_discrete_sequence=["#C8C8C8"],
        template="plotly"
    )
    fig2.update_layout(margin=dict(t=50))  # optional: spacing buffer from the title above
    st.plotly_chart(fig2, use_container_width=True)


# === Quarter Summary ===
elif page == "Quarter Summary":
    df = sheets["Quarter Summary"]
    st.subheader("Quarter Summary Data")
    st.dataframe(df)
