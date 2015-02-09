-- Delete all votes without corresponding questions
DELETE FROM SO_VOTES
WHERE NOT EXISTS(SELECT Id
                 FROM SO_POSTS AS p
                 WHERE p.Id = SO_VOTES.PostId);