-- Delete all there Posts where there is no owner. If the owner got deleted the
-- `OwnerUserId` is normally set to -1 by stackoverflow.
DELETE FROM posts WHERE `OwnerUserId` is NULL 