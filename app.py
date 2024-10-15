import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to simulate the production process
def run_simulation(production_cycle_time, num_production_lines, new_customer_orders_per_day, num_days, initial_backlog):
    backlog = initial_backlog
    wip = []
    completed_orders = []
    idle_lines = []
    daily_backlog = []
    customer_wait_times = []
    order_id = 1

    for day in range(1, num_days + 1):
        # Process work in progress (WIP)
        completed_today = [order_id for (order_id, days_left) in wip if days_left == 1]
        wip = [(order_id, days_left - 1) for (order_id, days_left) in wip if days_left > 1]
        
        idle_lines_today = max(0, num_production_lines - len(wip))
        
        # Pull orders from the backlog if lines are available
        while idle_lines_today > 0 and backlog > 0:
            wip.append((order_id, production_cycle_time))
            backlog -= 1
            order_id += 1
            idle_lines_today -= 1
        
        # Update daily statistics
        daily_backlog.append(backlog)
        completed_orders.append(len(completed_today))
        idle_lines.append(idle_lines_today)
        customer_wait_times.append(backlog / max(1, num_production_lines * production_cycle_time))
        
        # Add new customer orders to the backlog
        backlog += new_customer_orders_per_day

    # Convert results to a DataFrame for display
    return pd.DataFrame({
        'Day': list(range(1, num_days + 1)),
        'Backlog': daily_backlog,
        'Completed Orders': completed_orders,
        'Idle Production Lines': idle_lines,
        'Customer Wait Time (days)': customer_wait_times
    })

# Streamlit app interface
st.title("Production Simulation App")

# Input elements
production_cycle_time = st.number_input('Production Cycle Time (in days)', min_value=1, value=5)
num_production_lines = st.number_input('Number of Production Lines', min_value=1, value=3)
new_customer_orders_per_day = st.number_input('Number of New Customer Orders per Day', min_value=1, value=10)
num_days = st.slider('Simulation Time Frame (Number of Business Days)', min_value=1, max_value=100, value=30)
initial_backlog = st.number_input('Initial Backlog of Orders', min_value=0, value=20)

# Run the simulation
if st.button('Run Simulation'):
    result = run_simulation(production_cycle_time, num_production_lines, new_customer_orders_per_day, num_days, initial_backlog)

    # Output results
    st.subheader("Simulation Results")
    st.dataframe(result)

    # Plotting backlog and completed orders
    st.subheader("Backlog and Completed Orders Over Time")
    fig, ax = plt.subplots()
    ax.plot(result['Day'], result['Backlog'], label='Backlog')
    ax.plot(result['Day'], result['Completed Orders'], label='Completed Orders')
    ax.set_xlabel('Day')
    ax.set_ylabel('Orders')
    ax.legend()
    st.pyplot(fig)

    # Plotting idle production lines and customer wait times
    st.subheader("Idle Production Lines and Customer Wait Times")
    fig, ax = plt.subplots()
    ax.plot(result['Day'], result['Idle Production Lines'], label='Idle Production Lines')
    ax.plot(result['Day'], result['Customer Wait Time (days)'], label='Customer Wait Time (days)', color='orange')
    ax.set_xlabel('Day')
    ax.set_ylabel('Lines / Wait Time (days)')
    ax.legend()
    st.pyplot(fig)

    # Order summary
    st.subheader("Order Summary Table")
    st.write(result)
