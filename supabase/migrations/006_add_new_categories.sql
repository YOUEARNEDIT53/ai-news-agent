-- Add new item categories for better classification

-- Add new enum values (PostgreSQL allows adding values to enums)
DO $$ BEGIN
  -- Note: ALTER TYPE ... ADD VALUE cannot run inside a transaction block in older versions
  -- but works in modern PostgreSQL. We handle any errors.
  ALTER TYPE item_category ADD VALUE IF NOT EXISTS 'research_breakthrough';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TYPE item_category ADD VALUE IF NOT EXISTS 'lab_announcement';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TYPE item_category ADD VALUE IF NOT EXISTS 'open_source';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TYPE item_category ADD VALUE IF NOT EXISTS 'enterprise';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TYPE item_category ADD VALUE IF NOT EXISTS 'industrial';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TYPE item_category ADD VALUE IF NOT EXISTS 'community';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
