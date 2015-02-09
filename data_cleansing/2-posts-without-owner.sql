-- Delete all there Posts where there is no owner. If the owner got deleted the
-- OwnerUserId is normally set to -1 by stackoverflow.
DELETE FROM SO_POSTS
WHERE OwnerUserId IS NULL