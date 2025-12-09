from litestar import Controller, get
from litestar.response import Response


class HealthController(Controller):
    path = "/health"
    tags = ["System"]

    @get("/")
    async def health_check(self) -> dict[str, str]:
        """Health check endpoint for Kubernetes probes."""
        return {"status": "ok"}

    @get("/ready")
    async def readiness_check(self) -> dict[str, str]:
        """Readiness check endpoint."""
        return {"status": "ready"}
