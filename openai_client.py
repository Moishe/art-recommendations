import json
from openai import OpenAI

SYSTEM_PROMPT = """
You are an expert art historian, with deep knowledge of many artists, both mainstream and esoteric,
including who they studied with and the themes of their work. Your goal is to help an artist find
more inspiration for their art, given their current inspirations. When you provide links, they should
always be available on the internet and should be the best representation of the artist's work.
"""

def few_shot_example():
    # Define the prompt
    prompt = (
        "I have a list of inspirations for a photo project I'm working on. "
        "Can you recommend 5 or 6 more artists or and specific pieces of their work that might be similar? "
        "Here's my list:\n"
        "* Edward Weston\n"
        "* Diane Arbus\n"
        "* Richard Avedon\n"
        "\nMy themes are black and white, nature, portrait\n\n"
        "Please provide the recommendations in the following JSON format, with at least 3 but preferably 5 or 6 artists:\n"
        "[\n"
        "  {\n"
        "    \"artist\": \"First Artist Name\",\n"
        "    \"description\": \"Description of the artist\",\n"
        "    \"link\": \"URL to their website, or the best website about them.\"\n"
        "  },\n"
        "  {\n"
        "    \"artist\": \"Second Artist Name\",\n"
        "    \"description\": \"Description of the artist\",\n"
        "    \"link\": \"URL to their website, or the best website about them.\"\n"
        "  },\n"
        "  ...\n"
        "]\n\n"
    )

    response = [
        {
            "artist": "Michael Kenna",
            "description": "Known for minimalist, high-contrast landscapes that echo Weston’s emphasis on form and tonal nuance.",
            "link": "https://michaelkenna.net/"
        },
        {
            "artist": "Platon",
            "description": "Renowned for stripped-down, intense black-and-white portraits capturing raw emotion, reminiscent of Avedon’s direct style.",
            "link": "https://www.platonphoto.com/"
        },
        {
            "artist": "Nick Brandt",
            "description": "Portrays wildlife in majestic, black-and-white compositions, emphasizing the sculptural beauty of his subjects.",
            "link": "http://www.nickbrandt.com/"
        },
        {
            "artist": "Mark Seliger",
            "description": "A portrait photographer whose classic, often black-and-white images of celebrities showcase striking simplicity and intimacy.",
            "link": "https://www.markseliger.com/"
        },
        {
            "artist": "Greg Gorman",
            "description": "Focuses on celebrity portraits with strong contrasts and a clean, timeless feel akin to Avedon’s controlled portraiture.",
            "link": "https://www.gormanphotography.com/"
        },
        {
            "artist": "Hiroshi Sugimoto",
            "description": "Creates conceptual black-and-white works exploring minimalist seascapes, architecture, and the essence of time.",
            "link": "https://www.sugimotohiroshi.com/"
        },
        {
            "artist": "Sebastião Salgado",
            "description": "A documentary photographer whose epic-scale black-and-white images focus on humanity and the environment.",
            "link": "https://www.amazonasimages.com/"
        }
    ]

    return [[prompt, f"```json {json.dumps(response)}```"]]

def get_system_prompt_with_few_shot(few_shot):
    system_prompt = SYSTEM_PROMPT
    for prompt, response in few_shot:
        system_prompt += f"\n\nUser: {prompt}\nAssistant: {response}\n"
    return system_prompt


def create_prompt(inspirations, project_themes):
    # Construct the prompt
    prompt = (
        "I have a list of inspirations for a photo project I'm working on. "
        "Can you recommend 5 or 6 more artists or and specific pieces of their work that might be similar? "
        "Here's my list:\n"
    )
    for inspiration in inspirations:
        prompt += f"* {inspiration}\n"

    if project_themes:
        prompt += f"\nMy themes are {project_themes}\n\n"

    prompt += (
        "Please provide the recommendations in the following JSON format, with at least 3 but preferably 5 or 6 artists:\n"
        "[\n"
        "  {\n"
        "    \"artist\": \"First Artist Name\",\n"
        "    \"description\": \"Description of the artist\",\n"
        "    \"link\": \"URL to their website, or the best website about them.\"\n"
        "  },\n"
        "  {\n"
        "    \"artist\": \"Second Artist Name\",\n"
        "    \"description\": \"Description of the artist\",\n"
        "    \"link\": \"URL to their website, or the best website about them.\"\n"
        "  },\n"
        "  ...\n"
        "]\n\n"
    )

    return prompt

def extract_json_from_response(response):
    start = response.find("```json")
    end = response.rfind("```")
    return response[start + len("````json"):end]

def get_openai_recommendations(prompt):
    client = OpenAI()

    few_shot = few_shot_example()
    system_prompt = get_system_prompt_with_few_shot(few_shot)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    openai_response = extract_json_from_response(completion.choices[0].message.content)

    assert openai_response

    try:
        recommendations = json.loads(openai_response)
    except json.JSONDecodeError as e:
        print("Error parsing JSON content: %s", e)
        recommendations = []

    return openai_response, recommendations

if __name__=="__main__":
    """
    inspirations = [
        "Ansel Adams",
        "Diane Arbus",
        "Richard Avedon",
    ]
    project_themes = "black and white, nature, portrait"
    prompt = create_prompt(inspirations, project_themes)
    openai_response, recommendations = get_openai_recommendations(prompt)
    print("OpenAI Response:")
    print(openai_response)
    print("\nRecommendations:")
    print(recommendations)
    """
    test_response = """ly! Here's a list of artists who may complement your inspirations and themes: ```json [ { "artist": "Francesca Woodman", "description": "Known for ethereal self-portraits and experimental techniques in black and white, Woodman explored themes of identity and the ephemeral nature of existence.", "link": "https://www.tate.org.uk/art/artists/francesca-woodman-10231" }, { "artist": "Tommy Ingberg", "description": "A surrealist photographer who creates black-and-white images combining reality and dreams, exploring themes similar to Burnstine's introspective narratives.", "link": "https://www.ingberg.com/" }, { "artist": "Sally Mann", "description": "Celebrated for her haunting and painterly black-and-white photographs that explore the complexities of childhood, identity, and southern landscapes.", "link": "http://sallymann.com/" }, { "artist": "Saul Leiter", "description": "Though best known for color photography, Leiter's black-and-white work captures intimate cityscapes and abstracted figures, echoing dreamlike qualities.", "link": "https://www.saulleiterfoundation.org/" }, { "artist": "Harry Callahan", "description": "Renowned for his experimental approach to black-and-white photography, Callahan often explored multiple exposures and abstraction in both urban and natural environments.", "link": "https://www.icp.org/browse/archive/constituents/harry-callahan" }, { "artist": "Duane Michals", "description": "Famous for his series of sequentiual narratives and use of handwritten text, Michals explores complex narratives and metaphysical themes in black and white.", "link": "https://www.dcmooregallery.com/artists/duane-michals" } ] ``` These artists share themes of dream-like and introspective imagery, often using innovative techniques to explore identity, memory, and the surr"""
    print(extract_json_from_response(test_response))
