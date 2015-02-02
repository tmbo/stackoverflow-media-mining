-- Delete all votes without corresponding questions
DELETE FROM Votes AS v 
WHERE NOT EXISTS (SELECT Id FROM POSTS as p WHERE p.Id =  v.PostId)