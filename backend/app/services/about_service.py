from app.exceptions.http_exceptions import BadRequestException
from app.schemas.about import AboutData, AboutRequest, TeamMemberData
from app.services.google_analytics_service import GoogleAnalyticsService

_ABOUT_ID = "about-us"
_ABOUT_LINK = "/api/about"

_ABOUT_DESCRIPTION = (
    "Individual agents are the heartbeat of real estate. "
    "Agentwise helps agents spend less time marketing and more time "
    "closing deals."
)

_MARKETING_CONTENT = (
    "Agentwise is set to launch in August 2026. Until then, we are "
    "welcoming 100 partners onto the waitlist that will beta-test the "
    "system and get early access to the platform."
)

# Team roster aligned with the About Us Figma / FE Meet Our Team section.
_TEAM_ROSTER: tuple[tuple[str, str, str, str], ...] = (
    (
        "abby",
        "Abby",
        "CEO/Founder",
        "Abby is the CEO and founder of Agentwise.",
    ),
    (
        "cam",
        "Cam",
        "Director of Content",
        "Cam leads the content strategy for Agentwise.",
    ),
    (
        "hunter",
        "Hunter",
        "Marketing Coordinator",
        "Hunter coordinates marketing efforts for Agentwise.",
    ),
    (
        "josh",
        "Josh",
        "Partner",
        "Josh is a partner at Agentwise.",
    ),
    (
        "nova",
        "Nova",
        "Partner",
        "Nova is a partner at Agentwise.",
    ),
)


class AboutService:
    """Business logic for About Us content retrieval."""

    def __init__(self) -> None:
        self.analytics = GoogleAnalyticsService()

    @staticmethod
    def _build_team_members() -> list[TeamMemberData]:
        members: list[TeamMemberData] = []
        for member_id, name, role, description in _TEAM_ROSTER:
            members.append(
                TeamMemberData(
                    id=member_id,
                    name=name,
                    role=role,
                    roles=[role],
                    description=description,
                    link=f"{_ABOUT_LINK}#{member_id}",
                    error=None,
                )
            )
        return members

    @staticmethod
    def _validate_about_payload(data: AboutData) -> None:
        """Ensure required About Us fields are present and well-formed."""
        details: list[dict[str, str]] = []

        if not data.description or not data.description.strip():
            details.append(
                {
                    "field": "description",
                    "message": "About Us description is required",
                }
            )
        if not data.marketing_content or not data.marketing_content.strip():
            details.append(
                {
                    "field": "marketing_content",
                    "message": "Marketing content is required",
                }
            )
        if not data.phone or not data.phone.strip():
            details.append(
                {
                    "field": "phone",
                    "message": "Phone number is required",
                }
            )
        if data.terms_accepted is not True:
            details.append(
                {
                    "field": "terms_accepted",
                    "message": (
                        "You must accept the Terms of Use and Privacy Policy"
                    ),
                }
            )

        for index, member in enumerate(data.team_members):
            prefix = f"team_members.{index}"
            if not member.name or not member.name.strip():
                details.append(
                    {
                        "field": f"{prefix}.name",
                        "message": "Team member name is required",
                    }
                )
            if not member.role or not member.role.strip():
                details.append(
                    {
                        "field": f"{prefix}.role",
                        "message": "Team member role is required",
                    }
                )
            if not member.description or not member.description.strip():
                details.append(
                    {
                        "field": f"{prefix}.description",
                        "message": "Team member description is required",
                    }
                )
            if not member.roles:
                details.append(
                    {
                        "field": f"{prefix}.roles",
                        "message": "Team member roles are required",
                    }
                )

        if details:
            raise BadRequestException(
                message="Validation error",
                code="VALIDATION_ERROR",
                details=details,
            )

    def get_about_content(
        self,
        payload: AboutRequest,
        *,
        user_id: str | None = None,
    ) -> AboutData:
        """Return About Us page content after validating required fields."""
        team_members = self._build_team_members()
        roles = list(dict.fromkeys(member.role for member in team_members))

        data = AboutData(
            id=_ABOUT_ID,
            description=_ABOUT_DESCRIPTION,
            link=_ABOUT_LINK,
            roles=roles,
            error=None,
            team_members=team_members,
            marketing_content=_MARKETING_CONTENT,
            phone=payload.phone,
            terms_accepted=payload.terms_accepted,
        )
        self._validate_about_payload(data)

        self.analytics.track_event(
            "about_page_viewed",
            user_id=user_id,
            extra_params={
                "page": "about_us",
                "phone": payload.phone,
            },
        )
        return data
