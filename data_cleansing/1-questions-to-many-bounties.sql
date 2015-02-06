-- !!!! DOSN'T WORK ON HANA !!!!

-- Question with more Bounty starts then Bounty Ends. 
-- doesn't work in MySQL (no `with` support)

with BS as (
  Select v.Id as VoteId, p.Id, Count(v.Id) bountyCount
  FROM Votes v, Posts p
  WHERE v.VoteTypeId = 8    -- open bounty vote
    AND p.Id = v.PostId
  GROUP BY p.Id
), BE_QUESTION as(
  Select p.Id, Count(v.Id) bountyCount
  FROM Votes v, Posts p
  WHERE v.VoteTypeId = 9    -- closed bounty vote
    AND p.Id = v.PostId 
    AND p.ParentId is null
  GROUP BY p.Id
), BE_ANSWER as(
  Select p.ParentId, Count(v.Id) bountyCount
  FROM Votes v, Posts p
  WHERE v.VoteTypeId = 9    -- closed bounty vote
    AND p.Id = v.PostId 
    AND p.ParentId is not null
  GROUP BY p.ParentId
)

DELETE v FROM Votes v,
  BS, BE_QUESTION, BE_ANSWER
WHERE BS.VoteId = v.Id
  AND BS.Id = BE_QUESTION.Id 
  AND BS.Id = BE_ANSWER.ParentId 
  AND not (BS.bountyCount - BE_QUESTION.bountyCount - BE_ANSWER.bountyCount) = 0