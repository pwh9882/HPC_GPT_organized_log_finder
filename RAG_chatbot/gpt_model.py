import openai

# OpenAI API 키 설정
openai.api_key = 'YOUR_OPENAI_API_KEY'

# GPT-4 모델을 사용하여 텍스트 생성
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()
