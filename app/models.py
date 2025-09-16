from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for type safety
class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MaterialType(str, Enum):
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    IMAGE = "image"
    INTERACTIVE = "interactive"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODING = "coding"


class GenerationStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# Persistent models (stored in database)
class Bootcamp(SQLModel, table=True):
    __tablename__ = "bootcamps"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    topic: str = Field(max_length=100)
    description: str = Field(default="", max_length=2000)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    estimated_duration_hours: int = Field(default=40, ge=1, le=1000)
    learning_objectives: List[str] = Field(default=[], sa_column=Column(JSON))
    prerequisites: List[str] = Field(default=[], sa_column=Column(JSON))
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    generation_status: GenerationStatus = Field(default=GenerationStatus.PENDING)
    generation_prompt: str = Field(default="", max_length=5000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    courses: List["Course"] = Relationship(back_populates="bootcamp", cascade_delete=True)


class Course(SQLModel, table=True):
    __tablename__ = "courses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    bootcamp_id: int = Field(foreign_key="bootcamps.id")
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    order_index: int = Field(ge=0)
    estimated_duration_hours: int = Field(default=8, ge=1, le=100)
    learning_outcomes: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    bootcamp: Bootcamp = Relationship(back_populates="courses")
    lessons: List["Lesson"] = Relationship(back_populates="course", cascade_delete=True)


class Lesson(SQLModel, table=True):
    __tablename__ = "lessons"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="courses.id")
    title: str = Field(max_length=200)
    content: str = Field(default="")
    summary: str = Field(default="", max_length=1000)
    order_index: int = Field(ge=0)
    estimated_duration_minutes: int = Field(default=60, ge=1, le=480)
    key_concepts: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    course: Course = Relationship(back_populates="lessons")
    materials: List["LearningMaterial"] = Relationship(back_populates="lesson", cascade_delete=True)
    quizzes: List["Quiz"] = Relationship(back_populates="lesson", cascade_delete=True)


class LearningMaterial(SQLModel, table=True):
    __tablename__ = "learning_materials"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lessons.id")
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    material_type: MaterialType = Field(default=MaterialType.TEXT)
    content: str = Field(default="")
    url: Optional[str] = Field(default=None, max_length=500)
    file_path: Optional[str] = Field(default=None, max_length=500)
    order_index: int = Field(ge=0)
    material_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lesson: Lesson = Relationship(back_populates="materials")


class Quiz(SQLModel, table=True):
    __tablename__ = "quizzes"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: Optional[int] = Field(default=None, foreign_key="lessons.id")
    bootcamp_id: Optional[int] = Field(default=None, foreign_key="bootcamps.id")
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    is_exam: bool = Field(default=False)
    time_limit_minutes: Optional[int] = Field(default=None, ge=1, le=300)
    passing_score_percentage: int = Field(default=70, ge=0, le=100)
    max_attempts: int = Field(default=3, ge=1, le=10)
    order_index: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    lesson: Optional[Lesson] = Relationship(back_populates="quizzes")
    questions: List["Question"] = Relationship(back_populates="quiz", cascade_delete=True)


class Question(SQLModel, table=True):
    __tablename__ = "questions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quizzes.id")
    question_text: str = Field(max_length=2000)
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE)
    options: List[str] = Field(default=[], sa_column=Column(JSON))
    correct_answers: List[str] = Field(default=[], sa_column=Column(JSON))
    explanation: str = Field(default="", max_length=1000)
    points: int = Field(default=1, ge=1, le=10)
    order_index: int = Field(ge=0)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    quiz: Quiz = Relationship(back_populates="questions")


# Non-persistent schemas (for validation, forms, API requests/responses)
class BootcampCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    topic: str = Field(max_length=100)
    description: str = Field(default="", max_length=2000)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    estimated_duration_hours: int = Field(default=40, ge=1, le=1000)
    learning_objectives: List[str] = Field(default=[])
    prerequisites: List[str] = Field(default=[])
    tags: List[str] = Field(default=[])
    generation_prompt: str = Field(default="", max_length=5000)


class BootcampUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    difficulty_level: Optional[DifficultyLevel] = Field(default=None)
    estimated_duration_hours: Optional[int] = Field(default=None, ge=1, le=1000)
    learning_objectives: Optional[List[str]] = Field(default=None)
    prerequisites: Optional[List[str]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    generation_status: Optional[GenerationStatus] = Field(default=None)


class CourseCreate(SQLModel, table=False):
    bootcamp_id: int
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    order_index: int = Field(ge=0)
    estimated_duration_hours: int = Field(default=8, ge=1, le=100)
    learning_outcomes: List[str] = Field(default=[])


class LessonCreate(SQLModel, table=False):
    course_id: int
    title: str = Field(max_length=200)
    content: str = Field(default="")
    summary: str = Field(default="", max_length=1000)
    order_index: int = Field(ge=0)
    estimated_duration_minutes: int = Field(default=60, ge=1, le=480)
    key_concepts: List[str] = Field(default=[])


class LearningMaterialCreate(SQLModel, table=False):
    lesson_id: int
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    material_type: MaterialType = Field(default=MaterialType.TEXT)
    content: str = Field(default="")
    url: Optional[str] = Field(default=None, max_length=500)
    file_path: Optional[str] = Field(default=None, max_length=500)
    order_index: int = Field(ge=0)
    material_metadata: Dict[str, Any] = Field(default={})


class QuizCreate(SQLModel, table=False):
    lesson_id: Optional[int] = Field(default=None)
    bootcamp_id: Optional[int] = Field(default=None)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    is_exam: bool = Field(default=False)
    time_limit_minutes: Optional[int] = Field(default=None, ge=1, le=300)
    passing_score_percentage: int = Field(default=70, ge=0, le=100)
    max_attempts: int = Field(default=3, ge=1, le=10)
    order_index: int = Field(ge=0)


class QuestionCreate(SQLModel, table=False):
    quiz_id: int
    question_text: str = Field(max_length=2000)
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE)
    options: List[str] = Field(default=[])
    correct_answers: List[str] = Field(default=[])
    explanation: str = Field(default="", max_length=1000)
    points: int = Field(default=1, ge=1, le=10)
    order_index: int = Field(ge=0)
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    tags: List[str] = Field(default=[])


# Response schemas for API
class BootcampResponse(SQLModel, table=False):
    id: int
    title: str
    topic: str
    description: str
    difficulty_level: DifficultyLevel
    estimated_duration_hours: int
    learning_objectives: List[str]
    prerequisites: List[str]
    tags: List[str]
    generation_status: GenerationStatus
    created_at: str
    updated_at: str


class CourseWithLessonsResponse(SQLModel, table=False):
    id: int
    title: str
    description: str
    order_index: int
    estimated_duration_hours: int
    learning_outcomes: List[str]
    lessons_count: int


class LessonDetailResponse(SQLModel, table=False):
    id: int
    title: str
    content: str
    summary: str
    order_index: int
    estimated_duration_minutes: int
    key_concepts: List[str]
    materials_count: int
    quizzes_count: int
