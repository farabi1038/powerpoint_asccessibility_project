1.It is a powerpoint accessibility project. It means in this project we will take a power point in python. We need to have the capability of laoding it in python. After we load it we need to do WCAG scoring .  
Once the scoring is done, we will check which side it is failing. Then using the the llm from ollama we will try to improve it. 
For improvement, if there is a figure we should genearate a small caption using the LLM for each image on the slide. The caption should be below the image.

All these things need to be done based on the scoring on WCAG. So making it right is really crucial 

If there is issue with color contrast that need to be fixed too
If the font does not fall under the WCAG guideline , you need to make it that size
If there is complex text according to the WCAG report, we need to fix it too 

Finally a Streamlit app to accomany it