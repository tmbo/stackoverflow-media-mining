-- create table that contains the subscriber statistics
CREATE TABLE SO_TAG_SUBSCRIBERS (
  TAG VARCHAR(255) NOT NULL DEFAULT '',
  ALL_SUBSCRIBERS INT DEFAULT NULL,
  ACTIVE_SUBSCRIBERS INT DEFAULT NULL,
  RESPONSIVE_SUBSCRIBERS INT DEFAULT NULL,
  PRIMARY KEY (TAG)
);

-- create some temp tables to store intermediate results
-- will be deleted later
CREATE TABLE SO_TAG_SUBSCRIBERS_ACTIVE_TEMP (
  TAG VARCHAR(255) NOT NULL DEFAULT '',
  ACTIVE_SUBSCRIBERS INT DEFAULT NULL,
  PRIMARY KEY (TAG)
);

CREATE TABLE SO_TAG_SUBSCRIBERS_RESPONSIVE_TEMP (
  TAG VARCHAR(255) NOT NULL DEFAULT '',
  RESPONSIVE_SUBSCRIBERS INT DEFAULT NULL,
  PRIMARY KEY (TAG)
);

CREATE TABLE SO_TAG_TEMP (
  TAG VARCHAR(255) NOT NULL DEFAULT '',
  USERID INT NOT NULL DEFAULT NULL,
  ANSWER_CREATIONDATE DATETIME NOT NULL DEFAULT NULL,
  QUESTION_CREATIONDATE DATETIME NOT NULL DEFAULT NULL
);

-- store expensive join for subsequent queries
INSERT INTO SO_TAG_TEMP (TAG, USERID, QUESTION_CREATIONDATE, ANSWER_CREATIONDATE)
SELECT
  t.Tag,
  u.Id,
  question.CreationDate,
  answer.CreationDate
  FROM SO_USERS u
    INNER JOIN SO_POSTS answer
      ON u.Id = answer.OwnerUserId
    INNER JOIN SO_POSTS question
      ON answer.ParentId = question.Id
    INNER JOIN SO_TAG_POSTS m
      ON question.Id = m.PostId
    INNER JOIN SO_TAGS t
      ON m.TagId = t.Id
;

-- find all subscribers to tag
-- users who answered to a tag in the last 30 days, starting at the day of the data dump
INSERT INTO SO_TAG_SUBSCRIBERS (TAG, ALL_SUBSCRIBERS)
SELECT TAG, Count(USERID) FROM
  (SELECT TAG, USERID
  FROM SO_TAG_TEMP
  WHERE
    DAYS_BETWEEN(ANSWER_CREATIONDATE, TO_DATE ('2014-08-31', 'YYYY-MM-DD')) <= 30
  GROUP BY TAG, USERID)
GROUP BY TAG
;

-- find all responsive subscribers
-- users who answered to a tag in the last 30 days and answered within one hour
INSERT INTO SO_TAG_SUBSCRIBERS_RESPONSIVE_TEMP (TAG, RESPONSIVE_SUBSCRIBERS)
SELECT TAG, Count(USERID) FROM
  (SELECT TAG, USERID
  FROM SO_TAG_TEMP
  WHERE
    DAYS_BETWEEN(ANSWER_CREATIONDATE, TO_DATE ('2014-08-31', 'YYYY-MM-DD')) <= 30
    AND SECONDS_BETWEEN(QUESTION_CREATIONDATE, ANSWER_CREATIONDATE) <= 1 * 3600
  GROUP BY TAG, USERID)
GROUP BY TAG
;

-- find all active subscribers
-- users who answered to a tag in the last 30 days and answered at least 10 times
INSERT INTO SO_TAG_SUBSCRIBERS_ACTIVE_TEMP (TAG, ACTIVE_SUBSCRIBERS)
SELECT TAG, Count(USERID) FROM
  (SELECT TAG,
          USERID,
          SUM(CASE WHEN DAYS_BETWEEN(ANSWER_CREATIONDATE, TO_DATE ('2014-08-31', 'YYYY-MM-DD')) <= 30 THEN 1 ELSE 0 END) AS NUM
  FROM SO_TAG_TEMP
  GROUP BY TAG, USERID)
WHERE NUM > 10
GROUP BY TAG
;

-- merged tables
UPDATE SO_TAG_SUBSCRIBERS, SO_TAG_SUBSCRIBERS_RESPONSIVE_TEMP
SET S.RESPONSIVE_SUBSCRIBERS = R.RESPONSIVE_SUBSCRIBERS
FROM SO_TAG_SUBSCRIBERS AS S, SO_TAG_SUBSCRIBERS_RESPONSIVE_TEMP AS R
WHERE S.TAG = R.TAG;

UPDATE SO_TAG_SUBSCRIBERS, SO_TAG_SUBSCRIBERS_ACTIVE_TEMP
SET S.ACTIVE_SUBSCRIBERS = A.ACTIVE_SUBSCRIBERS
FROM SO_TAG_SUBSCRIBERS as S, SO_TAG_SUBSCRIBERS_ACTIVE_TEMP as A
WHERE S.TAG = A.TAG;

-- delete temp tables
DROP TABLE SO_TAG_SUBSCRIBERS_RESPONSIVE_TEMP;
DROP TABLE SO_TAG_SUBSCRIBERS_ACTIVE_TEMP;
DROP TABLE SO_TAG_TEMP;

-- done