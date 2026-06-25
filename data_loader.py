import os
import pandas as pd

# Detailed dictionary mapping Washington cities in the dataset to their counties
CITY_TO_COUNTY = {
    # Snohomish County
    'everett': 'Snohomish',
    'mukilteo': 'Snohomish',
    'lynnwood': 'Snohomish',
    'sulton': 'Snohomish',  # raw data misspelling of Sultan
    'sultan': 'Snohomish',
    'mountlake terrace': 'Snohomish',
    'marysville': 'Snohomish',
    'snohomish': 'Snohomish',
    'monroe': 'Snohomish',
    'arlington': 'Snohomish',
    'mill creek': 'Snohomish',
    'edmonds': 'Snohomish',
    
    # King County
    'tukwila': 'King',
    'seattle': 'King',
    'renton': 'King',
    'enumclaw': 'King',
    'woodinville': 'King',
    'bellevue': 'King',
    'maple valley': 'King',
    'kent': 'King',
    'auburn': 'King',
    'mercer island': 'King',
    'redmond': 'King',
    'issaquah': 'King',
    'kirkland': 'King',
    'seatac': 'King',
    'shoreline': 'King',
    'vashon': 'King',
    
    # Pierce County
    'tacoma': 'Pierce',
    'sumner': 'Pierce',
    'fife': 'Pierce',
    'gig harbor': 'Pierce',
    'puyallup': 'Pierce',
    
    # Whatcom County
    'bellingham': 'Whatcom',
    'lynden': 'Whatcom',
    'custer': 'Whatcom',
    'blaine': 'Whatcom',
    'sumas': 'Whatcom',
    
    # Skagit County
    'anacortes': 'Skagit',
    'mount vernon': 'Skagit',
    'burlington': 'Skagit',
    'sedro woolley': 'Skagit',
    'sedro wooley': 'Skagit', # raw data misspelling
    
    # Benton County
    'kennewick': 'Benton',
    'prosser': 'Benton',
    
    # Spokane County
    'spokane': 'Spokane',
    
    # Franklin County
    'mesa': 'Franklin',
    
    # Thurston County
    'tumwater': 'Thurston',
    'olympia': 'Thurston',
    
    # Kitsap County
    'poulsbo': 'Kitsap',
    'bainbridge island': 'Kitsap',
    
    # Jefferson County
    'port hadlock': 'Jefferson',
    'port townsend': 'Jefferson',
    
    # Chelan County
    'chelan': 'Chelan',
    'leavenworth': 'Chelan',
    
    # Grays Harbor County
    'oakville': 'Grays Harbor',
    
    # Kittitas County
    'thorp': 'Kittitas',
    
    # Skamania County
    'underwood': 'Skamania',
    
    # Klickitat County
    'wishrom': 'Klickitat', # raw data misspelling
    'wishram': 'Klickitat',
    'goldendale': 'Klickitat',
    
    # Walla Walla County
    'walla walla': 'Walla Walla',
    'lowden': 'Walla Walla',
    
    # Yakima County
    'yakima': 'Yakima',
    'wapato': 'Yakima',
    
    # Adams County
    'othello': 'Adams',
    
    # Mason County
    'belfair': 'Mason',
    
    # Lincoln County
    'odessa': 'Lincoln',
    
    # Clark County
    'vancouver': 'Clark',
}

# Standard month ordering for renewal timeline
MONTH_ORDER = {
    'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4, 'MAY': 5, 'JUNE': 6,
    'JULY': 7, 'AUGUST': 8, 'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
}

def map_city_to_county(city):
    if pd.isna(city):
        return "Unknown"
    
    city_clean = str(city).strip().lower()
    if not city_clean:
        return "Unknown"
        
    # Handle out of state formats e.g. "Tensed, ID"
    if ',' in city_clean:
        parts = city_clean.split(',')
        state = parts[-1].strip()
        if state in ['id', 'idaho', 'or', 'oregon', 'ca', 'california']:
            return f"Out of State ({state.upper()})"
            
    # Check direct dictionary mapping
    if city_clean in CITY_TO_COUNTY:
        return CITY_TO_COUNTY[city_clean]
        
    return "Other County"

def load_member_data(filepath="members.csv"):
    """
    Loads and cleans the member data from the raw CSV file.
    Renames columns to maintain UI compatibility and maps City to County.
    """
    if not os.path.exists(filepath):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filepath)
        
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Member data file not found at {filepath}")
        
    df = pd.read_csv(filepath)
    
    # Strip whitespace from column headers
    df.columns = [col.strip() for col in df.columns]
    
    # Drop completely empty rows if they exist
    df = df.dropna(how='all')
    
    # Normalize string values in all text columns, keeping NaNs as empty strings
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].fillna('').astype(str).str.strip()
        
    # Rename columns for compatibility with the app UI
    df = df.rename(columns={
        'Company': 'Company Name',
        'Category': 'Sector'
    })
    
    # Apply city-to-county mapping
    df['County'] = df['City'].apply(map_city_to_county)
    
    # Standardize Renewal Month (clean up trailing notes like "** Renews June **;")
    def clean_renewal_month(m):
        m_str = str(m).upper()
        for month in MONTH_ORDER.keys():
            if month in m_str:
                return month
        return 'N/A'
        
    df['Renewal Month Standardized'] = df['Renewal Month'].apply(clean_renewal_month)
    
    return df

def get_county_metrics(df):
    """
    Returns summarized metrics for counties.
    """
    metrics = df.groupby('County').agg(
        member_count=('Company Name', 'count')
    ).reset_index()
    
    total_members = len(df)
    metrics['percentage'] = (metrics['member_count'] / total_members * 100).round(1)
    metrics = metrics.sort_values(by='member_count', ascending=False).reset_index(drop=True)
    return metrics

def get_sector_metrics(df):
    """
    Returns summarized metrics for sectors (categories).
    """
    metrics = df.groupby('Sector').agg(
        member_count=('Company Name', 'count')
    ).reset_index()
    
    total_members = len(df)
    metrics['percentage'] = (metrics['member_count'] / total_members * 100).round(1)
    metrics = metrics.sort_values(by='member_count', ascending=False).reset_index(drop=True)
    return metrics

def get_monthly_renewal_metrics(df):
    """
    Groups member count by renewal month, sorted chronologically.
    """
    # Exclude N/A from chronological sorting or place it at the end
    df_valid = df[df['Renewal Month Standardized'] != 'N/A']
    
    metrics = df_valid.groupby('Renewal Month Standardized').agg(
        member_count=('Company Name', 'count')
    ).reset_index()
    
    # Map to month order index for sorting
    metrics['Month Index'] = metrics['Renewal Month Standardized'].map(MONTH_ORDER)
    metrics = metrics.sort_values(by='Month Index').drop(columns=['Month Index']).reset_index(drop=True)
    
    return metrics

def get_health_trust_penetration(df):
    """
    Computes Health Trust participation count and enrollment rate by Sector.
    """
    # Group by Sector and calculate stats
    grouped = df.groupby('Sector').agg(
        total_members=('Company Name', 'count'),
        enrolled_members=('CAMPS Health Trust', lambda x: (x.str.upper() == 'YES').sum())
    ).reset_index()
    
    grouped['enrollment_rate'] = (grouped['enrolled_members'] / grouped['total_members'] * 100).round(1)
    return grouped.sort_values(by='total_members', ascending=False).reset_index(drop=True)

def get_health_trust_prospects(df):
    """
    Generates a lead list of Manufacturers or Supply Chain members who are not enrolled in the Health Trust.
    """
    # Eligible sectors are typically Manufacturers and Supply Chain
    eligible_sectors = [s for s in df['Sector'].unique() if 'MANUFACTURERS' in s.upper() or 'SUPPLY CHAIN' in s.upper()]
    
    prospects = df[
        (df['Sector'].isin(eligible_sectors)) & 
        (df['CAMPS Health Trust'].str.upper() != 'YES')
    ]
    return prospects
