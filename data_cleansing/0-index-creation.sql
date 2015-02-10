-- Create index on tables if not yet existent
-- Create necessary IDXs on post table
CREATE INDEX posts_idx_1 ON SO_POSTS (AcceptedAnswerId);
CREATE INDEX posts_idx_2 ON SO_POSTS (ParentId);
CREATE INDEX posts_idx_3 ON SO_POSTS (OwnerUserId);
CREATE INDEX posts_idx_4 ON SO_POSTS (LastEditorUserId);
CREATE INDEX posts_idx_5 ON SO_POSTS (PostTypeId);

-- Create necessary IDXs on votes table
CREATE INDEX votes_idx_1 ON SO_VOTES (PostId);

-- Create necessary IDXs on comments table
CREATE INDEX comments_idx_1 ON SO_COMMENTS (PostId);