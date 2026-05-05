-- LifeHub Database Initialization
-- Tables are auto-created by SQLAlchemy on application startup.
-- This file can be used for additional initialization like extensions.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lifehub TO lifehub;
