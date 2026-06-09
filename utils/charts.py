import os
import logging
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def generate_matplotlib_chart(chart_def: Dict[str, Any], output_dir: str) -> str:
    """
    Generate a static matplotlib chart and save it as a PNG.
    Returns the file path to the saved PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    title = chart_def.get("title", "Chart")
    chart_type = chart_def.get("type", "bar").lower()
    labels = chart_def.get("labels", [])
    values = chart_def.get("values", [])
    x_label = chart_def.get("x_label", "")
    y_label = chart_def.get("y_label", "")
    
    # Check if we have valid data
    if not labels or not values or len(labels) != len(values):
        logger.warning(f"Invalid chart data for {title}: labels and values mismatch or empty.")
        return ""
    
    # Safe filename from title
    safe_title = "".join([c if c.isalnum() else "_" for c in title]).strip("_").lower()
    filename = f"{safe_title}_{chart_type}.png"
    filepath = os.path.join(output_dir, filename)
    
    try:
        # Clear current figure
        plt.figure(figsize=(7, 4.5))
        
        # Style adjustments
        # Dark-themed modern chart aesthetics
        primary_color = "#1f77b4"
        accent_color = "#ff7f0e"
        
        if chart_type == "bar":
            plt.bar(labels, values, color=primary_color, edgecolor="#eaeaea")
            plt.xticks(rotation=15, ha='right')
        elif chart_type == "line":
            plt.plot(labels, values, marker='o', color=accent_color, linewidth=2)
            plt.xticks(rotation=15, ha='right')
        elif chart_type == "pie":
            colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a']
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors[:len(labels)])
            
        plt.title(title, fontsize=12, fontweight='bold', pad=15)
        if chart_type != "pie":
            if x_label:
                plt.xlabel(x_label, fontsize=10, labelpad=8)
            if y_label:
                plt.ylabel(y_label, fontsize=10, labelpad=8)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
        plt.tight_layout()
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        logger.info(f"Generated matplotlib chart saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error generating matplotlib chart {title}: {e}")
        return ""

def create_plotly_figure(chart_def: Dict[str, Any]) -> go.Figure:
    """
    Generate an interactive Plotly Figure object from a chart definition.
    """
    title = chart_def.get("title", "Chart")
    chart_type = chart_def.get("type", "bar").lower()
    labels = chart_def.get("labels", [])
    values = chart_def.get("values", [])
    x_label = chart_def.get("x_label", "")
    y_label = chart_def.get("y_label", "")
    
    fig = go.Figure()
    
    # Premium theme colors
    plotly_template = "plotly_white"
    
    if chart_type == "bar":
        fig.add_trace(go.Bar(
            x=labels, 
            y=values,
            marker_color='#3B82F6', # beautiful modern blue
            marker_line=dict(width=1, color='#1E40AF')
        ))
    elif chart_type == "line":
        fig.add_trace(go.Scatter(
            x=labels, 
            y=values, 
            mode='lines+markers',
            line=dict(color='#F59E0B', width=3), # elegant gold/orange
            marker=dict(size=8, color='#B45309')
        ))
    elif chart_type == "pie":
        fig.add_trace(go.Pie(
            labels=labels, 
            values=values,
            hole=0.4, # elegant donut chart
            marker=dict(colors=['#3B82F6', '#F59E0B', '#10B981', '#EC4899', '#8B5CF6', '#EF4444'])
        ))
        
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16, 'family': 'Arial, sans-serif', 'weight': 'bold'}
        },
        template=plotly_template,
        margin=dict(l=40, r=40, t=60, b=40),
        height=380,
    )
    
    if chart_type != "pie":
        fig.update_layout(
            xaxis=dict(title=x_label, showgrid=True, gridcolor='#E5E7EB'),
            yaxis=dict(title=y_label, showgrid=True, gridcolor='#E5E7EB')
        )
        
    return fig
