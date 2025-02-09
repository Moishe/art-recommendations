import json
from openai import OpenAI

def get_openai_recommendations(prompt):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "developer", "content": "You are an expert art historian, with deep knowledge of many artists, both mainstream and esoteric, including who they studied with and the themes of their work. Your goal is to help an artist find more inspiration for their art, given their current inspirations. You always provide images that are available on the internet at the time you respond to the prompt."},
            {"role": "user", "content": prompt}
        ]
    )

    openai_response = completion.choices[0].message.content

    START_TOKEN = '```json\n'
    json_start = openai_response.find(START_TOKEN)
    json_end = openai_response.rfind("```")
    if json_start != -1 and json_end != -1:
        json_content = openai_response[json_start + len(START_TOKEN):json_end].strip()
        try:
            recommendations = json.loads(json_content)
        except json.JSONDecodeError as e:
            print("Error parsing JSON content: %s", e)
            recommendations = []
    else:
        print("No JSON content found in the response.")
        recommendations = []

    return openai_response, recommendations
