from fastapi.responses import HTMLResponse

from server.app import app


@app.get("/", include_in_schema=False)
def root() -> HTMLResponse:
    return HTMLResponse(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Executive Assistant Negotiation Env</title>
          <style>
            body {
              font-family: Arial, sans-serif;
              margin: 0;
              padding: 32px;
              background: #f8fafc;
              color: #0f172a;
            }
            main {
              max-width: 760px;
              margin: 0 auto;
              background: white;
              border: 1px solid #e2e8f0;
              border-radius: 12px;
              padding: 32px;
            }
            h1 {
              margin-top: 0;
            }
            ul {
              padding-left: 20px;
            }
            a {
              color: #0f766e;
            }
            code {
              background: #f1f5f9;
              padding: 2px 6px;
              border-radius: 6px;
            }
          </style>
        </head>
        <body>
          <main>
            <h1>Executive Assistant Negotiation Env</h1>
            <p>
              This Hugging Face Space hosts an OpenEnv-compatible FastAPI server for
              multi-agent executive assistant planning tasks.
            </p>
            <ul>
              <li><a href="/docs">API docs</a></li>
              <li><a href="/health">Health check</a></li>
              <li><a href="/metadata">Environment metadata</a></li>
              <li><a href="/state">Current state endpoint</a></li>
            </ul>
            <p>
              Root <code>/</code> is a landing page; the environment API is exposed through
              the OpenEnv server endpoints.
            </p>
          </main>
        </body>
        </html>
        """
    )
