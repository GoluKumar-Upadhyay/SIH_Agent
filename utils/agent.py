
import os
import base64
import io
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from langchain_google_vertexai import ChatVertexAI, HarmBlockThreshold, HarmCategory
from utils.prompt import AGENT_PROMPT
from utils.db import run_sql

load_dotenv()

safety_settings = {
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

llm = ChatVertexAI(
    model="gemini-2.5-flash-lite",
    temperature=0.2,
    max_output_tokens=2048,
    safety_settings=safety_settings
)

def generate_chart(df, x, y, chart_type="bar"):
    """
    Generates a chart (bar, pie, donut, or line) from the dataframe.

    Args:
        df (pd.DataFrame): Data to plot
        x (str): Column name for x-axis (or labels for pie/donut)
        y (str): Column name for y-axis (or values for pie/donut)
        chart_type (str): Type of chart - "bar", "pie", "donut", or "line"
    
    Returns:
        str: Base64 encoded image of the chart
    """
    plt.figure(figsize=(6, 4))

    if chart_type == "bar":
        plt.bar(df[x], df[y], color='skyblue')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"{y} by {x}")

    elif chart_type == "pie":
        plt.pie(df[y], labels=df[x], autopct="%1.1f%%", startangle=90)
        plt.title(f"{y} distribution by {x}")

    elif chart_type == "donut":
        wedges, texts, autotexts = plt.pie(
            df[y], labels=df[x], autopct="%1.1f%%", startangle=90
        )
       
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        plt.gca().add_artist(centre_circle)
        plt.title(f"{y} distribution by {x} (Donut Chart)")

    elif chart_type == "line":
        plt.plot(df[x], df[y], marker='o', linestyle='-', color='green')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"{y} trend by {x}")

    else:
        # default to bar chart
        plt.bar(df[x], df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"{y} by {x}")

    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return base64.b64encode(img.read()).decode()



def ai_agent(user_query):
    prompt = AGENT_PROMPT.format(query=user_query)
    response = llm.invoke(prompt).content.strip()

    
       
    if response.startswith("GRAPH_REQUEST"):
        sql = response.replace("GRAPH_REQUEST:", "").strip()
        df = run_sql(sql)

        
        query_lower = user_query.lower()
        if "donut" in query_lower or "doughnut" in query_lower:
            chart_type = "donut"
        elif "pie" in query_lower:
            chart_type = "pie"
        elif "line" in query_lower or "trend" in query_lower:
            chart_type = "line"
        else:
            chart_type = "bar"

        chart = generate_chart(df, df.columns[0], df.columns[1], chart_type=chart_type)
        return {"type": "graph", "chart": chart}



    
    if response.startswith("SUMMARY_REQUEST"):
        sql = response.replace("SUMMARY_REQUEST:", "").strip()
        df = run_sql(sql)
        text = "\n".join(df[df.columns[0]])
        summary = llm.invoke("Summarize this:\n" + text).content
        return {"type": "summary", "summary": summary}

   
    if response.startswith("SQL:"):
        sql = response.replace("SQL:", "").strip()
        df = run_sql(sql)
        return {"type": "table", "rows": df.to_dict(orient="records")}

    
    if response.lower().startswith("select"):
        df = run_sql(response)
        return {"type": "table", "rows": df.to_dict(orient="records")}

   
    return {"type": "text", "response": response}
