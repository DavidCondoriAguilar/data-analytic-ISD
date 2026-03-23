"""CSS styles for the dashboard."""

from config import COLORS

def get_dashboard_styles() -> str:
    """Return the complete CSS styles for the dashboard."""
    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    --primary: {COLORS['primary']};
    --secondary: {COLORS['secondary']};
    --accent: {COLORS['accent']};
    --warning: {COLORS['warning']};
    --danger: {COLORS['danger']};
    --bg-dark: {COLORS['bg_dark']};
    --bg-card: {COLORS['bg_card']};
    --text: {COLORS['text']};
    --text-muted: {COLORS['text_muted']};
}}

* {{ font-family: 'Inter', sans-serif; }}

.header {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    padding: 2rem 3rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    color: white;
}}

.header h1 {{
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
    margin-bottom: 2rem;
}}

.kpi-card {{
    background: var(--bg-card);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(255,255,255,0.1);
}}

.kpi-label {{
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}}

.kpi-value {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
}}

.kpi-value.positive {{ color: var(--accent); }}
.kpi-value.negative {{ color: var(--danger); }}
.kpi-value.neutral {{ color: var(--secondary); }}

.section-title {{
    background: var(--bg-card);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--secondary);
}}

.section-title h3 {{
    margin: 0;
    font-size: 1rem;
    color: var(--text);
}}

.section-title p {{
    margin: 0.25rem 0 0 0;
    font-size: 0.75rem;
    color: var(--text-muted);
}}

.info-box {{
    background: rgba(59, 130, 246, 0.1);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--secondary);
}}

.info-box h4 {{
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: var(--secondary);
}}

.info-box p {{
    margin: 0;
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.5;
}}

.warning-box {{
    background: rgba(245, 158, 11, 0.1);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--warning);
}}

.warning-box h4 {{
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: var(--warning);
}}

.danger-box {{
    background: rgba(239, 68, 68, 0.1);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--danger);
}}

.danger-box h4 {{
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: var(--danger);
}}

.success-box {{
    background: rgba(16, 185, 129, 0.1);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--accent);
}}

.success-box h4 {{
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: var(--accent);
}}

[data-testid="stSidebar"] {{ background: var(--bg-dark); }}

.stTabs [data-baseweb="tab"] {{
    background: var(--bg-card);
    border-radius: 10px;
    padding: 0.75rem 1.5rem;
}}

.stTabs [data-baseweb="tab"][aria-selected="true"] {{
    background: var(--secondary) !important;
    color: white !important;
}}
</style>"""

def get_header_html(title: str, subtitle: str) -> str:
    """Generate header HTML."""
    return f"""
<div class="header">
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
"""

def get_section_title_html(title: str, description: str) -> str:
    """Generate section title HTML."""
    return f"""
<div class="section-title">
    <h3>{title}</h3>
    <p>{description}</p>
</div>
"""

def get_info_box_html(title: str, description: str) -> str:
    """Generate info box HTML."""
    return f"""
<div class="info-box">
    <h4>{title}</h4>
    <p>{description}</p>
</div>
"""

def get_warning_box_html(title: str, description: str) -> str:
    """Generate warning box HTML."""
    return f"""
<div class="warning-box">
    <h4>{title}</h4>
    <p>{description}</p>
</div>
"""

def get_danger_box_html(title: str, description: str) -> str:
    """Generate danger box HTML."""
    return f"""
<div class="danger-box">
    <h4>{title}</h4>
    <p>{description}</p>
</div>
"""

def get_success_box_html(title: str, description: str) -> str:
    """Generate success box HTML."""
    return f"""
<div class="success-box">
    <h4>{title}</h4>
    <p>{description}</p>
</div>
"""
