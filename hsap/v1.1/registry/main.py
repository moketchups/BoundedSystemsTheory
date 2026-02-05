"""
HSAP v1.1 Central Registry Service
FastAPI-based registry for attestation discovery.

Endpoints:
- GET /lookup/{hash} - Find attestation servers for content hash
- POST /register-publisher - Register a new publisher
- GET /publishers - List verified publishers
- GET /stats - Public statistics
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import hashlib
import secrets
import asyncpg
import os

app = FastAPI(
    title="HSAP Registry",
    description="Human Source Attestation Protocol - Central Discovery Registry",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection pool
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://hsap:hsap@localhost:5432/hsap_registry"
)

db_pool = None

# Models
class PublisherRegistration(BaseModel):
    domain: str = Field(..., description="Publisher's domain (e.g., example.com)")
    public_key: str = Field(..., description="Ed25519 public key in PEM format")
    contact_email: str = Field(..., description="Contact email for verification")
    organization: Optional[str] = Field(None, description="Organization name")

class AttestationSubmission(BaseModel):
    content_hash: str = Field(..., description="SHA-256 hash of content")
    publisher_domain: str = Field(..., description="Domain of attesting publisher")

class LookupResponse(BaseModel):
    servers: List[str] = Field(..., description="List of publisher domains with attestations")
    ttl: int = Field(3600, description="Cache TTL in seconds")

class PublisherInfo(BaseModel):
    domain: str
    organization: Optional[str]
    verified: bool
    attestation_count: int
    registered_at: str

class StatsResponse(BaseModel):
    total_publishers: int
    verified_publishers: int
    total_attestations: int
    lookups_24h: int


# Database initialization
async def init_db():
    """Initialize database tables."""
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS publishers (
                id SERIAL PRIMARY KEY,
                domain VARCHAR(255) UNIQUE NOT NULL,
                public_key TEXT NOT NULL,
                contact_email VARCHAR(255) NOT NULL,
                organization VARCHAR(255),
                verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(64),
                verification_method VARCHAR(20),
                attestation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                verified_at TIMESTAMP WITH TIME ZONE
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS attestations (
                id SERIAL PRIMARY KEY,
                content_hash VARCHAR(64) NOT NULL,
                publisher_domain VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(content_hash, publisher_domain)
            )
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_attestations_hash
            ON attestations(content_hash)
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS lookup_log (
                id SERIAL PRIMARY KEY,
                content_hash VARCHAR(64),
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)


@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()


# Endpoints
@app.get("/", tags=["Info"])
async def root():
    """Registry service info."""
    return {
        "service": "HSAP Registry",
        "version": "1.1.0",
        "protocol": "Human Source Attestation Protocol",
        "endpoints": {
            "lookup": "/lookup/{content_hash}",
            "register": "/register-publisher",
            "publishers": "/publishers",
            "stats": "/stats"
        }
    }


@app.get("/lookup/{content_hash}", response_model=LookupResponse, tags=["Discovery"])
async def lookup_attestation(content_hash: str, background_tasks: BackgroundTasks):
    """
    Look up attestation servers for a content hash.

    Returns list of publisher domains that have attestations for this content.
    Clients should then query each publisher's /.well-known/hsap/attestations/{hash}.json
    """
    # Validate hash format
    if len(content_hash) != 64 or not all(c in '0123456789abcdef' for c in content_hash.lower()):
        raise HTTPException(status_code=400, detail="Invalid SHA-256 hash format")

    async with db_pool.acquire() as conn:
        # Log the lookup (async, non-blocking)
        background_tasks.add_task(log_lookup, content_hash)

        # Find all verified publishers with this attestation
        rows = await conn.fetch("""
            SELECT a.publisher_domain
            FROM attestations a
            JOIN publishers p ON a.publisher_domain = p.domain
            WHERE a.content_hash = $1 AND p.verified = TRUE
            ORDER BY p.attestation_count DESC
        """, content_hash.lower())

        servers = [row["publisher_domain"] for row in rows]

    return LookupResponse(servers=servers, ttl=3600)


async def log_lookup(content_hash: str):
    """Log lookup for analytics (runs in background)."""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO lookup_log (content_hash) VALUES ($1)",
                content_hash.lower()
            )
    except Exception:
        pass  # Non-critical, don't fail on logging errors


@app.post("/register-publisher", tags=["Publishers"])
async def register_publisher(registration: PublisherRegistration):
    """
    Register a new publisher for verification.

    Returns a verification token that must be placed at:
    - DNS TXT record: _hsap-verify.{domain}
    - OR file: https://{domain}/.well-known/hsap/verify.txt
    """
    domain = registration.domain.lower().strip()

    # Generate verification token
    verification_token = secrets.token_hex(32)

    async with db_pool.acquire() as conn:
        # Check if domain already registered
        existing = await conn.fetchrow(
            "SELECT id, verified FROM publishers WHERE domain = $1",
            domain
        )

        if existing:
            if existing["verified"]:
                raise HTTPException(status_code=400, detail="Domain already verified")
            else:
                # Update existing unverified registration
                await conn.execute("""
                    UPDATE publishers
                    SET public_key = $1, contact_email = $2, organization = $3,
                        verification_token = $4, created_at = NOW()
                    WHERE domain = $5
                """, registration.public_key, registration.contact_email,
                     registration.organization, verification_token, domain)
        else:
            # New registration
            await conn.execute("""
                INSERT INTO publishers (domain, public_key, contact_email, organization, verification_token)
                VALUES ($1, $2, $3, $4, $5)
            """, domain, registration.public_key, registration.contact_email,
                 registration.organization, verification_token)

    return {
        "status": "pending_verification",
        "domain": domain,
        "verification_token": verification_token,
        "verification_methods": {
            "dns": {
                "type": "TXT",
                "name": f"_hsap-verify.{domain}",
                "value": verification_token
            },
            "file": {
                "url": f"https://{domain}/.well-known/hsap/verify.txt",
                "content": verification_token
            }
        },
        "next_step": "POST /verify-publisher with your domain after placing the token"
    }


@app.post("/verify-publisher", tags=["Publishers"])
async def verify_publisher(domain: str, method: str = "file"):
    """
    Verify a publisher's domain ownership.

    Checks DNS TXT record or file-based verification.
    """
    import aiohttp
    import aiodns

    domain = domain.lower().strip()

    async with db_pool.acquire() as conn:
        publisher = await conn.fetchrow(
            "SELECT verification_token, verified FROM publishers WHERE domain = $1",
            domain
        )

        if not publisher:
            raise HTTPException(status_code=404, detail="Publisher not registered")

        if publisher["verified"]:
            return {"status": "already_verified", "domain": domain}

        token = publisher["verification_token"]
        verified = False

        if method == "dns":
            # Check DNS TXT record
            try:
                resolver = aiodns.DNSResolver()
                records = await resolver.query(f"_hsap-verify.{domain}", "TXT")
                for record in records:
                    if token in str(record.text):
                        verified = True
                        break
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"DNS verification failed: {str(e)}")

        elif method == "file":
            # Check file-based verification
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"https://{domain}/.well-known/hsap/verify.txt"
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            content = await resp.text()
                            if token in content:
                                verified = True
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"File verification failed: {str(e)}")

        else:
            raise HTTPException(status_code=400, detail="Invalid verification method. Use 'dns' or 'file'")

        if verified:
            await conn.execute("""
                UPDATE publishers
                SET verified = TRUE, verified_at = NOW(), verification_method = $1
                WHERE domain = $2
            """, method, domain)

            return {"status": "verified", "domain": domain, "method": method}
        else:
            raise HTTPException(status_code=400, detail="Verification token not found")


@app.post("/submit-attestation", tags=["Attestations"])
async def submit_attestation(submission: AttestationSubmission):
    """
    Submit an attestation record to the registry.

    Publisher must be verified. This registers that the publisher
    has an attestation for this content hash.
    """
    content_hash = submission.content_hash.lower()
    domain = submission.publisher_domain.lower()

    # Validate hash format
    if len(content_hash) != 64 or not all(c in '0123456789abcdef' for c in content_hash):
        raise HTTPException(status_code=400, detail="Invalid SHA-256 hash format")

    async with db_pool.acquire() as conn:
        # Check publisher is verified
        publisher = await conn.fetchrow(
            "SELECT verified FROM publishers WHERE domain = $1",
            domain
        )

        if not publisher:
            raise HTTPException(status_code=404, detail="Publisher not registered")

        if not publisher["verified"]:
            raise HTTPException(status_code=403, detail="Publisher not verified")

        # Insert attestation (ignore duplicates)
        try:
            await conn.execute("""
                INSERT INTO attestations (content_hash, publisher_domain)
                VALUES ($1, $2)
                ON CONFLICT (content_hash, publisher_domain) DO NOTHING
            """, content_hash, domain)

            # Update attestation count
            await conn.execute("""
                UPDATE publishers
                SET attestation_count = attestation_count + 1
                WHERE domain = $1
            """, domain)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "submitted", "content_hash": content_hash, "publisher": domain}


@app.get("/publishers", response_model=List[PublisherInfo], tags=["Publishers"])
async def list_publishers(verified_only: bool = True):
    """List registered publishers."""
    async with db_pool.acquire() as conn:
        if verified_only:
            rows = await conn.fetch("""
                SELECT domain, organization, verified, attestation_count, created_at
                FROM publishers WHERE verified = TRUE
                ORDER BY attestation_count DESC
            """)
        else:
            rows = await conn.fetch("""
                SELECT domain, organization, verified, attestation_count, created_at
                FROM publishers
                ORDER BY attestation_count DESC
            """)

    return [
        PublisherInfo(
            domain=row["domain"],
            organization=row["organization"],
            verified=row["verified"],
            attestation_count=row["attestation_count"],
            registered_at=row["created_at"].isoformat()
        )
        for row in rows
    ]


@app.get("/stats", response_model=StatsResponse, tags=["Info"])
async def get_stats():
    """Get public registry statistics."""
    async with db_pool.acquire() as conn:
        total_publishers = await conn.fetchval("SELECT COUNT(*) FROM publishers")
        verified_publishers = await conn.fetchval("SELECT COUNT(*) FROM publishers WHERE verified = TRUE")
        total_attestations = await conn.fetchval("SELECT COUNT(*) FROM attestations")
        lookups_24h = await conn.fetchval("""
            SELECT COUNT(*) FROM lookup_log
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)

    return StatsResponse(
        total_publishers=total_publishers,
        verified_publishers=verified_publishers,
        total_attestations=total_attestations,
        lookups_24h=lookups_24h
    )


@app.get("/health", tags=["Info"])
async def health_check():
    """Health check endpoint."""
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
