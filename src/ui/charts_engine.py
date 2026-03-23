import plotly.express as px
import plotly.graph_objects as go

def create_aging_bar(df_f):
    """Crea el gráfico de barras horizontales de antigüedad de cartera."""
    por_antiguedad = df_f.groupby("RANGO_DIAS")["IMPORTE"].sum().reset_index()
    por_antiguedad = por_antiguedad.sort_values("RANGO_DIAS")
    
    total = por_antiguedad["IMPORTE"].sum()
    por_antiguedad["PORC"] = (por_antiguedad["IMPORTE"] / total * 100).round(1)

    colores_map = {
        "Al dia": "#10b981", "1-30": "#3b82f6", "31-60": "#f59e0b",
        "61-90": "#f97316", "91-180": "#ef4444", "181-365": "#dc2626", "+365": "#991b1b"
    }
    colores = [colores_map.get(str(r), "#64748b") for r in por_antiguedad["RANGO_DIAS"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=por_antiguedad["IMPORTE"],
        y=por_antiguedad["RANGO_DIAS"].astype(str),
        orientation="h",
        marker_color=colores,
        text=[f"S/. {v:,.0f} ({p}%)" for v, p in zip(por_antiguedad["IMPORTE"], por_antiguedad["PORC"])],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=11),
        hovertemplate="<b>%{y}</b><br>S/. %{x:,.0f}<br>(%{text})<extra></extra>",
    ))
    
    fig.update_layout(
        title=dict(text="Distribución de Riesgo por Antigüedad", font=dict(color="#f8fafc", size=16), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(color="#64748b", showgrid=True, gridcolor="rgba(255,255,255,0.03)"),
        yaxis=dict(color="#64748b"),
        margin=dict(t=50, b=50, l=100, r=50),
        height=350,
    )
    return fig

def create_bank_donut(df_f):
    """Crea el gráfico de rosca de distribución por banco."""
    valores = df_f.groupby("BANCO")["IMPORTE"].sum().sort_values(ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=valores.index,
        values=valores.values,
        hole=0.6,
        marker_colors=["#3b82f6", "#10b981", "#f59e0b", "#f43f5e", "#6366f1", "#06b6d4"],
        textinfo="percent",
        textposition="outside",
        textfont=dict(color="#94a3b8"),
        hovertemplate="<b>%{label}</b><br>S/. %{value:,.0f}<extra></extra>",
    )])
    
    fig.update_layout(
        title=dict(text="Distribución por Banco", font=dict(color="#f8fafc", size=16), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", font=dict(color="#94a3b8")),
        margin=dict(t=50, b=50, l=20, r=20),
        height=350,
    )
    return fig

def create_girador_bar(df_f):
    """Crea el gráfico de top 10 giradores."""
    top_10 = df_f.groupby("GIRADOR")["IMPORTE"].sum().sort_values(ascending=False).head(10).reset_index()
    
    fig = px.bar(
        top_10,
        x='IMPORTE',
        y='GIRADOR',
        orientation='h',
        color='IMPORTE',
        color_continuous_scale='Blues',
        labels={'IMPORTE': 'Monto Acumulado S/.', 'GIRADOR': 'Girador'}
    )
    
    fig.update_layout(
        title=dict(text="Top 10 Giradores por Monto", font=dict(color="#f8fafc", size=16), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        coloraxis_showscale=False,
        height=400,
    )
    return fig

def create_category_donut(df_f):
    """Crea el gráfico de rosca de distribución por categoría estratégica."""
    # Control de errores defensivo para evitar el KeyError si no ha cargado el caché nuevo
    if "CATEGORIA" not in df_f.columns:
        fig = go.Figure()
        fig.add_annotation(text="Cargando categorías estratégicas...<br>Por favor, limpie el caché de Streamlit.", 
                          showarrow=False, font={"color": "#94a3b8", "size": 14})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(visible=False), yaxis=dict(visible=False))
        return fig

    valores = df_f.groupby("CATEGORIA")["IMPORTE"].sum().sort_values(ascending=False)
    
    fig = go.Figure(data=[go.Pie(
        labels=valores.index,
        values=valores.values,
        hole=0.6,
        marker_colors=["#6366f1", "#f97316", "#10b981", "#ef4444", "#94a3b8"],
        textinfo="label+percent",
        textposition="outside",
        textfont=dict(color="#94a3b8"),
        hovertemplate="<b>%{label}</b><br>S/. %{value:,.0f}<extra></extra>",
    )])
    
    fig.update_layout(
        title=dict(text="Exposición por Categoría", font=dict(color="#f8fafc", size=16), x=0.5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(t=50, b=50, l=20, r=20),
        height=350,
    )
    return fig
