"""View-layer helpers for non-JSON responses."""

from fastapi.responses import HTMLResponse


def render_welcome_page(app_name: str) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
      <head><title>{app_name}</title></head>
      <body>
        <h1>{app_name}</h1>
        <p>API documentation is available at <a href="/docs">/docs</a>.</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
