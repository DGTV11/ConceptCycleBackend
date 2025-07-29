from openai import OpenAI

from config import (
    LLM_API_BASE_URL,
    LLM_API_KEY,
    LLM_NAME,
    VLM_API_BASE_URL,
    VLM_API_KEY,
    VLM_NAME,
)

llm_client = OpenAI(base_url=LLM_API_BASE_URL, api_key=LLM_API_KEY)
vlm_client = OpenAI(base_url=VLM_API_BASE_URL, api_key=VLM_API_KEY)


def call_llm(prompt):

    completion = llm_client.chat.completions.create(
        model=LLM_NAME,
        messages=[
            {
                "role": "system",
                "content": "Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.",  # *https://www.promptingguide.ai/models/mixtral#system-prompt-to-enforce-guardrails
            },
            {"role": "user", "content": prompt},
        ],
    )

    return completion.choices[0].message.content


def call_vlm(prompt, b64_image):

    completion = vlm_client.chat.completions.create(
        model=VLM_NAME,
        messages=[
            {
                "role": "system",
                "content": "Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.",  # *https://www.promptingguide.ai/models/mixtral#system-prompt-to-enforce-guardrails
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{b64_image}",
                    },
                ],
            },
        ],
    )

    return completion.choices[0].message.content
