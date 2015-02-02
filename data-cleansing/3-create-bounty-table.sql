-- Create Start-Date table for bounties. We need to crawl exact CreationDates
-- from SO. The datetimes contained in the dump have time set to 00:00:00. 
CREATE TABLE `start_bounties` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) NOT NULL,
  `VoteTypeId` smallint(6) DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `BountyAmount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `PostId` (`PostId`)
);

CREATE TABLE `start_corrected` (
  `Id` int(11) NOT NULL,
  `CreatedTime` datetime DEFAULT NULL,
  `CreatedDate` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
);

INSERT INTO start_bounties (id, PostId, VoteTypeId, UserId, CreationDate, BountyAmount)
SELECT *
FROM votes 
WHERE votes.VoteTypeId = 8 
AND EXISTS(SELECT * FROM posts WHERE posts.Id = votes.PostId);

-- Create End-Date table for bounties. We need to crawl exact CreationDates
-- from SO. The datetimes contained in the dump have time set to 00:00:00.
CREATE TABLE `end_bounties` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) NOT NULL,
  `VoteTypeId` smallint(6) DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `BountyAmount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `end_bounties_idx_2` (`PostId`)
);

CREATE TABLE `end_corrected` (
  `Id` int(11) NOT NULL,
  `CreatedTime` datetime DEFAULT NULL,
  `CreatedDate` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`)
);

INSERT INTO end_bounties (id, PostId, VoteTypeId, UserId, CreationDate, BountyAmount)
SELECT 
  votes.Id, 
  votes.PostId, 
  votes.VoteTypeId, 
  posts.OwnerUserId, 
  votes.CreationDate, 
  votes.BountyAmount
FROM votes, posts 
WHERE votes.VoteTypeId = 9 AND posts.Id = votes.PostId;

-- Create special table that contains a 'complete' bounty, referencing the start
-- vote and the end vote. This is very helpful in calculating answer durations

CREATE TABLE `bounties` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `QuestionId` int(11) NOT NULL,
  `AnswerId` int(11) NOT NULL,
  `StartId` int(11) NOT NULL,
  `EndId` int(11) NOT NULL,
  `CreatorId` int(11) DEFAULT NULL,
  `HunterId` int(11) DEFAULT NULL,
  `StartDate` datetime DEFAULT NULL,
  `EndDate` datetime DEFAULT NULL,
  `StartBountyAmount` int(11) DEFAULT NULL,
  `HuntedBountyAmount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `bounties_idx_8` (`HunterId`),
  KEY `QuestionId` (`QuestionId`),
  KEY `bounties_idx_9` (`CreatorId`),
  KEY `bounties_idx_2` (`StartId`),
  KEY `bounties_idx_3` (`EndId`),
  KEY `bounties_idx_4` (`AnswerId`),
  KEY `bounties_idx_5` (`StartDate`),
  KEY `bounties_idx_6` (`EndDate`)
);

INSERT INTO bounties (QuestionId, AnswerId, StartId, EndId, CreatorId, HunterId, StartDate, EndDate, StartBountyAmount, HuntedBountyAmount)
SELECT 
  start_bounties.PostId as QuestionId,
  end_bounties.PostId as AnswerId,
  start_bounties.Id as StartId,
  end_bounties.Id as EndId,
  start_bounties.UserId as CreatorId,
  end_bounties.UserId as HunterId,
  start_bounties.CreationDate as StartDate,
  end_bounties.CreationDate as EndDate,
  start_bounties.BountyAmount as StartBountyAmount,
  end_bounties.BountyAmount as HuntedBountyAmount
FROM start_bounties, end_bounties, active_posts as posts 
WHERE 
    -- either the bounty was successful
    (start_bounties.PostId = posts.ParentId AND end_bounties.PostId = posts.Id 
  OR 
    -- or the bounty was unsuccessful (no accepted answer)
    start_bounties.PostId = posts.Id AND end_bounties.PostId = posts.Id); 
