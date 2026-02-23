# ============================================================
# PRACTICAL GUIDE (Bokeh) - Fully commented, line by line
# Goal: Help you memorize the framework used in the assignment
# Demonstrates (assignment-relevant):
# (1) ColumnDataSource
# (2) figure() + glyphs (vbar / line / scatter)
# (3) Dual y-axis (extra_y_ranges + LinearAxis + y_range_name)
# (4) HoverTool (tooltips + formatting + mode="vline")
# Also: standalone HTML export (output_file + save)
# ============================================================

# ----------------------------
# 0) Imports (every line explained)
# ----------------------------

import pandas as pd                       # Use pandas to load/clean/transform tabular data
import numpy as np                        # Use numpy for numeric operations (min/max/padding)

from bokeh.io import output_file, save    # output_file: set HTML filename; save: export layout to standalone HTML
from bokeh.layouts import column, row     # column/row: build a dashboard layout (vertical/horizontal stacking)

from bokeh.models import (                # bokeh.models contains "building blocks" for plots and dashboards
    ColumnDataSource,                     # ColumnDataSource: Bokeh's core data container connecting data <-> plot
    HoverTool,                            # HoverTool: show tooltips when hovering over plot elements
    Range1d,                              # Range1d: define a numeric range (start, end), used for axes
    LinearAxis,                           # LinearAxis: add a new axis (e.g., right-side y-axis)
    Div                                  # Div: display HTML text (useful for KPI panels / explanations)
)

from bokeh.plotting import figure         # figure: create a plotting canvas
from bokeh.sampledata.stocks import AAPL  # AAPL: public sample dataset (Apple stock time series) shipped with Bokeh

# ----------------------------
# 1) Load and prepare data (like "cleaning + feature engineering")
# ----------------------------

df = pd.DataFrame(AAPL)                   # Convert Bokeh sample data (dict-like) into a pandas DataFrame
df["date"] = pd.to_datetime(df["date"])   # Ensure date is datetime (same idea as pd.to_datetime in your assignment)

# ---- Simulate "Sales" metrics from stock data (for teaching purposes) ----
# In your assignment:
# - transactions = number of purchases (row count)
# - revenue = sum of money
# - ARPT = revenue / transactions
# Here we simulate:
# - transactions = volume  (how many shares traded that day)
# - revenue = close * volume  (fake "money volume")
# - arpt = revenue / transactions = close (nice: ARPT becomes close price)

df["transactions"] = df["volume"]         # Create a "transactions" column (volume acts like transaction count)
df["revenue"] = df["close"] * df["volume"]# Create a "revenue" column (close*volume acts like total money)
df["arpt"] = df["revenue"] / df["transactions"]  # ARPT definition: revenue / transactions (here equals close)

# ---- Make x-axis friendly (categorical) ----
# In a dashboard, a categorical axis is often easier for discrete dates (string labels).
df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")  # Convert date to string for categorical x-axis labels

# ---- Optionally limit the dataset to keep the HTML lightweight ----
# You can remove this if you want the full dataset.
df = df.sort_values("date")               # Sort by date (important for time series plots)
df = df.tail(120).reset_index(drop=True)  # Keep last 120 days to keep the plot readable (demo choice)

# ----------------------------
# 2) ColumnDataSource (core Bokeh concept #1)
# ----------------------------

# ColumnDataSource stores data as "columns of lists".
# Every glyph uses the column names (strings) like "date", "transactions" to read values.
source = ColumnDataSource(                # Create a Bokeh data source from Python data
    data=dict(                            # data must be a dict: {column_name: list_of_values}
        date=df["date_str"].tolist(),     # x values (categorical strings)
        transactions=df["transactions"].tolist(),  # y values for bars (left axis)
        revenue=df["revenue"].tolist(),   # y values for revenue line (right axis)
        arpt=df["arpt"].tolist(),         # y values for arpt line (right axis)
    )
)

# ----------------------------
# 3) KPI panel (optional but assignment-like)
# ----------------------------

total_tx = int(df["transactions"].sum())  # Total transactions for KPI (sum volume)
total_rev = float(df["revenue"].sum())    # Total revenue for KPI (sum close*volume)
avg_arpt = float(total_rev / total_tx) if total_tx > 0 else 0.0  # ARPT = revenue/transactions

kpi_html = f"""                           # Build an HTML string that we can show in the dashboard
<div style="padding:10px;border:1px solid #ddd;border-radius:10px;">
  <h3 style="margin:0 0 8px 0;">Demo KPI Panel</h3>
  <div><b>Transactions:</b> {total_tx:,}</div>
  <div><b>Revenue (simulated):</b> {total_rev:,.2f}</div>
  <div><b>ARPT:</b> {avg_arpt:,.4f}</div>
  <div style="margin-top:6px;color:#666;">
    (Demo only) We simulate "sales" using stock volume and price.
  </div>
</div>
"""

kpi_div = Div(text=kpi_html, width=1000)  # Div shows HTML text; great for KPI blocks in dashboards

# ----------------------------
# 4) Create the figure (core Bokeh concept #2: figure + glyphs)
# ----------------------------

p = figure(                               # Create a plotting canvas
    x_range=source.data["date"],          # Use categorical x-axis factors (list of date strings)
    height=420,                           # Plot height in pixels
    width=1000,                           # Plot width in pixels
    title="Bokeh Practical: Bars + Dual-Axis Lines + HoverTool",  # Plot title
    toolbar_location="above"              # Place toolbar above the plot
)

p.xaxis.major_label_orientation = 0.9     # Rotate x labels so dates are readable
p.yaxis.axis_label = "Transactions"       # Left y-axis label (for bars)

# ----------------------------
# 5) Add glyphs: vbar on LEFT axis (transactions)
# ----------------------------

p.vbar(                                   # Draw vertical bars
    x="date",                             # x values come from source.data["date"]
    top="transactions",                   # bar height comes from source.data["transactions"]
    width=0.9,                            # bar width (0-1, since categorical)
    source=source,                        # bind the glyph to the ColumnDataSource
    legend_label="Transactions (bars)"    # legend label for this glyph
)

# ----------------------------
# 6) Dual y-axis (core Bokeh concept #3)
# ----------------------------

# Why dual axis?
# - Transactions can be huge (millions)
# - Revenue and ARPT have different magnitude
# So we create a separate y-range for right axis metrics.

rev_min = float(min(df["revenue"].min(), df["arpt"].min()))  # Compute min across revenue and arpt
rev_max = float(max(df["revenue"].max(), df["arpt"].max()))  # Compute max across revenue and arpt

# "pad" = padding space to avoid lines touching plot boundaries
pad = (rev_max - rev_min) * 0.10 if rev_max > rev_min else 1.0  # 10% margin; fallback if range is 0

p.extra_y_ranges = {                     # extra_y_ranges holds additional y ranges besides default left one
    "right_axis": Range1d(               # Define a new numeric range for the right axis
        start=rev_min - pad,             # lower bound with padding
        end=rev_max + pad                # upper bound with padding
    )
}

p.add_layout(                             # Add a new axis to the plot layout
    LinearAxis(                           # Create a new linear axis object
        y_range_name="right_axis",        # Bind this axis to p.extra_y_ranges["right_axis"]
        axis_label="Revenue / ARPT"       # Label for the right axis
    ),
    "right"                               # Place the axis on the right side of the plot
)

# ----------------------------
# 7) Add glyphs: lines on RIGHT axis (revenue and arpt)
# ----------------------------

p.line(                                   # Draw a line glyph
    x="date",                             # x values from source
    y="revenue",                          # y values from source
    source=source,                        # bind to ColumnDataSource
    y_range_name="right_axis",            # IMPORTANT: use the right y-axis range
    line_width=2,                         # make line thicker
    line_color="green",                   # set color for revenue line
    legend_label="Revenue (line)"         # legend label
)

p.scatter(                                # Draw scatter points on the revenue line (helps hover)
    x="date",                             # x values
    y="revenue",                          # y values
    source=source,                        # same source
    y_range_name="right_axis",            # also on right axis
    size=5,                               # point size
    fill_color="green",                   # fill color
    line_color="green",                   # border color
    legend_label="Revenue points"         # legend label (optional)
)

p.line(                                   # Draw ARPT line
    x="date",                             # x values
    y="arpt",                             # y values
    source=source,                        # same source
    y_range_name="right_axis",            # right axis
    line_width=2,                         # thickness
    line_color="orange",                  # different color from revenue
    legend_label="ARPT (line)"            # legend label
)

p.scatter(                                # Scatter points for ARPT (improves hover accuracy)
    x="date",                             # x values
    y="arpt",                             # y values
    source=source,                        # source
    y_range_name="right_axis",            # right axis
    size=4,                               # point size
    fill_color="orange",                  # fill color
    line_color="orange",                  # border color
    legend_label="ARPT points"            # legend label (optional)
)

# Legend interaction: click to hide/show a series
p.legend.click_policy = "hide"            # Allows user to click legend items to hide glyphs

# ----------------------------
# 8) HoverTool (core Bokeh concept #4)
# ----------------------------

# HoverTool reads values from ColumnDataSource using "@fieldname"
# Formatting examples:
# - {0,0} for integer with commas
# - {0,0.00} for decimals with commas and 2 decimals
# mode="vline" makes hover align across all glyphs sharing x coordinate

p.add_tools(                              # Add interactive tools to the plot
    HoverTool(                            # Create a hover tool
        tooltips=[                        # tooltips define what to display
            ("Date", "@date"),            # show the date string
            ("Transactions", "@transactions{0,0}"),  # show transactions with comma formatting
            ("Revenue", "@revenue{0,0.00}"),         # show revenue with 2 decimals
            ("ARPT", "@arpt{0,0.0000}")               # show arpt with 4 decimals
        ],
        mode="vline"                      # easier hover on categorical/time x-axis
    )
)

# ----------------------------
# 9) Layout (dashboard assembly)
# ----------------------------

layout = column(                          # column stacks items vertically
    kpi_div,                              # KPI panel at the top
    p                                    # plot below
)

# ----------------------------
# 10) Export to standalone HTML
# ----------------------------

output_file(                              # Configure output HTML file
    "bokeh_practical_dashboard_full_comments.html",  # filename
    title="Bokeh Practical Guide (Fully Commented)"  # HTML title
)

save(layout)                              # Save the layout to the HTML file (standalone, no server needed)

print("Saved: bokeh_practical_dashboard_full_comments.html")  # Print confirmation