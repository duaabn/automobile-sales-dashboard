import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# -----------------------
# Read data
# -----------------------
data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv"
)

# Feature Engineering: Date -> Year, Month
data["Date"] = pd.to_datetime(data["Date"])
data["Year"] = data["Date"].dt.year
data["Month"] = data["Date"].dt.month

# Keep year range 1980–2013
data = data[(data["Year"] >= 1980) & (data["Year"] <= 2013)].copy()

year_list = sorted(data["Year"].unique())

# -----------------------
# Dash app
# -----------------------
app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": 28},
        ),

        html.Div(
            children=[
                html.Label("Select Statistics:", style={"fontSize": 16}),
                dcc.Dropdown(
                    id="dropdown-statistics",
                    options=[
                        {"label": "Yearly Statistics", "value": "Yearly Statistics"},
                        {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
                    ],
                    value="Yearly Statistics",
                    clearable=False,
                    placeholder="Select a report type",
                ),
            ],
            style={"width": "60%", "margin": "auto"},
        ),

        html.Br(),

        html.Div(
            children=[
                html.Label("Select Year:", style={"fontSize": 16}),
                dcc.Dropdown(
                    id="select-year",
                    options=[{"label": y, "value": y} for y in year_list],
                    value=year_list[0],
                    clearable=False,
                    placeholder="Select a year",
                ),
            ],
            style={"width": "60%", "margin": "auto"},
        ),

        html.Br(),

        html.Div(id="output-container", style={"textAlign": "center", "fontSize": 16}),

        html.Div(
            children=[
                dcc.Graph(id="chart1"),
                dcc.Graph(id="chart2"),
            ],
            style={"width": "95%", "margin": "auto"},
        ),
    ]
)

# -----------------------
# Callback 1: Disable year dropdown for recession report
# -----------------------
@app.callback(
    Output("select-year", "disabled"),
    Input("dropdown-statistics", "value"),
)
def toggle_year_dropdown(selected_statistics):
    return selected_statistics == "Recession Period Statistics"

# -----------------------
# Callback 2: Update charts
# -----------------------
@app.callback(
    [
        Output("output-container", "children"),
        Output("chart1", "figure"),
        Output("chart2", "figure"),
    ],
    [
        Input("dropdown-statistics", "value"),
        Input("select-year", "value"),
    ],
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1].copy()

        # Chart 1: Average sales by Vehicle Type during recession
        avg_sales = (
            recession_data.groupby("Vehicle_Type")["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        fig1 = px.bar(
            avg_sales,
            x="Vehicle_Type",
            y="Automobile_Sales",
            title="Average Automobile Sales by Vehicle Type (Recession Periods)",
        )

        # Chart 2: Total advertising expenditure by Vehicle Type during recession
        ad_exp = (
            recession_data.groupby("Vehicle_Type")["Advertising_Expenditure"]
            .sum()
            .reset_index()
        )
        fig2 = px.pie(
            ad_exp,
            names="Vehicle_Type",
            values="Advertising_Expenditure",
            title="Total Advertising Expenditure by Vehicle Type (Recession Periods)",
        )

        output_text = "You selected: Recession Period Statistics"
        return output_text, fig1, fig2

    # Yearly Statistics
    yearly_data = data[data["Year"] == input_year].copy()

    # Chart 1: Total Monthly Automobile Sales in selected year
    monthly_sales = (
        yearly_data.groupby("Month")["Automobile_Sales"]
        .sum()
        .reset_index()
    )
    fig1 = px.line(
        monthly_sales,
        x="Month",
        y="Automobile_Sales",
        title=f"Total Monthly Automobile Sales in {input_year}",
    )

    # Chart 2: Average sales by Vehicle Type in selected year
    avg_sales_year = (
        yearly_data.groupby("Vehicle_Type")["Automobile_Sales"]
        .mean()
        .reset_index()
    )
    fig2 = px.bar(
        avg_sales_year,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title=f"Average Automobile Sales by Vehicle Type in {input_year}",
    )

    output_text = f"You selected: Yearly Statistics | Year: {input_year}"
    return output_text, fig1, fig2


# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
