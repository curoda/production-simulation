import pandas as pd
import streamlit as st
from collections import deque
import math

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        data.columns = data.columns.str.replace(' ', '_')  # Replace spaces with underscores in column names
        return data
    except FileNotFoundError:
        st.error("The specified file was not found. Please check the file path and try again.")
        return None
    except pd.errors.EmptyDataError:
        st.error("The file is empty. Please provide a valid CSV file.")
        return None
    except pd.errors.ParserError:
        st.error("The file could not be parsed. Please ensure it is a valid CSV file.")
        return None

def initialize_state():
    return {
        'backlog': deque(),
        'wip': deque(),
        'completed_orders': [],
        'order_counter': 1,
    }

def add_new_orders(state, new_orders):
    for _ in range(new_orders):
        state['backlog'].append(f"Order{state['order_counter']}")
        state['order_counter'] += 1

def process_orders(state, production_lines, production_cycle_time):
    # Reduce remaining days for WIP orders
    new_completed_orders = []
    updated_wip = deque()
    for order, days_left in state['wip']:
        days_left -= 1
        if days_left > 0:
            updated_wip.append((order, days_left))
        else:
            new_completed_orders.append(order)
    
    # Update WIP with remaining orders
    state['wip'] = updated_wip

    # Mark completed orders
    state['completed_orders'].extend(new_completed_orders)

    # Move backlog to WIP if available lines
    current_wip_count = len(state['wip'])
    idle_production_lines = max(production_lines - current_wip_count, 0)
    orders_pulled_from_backlog = 0
    while state['backlog'] and idle_production_lines > 0:
        order = state['backlog'].popleft()
        state['wip'].append((order, production_cycle_time))
        idle_production_lines -= 1
        orders_pulled_from_backlog += 1

    return new_completed_orders, orders_pulled_from_backlog, idle_production_lines

def estimated_days_to_clear_backlog(backlog_size, production_lines, production_cycle_time):
    if production_lines == 0:
        return float('inf')
    return math.ceil(backlog_size / production_lines) * production_cycle_time

def main():
    st.title("Production Simulation App")
    st.sidebar.write("### Sample CSV File Format")
    st.sidebar.write("""
    Date,Production Cycle Time,Number of Production Lines,Number of New Customer Orders
    2023-01-01,5,3,10
    2023-01-02,5,3,8
    2023-01-03,5,3,12
    ...
    """)
    st.sidebar.download_button(
        label="Download Sample CSV",
        data="Date,Production Cycle Time,Number of Production Lines,Number of New Customer Orders\n2023-01-01,5,3,10\n2023-01-02,5,3,8\n2023-01-03,5,3,12\n",
        file_name="sample_input.csv",
        mime="text/csv"
    )
    uploaded_file = st.sidebar.file_uploader("Upload Input CSV File", type="csv")

    if uploaded_file:
        data = load_data(uploaded_file)
        if data is not None:
            state = initialize_state()
            output_data = []

            for row in data.itertuples():
                date = row.Date
                production_cycle_time = int(row.Production_Cycle_Time)
                production_lines = int(row.Number_of_Production_Lines)
                new_orders = int(row.Number_of_New_Customer_Orders)

                # Validate data
                if production_cycle_time <= 0 or production_lines < 0 or new_orders < 0:
                    st.error(f"Invalid data on {date}: All values must be non-negative and production cycle time must be greater than zero.")
                    continue

                backlog_from_previous_day = len(state['backlog'])

                add_new_orders(state, new_orders)
                completed_orders, orders_pulled_from_backlog, idle_lines = process_orders(
                    state, production_lines, production_cycle_time)

                remaining_work_days = "; ".join([f"{order}:{days_left}" for order, days_left in state['wip']])
                estimated_backlog_days = estimated_days_to_clear_backlog(len(state['backlog']), production_lines, production_cycle_time)

                output_data.append({
                    'Date': date,
                    'Backlog from Previous Day': backlog_from_previous_day,
                    'Production Cycle Time': production_cycle_time,
                    'Number of Production Lines': production_lines,
                    'New Customer Orders': new_orders,
                    'WIP Orders': len(state['wip']),
                    'Remaining Work Days on Orders in Progress': remaining_work_days,
                    'Orders Finished': len(completed_orders),
                    'Orders Pulled from Backlog': orders_pulled_from_backlog,
                    'Idle Production Lines': idle_lines,
                    'Estimated Days to Clear Backlog': estimated_backlog_days,
                })

            output_df = pd.DataFrame(output_data)
            st.write("### Production Simulation Report")
            st.dataframe(output_df)

if __name__ == "__main__":
    main()
