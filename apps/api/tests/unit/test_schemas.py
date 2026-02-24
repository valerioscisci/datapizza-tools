"""Tests for Pydantic schema validation (api/schemas/).

Covers validation rules for JobResponse, ProfileUpdate,
ExperienceCreate, EducationCreate, ProposalCreate, and ProposalUpdate schemas.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from api.routes.jobs.schemas import JobResponse
from api.routes.profile.schemas import ProfileUpdate
from api.routes.profile.experiences.schemas import ExperienceCreate
from api.routes.profile.educations.schemas import EducationCreate
from api.routes.proposals.schemas import ProposalCreate, ProposalUpdate


class TestJobResponse:
    """Tests for the JobResponse Pydantic model."""

    def test_valid_job_response(self):
        """JobResponse should accept valid data with all required fields."""
        job = JobResponse(
            id="abc-123",
            title="Python Developer",
            company="TechCorp",
            location="Milano",
            work_mode="remote",
            description="A great job.",
            experience_level="mid",
            employment_type="full-time",
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        assert job.title == "Python Developer"
        assert job.tags == []  # default empty list
        assert job.salary_min is None

    def test_job_response_with_all_fields(self):
        """JobResponse should accept data with all optional fields populated."""
        job = JobResponse(
            id="abc-123",
            title="Python Developer",
            company="TechCorp",
            company_logo_url="https://logo.com/img.png",
            location="Milano",
            work_mode="hybrid",
            description="A great job.",
            salary_min=40000,
            salary_max=60000,
            tags=["Python", "FastAPI"],
            experience_level="senior",
            experience_years="5+ anni",
            employment_type="full-time",
            smart_working="2 giorni/settimana",
            welfare="Welfare 1000 euro",
            language="Inglese: B2",
            apply_url="https://example.com/apply",
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        assert job.salary_min == 40000
        assert job.salary_max == 60000
        assert job.tags == ["Python", "FastAPI"]
        assert job.smart_working == "2 giorni/settimana"

    def test_job_response_missing_required_field(self):
        """JobResponse should reject data missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            JobResponse(
                id="abc-123",
                # missing title, company, location, etc.
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            )
        errors = exc_info.value.errors()
        required_fields = {e["loc"][0] for e in errors}
        assert "title" in required_fields
        assert "company" in required_fields


class TestProfileUpdate:
    """Tests for the ProfileUpdate Pydantic model."""

    def test_valid_profile_update(self):
        """ProfileUpdate should accept partial data for updating profile fields."""
        update = ProfileUpdate(bio="New bio", location="Roma")
        assert update.bio == "New bio"
        assert update.location == "Roma"
        assert update.full_name is None  # not provided

    def test_profile_update_with_skills(self):
        """ProfileUpdate should accept a list of skill strings."""
        update = ProfileUpdate(skills=["Python", "React", "Docker"])
        assert update.skills == ["Python", "React", "Docker"]

    def test_profile_update_empty(self):
        """ProfileUpdate should accept an empty body (no fields to update)."""
        update = ProfileUpdate()
        dumped = update.model_dump(exclude_unset=True)
        assert dumped == {}

    def test_profile_update_full_name_min_length(self):
        """ProfileUpdate should reject full_name shorter than 1 character."""
        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(full_name="")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("full_name",) for e in errors)

    def test_profile_update_social_urls(self):
        """ProfileUpdate should accept social URL fields."""
        update = ProfileUpdate(
            linkedin_url="https://linkedin.com/in/test",
            github_url="https://github.com/test",
            portfolio_url="https://test.dev",
        )
        assert update.linkedin_url == "https://linkedin.com/in/test"
        assert update.github_url == "https://github.com/test"
        assert update.portfolio_url == "https://test.dev"


class TestExperienceCreate:
    """Tests for the ExperienceCreate Pydantic model."""

    def test_valid_experience_create(self):
        """ExperienceCreate should accept valid data with required fields."""
        exp = ExperienceCreate(
            title="Developer",
            company="ACME",
            start_year=2022,
        )
        assert exp.title == "Developer"
        assert exp.company == "ACME"
        assert exp.start_year == 2022
        assert exp.is_current is False  # default

    def test_experience_create_all_fields(self):
        """ExperienceCreate should accept all optional fields."""
        exp = ExperienceCreate(
            title="Senior Developer",
            company="BigCorp",
            employment_type="full-time",
            location="Milano",
            start_month=3,
            start_year=2020,
            end_month=12,
            end_year=2023,
            is_current=False,
            description="Led team of 5 developers.",
        )
        assert exp.start_month == 3
        assert exp.end_year == 2023
        assert exp.description == "Led team of 5 developers."

    def test_experience_create_start_year_required(self):
        """ExperienceCreate should reject missing start_year."""
        with pytest.raises(ValidationError) as exc_info:
            ExperienceCreate(
                title="Developer",
                company="ACME",
                # missing start_year
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("start_year",) for e in errors)

    def test_experience_create_title_required(self):
        """ExperienceCreate should reject missing title."""
        with pytest.raises(ValidationError) as exc_info:
            ExperienceCreate(
                company="ACME",
                start_year=2022,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("title",) for e in errors)

    def test_experience_create_company_required(self):
        """ExperienceCreate should reject missing company."""
        with pytest.raises(ValidationError) as exc_info:
            ExperienceCreate(
                title="Developer",
                start_year=2022,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("company",) for e in errors)

    def test_experience_create_start_year_min_value(self):
        """ExperienceCreate should reject start_year below 1950."""
        with pytest.raises(ValidationError):
            ExperienceCreate(
                title="Developer",
                company="ACME",
                start_year=1900,
            )

    def test_experience_create_start_month_range(self):
        """ExperienceCreate should reject start_month outside 1-12."""
        with pytest.raises(ValidationError):
            ExperienceCreate(
                title="Developer",
                company="ACME",
                start_year=2022,
                start_month=13,
            )


class TestEducationCreate:
    """Tests for the EducationCreate Pydantic model."""

    def test_valid_education_create(self):
        """EducationCreate should accept valid data with required fields."""
        edu = EducationCreate(
            institution="Politecnico di Milano",
            start_year=2018,
        )
        assert edu.institution == "Politecnico di Milano"
        assert edu.start_year == 2018
        assert edu.is_current is False  # default

    def test_education_create_all_fields(self):
        """EducationCreate should accept all optional fields."""
        edu = EducationCreate(
            institution="MIT",
            degree="Master of Science",
            degree_type="master",
            field_of_study="Computer Science",
            start_year=2020,
            end_year=2022,
            is_current=False,
            description="GPA 4.0",
        )
        assert edu.degree == "Master of Science"
        assert edu.degree_type == "master"
        assert edu.field_of_study == "Computer Science"

    def test_education_create_institution_required(self):
        """EducationCreate should reject missing institution."""
        with pytest.raises(ValidationError) as exc_info:
            EducationCreate(
                start_year=2020,
                # missing institution
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("institution",) for e in errors)

    def test_education_create_start_year_required(self):
        """EducationCreate should reject missing start_year."""
        with pytest.raises(ValidationError) as exc_info:
            EducationCreate(
                institution="MIT",
                # missing start_year
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("start_year",) for e in errors)

    def test_education_create_start_year_min_value(self):
        """EducationCreate should reject start_year below 1950."""
        with pytest.raises(ValidationError):
            EducationCreate(
                institution="MIT",
                start_year=1900,
            )

    def test_education_create_institution_min_length(self):
        """EducationCreate should reject empty institution string."""
        with pytest.raises(ValidationError) as exc_info:
            EducationCreate(
                institution="",
                start_year=2020,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("institution",) for e in errors)


class TestProposalCreate:
    """Tests for the ProposalCreate Pydantic model."""

    def test_valid_proposal_create(self):
        """ProposalCreate should accept valid data with required fields."""
        proposal = ProposalCreate(
            talent_id=str(uuid4()),
            course_ids=[str(uuid4())],
        )
        assert proposal.message is None
        assert proposal.budget_range is None
        assert len(proposal.course_ids) == 1

    def test_proposal_create_empty_course_ids_rejected(self):
        """ProposalCreate should reject empty course_ids list."""
        with pytest.raises(ValidationError):
            ProposalCreate(
                talent_id=str(uuid4()),
                course_ids=[],
            )

    def test_proposal_create_missing_talent_id(self):
        """ProposalCreate should reject missing talent_id."""
        with pytest.raises(ValidationError) as exc_info:
            ProposalCreate(
                course_ids=[str(uuid4())],
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("talent_id",) for e in errors)


class TestProposalUpdate:
    """Tests for the ProposalUpdate Pydantic model."""

    def test_valid_proposal_update_status(self):
        """ProposalUpdate should accept valid status values."""
        update = ProposalUpdate(status="accepted")
        assert update.status == "accepted"

    def test_proposal_update_invalid_status(self):
        """ProposalUpdate should reject invalid status values."""
        with pytest.raises(ValidationError):
            ProposalUpdate(status="invalid_status")
