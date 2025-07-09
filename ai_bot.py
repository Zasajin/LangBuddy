import logging
import db
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AILanguageBot:

    # Maybe adjust max.history
    def __init__(self, client, model_options):

        self.client = client
        self.model_options =  model_options
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = 20


    async def get_ai_response(self, message: str, user_id: str, model: str, system_prompt: Optional[str] = None) -> str:

        try:

            if user_id not in self.conversation_history:

                self.conversation_history[user_id] = []

            if system_prompt is None:

                # TODO: customize system prompt
                system_prompt = '' 
        
            print(f"Model for user {user_id}: {model}")  # Debugging line
            print(f"System prompt for user {user_id}: {system_prompt}")  # Debugging line
            print(f'Message for user {user_id}: {message}')  # Debugging line

            # Message array with added history 
            messages = [{'role': 'system', 'content': system_prompt}]
            messages.extend(self.conversation_history[user_id])
            messages.append({'role': 'user', 'content': message})

            print(f"Messages for user {user_id}: {messages}")  # Debugging line

            # Add default model
            response = await self.client.chat.completions.create(
                model=self.model_options.get(model, 'qwen/qwen3-8b'),
                messages=messages,
                max_tokens=100,  # Adjust as needed
                temperature=0.7,  # Adjust as needed
            )

            ai_response = response.choices[0].message.content
            print(f"AI response for user {user_id}: {ai_response}")  # Debugging line

            self.conversation_history[user_id].append({'role': 'user', 'content': message})
            self.conversation_history[user_id].append({'role': 'assistant', 'content': ai_response})

            print(f"Updated conversation history for user {user_id}: {self.conversation_history[user_id]}")  # Debugging line

            # TODO: adjust history cleanse logic
            if len(self.conversation_history[user_id]) > self.max_history:

                self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history:]

            if ai_response and ai_response.strip():

                return ai_response

        # Maybe adjust error message (output {str(e)})
        except Exception as e:

            logger.error(f"Error in get_ai_response: {str(e)}")

            return "Sorry, I couldn't process your request at the moment. Please try again later."


    # Maybe adjust for different use cases
    # i.e. admin only, keep some messages
    async def reset_conversation(self, user_id: str) -> bool:

        if user_id in self.conversation_history:

            del self.conversation_history[user_id]
            
            return True

        return False


    async def first_contact(self, ctx):

        try:

            result = await db.check_user(str(ctx.author.id))
            print(f"User check result: {result}")  # Debugging line

            if result:

                try:

                    response = await self.get_ai_response(
                        message=ctx.message.content,
                        user_id=str(ctx.author.id),
                        model= 'general',
                        system_prompt='You are an optimistic language teacher and one of your regular students approaches you. Greet them appropriately to the current central european daytime and ask them how you may help them.'
                    )
                    print(f"AI response: {response}")  # Debugging line

                    if response and response.strip():

                        await ctx.send(response)

                    else:

                        await ctx.send("I'm having trouble generating a response. Please try again later. 01")

                except Exception as e:

                    logger.error(f"Error in first_contact: {str(e)}")

                    await ctx.send("Sorry, I couldn't process your request at the moment. Please try again later. 01")

            else:

                try:

                    success = await db.add_user(str(ctx.author.id))

                    if success:

                        try:

                            response = await self.get_ai_response(
                                message=ctx.message.content,
                                user_id=str(ctx.author.id),
                                model='general',
                                system_prompt='You are an optimistic language teacher and a new students approaches you. Greet them appropriately to the current central europe daytime.'
                            )

                            # TODO: Add functionality to explain the user the bot
                            print(f"AI response: {response}")  # Debugging line

                            if response and response.strip():

                                await ctx.send(response)

                            else:

                                await ctx.send("I'm having trouble generating a response. Please try again later. 02")

                        except Exception as e:

                            logger.error(f"Error in first_contact: {str(e)}")

                            await ctx.send("Sorry, I couldn't process your request at the moment. Please try again later. 02")

                    else:

                        try:

                            response = await self.get_ai_response(
                                message=ctx.message.content,
                                user_id=str(ctx.author.id),
                                model='general',
                                system_prompt='You are an optimistic language teacher and a new student approaches you. Greet them, but tell them you could not register them (to the database)'
                            )

                            # TODO: Add functionality to explain the user the bot
                            print(f"AI response: {response}")  # Debugging line

                            if response and response.strip():

                                await ctx.send(response)

                            else:

                                await ctx.send("I'm having trouble generating a response. Please try again later. 03")

                        except Exception as e:

                            logger.error(f"Error in first_contact: {str(e)}")

                            await ctx.send("Sorry, I couldn't process your request at the moment. Please try again later. 03")

                except Exception as e:

                    logger.error(f"Error in first_contact: {str(e)}")

                    await ctx.send("Sorry, I couldn't process your request at the moment. Please try again later. 03")

        except Exception as e:

            logger.error(f"Error in first_contact: {str(e)}")

            await ctx.send("Sorry, I couldn't process your request at the moment. Please try again later. 03")
