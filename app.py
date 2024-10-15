import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to simulate the production process
def run_simulation(production_cycle_time, num_production_lines, new_customer_orders_per_day, num_days, initial_backlog):
    backlog = initial_backlog  # Orders not yet started (Backlog)
    wip = []  # Orders in progress with (order_id, days_left)
    completed_orders_count = 0  # Completed orders count
    daily_backlog = [backlog]  # Track backlog per day
    daily_wip = [len(wip)]  # Track WIP per day
    daily_completed_orders = [completed_orders_count]  # Track completed orders per day
    customer_wait_times = []
    order_id = 1  # Unique identifier for each order

    for day in range(1, num_days + 1):
        # 1. Move completed orders from WIP to Completed
        completed_today = [order for (order, days_left) in wip if days_left <= 0]
        completed_orders_count += len(completed_today)
        wip = [(order_id, days_left - 1) for (order_id, days_left) in wip if days_left > 0]

        # 2. Move new orders from backlog to WIP if production lines are available
        idle_lines_today = max(0, num_production_lines - len(wip))
        orders_to_start = min(idle_lines_today, backlog)
        wip.extend([(order_id + i, production_cycle_time) for i in range(orders_to_start)])
        backlog -= orders_to_start
        order_id += orders_to_start

        # 3. Add new customer orders to backlog
        backlog += new_customer_orders_per_day

        # 4. Track states for the day
        daily_backlog.append(backlog)
        daily_wip.append(len(wip))
        daily_completed_orders.append(completed_orders_count)

        # 5. Calculate customer wait time based on the backlog and production capacity
        customer_wait_times.append(backlog / max(1, num_production_lines * production_cycle_time))

    # Convert results to a DataFrame for display
    return pd.DataFrame({
        'Day': list(range(0, num_days + 1)),  # Adjusting for Day 0
        'Backlog (New Orders)': daily_backlog,
        'WIP Orders': daily_wip,
        'Completed Orders': daily_completed_orders,
        'Customer Wait Time (days)': [0] + customer_wait_times  # No wait on Day 0
    })

# Streamlit app interface
st.title("Production Simulation App")

# Sidebar for input elements
with st.sidebar:
    st.header("Simulation Inputs")
    production_cycle_time = st.number_input('Production Cycle Time (in days)', min_value=0.1, value=5.0, step=0.1, format="%.1f")
    num_production_lines = st.number_input('Number of Production Lines', min_value=1, value=3)
    new_customer_orders_per_day = st.number_input('Number of New Customer Orders per Day', min_value=0.1, value=1
