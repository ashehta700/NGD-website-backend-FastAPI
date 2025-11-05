from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base 
from app.models.lookups import SurveyQuestionCategory , SurveyTypeOfQuestion 

class UsersFeedbackQuestion(Base):
    __tablename__ = "UsersfeedbackQuestions"
    __table_args__ = {"schema": "Survey"}

    Id = Column(Integer, primary_key=True)
    CategoryId = Column(Integer, ForeignKey("Survey.QuestionCategory.Id"))
    MainQuestion = Column(String(1000))
    MainQuestion_Ar = Column(String(1000))
    TypeOfQuestionId = Column(Integer, ForeignKey("Survey.TypeOfQuestion.Id"))
    CreatedAt = Column(DateTime)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False)
    
    # ✅ Relationships
    category = relationship("SurveyQuestionCategory", back_populates="questions")
    type = relationship("SurveyTypeOfQuestion", back_populates="questions")
    choices = relationship("QuestionChoice", back_populates="question", cascade="all, delete-orphan")



class QuestionChoice(Base):
    __tablename__ = "QuestionChoices"
    __table_args__ = {"schema": "Survey"}

    Id = Column(Integer, primary_key=True)
    QuestionId = Column(Integer, ForeignKey("Survey.UsersfeedbackQuestions.Id"))
    Choice = Column(String(100), nullable=False)
    Choice_Ar = Column(String(100), nullable=False)
    CreatedAt = Column(DateTime)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False)

    # ✅ Relationship back to question
    question = relationship("UsersFeedbackQuestion", back_populates="choices")



class UsersFeedbackAnswer(Base):
    __tablename__ = "UsersFeedbackAnswers"
    __table_args__ = {"schema": "Survey"}

    Id = Column(Integer, primary_key=True)
    QuestionId = Column(Integer, ForeignKey("Survey.UsersfeedbackQuestions.Id"))
    ChoiceId = Column(Integer, ForeignKey("Survey.QuestionChoices.Id"))
    please_specify = Column(String(1000))
    CreatedAt = Column(DateTime)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False)
    VisitorId = Column(Integer)

    # ✅ Relationships for easy joins
    question = relationship("UsersFeedbackQuestion")
    choice = relationship("QuestionChoice")




# table for vote question and answer 
class Vote(Base):
    __tablename__ = "Vote"
    __table_args__ = {"schema": "Survey"}

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    UserId = Column(Integer,ForeignKey("Website.Users.UserID"), nullable=True)
    VisitorId = Column(Integer, ForeignKey("Website.Visitors.VisitorID"), nullable=True)  # FK to Visitors table

    Answer = Column(String(50), nullable=False)  # "Yes" / "No"
    SubAnswer = Column(String, nullable=True)   # Reason if "No"

    CreatedAt = Column(DateTime)


