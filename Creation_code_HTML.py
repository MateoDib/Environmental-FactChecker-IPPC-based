#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  3 22:15:19 2024

@author: mateodib
"""

import os
import json

# Directory containing the JSON files
json_dir = "/Users/mateodib/Desktop/Environmental_News_Checker-2/Data/resultats/resultats_intermediaires/articles_json/"

# Output HTML file
output_html = "/Users/mateodib/Desktop/Environmental_News_Checker-2/Visualisation_results.html"

# Read all JSON files in the directory and load them into a dictionary
articles_data = {}
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(json_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
            # Use the filename without the extension as the article key
            article_key = os.path.splitext(filename)[0]
            articles_data[article_key] = article_data
            
# Directory to store individual JSON files for each article
articles_data_dir = "/Users/mateodib/Desktop/Environmental_News_Checker-Mateo/articles_data/"
os.makedirs(articles_data_dir, exist_ok=True)

# Save each article's data as a separate JSON file
for article_key, article_data in articles_data.items():
    with open(os.path.join(articles_data_dir, f"{article_key}.json"), 'w', encoding='utf-8') as f:
        json.dump(article_data, f, indent=4, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Environmental News Checker</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* General Styling */
        body {{
            font-family: 'Roboto', sans-serif;
            background-color: #f4f4f9;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        h1, h2 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        /* Landing Page Styling */
        #landing-page {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-image: linear-gradient(to right, #6a11cb, #2575fc);
            color: white;
        }}
        #landing-page button {{
            background-color: #fff;
            color: #2575fc;
            padding: 10px 20px;
            font-size: 1.2em;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        #landing-page button:hover {{
            background-color: #2575fc;
            color: #fff;
        }}
        /* Container and Tabs */
        .container {{
            width: 90%;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: none;
        }}
        .tabs {{
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }}
        .tab {{
            cursor: pointer;
            padding: 10px;
            color: #2575fc;
            font-weight: bold;
        }}
        .tab.active {{
            border-bottom: 2px solid #2575fc;
        }}
        /* Navigation Buttons */
        .nav-buttons {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }}
        .nav-button {{
            padding: 8px 15px;
            font-size: 1em;
            background-color: #2575fc;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .nav-button:hover {{
            background-color: #1a5bbf;
        }}
        /* Phrase Styling */
        .phrase {{
            display: block;
            margin: 10px 0;
            padding: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .phrase:hover {{
            background-color: #e0f7fa;
        }}
        .highlighted-phrase {{
            color: #006400;
            font-weight: bold;
        }}
        /* Popup and Overlay */
        .popup, .overlay {{
            display: none;
        }}
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 5;
        }}
        .popup {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 8px;
            padding: 20px;
            max-width: 500px;
            z-index: 10;
        }}
        .close-btn {{
            position: absolute;
            top: 10px;
            right: 15px;
            cursor: pointer;
            font-weight: bold;
            color: #2575fc;
        }}
    </style>
</head>
<body>

<!-- Landing Page -->
<div id="landing-page">
    <h1>Environmental News Checker</h1>
    <p>Analyze the accuracy, bias, and tone of environmental news articles.</p>
    <button onclick="showArticleSelection()">Get Started</button>
</div>

<!-- Article Selection Page -->
<div id="article-selection-page" class="container">
    <h2>Select an Article to Analyze</h2>
    <select id="article-select" onchange="loadArticle(this.value)">
        <option value="">Select an article</option>
"""

# Add options for each article in the dropdown menu
for article_key in articles_data.keys():
    html_content += f'        <option value="{article_key}">{articles_data[article_key]["article_title"]}</option>\n'

html_content += """    </select>
    <div class="nav-buttons">
        <button class="nav-button" onclick="goHome()">Home</button>
    </div>
</div>

<!-- Article Analysis Page -->
<div id="analysis-page" class="container">
    <h1 id="article-title">Article Analysis</h1>
    <div id="article-content"></div>
    <div class="nav-buttons">
        <button class="nav-button" onclick="showArticleSelection()">Back</button>
        <button class="nav-button" onclick="goHome()">Home</button>
    </div>
</div>

<!-- Overlay and Popup for Phrase Analysis -->
<div class="overlay" id="overlay" onclick="closePopup()"></div>
<div class="popup" id="popup">
    <span class="close-btn" onclick="closePopup()">X</span>
    <h2>Phrase Analysis</h2>
    <div class="tabs">
        <span class="tab" onclick="showTab('accuracy')">Accuracy</span>
        <span class="tab" onclick="showTab('bias')">Bias</span>
        <span class="tab" onclick="showTab('tone')">Tone</span>
    </div>
    <div id="accuracy" class="tab-content">
        <p><strong>Accuracy Score:</strong> <span id="accuracy-score" class="score"></span></p>
        <div id="justification-accuracy" class="justification-text"></div>
    </div>
    <div id="bias" class="tab-content" style="display: none;">
        <p><strong>Bias Score:</strong> <span id="bias-score" class="score"></span></p>
        <div id="justification-bias" class="justification-text"></div>
    </div>
    <div id="tone" class="tab-content" style="display: none;">
        <p><strong>Tone Score:</strong> <span id="tone-score" class="score"></span></p>
        <div id="justification-tone" class="justification-text"></div>
    </div>
</div>

<script>
function showArticleSelection() {
    document.getElementById('landing-page').style.display = 'none';
    document.getElementById('analysis-page').style.display = 'none';
    document.getElementById('article-selection-page').style.display = 'block';
}

function goHome() {
    document.getElementById('landing-page').style.display = 'block';
    document.getElementById('article-selection-page').style.display = 'none';
    document.getElementById('analysis-page').style.display = 'none';
}

function loadArticle(articleKey) {
    if (!articleKey) return;
    
    const articleDataScript = document.getElementById(`article-data-${articleKey}`);
    if (!articleDataScript) return;
    
    const data = JSON.parse(articleDataScript.textContent);
    displayArticle(data);
    document.getElementById('article-selection-page').style.display = 'none';
    document.getElementById('analysis-page').style.display = 'block';
}

function displayArticle(data) {
    document.getElementById("article-title").innerText = data.article_title;
    document.getElementById("article-content").innerHTML = '';
    
    Object.keys(data.phrases).forEach(id => {
        const phraseData = data.phrases[id];
        const hasValidAnalysis = Object.values(phraseData.analysis).some(metric => metric.score !== null);
        
        const phraseElement = document.createElement("span");
        phraseElement.className = hasValidAnalysis ? "phrase highlighted-phrase" : "phrase";
        phraseElement.innerText = phraseData.text;
        phraseElement.onclick = () => showPopup(id, data.phrases);
        
        document.getElementById("article-content").appendChild(phraseElement);
        document.getElementById("article-content").appendChild(document.createElement("br"));
    });
}

function showPopup(id, phrases) {
    const phraseData = phrases[id].analysis;
    document.getElementById("accuracy-score").textContent = phraseData.accuracy.score || "N/A";
    document.getElementById("bias-score").textContent = phraseData.bias.score || "N/A";
    document.getElementById("tone-score").textContent = phraseData.tone.score || "N/A";
    
    document.getElementById("justification-accuracy").textContent = phraseData.accuracy.justifications || "No justification available.";
    document.getElementById("justification-bias").textContent = phraseData.bias.justifications || "No justification available.";
    document.getElementById("justification-tone").textContent = phraseData.tone.justifications || "No justification available.";
    
    document.getElementById("overlay").style.display = "block";
    document.getElementById("popup").style.display = "block";
}

function closePopup() {
    document.getElementById("overlay").style.display = "none";
    document.getElementById("popup").style.display = "none";
}

function showTab(tabName) {
    document.querySelectorAll(".tab-content").forEach(content => {
        content.style.display = "none";
    });
    document.getElementById(tabName).style.display = "block";
    document.querySelectorAll(".tab").forEach(tab => {
        tab.classList.remove("active");
    });
    document.querySelector(`.tab[onclick="showTab('${tabName}')"]`).classList.add("active");
}
</script>
</body>
</html>
"""

# Embed each article's JSON data as separate <script> blocks
for article_key, article_data in articles_data.items():
    html_content += f'<script type="application/json" id="article-data-{article_key}">\n'
    html_content += json.dumps(article_data, indent=4)
    html_content += "\n</script>\n"

# Embed each article's JSON data as separate <script> blocks
for article_key, article_data in articles_data.items():
    html_content += f'<script type="application/json" id="article-data-{article_key}">\n'
    html_content += json.dumps(article_data, indent=4)
    html_content += "\n</script>\n"

# Write the HTML content to the output file
with open(output_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML file created at {output_html}")
