-- There are to many bounty combinations of start and end in the table.
-- This is because from the data it is not clear which bounty end belongs
-- to which bounty start. Therefore we need to delete unnecessary bounties.

-- We can't delete them directly because we cannot use an EXIST on the table 
-- where the delete is happening. Therefore we need an intermediate table
CREATE TABLE `bounties_delete` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`Id`),
};

INSERT INTO bounties_delete(Id) 
SELECT Id FROM bounties a 
WHERE EXISTS( -- We only want the combinations that are closest together
  SELECT * 
  FROM bounties b
  WHERE NOT(b.Id = a.Id) 
    AND a.StartId = b.StartId 
    AND b.EndDate < a.EndDate
  );

DELETE 
FROM bounties 
WHERE EXISTS (
  SELECT bounties_delete.Id 
  FROM bounties_delete 
  WHERE bounties_delete.Id = bounties_n.Id
  );

DELETE
FROM bounties_delete;

-- Started Bounties without an end bounty event
INSERT INTO bounties_delete(Id)
(
  SELECT b.Id FROM bounties b
  WHERE b.StartDate > b.EndDate
    AND NOT EXISTS (
      SELECT * FROM bounties 
      WHERE bounties.StartDate < bounties.EndDate 
        AND bounties.StartDate = b.StartDate 
        AND bounties.QuestionId = b.QuestionId
    )
);

DELETE 
FROM bounties 
WHERE EXISTS (
  SELECT bounties_delete.Id 
  FROM bounties_delete 
  WHERE bounties_delete.Id = bounties_n.Id
  );


DROP TABLE `bounties_delete`;

-- Wrongly ordered bounty events
DELETE
FROM bounties
WHERE bounties.StartDate > bounties.EndDate;

-- Delete awarded Bounties without a valid bounty hunter
DELETE 
FROM bounties 
WHERE bounties.HunterId is null 
  AND bounties.HuntedBountyAmount is not null;