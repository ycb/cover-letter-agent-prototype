import os
import openai

def main():
    with open('users/peter/resume_raw_text.txt', 'r') as f:
        resume_text = f.read()
    prompt = f'''
You are an expert resume parser. Given the following raw resume text, extract the work history, education, and skills into structured YAML.
- For work history, include: company, title, start_date, end_date, description, and achievements (as a list of bullets).
- For consulting or multi-company roles, list each company as a separate entry if possible.
- For education, include: degree, institution, and graduation year if available.
- For skills, group them by category if possible.

Output YAML in the following structure:

id: resume_2024_06
type: resume
source: users/peter/Peter Spannagle-Resume.pdf
import_date: 2024-06-10
examples:
  - company: ...
    title: ...
    start_date: ...
    end_date: ...
    description: ...
    achievements:
      - ...
education:
  - degree: ...
    institution: ...
    year: ...
skills:
  business: [...]
  technical: [...]
  product: [...]
  leadership: [...]

Resume text:
"""
{resume_text}
"""
'''
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.chat.completions.create(
        model='gpt-4-turbo',
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    print(response.choices[0].message.content)

if __name__ == '__main__':
    main() 