-- ============================================================
-- seed.sql — Test data for TaskFlow
-- ============================================================
-- Creates 1 user, 1 project, and 3 tasks with different statuses.
--
-- Test user credentials:
--   email:    test@taskflow.com
--   password: password123
--
-- The password hash below is bcrypt($2b$12$) for "password123"
-- ============================================================

-- Insert test user (password: password123)
INSERT INTO users (id, name, email, password, created_at)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Test User',
    'test@taskflow.com',
    '$2b$12$LJ3m4ys3Lg2Dqp0t3M7cXOQhP1FeRM0GRfCGq1JqzGKXOiV3P4xLe',
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Insert test project
INSERT INTO projects (id, name, description, owner_id, created_at)
VALUES (
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'Demo Project',
    'A sample project for testing TaskFlow features',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    NOW()
)
ON CONFLICT DO NOTHING;

-- Insert 3 tasks with different statuses
INSERT INTO tasks (id, title, description, status, priority, project_id, assignee_id, creator_id, due_date, created_at, updated_at)
VALUES
    (
        'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
        'Design database schema',
        'Create the initial PostgreSQL schema with users, projects, and tasks tables',
        'done',
        'high',
        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        CURRENT_DATE + INTERVAL '7 days',
        NOW(),
        NOW()
    ),
    (
        'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
        'Implement REST API endpoints',
        'Build all CRUD endpoints for projects and tasks with proper auth',
        'in_progress',
        'high',
        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        CURRENT_DATE + INTERVAL '14 days',
        NOW(),
        NOW()
    ),
    (
        'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a55',
        'Write integration tests',
        'Add comprehensive tests for auth, project, and task endpoints',
        'todo',
        'medium',
        'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        NULL,
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        CURRENT_DATE + INTERVAL '21 days',
        NOW(),
        NOW()
    )
ON CONFLICT DO NOTHING;
