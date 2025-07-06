import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AILanguageBot:

    # Maybe adjust max.history
    def __init__(self, client):

        self.client = client
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = 50

    # TODO: insert model/s
    async def get_ai_response(self, message: str, user_id: str, model: str = 'openrouter/cypher-alpha:free', system_prompt: Optional[str] = None) -> str:

        try:

            if user_id not in self.conversation_history:

                self.conversation_history[user_id] = []

            if system_prompt is None:

                # TODO: customize system prompt
                system_prompt = '' 
        
            # Message array with added history 
            messages = [{'role': 'system', 'content': system_prompt}]
            messages.extend(self.conversation_history[user_id])
            messages.append({'role': 'user', 'content': message})

            # Add default model
            response = await self.client.chat.completions.create(
                model=MODEL_OPTIONS.get(model, 'openrouter/cypher-alpha:free'),
                messages=messages,
                max_tokens=500,  # Adjust as needed
                temperature=0.7,  # Adjust as needed
            )

            ai_response = response.choices[0].message.content

            self.conversation_history[user_id].append({'role': 'user', 'content': message})
            self.conversation_history[user_id].append({'role': 'assistant', 'content': ai_response})

            # TODO: adjust history cleanse logic
            if len(self.conversation_history[user_id]) > self.max_history:

                self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history:]

            return ai_response
        
        # Maybe adjust error message (output {str(e)})
        except Exception as e:

            logger.error(f"Error in get_ai_response: {str(e)}")

            return "Sorry, I couldn't process your request at the moment. Please try again later."

    # Maybe adjust for different use cases
    # i.e. admin only, keep some messages
    def reset_conversation(self, user_id: str) -> bool:

        if user_id in self.conversation_history:

            del self.conversation_history[user_id]
            
            return True

        return False