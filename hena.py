import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="Electricity Consumption Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .day-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .day-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .consumption-value {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .appliance-checkbox {
        font-size: 1.1rem;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 8px;
        background: #f8f9fa;
        transition: background 0.3s ease;
    }
    
    .appliance-checkbox:hover {
        background: #e9ecef;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 1px solid #2196f3;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(33, 150, 243, 0.2);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border: 1px solid #ff9800;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(255, 152, 0, 0.2);
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border: 1px solid #4caf50;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.2);
    }
    
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 10px;
    }
    
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("""
<div class="main-header">
    <h1>⚡ Smart Electricity Tracker</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">Advanced analytics for your daily electricity consumption patterns</p>
    <p style="font-size: 1rem; opacity: 0.8;">💡 Track • Analyze • Optimize • Save</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for configuration
st.sidebar.markdown("### 🏠 House Configuration")
bhk = st.sidebar.number_input("Enter your BHK:", min_value=1, max_value=10, value=2, step=1)
electricity_rate = st.sidebar.number_input("Electricity Rate (₹/kWh):", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

# Calculate base consumption
base_consumption = (bhk + 1) * 0.4 + (bhk + 1) * 0.8

st.sidebar.markdown(f"""
<div class="metric-card">
    <h4>⚡ Base Daily Consumption</h4>
    <div class="consumption-value">{base_consumption:.1f} kWh</div>
    <small>Based on {bhk} BHK configuration</small>
</div>
""", unsafe_allow_html=True)

# Sidebar settings
st.sidebar.markdown("### ⚙️ Display Settings")
show_predictions = st.sidebar.checkbox("Show Predictions", value=True)
show_comparisons = st.sidebar.checkbox("Show Comparisons", value=True)
chart_theme = st.sidebar.selectbox("Chart Theme", ["plotly", "plotly_dark", "plotly_white"])

# Days of the week
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
appliances = ["AC", "Fridge", "Washing Machine"]

# Initialize session state
if 'days_elec' not in st.session_state:
    st.session_state.days_elec = {}
if 'appliance_usage' not in st.session_state:
    st.session_state.appliance_usage = {day: {"AC": False, "Fridge": False, "Washing Machine": False} for day in days}

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Daily Input", "📊 Analytics Dashboard", "📈 Advanced Charts", "🎯 Insights & Tips", "💰 Cost Analysis"])

with tab1:
    st.markdown("### 📅 Daily Consumption Tracker")
    st.markdown("Select the appliances you used each day to track your electricity consumption.")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    for i, day in enumerate(days):
        current_col = col1 if i % 2 == 0 else col2
        
        with current_col:
            st.markdown(f"""
            <div class="day-card">
                <h4 style="color: #667eea; margin-bottom: 1rem;">{day}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate energy for this day
            cal_energy = base_consumption
            
            # Appliance checkboxes with icons
            appliance_icons = {"AC": "🌡️", "Fridge": "🧊", "Washing Machine": "🧺"}
            
            for appliance in appliances:
                checked = st.checkbox(
                    f"{appliance_icons[appliance]} {appliance} (+3 kWh)", 
                    key=f"{appliance.lower().replace(' ', '_')}_{day}",
                    value=st.session_state.appliance_usage[day][appliance]
                )
                st.session_state.appliance_usage[day][appliance] = checked
                if checked:
                    cal_energy += 3
            
            # Store in session state
            st.session_state.days_elec[day] = cal_energy
            
            # Display consumption with enhanced styling
            consumption_color = "#28a745" if cal_energy <= base_consumption + 3 else "#ffc107" if cal_energy <= base_consumption + 6 else "#dc3545"
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1.5rem; padding: 1rem; background: {consumption_color}20; border-radius: 10px;">
                <h5 style="margin: 0; color: {consumption_color};">Daily Consumption: {cal_energy:.1f} kWh</h5>
                <small style="color: #666;">Cost: ₹{cal_energy * electricity_rate:.2f}</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")

with tab2:
    st.markdown("### 📊 Consumption Analytics Dashboard")
    
    # Calculate statistics
    total_consumption = sum(st.session_state.days_elec.values())
    avg_consumption = total_consumption / 7 if st.session_state.days_elec else 0
    estimated_monthly = total_consumption * 4.33 * electricity_rate
    max_day = max(st.session_state.days_elec.items(), key=lambda x: x[1]) if st.session_state.days_elec else ("N/A", 0)
    min_day = min(st.session_state.days_elec.items(), key=lambda x: x[1]) if st.session_state.days_elec else ("N/A", 0)
    
    # Enhanced metrics with better styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔌 Total Weekly",
            value=f"{total_consumption:.1f} kWh",
            delta=f"{total_consumption - (base_consumption * 7):.1f} kWh"
        )
    
    with col2:
        st.metric(
            label="📊 Daily Average",
            value=f"{avg_consumption:.1f} kWh",
            delta=f"{avg_consumption - base_consumption:.1f} kWh"
        )
    
    with col3:
        st.metric(
            label="💰 Monthly Bill",
            value=f"₹{estimated_monthly:.0f}",
            delta=f"₹{(estimated_monthly - base_consumption * 30 * electricity_rate):.0f}"
        )
    
    with col4:
        st.metric(
            label="⚡ Peak Day",
            value=f"{max_day[1]:.1f} kWh",
            delta=f"{max_day[0]}"
        )
    
    # Enhanced bar chart with dual axis
    if st.session_state.days_elec:
        df_viz = pd.DataFrame(list(st.session_state.days_elec.items()), columns=['Day', 'Consumption'])
        df_viz['Cost'] = df_viz['Consumption'] * electricity_rate
        df_viz['Efficiency'] = df_viz['Consumption'] / base_consumption
        
        fig_bar = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Daily Consumption (kWh)', 'Daily Cost (₹)'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Consumption bar chart
        fig_bar.add_trace(
            go.Bar(
                x=df_viz['Day'],
                y=df_viz['Consumption'],
                name='Consumption',
                marker_color='#667eea',
                text=df_viz['Consumption'].round(1),
                textposition='auto',
            ),
            row=1, col=1
        )
        
        # Cost bar chart
        fig_bar.add_trace(
            go.Bar(
                x=df_viz['Day'],
                y=df_viz['Cost'],
                name='Cost',
                marker_color='#28a745',
                text=df_viz['Cost'].round(2),
                textposition='auto',
            ),
            row=1, col=2
        )
        
        fig_bar.add_hline(y=base_consumption, line_dash="dash", line_color="red", 
                         annotation_text="Base Consumption", row=1, col=1)
        fig_bar.add_hline(y=base_consumption * electricity_rate, line_dash="dash", line_color="red", 
                         annotation_text="Base Cost", row=1, col=2)
        
        fig_bar.update_layout(
            height=400,
            showlegend=False,
            template=chart_theme,
            title_text="Daily Consumption & Cost Analysis"
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Efficiency gauge
        avg_efficiency = df_viz['Efficiency'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_efficiency,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Efficiency Ratio (vs Base Consumption)"},
            delta={'reference': 1},
            gauge={
                'axis': {'range': [None, 3]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 1], 'color': "#28a745"},
                    {'range': [1, 1.5], 'color': "#ffc107"},
                    {'range': [1.5, 3], 'color': "#dc3545"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 2
                }
            }
        ))
        fig_gauge.update_layout(height=300, template=chart_theme)
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab3:
    st.markdown("### 📈 Advanced Visualization & Analytics")
    
    if st.session_state.days_elec:
        # Create enhanced dataframe
        df_viz = pd.DataFrame(list(st.session_state.days_elec.items()), columns=['Day', 'Consumption'])
        df_viz['Cost'] = df_viz['Consumption'] * electricity_rate
        df_viz['Day_Num'] = range(len(df_viz))
        
        # Calculate appliance contributions
        appliance_data = []
        for day in days:
            for appliance in appliances:
                if st.session_state.appliance_usage[day][appliance]:
                    appliance_data.append({'Day': day, 'Appliance': appliance, 'Consumption': 3})
        
        df_appliances = pd.DataFrame(appliance_data)
        
        # Multi-chart layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Radar chart for weekly pattern
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=df_viz['Consumption'].tolist(),
                theta=df_viz['Day'].tolist(),
                fill='toself',
                name='Weekly Pattern',
                line_color='#667eea'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(df_viz['Consumption']) * 1.1]
                    )),
                showlegend=False,
                title="Weekly Consumption Pattern",
                template=chart_theme,
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Stacked bar chart for appliance breakdown
            if not df_appliances.empty:
                fig_stack = px.bar(
                    df_appliances, 
                    x='Day', 
                    y='Consumption',
                    color='Appliance',
                    title='Appliance Usage Breakdown',
                    color_discrete_map={
                        'AC': '#ff6b6b',
                        'Fridge': '#4ecdc4',
                        'Washing Machine': '#45b7d1'
                    }
                )
                fig_stack.update_layout(height=400, template=chart_theme)
                st.plotly_chart(fig_stack, use_container_width=True)
            else:
                st.info("Select some appliances to see the breakdown chart.")
        
        # Heatmap for appliance usage
        heatmap_data = []
        for day in days:
            row = []
            for appliance in appliances:
                row.append(1 if st.session_state.appliance_usage[day][appliance] else 0)
            heatmap_data.append(row)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=appliances,
            y=days,
            colorscale='RdYlBu_r',
            text=heatmap_data,
            texttemplate="%{text}",
            textfont={"size": 16},
            hoverongaps=False
        ))
        fig_heatmap.update_layout(
            title="Appliance Usage Heatmap",
            template=chart_theme,
            height=400
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Time series with trend
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_viz['Day'],
            y=df_viz['Consumption'],
            mode='lines+markers',
            name='Actual Consumption',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        # Add trend line
        z = np.polyfit(df_viz['Day_Num'], df_viz['Consumption'], 1)
        p = np.poly1d(z)
        fig_trend.add_trace(go.Scatter(
            x=df_viz['Day'],
            y=p(df_viz['Day_Num']),
            mode='lines',
            name='Trend Line',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig_trend.add_hline(y=base_consumption, line_dash="dot", line_color="green", 
                           annotation_text="Base Consumption")
        
        fig_trend.update_layout(
            title="Consumption Trend Analysis",
            xaxis_title="Day",
            yaxis_title="Consumption (kWh)",
            template=chart_theme,
            height=400
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Distribution analysis
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                df_viz, 
                x='Consumption', 
                nbins=10,
                title='Consumption Distribution',
                color_discrete_sequence=['#667eea']
            )
            fig_hist.update_layout(template=chart_theme, height=300)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            fig_box = px.box(
                df_viz, 
                y='Consumption',
                title='Consumption Statistics',
                color_discrete_sequence=['#667eea']
            )
            fig_box.update_layout(template=chart_theme, height=300)
            st.plotly_chart(fig_box, use_container_width=True)

with tab4:
    st.markdown("### 🎯 Smart Insights & Energy Saving Tips")
    
    if st.session_state.days_elec:
        total_consumption = sum(st.session_state.days_elec.values())
        avg_consumption = total_consumption / 7
        
        # Smart insights
        if avg_consumption > base_consumption * 1.5:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ High Consumption Alert</h4>
                <p>Your average consumption is significantly higher than the base consumption. Consider optimizing appliance usage.</p>
            </div>
            """, unsafe_allow_html=True)
        elif avg_consumption < base_consumption * 1.2:
            st.markdown("""
            <div class="success-box">
                <h4>✅ Excellent Energy Efficiency</h4>
                <p>Great job! You're maintaining excellent energy efficiency with minimal excess consumption.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <h4>📊 Moderate Consumption</h4>
                <p>Your consumption is moderate. There's room for improvement with smart energy practices.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Personalized recommendations
        st.markdown("#### 💡 Personalized Recommendations")
        
        # Analyze appliance usage
        total_ac_usage = sum(1 for day in days if st.session_state.appliance_usage[day]["AC"])
        total_fridge_usage = sum(1 for day in days if st.session_state.appliance_usage[day]["Fridge"])
        total_wm_usage = sum(1 for day in days if st.session_state.appliance_usage[day]["Washing Machine"])
        
        recommendations = []
        
        if total_ac_usage > 5:
            recommendations.append("🌡️ Consider using AC more efficiently: Set temperature to 24°C, use timers, and ensure proper insulation.")
        
        if total_fridge_usage == 7:
            recommendations.append("🧊 Optimize fridge usage: Keep it well-organized, avoid frequent opening, and maintain proper temperature.")
        
        if total_wm_usage > 4:
            recommendations.append("🧺 Washing machine efficiency: Use cold water when possible, run full loads, and clean the filter regularly.")
        
        if not recommendations:
            recommendations.append("✨ You're doing great! Continue monitoring your usage patterns.")
        
        for rec in recommendations:
            st.markdown(f"• {rec}")
        
        # Potential savings calculation
        st.markdown("#### 💰 Potential Savings")
        
        potential_savings = []
        if total_ac_usage > 0:
            ac_savings = total_ac_usage * 3 * 0.2 * electricity_rate  # 20% savings possible
            potential_savings.append(f"AC optimization: ₹{ac_savings:.2f}/week")
        
        if total_fridge_usage > 0:
            fridge_savings = total_fridge_usage * 3 * 0.1 * electricity_rate  # 10% savings possible
            potential_savings.append(f"Fridge optimization: ₹{fridge_savings:.2f}/week")
        
        if potential_savings:
            st.success(f"Potential weekly savings: {', '.join(potential_savings)}")
    else:
        st.info("Enter your daily consumption data to get personalized insights and recommendations.")

with tab5:
    st.markdown("### 💰 Detailed Cost Analysis")
    
    if st.session_state.days_elec:
        df_viz = pd.DataFrame(list(st.session_state.days_elec.items()), columns=['Day', 'Consumption'])
        df_viz['Cost'] = df_viz['Consumption'] * electricity_rate
        df_viz['Base_Cost'] = base_consumption * electricity_rate
        df_viz['Extra_Cost'] = df_viz['Cost'] - df_viz['Base_Cost']
        
        # Cost metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Weekly Cost", f"₹{df_viz['Cost'].sum():.2f}")
        
        with col2:
            st.metric("Daily Average", f"₹{df_viz['Cost'].mean():.2f}")
        
        with col3:
            st.metric("Monthly Estimate", f"₹{df_viz['Cost'].sum() * 4.33:.2f}")
        
        with col4:
            st.metric("Annual Estimate", f"₹{df_viz['Cost'].sum() * 52:.2f}")
        
        # Cost breakdown charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily cost breakdown
            fig_cost_bar = px.bar(
                df_viz, 
                x='Day', 
                y=['Base_Cost', 'Extra_Cost'],
                title='Daily Cost Breakdown',
                color_discrete_map={'Base_Cost': '#28a745', 'Extra_Cost': '#dc3545'}
            )
            fig_cost_bar.update_layout(template=chart_theme, height=400)
            st.plotly_chart(fig_cost_bar, use_container_width=True)
        
        with col2:
            # Cost vs consumption scatter
            fig_scatter = px.scatter(
                df_viz, 
                x='Consumption', 
                y='Cost',
                size='Extra_Cost',
                color='Day',
                title='Cost vs Consumption Analysis',
                hover_data=['Day', 'Consumption', 'Cost']
            )
            fig_scatter.update_layout(template=chart_theme, height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Cost comparison table
        st.markdown("#### 📊 Detailed Cost Breakdown")
        df_display = df_viz.copy()
        df_display['Efficiency'] = (df_display['Consumption'] / base_consumption).round(2)
        df_display = df_display.round(2)
        
        st.dataframe(
            df_display[['Day', 'Consumption', 'Cost', 'Base_Cost', 'Extra_Cost', 'Efficiency']],
            use_container_width=True
        )
        
        # Rate comparison
        st.markdown("#### ⚖️ Rate Comparison Impact")
        rates = [3, 4, 5, 6, 7, 8]
        total_consumption = df_viz['Consumption'].sum()
        
        comparison_data = []
        for rate in rates:
            weekly_cost = total_consumption * rate
            monthly_cost = weekly_cost * 4.33
            comparison_data.append({
                'Rate (₹/kWh)': rate,
                'Weekly Cost': f"₹{weekly_cost:.2f}",
                'Monthly Cost': f"₹{monthly_cost:.2f}",
                'Annual Cost': f"₹{weekly_cost * 52:.2f}"
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
    else:
        st.info("Enter your daily consumption data to see detailed cost analysis.")

# Footer with additional info
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px;">
    <h4>🌟 Energy Efficiency Tips</h4>
    <p>💡 Use LED bulbs • 🌡️ Optimize AC temperature • 🧊 Keep fridge well-organized • 🧺 Run full loads in washing machine</p>
    <p><strong>Built with ❤️ using Streamlit • Enhanced with Plotly Visualizations</strong></p>
</div>
""", unsafe_allow_html=True)

# Export functionality
if st.session_state.days_elec:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Options")
    
    # Create comprehensive export data
    export_data = []
    for day in days:
        row = {
            'Day': day,
            'Consumption_kWh': st.session_state.days_elec.get(day, 0),
            'Cost_INR': st.session_state.days_elec.get(day, 0) * electricity_rate,
            'AC_Used': st.session_state.appliance_usage[day]["AC"],
            'Fridge_Used': st.session_state.appliance_usage[day]["Fridge"],
            'Washing_Machine_Used': st.session_state.appliance_usage[day]["Washing Machine"]
        }
        export_data.append(row)
    
    df_export = pd.DataFrame(export_data)
    
    # Add summary row
    summary_row = {
        'Day': 'TOTAL/AVERAGE',
        'Consumption_kWh': df_export['Consumption_kWh'].sum(),
        'Cost_INR': df_export['Cost_INR'].sum(),
        'AC_Used': df_export['AC_Used'].sum(),
        'Fridge_Used': df_export['Fridge_Used'].sum(),
        'Washing_Machine_Used': df_export['Washing_Machine_Used'].sum()
    }
    df_export = pd.concat([df_export, pd.DataFrame([summary_row])], ignore_index=True)
    
    csv = df_export.to_csv(index=False)
    st.sidebar.download_button(
        label="📊 Download Detailed Report (CSV)",
        data=csv,
        file_name=f"electricity_consumption_report_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Quick stats in sidebar
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Total Consumption", f"{sum(st.session_state.days_elec.values()):.1f} kWh")
    st.sidebar.metric("Total Cost", f"₹{sum(st.session_state.days_elec.values()) * electricity_rate:.2f}")
    st.sidebar
