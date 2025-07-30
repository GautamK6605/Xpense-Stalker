import streamlit as st
import pandas as pd
import altair as alt
import os
st.title("XpenseStalker")
csv_path = "expenses.csv"
columns = ["Date", "Grocery", "Shopping", "Bills", "Personal", "Total"]
categories = ["Grocery", "Shopping", "Bills", "Personal"]


if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
    df_init = pd.DataFrame(columns=columns)
    df_init.to_csv(csv_path, index=False)

df = pd.read_csv(csv_path)

with st.form("Adding expense"):
    date = st.date_input("Select the date")
    category = st.selectbox(label="Select the category", options=categories)
    amount = st.number_input("Enter the amount", min_value=0)
    submitted = st.form_submit_button("Add Expense")

if submitted:
    date_str = date.isoformat()
    if (df["Date"] == date_str).any():
        idx = df.index[df["Date"] == date_str][0]
        current_val = df.at[idx, category]
        if pd.isna(current_val):
            current_val = 0
        df.at[idx, category] = current_val + amount
    else:
        new_row = {col: 0 for col in columns}
        new_row["Date"] = date_str
        new_row[category] = amount
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df["Total"] = df[categories].sum(axis=1)
    df.to_csv(csv_path, index=False)
    st.success(f"Added {amount:.2f} to {category} on {date_str}")

st.markdown("---")
chart_type = st.radio(
    "Choose chart view",
    ["Category Breakdown for a Date", "Month at a Glance"],
)

if chart_type == "Category Breakdown for a Date":
    selected_date = st.selectbox("Select date to display", options=df["Date"].unique())
    data_for_chart = df[df["Date"] == selected_date]
    df_long = data_for_chart.melt(
        id_vars=["Date"], value_vars=categories,
        var_name="Category", value_name="Amount"
    )
    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('Category:N', title='Category'),
        y=alt.Y('Amount:Q', title='Amount'),
        color=alt.Color('Category:N')
    ).properties(
        title=f"Expenses Breakdown for {selected_date}"
    )
    st.altair_chart(chart, use_container_width=True)
else:
    cat_options = ["Total"] + categories
    chosen_metric = st.selectbox("Show total or select a specific category", options=cat_options)
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Date:N', title='Date', sort=df["Date"].tolist()),
        y=alt.Y(f'{chosen_metric}:Q', title=chosen_metric),
        color=alt.Color('Date:N', legend=None) if chosen_metric != "Total" else alt.value('#1f77b4')
    ).properties(
        title=f"{chosen_metric} spent per day in {pd.to_datetime(df['Date']).dt.strftime('%B %Y').iloc[0]}"
    )
    st.altair_chart(chart, use_container_width=True)

df_display = df.set_index("Date")
st.dataframe(df_display)
