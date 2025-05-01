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

def generate_report_html(before_score, after_score, before_wcag_report, after_wcag_report, wmf_count=0):
    """
    Generate an HTML report comparing before and after accessibility improvements
    
    Args:
        before_score (dict): Score report before enhancement
        after_score (dict): Score report after enhancement
        before_wcag_report (dict): WCAG report before enhancement
        after_wcag_report (dict): WCAG report after enhancement
        wmf_count (int): Number of WMF images found
        
    Returns:
        str: HTML report content
    """
    # Calculate statistics
    alt_text_count = after_score["category_scores"]["alt_text"] - before_score["category_scores"]["alt_text"]
    font_size_improvement = after_score["category_scores"]["font_size"] - before_score["category_scores"]["font_size"]
    contrast_improvement = after_score["category_scores"]["contrast"] - before_score["category_scores"]["contrast"]
    text_simpler = after_score["category_scores"]["text_complexity"] - before_score["category_scores"]["text_complexity"]
    
    # Convert negative improvements to zero (in case something got worse)
    alt_text_count = max(0, alt_text_count)
    font_size_improvement = max(0, font_size_improvement)
    contrast_improvement = max(0, contrast_improvement)
    text_simpler = max(0, text_simpler)
    
    # Create comprehensive HTML report
    html_report = f"""
    <html>
    <head>
        <title>Accessibility Enhancement Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2E7D32; }}
            h2 {{ color: #1565C0; }}
            .section {{ background: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .warning {{ background: #FFF3E0; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .comparison {{ display: flex; justify-content: space-between; }}
            .score-card {{ flex: 1; margin: 10px; padding: 15px; border-radius: 8px; background: #f5f5f5; }}
            .improvement {{ color: green; font-weight: bold; }}
            .card {{ padding: 15px; margin: 10px 0; border-radius: 8px; }}
            .green-card {{ background-color: #E8F5E9; }}
            .blue-card {{ background-color: #E3F2FD; }}
            .yellow-card {{ background-color: #FFF8E1; }}
            .purple-card {{ background-color: #F3E5F5; }}
        </style>
    </head>
    <body>
        <h1>PowerPoint Accessibility Report</h1>
        
        <div class="section">
            <h2>Summary</h2>
            <p>Your presentation has been enhanced with several accessibility improvements:</p>
            
            <div class="comparison">
                <div class="score-card">
                    <h3>Before</h3>
                    <p><strong>Overall Score:</strong> {before_score["overall_score"]}/100</p>
                </div>
                <div class="score-card" style="background-color: #E8F5E9;">
                    <h3>After</h3>
                    <p><strong>Overall Score:</strong> {after_score["overall_score"]}/100</p>
                    <p class="improvement">Improvement: +{after_score["overall_score"] - before_score["overall_score"]} points</p>
                </div>
            </div>
        </div>
        
        <h2>Accessibility Improvements</h2>
        
        <div class="card green-card">
            <h3>Image Accessibility</h3>
            <p><strong>Before:</strong> {before_score["category_scores"]["alt_text"]}/100</p>
            <p><strong>After:</strong> {after_score["category_scores"]["alt_text"]}/100</p>
            <p>Added or improved alt text for images to assist screen reader users.</p>
        </div>
        
        <div class="card blue-card">
            <h3>Font Size Readability</h3>
            <p><strong>Before:</strong> {before_score["category_scores"]["font_size"]}/100</p>
            <p><strong>After:</strong> {after_score["category_scores"]["font_size"]}/100</p>
            <p>Increased font sizes to improve readability for those with visual impairments.</p>
        </div>
        
        <div class="card yellow-card">
            <h3>Contrast Enhancement</h3>
            <p><strong>Before:</strong> {before_score["category_scores"]["contrast"]}/100</p>
            <p><strong>After:</strong> {after_score["category_scores"]["contrast"]}/100</p>
            <p>Improved text contrast to make content more readable.</p>
        </div>
        
        <div class="card purple-card">
            <h3>Text Simplification</h3>
            <p><strong>Before:</strong> {before_score["category_scores"]["text_complexity"]}/100</p>
            <p><strong>After:</strong> {after_score["category_scores"]["text_complexity"]}/100</p>
            <p>Simplified complex text to be more understandable.</p>
        </div>
        
        {f'<div class="warning"><h3>Special Image Formats</h3><p>Found {wmf_count} WMF/EMF image(s) that require special handling. These formats have limited accessibility support in PowerPoint.</p></div>' if wmf_count > 0 else ''}
        
        <div class="section">
            <h2>Next Steps</h2>
            <p>To further improve your presentation's accessibility:</p>
            <ul>
                <li>Review the alt text generated for images and make adjustments as needed</li>
                <li>Consider adding closed captions if your presentation includes audio or video</li>
                <li>Use built-in slide layouts rather than free-floating text boxes</li>
                <li>Ensure logical reading order for all slide elements</li>
                <li>Test with a screen reader to verify accessibility</li>
            </ul>
        </div>
        
        <p style="margin-top: 30px; color: #666; font-size: 0.8em;">
            Generated by PowerPoint Accessibility Enhancer
        </p>
    </body>
    </html>
    """
    
    return html_report

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