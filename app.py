import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to simulate the production process
def run_simulation(production_cycle_time, num_production_lines, new_customer_orders_per_day, num_days, initial_backlog):
    backlog = initial_backlog
    wip = []  # List of WIP orders with (order_id, days_left)
    completed_orders = []
    idle_lines = []
    daily_backlog = [backlog]  # Day 0 with initial backlog
    customer_wait_times = []
    wip_orders = [len(wip)]  # Track WIP orders on each day
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
        
        # Ensure backlog doesn't go negative
        backlog = max(0, backlog)
        
        # Update daily statistics
        daily_backlog.append(backlog)
        completed_orders.append(len(completed_today))  # Ensure completed orders are counted correctly
        idle_lines.append(idle_lines_today)
        customer_wait_times.append(backlog / max(1, num_production_lines * production_cycle_time))
        wip_orders.append(len(wip))  # Track WIP orders

        # Add new customer orders to the backlog
        backlog += new_customer_orders_per_day

    # Convert results to a DataFrame for display
    return pd.DataFrame({
        'Day': list(range(0, num_days + 1)),  # Adjusting for Day 0
        'Backlog': daily_backlog,
        'WIP Orders': wip_orders,  # New column for WIP
        'Completed Orders': [0] + completed_orders,  # No orders completed on Day 0
        'Idle Production Lines': [num_production_lines] + idle_lines,  # Idle lines on Day 0
        'Customer Wait Time (days)': [0] + customer_wait_times  # No wait on Day 0
    })

# Streamlit app interface
st.title("Production Simulation App")

# Sidebar for input elements
with st.sidebar:
    st.header("Simulation Inputs")
    production_cycle_time = st.number_input('Production Cycle Time (in days)', min_value=0.1, value=5.0, step=0.1, format="%.1f")
    num_production_lines = st.number_input('Number of Production Lines', min_value=1, value=3)
    new_customer_orders_per_day = st.number_input('Number of New Customer Orders per Day', min_value=0.1, value=1.0, step=0.1, format="%.1f")
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

    # Plotting idle production lines separately
    st.subheader("Idle Production Lines Over Time")
    fig, ax = plt.subplots()
    ax.plot(result['Day'], result['Idle Production Lines'], label='Idle Production Lines', color='blue')
    ax.set_xlabel('Day')
    ax.set_ylabel('Idle Lines')
    ax.legend()
    st.pyplot(fig)

    # Plotting customer wait times separately
    st.subheader("Customer Wait Times Over Time")
    fig, ax = plt.subplots()
    ax.plot(result['Day'], result['Customer Wait Time (days)'], label='Customer Wait Time (days)', color='orange')
    ax.set_xlabel('Day')
    ax.set_ylabel('Wait Time (days)')
    ax.legend()
    st.pyplot(fig)

    # Plotting WIP orders over time
    st.subheader("WIP Orders Over Time")
    fig, ax = plt.subplots()
    ax.plot(result['Day'], result['WIP Orders'], label='WIP Orders', color='green')
    ax.set_xlabel('Day')
    ax.set_ylabel('WIP Orders')
    ax.legend()
    st.pyplot(fig)
