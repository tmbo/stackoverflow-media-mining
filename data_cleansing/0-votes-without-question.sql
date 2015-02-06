-- Delete all votes without corresponding questions
DELETE FROM SO_VOTES AS v 
WHERE NOT EXISTS (SELECT Id FROM SO_POSTS as p WHERE p.Id =  v.PostId);