"""
Utility functions for the PowerPoint Accessibility Enhancer
"""

import os
import tempfile
import base64
import pandas as pd
import matplotlib.pyplot as plt
import io

def create_comparison_chart(before_score, after_score, categories):
    """Create a comparison chart of before and after scores"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract category scores
    before_cat_scores = [before_score['category_scores'][cat] for cat in categories]
    after_cat_scores = [after_score['category_scores'][cat] for cat in categories]
    
    # Add overall scores
    categories = categories + ['Overall']
    before_cat_scores.append(before_score['overall_score'])
    after_cat_scores.append(after_score['overall_score'])
    
    x = range(len(categories))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], before_cat_scores, width, label='Before', color='#ff9999')
    ax.bar([i + width/2 for i in x], after_cat_scores, width, label='After', color='#99cc99')
    
    ax.set_ylabel('Score')
    ax.set_title('Accessibility Score Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    
    plt.ylim(0, 100)
    
    for i, v in enumerate(before_cat_scores):
        ax.text(i - width/2, v + 3, str(round(v)), ha='center')
    
    for i, v in enumerate(after_cat_scores):
        ax.text(i + width/2, v + 3, str(round(v)), ha='center')
    
    # Save chart to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Get image as base64 string
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    plt.close()
    
    return image_base64

def generate_report_html(before_score, after_score):
    """Generate an HTML report comparing before and after scores"""
    # Category names for better display
    category_names = {
        "alt_text": "Alt Text",
        "font_size": "Font Size",
        "contrast": "Contrast",
        "text_complexity": "Text Complexity"
    }
    
    # Create comparison chart
    chart_base64 = create_comparison_chart(
        before_score, 
        after_score, 
        list(category_names.keys())
    )
    
    # Generate issue tables
    issue_html = ""
    
    for category, display_name in category_names.items():
        if before_score['issues'][category]:
            issue_html += f"<h3>{display_name} Issues</h3>"
            issue_html += "<ul>"
            for issue in before_score['issues'][category]:
                issue_html += f"<li>{issue}</li>"
            issue_html += "</ul>"
    
    # Create the full HTML report
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .report-container {{ max-width: 800px; margin: 0 auto; }}
            .score-container {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            .score-box {{ text-align: center; padding: 20px; border-radius: 5px; width: 45%; }}
            .before-score {{ background-color: #ffe6e6; }}
            .after-score {{ background-color: #e6ffe6; }}
            .score-value {{ font-size: 48px; font-weight: bold; margin: 10px 0; }}
            .chart {{ text-align: center; margin: 30px 0; }}
            .improvements {{ margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <h1>PowerPoint Accessibility Report</h1>
            
            <div class="score-container">
                <div class="score-box before-score">
                    <h2>Before Enhancement</h2>
                    <div class="score-value">{before_score['overall_score']}</div>
                    <p>{before_score['summary']}</p>
                </div>
                
                <div class="score-box after-score">
                    <h2>After Enhancement</h2>
                    <div class="score-value">{after_score['overall_score']}</div>
                    <p>{after_score['summary']}</p>
                </div>
            </div>
            
            <div class="chart">
                <h2>Score Comparison</h2>
                <img src="data:image/png;base64,{chart_base64}" alt="Accessibility Score Comparison Chart">
            </div>
            
            <div class="improvements">
                <h2>Identified Issues</h2>
                {issue_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html 

def create_wcag_compliance_chart(wcag_report):
    """Create a chart showing WCAG compliance status"""
    compliance_status = {
        "Pass": 0,
        "Fail": 0
    }
    
    # Count pass/fail criteria
    for criteria, details in wcag_report.items():
        compliance_status[details["compliance"]] += 1
    
    # Create a pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Colors for the pie chart
    colors = ['#4CAF50', '#F44336']
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        [compliance_status["Pass"], compliance_status["Fail"]], 
        labels=["Pass", "Fail"],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90
    )
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')
    plt.title('WCAG 2.0 Compliance Status')
    
    # Save chart to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Get image as base64 string
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    plt.close()
    
    return image_base64 