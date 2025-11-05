from typing import List, Optional, Union
from pydantic import BaseModel

# -------------------------------
# Request model for bulk answers with multi-choice support
# -------------------------------
class AnswerItem(BaseModel):
    QuestionId: int
    ChoiceId: Optional[Union[int, List[int]]] = None  # Single or multiple choices
    TextAnswer: Optional[str] = None

class BulkAnswerRequest(BaseModel):
    answers: List[AnswerItem]