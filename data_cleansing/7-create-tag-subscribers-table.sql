CREATE TABLE SO_TAG_SUBSCRIBERS (
  Tag VARCHAR(255) NOT NULL DEFAULT '',
  all_subscribers INT DEFAULT NULL,
  active_subscribers INT DEFAULT NULL,
  responsive_subscribers INT DEFAULT NULL,
  PRIMARY KEY (Tag)
)

CREATE TABLE SO_TAG_SUBSCRIBERS_ACTIVE (
  Tag VARCHAR(255) NOT NULL DEFAULT '',
  active_subscribers INT DEFAULT NULL,
  PRIMARY KEY (Tag)
)

-- find all responsive subscribers
INSERT INTO SO_TAG_SUBSCRIBERS (TAG, RESPONSIVE_SUBSCRIBERS)
SELECT Tag, Count(Id) FROM
(SELECT
  t.Tag,
  u.Id FROM SO_USERS u
      INNER JOIN SO_POSTS answer
        ON u.Id = answer.OwnerUserId
      INNER JOIN SO_POSTS question
        ON answer.ParentId = question.Id
      INNER JOIN SO_TAG_POSTS m
        ON question.Id = m.PostId
      INNER JOIN SO_TAGS t
        ON m.TagId = t.Id
   WHERE
       DAYS_BETWEEN(answer.CreationDate, NOW()) <= 30
      AND SECONDS_BETWEEN(question.CreationDate, answer.CreationDate) <= 1 * 3600
   GROUP BY t.TAG, u.Id) AS X
GROUP BY Tag


-- find all active subscribers
INSERT INTO SO_TAG_SUBSCRIBERS_ACTIVE (TAG, ACTIVE_SUBSCRIBERS)
SELECT Tag, Count(Id) numUsers FROM
(SELECT
  t.Tag,
  u.Id,
  SUM(CASE WHEN DAYS_BETWEEN(answer.CreationDate, NOW()) <= 30 THEN 1 ELSE 0 END) AS Num FROM SO_USERS u
      INNER JOIN SO_POSTS answer
        ON u.Id = answer.OwnerUserId
      INNER JOIN SO_POSTS question
        ON answer.ParentId = question.Id
      INNER JOIN SO_TAG_POSTS m
        ON question.Id = m.PostId
      INNER JOIN SO_TAGS t
        ON m.TagId = t.Id
   GROUP BY t.Tag, u.Id) AS X
WHERE Num > 10
GROUP BY Tag
ORDER BY numUsers DESC


--find all subscribers
--TODO

--merged tables
-- TODO