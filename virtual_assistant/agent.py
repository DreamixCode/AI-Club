from states import StateType, StateData, InitialState, NeedsDiscoveryState, ObjectionState, PricingState, ClosingState, UnrelatedQuestionState
from dotenv import load_dotenv
import os
from openai import OpenAI

import json
from states import StateType, StateData, InitialState, NeedsDiscoveryState, ObjectionState, PricingState, ClosingState
from dotenv import load_dotenv
import os
from openai import OpenAI

class StateManager:
    def __init__(self, client):
        self.client = client
        self.states = {
            StateType.INITIAL: InitialState(StateType.INITIAL),
            StateType.NEEDS_DISCOVERY: NeedsDiscoveryState(StateType.NEEDS_DISCOVERY),
            StateType.OBJECTION: ObjectionState(StateType.OBJECTION),
            StateType.PRICING: PricingState(StateType.PRICING),
            StateType.CLOSING: ClosingState(StateType.CLOSING),
            StateType.UNRELATED_QUESTION: UnrelatedQuestionState(StateType.UNRELATED_QUESTION),
        }
        self.current_state = StateType.INITIAL
        self.conversation_history = []
        self.context = {}
        self._load_pricing_plans()

    def _load_pricing_plans(self):
        try:
            with open('pricing_plans.json', 'r') as f:
                self.context['pricing_plans'] = json.load(f)
        except Exception:
            self.context['pricing_plans'] = {}

    def detect_state(self, user_input: str) -> StateType:
        prompt = f"""
        You are a state detection system for a virtual assistant. 
        Based on the user's message and conversation history, determine the most appropriate state.
        
        Current States:
        {', '.join(StateType.list())}
        
        Conversation History:
        {self._format_conversation_history()}
        
        User's Message: {user_input}
        
        Please respond with ONLY the appropriate state name (e.g., "needs_discovery").
        """
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        state_name = response.choices[0].message.content.strip().lower()
        for s in StateType:
            if s.value == state_name:
                return s
        return self.current_state

    def _format_conversation_history(self) -> str:
        if not self.conversation_history:
            return "No previous conversation history."
        formatted_history = "\n".join(
            f"{turn['role'].upper()}: {turn['message']}" 
            for turn in self.conversation_history[-5:]
        )
        return formatted_history

    def get_prompt(self, state: StateType) -> str:
        return self.states[state].get_prompt(self.context)

    def transition(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "message": user_input})
        detected_state = self.detect_state(user_input)

        print(detected_state)

        self.current_state = detected_state
        if detected_state == StateType.COMPLETED:
            completion_message = "Thank you for your time! The conversation is now complete."
            self.conversation_history.append({"role": "assistant", "message": completion_message})
            # Set a flag in context for the UI/console to check
            self.context['conversation_completed'] = True
            return completion_message
        system_prompt = self.get_prompt(detected_state)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.5
        )
        assistant_reply = response.choices[0].message.content.strip()
        self.conversation_history.append({"role": "assistant", "message": assistant_reply})
        return assistant_reply

class VirtualAssistant:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.manager = StateManager(self.client)

    def process_input(self, user_input: str) -> str:
        return self.manager.transition(user_input)

