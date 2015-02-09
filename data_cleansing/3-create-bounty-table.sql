-- Create Start-Date table for bounties. We need to crawl exact CreationDates
-- from SO. The datetimes contained in the dump have time set to 00:00:00. 
CREATE TABLE SO_START_BOUNTIES (
  Id           INT NOT NULL,
  PostId       INT NOT NULL,
  VoteTypeId   SMALLINT DEFAULT NULL,
  UserId       INT      DEFAULT NULL,
  CreationDate DATETIME DEFAULT NULL,
  BountyAmount INT      DEFAULT NULL,
  PRIMARY KEY (Id)
);

CREATE INDEX "start_bounties_1" ON SO_START_BOUNTIES (PostId);

CREATE TABLE SO_START_CORRECTED (
  Id          INT NOT NULL,
  CreatedTime DATETIME DEFAULT NULL,
  CreatedDate DATETIME DEFAULT NULL,
  PRIMARY KEY (Id)
);

INSERT INTO SO_START_BOUNTIES (id, PostId, VoteTypeId, UserId, CreationDate, BountyAmount)
  SELECT *
  FROM SO_VOTES AS votes
  WHERE votes.VoteTypeId = 8
        AND EXISTS(SELECT *
                   FROM SO_POSTS AS posts
                   WHERE posts.Id = votes.PostId);


-- Create End-Date table for bounties. We need to crawl exact CreationDates
-- from SO. The datetimes contained in the dump have time set to 00:00:00.
CREATE TABLE SO_END_BOUNTIES (
  Id           INT NOT NULL,
  PostId       INT NOT NULL,
  VoteTypeId   SMALLINT DEFAULT NULL,
  UserId       INT      DEFAULT NULL,
  CreationDate DATETIME DEFAULT NULL,
  BountyAmount INT      DEFAULT NULL,
  PRIMARY KEY (Id)
);

CREATE INDEX "end_bounties_idx_2" ON SO_END_BOUNTIES (PostId);

CREATE TABLE SO_END_CORRECTED (
  Id          INT NOT NULL,
  CreatedTime DATETIME DEFAULT NULL,
  CreatedDate DATETIME DEFAULT NULL,
  PRIMARY KEY (Id)
);

INSERT INTO SO_END_BOUNTIES (id, PostId, VoteTypeId, UserId, CreationDate, BountyAmount)
  SELECT
    votes.Id,
    votes.PostId,
    votes.VoteTypeId,
    posts.OwnerUserId,
    votes.CreationDate,
    votes.BountyAmount
  FROM SO_VOTES AS votes, SO_POSTS AS posts
  WHERE votes.VoteTypeId = 9 AND posts.Id = votes.PostId;

-- Create special table that contains a 'complete' bounty, referencing the start
-- vote and the end vote. This is very helpful in calculating answer durations

CREATE TABLE SO_BOUNTIES (
  Id                 INT NOT NULL PRIMARY KEY,
  QuestionId         INT NOT NULL,
  AnswerId           INT NOT NULL,
  StartId            INT NOT NULL,
  EndId              INT NOT NULL,
  CreatorId          INT      DEFAULT NULL,
  HunterId           INT      DEFAULT NULL,
  StartDate          DATETIME DEFAULT NULL,
  EndDate            DATETIME DEFAULT NULL,
  StartBountyAmount  INT      DEFAULT NULL,
  HuntedBountyAmount INT      DEFAULT NULL
);

CREATE INDEX bounties_idx_8 ON SO_BOUNTIES (HunterId);
CREATE INDEX bounties_idx_1 ON SO_BOUNTIES (QuestionId);
CREATE INDEX bounties_idx_9 ON SO_BOUNTIES (CreatorId);
CREATE INDEX bounties_idx_2 ON SO_BOUNTIES (StartId);
CREATE INDEX bounties_idx_3 ON SO_BOUNTIES (EndId);
CREATE INDEX bounties_idx_4 ON SO_BOUNTIES (AnswerId);
CREATE INDEX bounties_idx_5 ON SO_BOUNTIES (StartDate);
CREATE INDEX bounties_idx_6 ON SO_BOUNTIES (EndDate);

CREATE SEQUENCE SO_BOUNTIES_SEQ START WITH 1;

INSERT INTO SO_BOUNTIES (Id, QuestionId, AnswerId, StartId, EndId, CreatorId, HunterId, StartDate, EndDate, StartBountyAmount, HuntedBountyAmount)
  SELECT
    SO_BOUNTIES_SEQ.NEXTVAL,
    start_bounties.PostId       AS QuestionId,
    end_bounties.PostId         AS AnswerId,
    start_bounties.Id           AS StartId,
    end_bounties.Id             AS EndId,
    start_bounties.UserId       AS CreatorId,
    end_bounties.UserId         AS HunterId,
    start_bounties.CreationDate AS StartDate,
    end_bounties.CreationDate   AS EndDate,
    start_bounties.BountyAmount AS StartBountyAmount,
    end_bounties.BountyAmount   AS HuntedBountyAmount
  FROM SO_START_BOUNTIES AS start_bounties, SO_END_BOUNTIES AS end_bounties, SO_POSTS AS posts
  WHERE
-- either the bounty was successful
    (start_bounties.PostId = posts.ParentId AND end_bounties.PostId = posts.Id
     OR
     -- or the bounty was unsuccessful (no accepted answer)
     start_bounties.PostId = posts.Id AND end_bounties.PostId = posts.Id);
