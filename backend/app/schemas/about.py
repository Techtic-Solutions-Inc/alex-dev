import re

from pydantic import BaseModel, Field, field_validator

_PHONE_PATTERN = re.compile(r"^\+?[\d\s\-().]{7,20}$")


def _validate_terms_accepted(value: bool) -> bool:
    if not value:
        raise ValueError(
            "You must accept the Terms of Use and Privacy Policy"
        )
    return value


def _validate_phone(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Phone number is required")
    if not _PHONE_PATTERN.match(stripped):
        raise ValueError("Invalid phone number format")
    return stripped


class AboutRequest(BaseModel):
    """Request body for retrieving About Us content.

    Figma form fields (Mobile App Development / Privacy Policy) must be
    supplied so the API can validate acceptance before returning page data.
    """

    phone: str = Field(
        ...,
        description="Contact phone number (Mobile App Development field)",
        examples=["+1-555-0100"],
    )
    terms_accepted: bool = Field(
        ...,
        description=(
            "Privacy Policy / Terms checkbox; must be true to confirm "
            "acceptance of the Terms of Use and Privacy Policy"
        ),
        examples=[True],
    )

    @field_validator("terms_accepted")
    @classmethod
    def terms_must_be_accepted(cls, value: bool) -> bool:
        return _validate_terms_accepted(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return _validate_phone(value)


class TeamMemberData(BaseModel):
    """A single team member shown on the About Us / Meet Our Team section."""

    id: str = Field(
        ...,
        description="Stable identifier for the team member",
        examples=["abby"],
    )
    name: str = Field(
        ...,
        description="Team member display name",
        examples=["Abby"],
    )
    role: str = Field(
        ...,
        description="Primary role / title shown under the name",
        examples=["CEO/Founder"],
    )
    roles: list[str] = Field(
        ...,
        description="Role labels associated with this team member",
        examples=[["CEO/Founder"]],
    )
    description: str = Field(
        ...,
        description="Short bio displayed on the About Us page",
        examples=["Abby is the CEO and founder of Agentwise."],
    )
    link: str = Field(
        ...,
        description="Relative link for this team member resource",
        examples=["/api/about#abby"],
    )
    error: str | None = Field(
        None,
        description=(
            "UI-facing error detail for this team member; null on success"
        ),
        examples=[None],
    )


class AboutData(BaseModel):
    """About Us page payload returned to the frontend."""

    id: str = Field(
        ...,
        description="Stable identifier for the About Us resource",
        examples=["about-us"],
    )
    description: str = Field(
        ...,
        description=(
            "Primary About Agentwise summary used by the About Us page"
        ),
        examples=[
            "Individual agents are the heartbeat of real estate. "
            "Agentwise helps agents spend less time marketing and more "
            "time closing deals."
        ],
    )
    link: str = Field(
        ...,
        description="Relative URL to the About Us endpoint",
        examples=["/api/about"],
    )
    roles: list[str] = Field(
        ...,
        description="Unique team roles featured on the About Us page",
        examples=[
            [
                "CEO/Founder",
                "Director of Content",
                "Marketing Coordinator",
                "Partner",
            ]
        ],
    )
    error: str | None = Field(
        None,
        description=(
            "UI-facing error detail for the About Us screen; "
            "null on successful responses"
        ),
        examples=[None],
    )
    team_members: list[TeamMemberData] = Field(
        ...,
        description="Team members displayed in the Meet Our Team section",
    )
    marketing_content: str = Field(
        ...,
        description=(
            "Marketing section copy (waitlist / launch messaging)"
        ),
        examples=[
            "Agentwise is set to launch in August 2026. Until then, we are "
            "welcoming 100 partners onto the waitlist that will beta-test "
            "the system and get early access to the platform."
        ],
    )
    phone: str = Field(
        ...,
        description="Contact phone number (Mobile App Development)",
        examples=["+1-555-0100"],
    )
    terms_accepted: bool = Field(
        ...,
        description="Whether Terms of Use and Privacy Policy were accepted",
        examples=[True],
    )


class AboutResponse(BaseModel):
    """Success response for the About Us page."""

    success: bool = Field(True, description="Indicates the request succeeded")
    message: str = Field(
        ...,
        description="Human-readable success message",
        examples=["About Us content retrieved successfully"],
    )
    data: AboutData
