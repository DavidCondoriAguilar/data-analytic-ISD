import streamlit as st

def apply_custom_styles():
    """Aplica los estilos CSS premium al dashboard."""
    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --bg-primary: #0a0f1c;
            --bg-secondary: #111827;
            --bg-card: #1a1f2e;
            --bg-card-hover: #232b3e;
            --border: rgba(255,255,255,0.06);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-blue-dim: rgba(59,130,246,0.15);
            --accent-emerald: #10b981;
            --accent-emerald-dim: rgba(16,185,129,0.15);
            --accent-amber: #f59e0b;
            --accent-amber-dim: rgba(245,158,11,0.15);
            --accent-rose: #f43f5e;
            --accent-rose-dim: rgba(244,63,94,0.15);
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -2px rgba(0,0,0,0.2);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.4), 0 4px 6px -4px rgba(0,0,0,0.3);
        }
        
        * { font-family: 'Inter', sans-serif; }
        
        .stApp { background: var(--bg-primary); }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--bg-card); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
        
        /* Header Premium */
        .header-container {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }
        .header-container::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 300px;
            height: 100%;
            background: linear-gradient(135deg, var(--accent-blue-dim) 0%, transparent 60%);
            pointer-events: none;
        }
        .header-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
            letter-spacing: -0.02em;
        }
        .header-subtitle {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin: 0.5rem 0 0 0;
            font-weight: 400;
        }
        .header-date {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }
        
        /* Metric Cards */
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        .metric-card:hover {
            background: var(--bg-card-hover);
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            border-radius: 12px 12px 0 0;
        }
        .metric-card.blue::before { background: var(--accent-blue); }
        .metric-card.emerald::before { background: var(--accent-emerald); }
        .metric-card.amber::before { background: var(--accent-amber); }
        .metric-card.rose::before { background: var(--accent-rose); }
        
        .metric-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.2;
        }
        .metric-subtext {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }
        
        /* Status Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.625rem;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .badge.blue { background: var(--accent-blue-dim); color: var(--accent-blue); }
        .badge.emerald { background: var(--accent-emerald-dim); color: var(--accent-emerald); }
        .badge.amber { background: var(--accent-amber-dim); color: var(--accent-amber); }
        .badge.rose { background: var(--accent-rose-dim); color: var(--accent-rose); }
        
        /* Sidebar */
        [data-testid="stSidebar"] { 
            background: var(--bg-secondary) !important; 
            border-right: 1px solid var(--border);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.2s;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: var(--accent-blue) !important;
            color: white !important;
            border-color: var(--accent-blue);
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

def inject_expert_tip(msg):
    """Inyecta una caja de consejo de experto estilizada."""
    st.markdown(
        f"""
        <div style="background: rgba(59,130,246,0.05); border-radius: 8px; padding: 1rem; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 1.5rem;">
            <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">
                <b>Consejo de Experto:</b> {msg}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
