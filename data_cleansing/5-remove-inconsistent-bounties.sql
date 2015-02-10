-- There are to many bounty combinations of start and end in the table.
-- This is because from the data it is not clear which bounty end belongs
-- to which bounty start. Therefore we need to delete unnecessary bounties.

-- We can't delete them directly because we cannot use an EXIST on the table 
-- where the delete is happening. Therefore we need an intermediate table
CREATE TABLE SO_BOUNTIES_DELETE (
  Id INT NOT NULL PRIMARY KEY
);

INSERT INTO SO_BOUNTIES_DELETE (Id)
  SELECT a.Id
  FROM SO_BOUNTIES a
  WHERE EXISTS(-- We only want the combinations that are closest together
      SELECT *
      FROM SO_BOUNTIES b
      WHERE NOT (b.Id = a.Id)
            AND a.StartId = b.StartId
            AND b.EndDate < a.EndDate
  );

DELETE
FROM SO_BOUNTIES
WHERE EXISTS(
    SELECT SO_BOUNTIES_DELETE.Id
    FROM SO_BOUNTIES_DELETE
    WHERE SO_BOUNTIES_DELETE.Id = SO_BOUNTIES.Id
);

DELETE
FROM SO_BOUNTIES_DELETE;

-- Started Bounties without an end bounty event
INSERT INTO SO_BOUNTIES_DELETE (Id)
  (
    SELECT b.Id
    FROM SO_BOUNTIES b
    WHERE b.StartDate > b.EndDate
          AND NOT EXISTS(
        SELECT *
        FROM SO_BOUNTIES a
        WHERE a.StartDate < a.EndDate
              AND a.StartDate = b.StartDate
              AND a.QuestionId = b.QuestionId
    )
  );

DELETE
FROM SO_BOUNTIES
WHERE EXISTS(
    SELECT SO_BOUNTIES_DELETE.Id
    FROM SO_BOUNTIES_DELETE
    WHERE SO_BOUNTIES_DELETE.Id = SO_BOUNTIES.Id
);


DROP TABLE SO_BOUNTIES;

-- Wrongly ordered bounty events
DELETE
FROM SO_BOUNTIES
WHERE SO_BOUNTIES.StartDate > SO_BOUNTIES.EndDate;

-- Delete awarded Bounties without a valid bounty hunter
DELETE
FROM SO_BOUNTIES
WHERE SO_BOUNTIES.HunterId IS NULL
      AND SO_BOUNTIES.HuntedBountyAmount IS NOT NULL;