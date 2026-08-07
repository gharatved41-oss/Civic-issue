# Civic Sense AI — container image for Docker / Render / Railway / Fly.io /
# any host that runs an OCI image. Streamlit Community Cloud does NOT need
# this file (it builds directly from requirements.txt) — see README.

FROM python:3.11-slim

WORKDIR /app

# System deps: curl only for the HEALTHCHECK below; pandas/pydeck/folium
# install from wheels on this base image, no other system deps needed.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Persisted at runtime: civic_sense.db (SQLite) and uploaded_images/.
# Mount a volume at /app if you need these to survive container restarts —
# see the "Persistent storage" note in README.md.
RUN mkdir -p uploaded_images

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# $PORT lets PaaS platforms (Render, Railway, Fly.io) override the port;
# defaults to 8501 for plain `docker run`.
ENV PORT=8501
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
