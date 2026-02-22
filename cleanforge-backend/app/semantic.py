import os
import json
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


# Connect to Groq using OpenAI-compatible client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def generate_semantic_analysis(df: pd.DataFrame):

    # Take small sample for each column
    sample_data = {}

    for col in df.columns:
        sample_data[col] = df[col].dropna().astype(str).head(5).tolist()

    prompt = f"""
You are a data quality AI.

Given the dataset column samples below:

{sample_data}

For each column:
1. Identify semantic meaning (e.g., Email, Phone, Age, Country, Salary).
2. Detect potential issues.
3. Suggest cleaning improvements.

Return ONLY valid JSON in this format:

{{
  "ColumnName": {{
      "semantic_type": "",
      "issues_detected": [],
      "suggested_fixes": []
  }}
}}

Do not include explanations.
Return JSON only.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    # Try to safely parse JSON
    try:
        return json.loads(content)
    except:
        return {"raw_output": content}
