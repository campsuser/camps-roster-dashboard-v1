import streamlit as st
import pandas as pd
import os
import plotly.express as px
from data_loader import (
    load_member_data, 
    get_county_metrics, 
    get_sector_metrics,
    get_monthly_renewal_metrics,
    get_health_trust_penetration,
    get_health_trust_prospects,
    MONTH_ORDER
)

# Set page configurations
st.set_page_config(
    page_title="CAMPS Membership Intelligence Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Theme & Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Core Font Styling */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Elegant Title and Header styling */
    .dashboard-title {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
    }
    
    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-bottom: 1.5rem;
    }
    
    /* Premium Glassmorphic Card Styling */
    .kpi-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 22px;
        text-align: left;
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 242, 254, 0.6);
        box-shadow: 0 8px 30px rgba(0, 242, 254, 0.25);
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
        margin-top: 5px;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    
    /* Sidebar Metric Styling */
    .sidebar-metric {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .sidebar-metric-title {
        font-size: 0.85rem;
        color: #cbd5e1;
        font-weight: 600;
    }
    
    .sidebar-metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #00f2fe;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #f8fafc;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #00f2fe;
        padding-left: 12px;
    }
    
    /* Profile Contact Card Layout */
    .profile-card {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }
    
    .profile-company {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 5px;
    }
    
    .profile-category {
        display: inline-block;
        background: rgba(0, 242, 254, 0.15);
        border: 1px solid rgba(0, 242, 254, 0.3);
        color: #00f2fe;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 20px;
        text-transform: uppercase;
    }
    
    .profile-detail-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 2px;
    }
    
    .profile-detail-value {
        font-size: 1.1rem;
        color: #f1f5f9;
        font-weight: 500;
        margin-bottom: 15px;
    }
    
    .profile-notes {
        background: rgba(245, 158, 11, 0.08);
        border: 1px dashed rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 15px;
        color: #fef3c7;
        margin-top: 15px;
        font-size: 0.95rem;
    }
    
    .website-button {
        display: inline-block;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #0f172a !important;
        font-weight: 600;
        padding: 10px 22px;
        border-radius: 8px;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-top: 10px;
        text-align: center;
        text-decoration: none;
    }
    
    .website-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to create premium KPI cards
def render_kpi_card(label, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

# Load membership data
try:
    df_raw = load_member_data()
except Exception as e:
    st.error(f"Error loading CSV data: {e}")
    st.stop()

# --- SIDEBAR: COUNTY METRICS AND FILTERS ---
st.sidebar.markdown("<h2 style='color:#ffffff; margin-bottom: 0.5rem;'>CAMPS Hub</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color:#94a3b8; font-size:0.9rem; margin-bottom: 1.5rem;'>Washington Manufacturing Network</p>", unsafe_allow_html=True)

# Sidebar County Metrics
st.sidebar.markdown("<div style='border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='color:#ffffff; font-size:1.1rem; margin-bottom:10px;'>County Member Share</h3>", unsafe_allow_html=True)

county_summary = get_county_metrics(df_raw)
top_counties = county_summary.head(4)
other_count = county_summary.iloc[4:]['member_count'].sum() if len(county_summary) > 4 else 0

for idx, row in top_counties.iterrows():
    st.sidebar.markdown(f"""
    <div class="sidebar-metric">
        <div class="sidebar-metric-title">{row['County']} County</div>
        <div class="sidebar-metric-value">{row['member_count']} <span style='font-size: 0.8rem; color: #94a3b8; font-weight: normal;'>({row['percentage']}%)</span></div>
    </div>
    """, unsafe_allow_html=True)

if other_count > 0:
    total_members = len(df_raw)
    other_percentage = round((other_count / total_members) * 100, 1)
    st.sidebar.markdown(f"""
    <div class="sidebar-metric">
        <div class="sidebar-metric-title">Other Areas</div>
        <div class="sidebar-metric-value">{other_count} <span style='font-size: 0.8rem; color: #94a3b8; font-weight: normal;'>({other_percentage}%)</span></div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.markdown("<div style='border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; margin-top: 1.5rem; margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='color:#ffffff; font-size:1.1rem; margin-bottom:10px;'>Filters</h3>", unsafe_allow_html=True)

all_counties = sorted([c for c in df_raw['County'].unique() if pd.notna(c)])
all_sectors = sorted([s for s in df_raw['Sector'].unique() if pd.notna(s)])

selected_counties = st.sidebar.multiselect(
    "Filter by County",
    options=all_counties,
    placeholder="Showing all counties"
)

selected_sectors = st.sidebar.multiselect(
    "Filter by Category",
    options=all_sectors,
    placeholder="Showing all categories"
)

# Apply filters
df_filtered = df_raw.copy()
if selected_counties:
    df_filtered = df_filtered[df_filtered['County'].isin(selected_counties)]
if selected_sectors:
    df_filtered = df_filtered[df_filtered['Sector'].isin(selected_sectors)]

# --- MAIN HEADER ---
st.markdown("<h1 class='dashboard-title'>CAMPS Membership Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p class='dashboard-subtitle'>Regional Manufacturing Innovation & Infrastructure</p>", unsafe_allow_html=True)

# Define Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Executive Overview", 
    "📅 Renewal Pipeline", 
    "🏥 Health Trust Intelligence", 
    "🔍 Member Profiles & Search"
])

theme_colors = ['#00f2fe', '#4facfe', '#6366f1', '#a855f7', '#ec4899', '#3b82f6', '#10b981', '#f59e0b']

# ==============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# ==============================================================================
with tab1:
    # KPI Cards Row
    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        st.markdown(render_kpi_card("Total Registered Members", len(df_filtered)), unsafe_allow_html=True)
    with kpi_cols[1]:
        active_counties_count = df_filtered['County'].nunique()
        st.markdown(render_kpi_card("Active Counties & Areas", active_counties_count), unsafe_allow_html=True)
    with kpi_cols[2]:
        active_sectors_count = df_filtered['Sector'].nunique()
        st.markdown(render_kpi_card("Categories Represented", active_sectors_count), unsafe_allow_html=True)

    # Visualizations Row
    st.markdown("<div class='section-header'>Regional Breakdown</div>", unsafe_allow_html=True)
    chart_cols = st.columns(2)

    # Chart 1: Members by County
    with chart_cols[0]:
        st.markdown("<h4 style='color:#94a3b8; margin-bottom: 15px;'>Member Concentration by County</h4>", unsafe_allow_html=True)
        if len(df_filtered) > 0:
            county_counts = df_filtered['County'].value_counts().reset_index()
            county_counts.columns = ['County', 'Members']
            
            fig_county = px.bar(
                county_counts.head(10),  # top 10
                x='County', y='Members', text='Members',
                color='County', color_discrete_sequence=theme_colors
            )
            fig_county.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_family='Outfit', font_color='#ffffff', showlegend=False,
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None),
                margin=dict(l=0, r=0, t=10, b=0), height=280
            )
            fig_county.update_traces(textposition='outside', opacity=0.9)
            st.plotly_chart(fig_county, use_container_width=True)
        else:
            st.info("No data available for selected filters.")

    # Chart 2: Members by Sector
    with chart_cols[1]:
        st.markdown("<h4 style='color:#94a3b8; margin-bottom: 15px;'>Categories Representation</h4>", unsafe_allow_html=True)
        if len(df_filtered) > 0:
            sector_counts = df_filtered['Sector'].value_counts().reset_index()
            sector_counts.columns = ['Sector', 'Members']
            
            fig_sector = px.bar(
                sector_counts,
                x='Members', y='Sector', orientation='h', text='Members',
                color='Sector', color_discrete_sequence=theme_colors
            )
            fig_sector.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_family='Outfit', font_color='#ffffff', showlegend=False,
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None),
                yaxis=dict(showgrid=False, title=None),
                margin=dict(l=0, r=0, t=10, b=0), height=280
            )
            fig_sector.update_traces(textposition='outside', opacity=0.9)
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            st.info("No data available for selected filters.")

    # Data Table
    st.markdown("<div class='section-header'>Member Directory</div>", unsafe_allow_html=True)
    if len(df_filtered) > 0:
        display_df = df_filtered[[
            'Company Name', 'Sector', 'County', 'City', 
            'Renewal Month', 'Website', 'CAMPS Health Trust'
        ]].copy()
        
        display_df['Website'] = display_df['Website'].fillna('')
        display_df['Renewal Month'] = display_df['Renewal Month'].fillna('N/A')
        
        st.dataframe(
            display_df,
            column_config={
                "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                "Sector": st.column_config.TextColumn("Category", width="medium"),
                "County": st.column_config.TextColumn("County", width="small"),
                "City": st.column_config.TextColumn("City", width="small"),
                "Renewal Month": st.column_config.TextColumn("Renewal Month", width="small"),
                "Website": st.column_config.LinkColumn("Website", width="medium"),
                "CAMPS Health Trust": st.column_config.TextColumn("Health Trust", width="small"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("No companies match the filter criteria.")

# ==============================================================================
# TAB 2: RENEWAL PIPELINE & RETENTION
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>Renewal Pipeline & Retention Risks</div>", unsafe_allow_html=True)
    
    # Calculate renewal alerts
    bounced_members = df_filtered[df_filtered['Notes'].str.upper().str.contains('BOUNCED', na=False)]
    opted_out_members = df_filtered[df_filtered['Notes'].str.upper().str.contains('OPTED OUT', na=False)]
    
    # Row 1: KPI Cards
    ren_kpi_cols = st.columns(3)
    with ren_kpi_cols[0]:
        total_valid_renewals = len(df_filtered[df_filtered['Renewal Month Standardized'] != 'N/A'])
        st.markdown(render_kpi_card("Tracked Renewals", total_valid_renewals), unsafe_allow_html=True)
    with ren_kpi_cols[1]:
        st.markdown(render_kpi_card("Bounced Contacts (Alerts)", len(bounced_members)), unsafe_allow_html=True)
    with ren_kpi_cols[2]:
        st.markdown(render_kpi_card("Opted Out Communications", len(opted_out_members)), unsafe_allow_html=True)
        
    # Row 2: Charts & Flags
    ren_cols = st.columns([2, 1])
    
    with ren_cols[0]:
        st.markdown("<h4 style='color:#94a3b8; margin-bottom: 15px;'>Chronological Monthly Renewal Forecast</h4>", unsafe_allow_html=True)
        renewal_metrics = get_monthly_renewal_metrics(df_filtered)
        if len(renewal_metrics) > 0:
            fig_renewal = px.bar(
                renewal_metrics,
                x='Renewal Month Standardized', y='member_count',
                text='member_count',
                color_discrete_sequence=['#4facfe']
            )
            fig_renewal.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_family='Outfit', font_color='#ffffff', showlegend=False,
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title=None),
                margin=dict(l=0, r=0, t=10, b=0), height=300
            )
            fig_renewal.update_traces(textposition='outside', opacity=0.9)
            st.plotly_chart(fig_renewal, use_container_width=True)
        else:
            st.info("No structured renewal month data found.")
            
    with ren_cols[1]:
        st.markdown("<h4 style='color:#94a3b8; margin-bottom: 15px;'>Retention Risk Alerts</h4>", unsafe_allow_html=True)
        alerts_df = pd.concat([bounced_members, opted_out_members]).drop_duplicates(subset=['Company Name'])
        
        if len(alerts_df) > 0:
            st.dataframe(
                alerts_df[['Company Name', 'Notes']],
                column_config={
                    "Company Name": st.column_config.TextColumn("Company", width="medium"),
                    "Notes": st.column_config.TextColumn("Alert Reason", width="medium"),
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.success("🎉 No active email bounces or opt-out flags in filtered data.")
            
    # Row 3: Upcoming Renewals Filter Table
    st.markdown("<div class='section-header'>Renewal Search Directory</div>", unsafe_allow_html=True)
    all_months = ['ALL'] + list(MONTH_ORDER.keys())
    selected_month = st.selectbox("Select Renewal Month to Inspect", options=all_months)
    
    if selected_month == 'ALL':
        renewal_detail_df = df_filtered[df_filtered['Renewal Month Standardized'] != 'N/A']
    else:
        renewal_detail_df = df_filtered[df_filtered['Renewal Month Standardized'] == selected_month]
        
    if len(renewal_detail_df) > 0:
        st.dataframe(
            renewal_detail_df[['Company Name', 'Sector', 'City', 'Renewal Month', 'Notes']],
            column_config={
                "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                "Sector": st.column_config.TextColumn("Category", width="medium"),
                "City": st.column_config.TextColumn("City", width="small"),
                "Renewal Month": st.column_config.TextColumn("Renewal Details", width="medium"),
                "Notes": st.column_config.TextColumn("Notes", width="large")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info(f"No memberships renewing in {selected_month.capitalize()} for current filters.")

# ==============================================================================
# TAB 3: HEALTH TRUST INTELLIGENCE
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>CAMPS Health Trust Analytics & Targets</div>", unsafe_allow_html=True)
    
    # Calculate global trust metrics
    total_trust = len(df_filtered[df_filtered['CAMPS Health Trust'].str.upper() == 'YES'])
    total_non_trust = len(df_filtered[df_filtered['CAMPS Health Trust'].str.upper() != 'YES'])
    trust_percentage = round((total_trust / len(df_filtered)) * 100, 1) if len(df_filtered) > 0 else 0
    
    prospects = get_health_trust_prospects(df_filtered)
    
    # KPI Row
    ht_kpi_cols = st.columns(3)
    with ht_kpi_cols[0]:
        st.markdown(render_kpi_card("Enrolled Members", total_trust), unsafe_allow_html=True)
    with ht_kpi_cols[1]:
        st.markdown(render_kpi_card("Trust Penetration Rate", f"{trust_percentage}%"), unsafe_allow_html=True)
    with ht_kpi_cols[2]:
        st.markdown(render_kpi_card("Qualified Cross-Sell Prospects", len(prospects)), unsafe_allow_html=True)
        
    # Chart Row
    ht_cols = st.columns([1, 1])
    
    with ht_cols[0]:
        st.markdown("<h4 style='color:#94a3b8; margin-bottom: 15px;'>Health Trust Penetration by Member Category</h4>", unsafe_allow_html=True)
        penetration_df = get_health_trust_penetration(df_filtered)
        if len(penetration_df) > 0:
            fig_penetration = px.bar(
                penetration_df,
                x='enrollment_rate', y='Sector',
                orientation='h', text=penetration_df['enrollment_rate'].apply(lambda x: f"{x}%"),
                color='Sector', color_discrete_sequence=theme_colors
            )
            fig_penetration.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_family='Outfit', font_color='#ffffff', showlegend=False,
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Penetration Rate (%)"),
                yaxis=dict(showgrid=False, title=None),
                margin=dict(l=0, r=0, t=10, b=0), height=300
            )
            fig_penetration.update_traces(textposition='outside', opacity=0.9)
            st.plotly_chart(fig_penetration, use_container_width=True)
        else:
            st.info("No category trust data available.")
            
    with ht_cols[1]:
        st.markdown("<h4 style='color:#94a3b8; margin-bottom: 15px;'>Participation Mix (Pie Chart)</h4>", unsafe_allow_html=True)
        pie_data = pd.DataFrame({
            'Status': ['Enrolled (Yes)', 'Not Enrolled / Other'],
            'Count': [total_trust, total_non_trust]
        })
        fig_pie = px.pie(
            pie_data, values='Count', names='Status',
            color_discrete_sequence=['#00f2fe', '#1e293b'],
            hole=0.4
        )
        fig_pie.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_family='Outfit', font_color='#ffffff',
            margin=dict(l=0, r=0, t=10, b=0), height=300
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Lead list generator
    st.markdown("<div class='section-header'>Qualified Cross-Sell Leads List</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#cbd5e1; font-size:0.95rem; margin-bottom:15px;'>The list below displays manufacturers and supply chain members who are not enrolled in the CAMPS Health Trust. These represent qualified outreach opportunities.</p>", unsafe_allow_html=True)
    
    if len(prospects) > 0:
        display_prospects = prospects[[
            'Company Name', 'Sector', 'County', 'City', 'Website'
        ]].copy()
        
        st.dataframe(
            display_prospects,
            column_config={
                "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                "Sector": st.column_config.TextColumn("Category", width="medium"),
                "County": st.column_config.TextColumn("County", width="small"),
                "City": st.column_config.TextColumn("City", width="small"),
                "Website": st.column_config.LinkColumn("Website Link", width="medium")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("🎉 All manufacturer and supply chain members are enrolled in the Health Trust!")

# ==============================================================================
# TAB 4: MEMBER PROFILES & SEARCH
# ==============================================================================
with tab4:
    st.markdown("<div class='section-header'>Single Member Lookup & Profiles</div>", unsafe_allow_html=True)
    
    # Selected member
    member_list = sorted(df_raw['Company Name'].unique())
    selected_member = st.selectbox("Search and Select a Company", options=member_list, placeholder="Start typing...")
    
    if selected_member:
        comp_data = df_raw[df_raw['Company Name'] == selected_member].iloc[0]
        
        # Profile details card
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-company">{comp_data['Company Name']}</div>
            <div class="profile-category">{comp_data['Sector']}</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                <div>
                    <div class="profile-detail-label">City & County</div>
                    <div class="profile-detail-value">{comp_data['City']}, {comp_data['County']} County</div>
                    <div class="profile-detail-label">Address</div>
                    <div class="profile-detail-value">{comp_data['Address'] if pd.notna(comp_data['Address']) and comp_data['Address'].strip() else 'N/A'}</div>
                    <div class="profile-detail-label">Zip Code</div>
                    <div class="profile-detail-value">{comp_data['Zip'] if pd.notna(comp_data['Zip']) and str(comp_data['Zip']).strip() else 'N/A'}</div>
                </div>
                <div>
                    <div class="profile-detail-label">Renewal Month</div>
                    <div class="profile-detail-value">{comp_data['Renewal Month'] if pd.notna(comp_data['Renewal Month']) and str(comp_data['Renewal Month']).strip() else 'N/A'}</div>
                    <div class="profile-detail-label">CAMPS Health Trust Status</div>
                    <div class="profile-detail-value">
                        <span style="color: {'#00f2fe' if comp_data['CAMPS Health Trust'].upper() == 'YES' else '#f87171'}; font-weight: bold;">
                            {comp_data['CAMPS Health Trust']}
                        </span>
                    </div>
                    <div class="profile-detail-label">Roster Reference Row</div>
                    <div class="profile-detail-value">Row #{int(comp_data['Original Row']) if pd.notna(comp_data['Original Row']) else 'N/A'}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Render notes block if present
        notes_str = comp_data['Notes']
        if pd.notna(notes_str) and notes_str.strip():
            st.markdown(f"""
            <div class="profile-notes">
                <strong>📝 Administrative Notes & Directives:</strong><br>
                {notes_str}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True) # close profile-card
        
        # Clickable website redirect button
        web_url = comp_data['Website']
        if pd.notna(web_url) and web_url.strip():
            # Add protocol prefix if missing
            url_clean = str(web_url).strip()
            if not url_clean.startswith(('http://', 'https://')):
                url_clean = 'https://' + url_clean
            
            st.markdown(f'<a href="{url_clean}" target="_blank" class="website-button">🌐 Visit Company Website</a>', unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#94a3b8; font-style:italic; margin-top: 15px;'>No website URL registered for this member company.</p>", unsafe_allow_html=True)
