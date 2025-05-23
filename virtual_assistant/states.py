from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class StateType(Enum):
    INITIAL = "initial"
    NEEDS_DISCOVERY = "needs_discovery"
    OBJECTION = "objection"
    PRICING = "pricing"
    CLOSING = "closing"
    COMPLETED = "completed"
    UNRELATED_QUESTION = "unrelated_question"

    @classmethod
    def list(cls):
        return [e.value for e in cls]


class StateData(BaseModel):
    current_state: StateType
    user_input: Optional[str] = None
    context: Dict[str, Any] = {}

class BaseState(ABC):
    def __init__(self, state_type: StateType):
        self.state_type = state_type

    @abstractmethod
    def get_prompt(self, context: dict) -> str:
        pass

class InitialState(BaseState):
    def get_prompt(self, context: dict) -> str:
        return (
            "You are a helpful virtual assistant.\n"
            "Goal: Greet the user and offer assistance.\n"
            "Instruction: Politely introduce yourself and ask how you can help the user today."
        )

class NeedsDiscoveryState(BaseState):
    def get_prompt(self, context: dict) -> str:
        return (
            "You are a helpful virtual assistant.\n"
            "Goal: Discover the user's needs or problems.\n"
            "Instruction: Ask clarifying questions to understand what the user wants or what challenges they are facing. Be empathetic and encourage them to share details."
        )

class ObjectionState(BaseState):
    def get_prompt(self, context: dict) -> str:
        return (
            "You are a helpful virtual assistant.\n"
            "Goal: Address the user's objection or concern and try to move them toward a positive decision.\n"
            "Instruction: Listen to the user's concern, provide a thoughtful response that addresses their objection, and encourage them to continue the conversation or consider the value of your offering."
        )

class PricingState(BaseState):
    def get_prompt(self, context: dict) -> str:
        plans = context.get('pricing_plans', {})
        plan_strings = []
        if plans:
            plan_strings = [f"{name.title()}: ${info['price']} - {', '.join(info['features'])}" for name, info in plans.items()]
            plans_text = "\n".join(plan_strings)
        else:
            plans_text = "[No plans loaded]"
        return (
            "You are a helpful virtual assistant.\n"
            "Goal: Clearly present the available pricing plans and help the user choose the best fit for their needs.\n"
            f"Instruction: Share the following pricing plans with the user and offer to answer any questions about them.\n\n{plans_text}"
        )

class UnrelatedQuestionState(BaseState):
    def get_prompt(self, context: dict) -> str:
        return (
            "You are a helpful virtual assistant.\n"
            "Goal: Politely redirect the user back to the conversation about the product or service.\n"
            "Instruction: The user asked a question that is not related to the product or service. Kindly acknowledge their question, but steer the conversation back to how you can help them with the product or their needs."
        )

class ClosingState(BaseState):
    def get_prompt(self, context: dict) -> str:
        return (
            "You are a helpful virtual assistant.\n"
            "Goal: Help the user make a final decision or address any last questions before closing the conversation.\n"
            "Instruction: Ask if the user would like to proceed with a plan or if they have any remaining questions. Be supportive and clear."
        )
