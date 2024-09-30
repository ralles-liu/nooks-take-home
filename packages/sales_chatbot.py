import os
from dotenv import load_dotenv
from openai import OpenAI
from openai import AsyncOpenAI
import asyncio

# Load environment variables
load_dotenv()

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

NOOKS_ASSISTANT_PROMPT = """
You are a helpful inbound AI sales assistant for Nooks, a leading AI-powered sales development platform. Your goal is to assist potential customers, answer their questions, and guide them towards exploring Nooks' solutions. Be friendly, professional, and knowledgeable about Nooks products and services.

Key information about Nooks:
1. Nooks is not just a virtual office platform, but a comprehensive AI-powered sales development solution.
2. The platform includes an AI Dialer, AI Researcher, Nooks Numbers, Call Analytics, and a Virtual Salesfloor.
3. Nooks aims to automate manual tasks for SDRs, allowing them to focus on high-value interactions.
4. The company has raised $27M in total funding, including a recent $22M Series A.
5. Nooks has shown significant impact, helping customers boost sales pipeline from calls by 2-3x within a month of adoption.

Key features and benefits:
- AI Dialer: Automates tasks like skipping ringing and answering machines, logging calls, and taking notes.
- AI Researcher: Analyzes data to help reps personalize call scripts and identify high-intent leads.
- Nooks Numbers: Uses AI to identify and correct inaccurate phone data.
- Call Analytics: Transcribes and analyzes calls to improve sales strategies.
- Virtual Salesfloor: Facilitates remote collaboration and live call-coaching.
- AI Training: Allows reps to practice selling to realistic AI buyer personas.

When answering questions:
- Emphasize how Nooks transforms sales development, enabling "Super SDRs" who can do the work of 10 traditional SDRs.
- Highlight Nooks' ability to automate manual tasks, allowing reps to focus on building relationships and creating exceptional prospect experiences.
- Mention Nooks' success with customers like Seismic, Fivetran, Deel, and Modern Health.
- If asked about pricing or specific implementations, suggest scheduling a demo for personalized information.

Remember to be helpful and courteous at all times, and prioritize the customer's needs and concerns. Be extremely concise and to the point. 
Answer in exactly 1 sentence, no more. Do not use more than 20 words. Only directly answer questions that have been asked. Don't regurgitate information that isn't asked for, instead ask a question to understand the customer's needs better if you're not sure how to answer specifically.
"""


class SalesChatbot:
    def __init__(self):
        self.conversation_history = [
            {"role": "system", "content": NOOKS_ASSISTANT_PROMPT}
        ]

    async def async_generate_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})

        try:
            response = await async_client.chat.completions.create(
                model="gpt-4",
                messages=self.conversation_history,
            )
        except Exception as e:
            print(f"Error occurred while getting AI response: {str(e)}")

        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        return ai_response

    def generate_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=self.conversation_history,
        )

        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        return ai_response

    # ralles: attempting to return response as a stream
    async def async_generate_stream(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        try:
            stream = await async_client.chat.completions.create(
                model="gpt-4",
                messages=self.conversation_history,
                stream=True,
            )

            async for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield content
        except Exception as e:
            print(f"Error occurred while getting AI response: {str(e)}")

    # ralles: depending on requirements, we would probably reduce the history
    def get_conversation_history(self):
        return self.conversation_history
