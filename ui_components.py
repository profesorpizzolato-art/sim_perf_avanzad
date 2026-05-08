import plotly.graph_objects as go

def crear_manometro(valor, titulo, unidad, max_val, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        title={'text': f"<b>{titulo}</b><br><span style='font-size:0.8em'>{unidad}</span>"},
        gauge={
            'axis': {'range': [0, max_val], 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'steps': [
                {'range': [0, max_val*0.8], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [max_val*0.8, max_val], 'color': 'rgba(255, 0, 0, 0.2)'}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': max_val * 0.9}
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=20, r=20, t=50, b=20),
        font={'color': "white"}
    )
    return fig