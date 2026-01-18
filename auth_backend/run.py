import os

from app import app

if __name__ == "__main__":
    # Preview expects port 3001. Respect PORT if provided, default to 3001.
    port = int(os.getenv("PORT", "3001"))
    app.run(host="0.0.0.0", port=port, debug=False)
