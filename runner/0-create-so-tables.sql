-- Creates all Stackoverflow tables. After creating them, data should be imported using a script

CREATE TABLE SO_USERS (
  Id             INT NOT NULL,
  Reputation     INT NOT NULL,
  CreationDate   DATETIME DEFAULT NULL,
  DisplayName    VARCHAR  DEFAULT NULL,
  LastAccessDate DATETIME DEFAULT NULL,
  Views          INT      DEFAULT '0',
  WebsiteUrl     VARCHAR  DEFAULT NULL,
  Location       VARCHAR  DEFAULT NULL,
  AboutMe        CLOB,
  Age            INT      DEFAULT NULL,
  UpVotes        INT      DEFAULT NULL,
  DownVotes      INT      DEFAULT NULL,
  EmailHash      VARCHAR  DEFAULT NULL,
  PRIMARY KEY (Id)
);

-- CREATE TABLE SO_VOTES (
--   Id           INT NOT NULL,
--   PostId       INT NOT NULL,
--   VoteTypeId   SMALLINT DEFAULT NULL,
--   UserId       INT      DEFAULT NULL,
--   CreationDate DATETIME DEFAULT NULL,
--   BountyAmount INT      DEFAULT NULL,
--   PRIMARY KEY (Id)
-- );
--
-- CREATE INDEX votes_1 ON SO_VOTES (PostId);
--
-- CREATE TABLE SO_POSTS (
--   Id               INT NOT NULL,
--   PostTypeId       SMALLINT DEFAULT NULL,
--   AcceptedAnswerId INT      DEFAULT NULL,
--   ParentId         INT      DEFAULT NULL,
--   Score            INT      DEFAULT NULL,
--   ViewCount        INT      DEFAULT NULL,
--   Body             CLOB,
--   OwnerUserId      INT      DEFAULT NULL,
--   LastEditorUserId INT      DEFAULT NULL,
--   LastEditDate     DATETIME DEFAULT NULL,
--   LastActivityDate DATETIME DEFAULT NULL,
--   Title            VARCHAR  DEFAULT NULL,
--   Tags             VARCHAR  DEFAULT NULL,
--   AnswerCount      INT      DEFAULT '0',
--   CommentCount     INT      DEFAULT '0',
--   FavoriteCount    INT      DEFAULT '0',
--   CreationDate     DATETIME DEFAULT NULL,
--   PRIMARY KEY (Id)
-- );
--
-- CREATE INDEX posts_idx_1 ON SO_POSTS (AcceptedAnswerId);
-- CREATE INDEX posts_idx_2 ON SO_POSTS (ParentId);
-- CREATE INDEX posts_idx_3 ON SO_POSTS (OwnerUserId);
-- CREATE INDEX posts_idx_4 ON SO_POSTS (LastEditorUserId);
-- CREATE INDEX posts_idx_5 ON SO_POSTS (PostTypeId);
--
-- CREATE TABLE SO_POST_HISTORY (
--   Id                INT      NOT NULL,
--   PostHistoryTypeId SMALLINT NOT NULL,
--   PostId            INT      NOT NULL,
--   RevisionGUID      VARCHAR  DEFAULT NULL,
--   CreationDate      DATETIME DEFAULT NULL,
--   UserId            INT      DEFAULT NULL,
--   Text              CLOB,
--   PRIMARY KEY (Id)
-- );
--
-- CREATE INDEX post_history_idx_1 ON SO_POST_HISTORY (PostId);
-- CREATE INDEX post_history_idx_2 ON SO_POST_HISTORY (UserId);
-- CREATE INDEX post_history_idx_3 ON SO_POST_HISTORY (PostHistoryTypeId);