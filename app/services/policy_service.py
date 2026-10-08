'''
    Responsibilities:

 Retrieve relevant policies
 Rerank candidates
 Return verified policy context
 Handle no/low-confidence match
'''
from enum import Enum
from pydantic import BaseModel, Field


class PolicyMatchStatus(str, Enum):
    MATCH = "MATCH"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NO_MATCH = "NO_MATCH"


class PolicyResult(BaseModel):
    status: PolicyMatchStatus
    policy_text: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class PolicyService:

    def __init__(
        self,
        repository,
        similarity_threshold: float = 0.7,
        low_confidence_threshold: float = 0.4,
    ):
        self.repository = repository
        self.high_threshold = similarity_threshold
        self.low_threshold = low_confidence_threshold

    def get_policy_context(self, user_query: str) -> PolicyResult:
        # Step 1: Search repository for top matching candidate
        top_candidate, confidence_score = (
            self.repository.find_most_similar_policy(user_query)
        )

        # Guard Clause: Handle missing candidate or empty text safely
        if not top_candidate or not getattr(top_candidate, "text", None):
            return PolicyResult(
                status=PolicyMatchStatus.NO_MATCH,
                policy_text=None,
                confidence=0.0,
            )

        # Step 2: Check confidence against thresholds
        if confidence_score >= self.high_threshold:
            return PolicyResult(
                status=PolicyMatchStatus.MATCH,
                policy_text=top_candidate.text,
                confidence=confidence_score,
            )

        elif confidence_score >= self.low_threshold:
            return PolicyResult(
                status=PolicyMatchStatus.LOW_CONFIDENCE,
                policy_text=top_candidate.text,
                confidence=confidence_score,
            )

        else:
            return PolicyResult(
                status=PolicyMatchStatus.NO_MATCH,
                policy_text=None,
                confidence=confidence_score,
            )

class PolicyResponseHandler:
    @staticmethod
    def handle_policy_inquiry(user_query, policy_service, llm_client):
        # Call the service
        result = policy_service.get_policy_context(user_query)

        # Decision tree based on structured result
        if result.status == PolicyMatchStatus.MATCH:
            # Safe to let LLM formulate a polite response using strictly verified policy_text
            response = llm_client.format_policy_answer(user_query, result.policy_text)
            return response

        elif result.status == PolicyMatchStatus.LOW_CONFIDENCE:
            # Ask customer for clarification without guessing
            return "ممكن توضح سؤالك أكتر؟ 😊"

        elif result.status == PolicyMatchStatus.NO_MATCH:
            # Complete fall-back to prevent LLM hallucination
            return "معلش، المعلومة دي مش واضحة عندي حالياً. ممكن تحب أربطك بحد من خدمة العملاء؟ 🌸"
