-- Calculates features and creates the initial set of training examples in the training_features table

INSERT INTO SO_TRAINING_FEATURES (Id, StartDate, EndDate, bounty_height)
  SELECT
    b.id,
    b.StartDate,
    b.EndDate,
    b.StartBountyAmount
  FROM SO_BOUNTIES b;

-- Calculate bounty creation time and view count

UPDATE SO_TRAINING_FEATURES
SET time_till_bounty_creation   = SECONDS_BETWEEN(question_date, SO_TRAINING_FEATURES.StartDate) / 60,
  log_time_till_bounty_creation = FLOOR(LOG(10, SECONDS_BETWEEN(question_date, SO_TRAINING_FEATURES.StartDate) / 60)),
  view_count                    = viewcount,
  log_view_count                = FLOOR(LOG(2,viewcount)),
  log_avg_daily_views           = FLOOR(
      LOG(2,viewcount / (SECONDS_BETWEEN(question_date, SO_TRAINING_FEATURES.StartDate) / 60)))
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT
      b.Id                  AS Id,
      question.CreationDate AS question_date,
      viewcount
    FROM SO_BOUNTIES b, SO_POSTS question
    WHERE b.QuestionId = question.Id
  ) AS A ON A.Id = SO_TRAINING_FEATURES.Id;

-- Calculate Answer Date and Duration

UPDATE SO_TRAINING_FEATURES
SET AnswerDate   = answer_date,
  answer_duration = SECONDS_BETWEEN(SO_TRAINING_FEATURES.StartDate, answer_date) / 60
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT
      b.Id                AS ID,
      answer.CreationDate AS answer_date
    FROM SO_BOUNTIES b, SO_POSTS answer
    WHERE b.AnswerId != b.QuestionId AND
          b.AnswerId = answer.Id AND
          b.StartDate < answer.CreationDate
  ) AS X ON X.Id = SO_TRAINING_FEATURES.Id;

-- Flag if answer was edited and therefore created before the bounty start

UPDATE SO_TRAINING_FEATURES
SET answer_was_edited = TRUE
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT
      b.Id                AS ID
    FROM SO_BOUNTIES b, SO_POSTS answer
    WHERE b.AnswerId != b.QuestionId AND
          b.AnswerId = answer.Id AND
          b.StartDate >= answer.CreationDate
  ) AS X ON X.Id = SO_TRAINING_FEATURES.Id;

-- Calculate success feature

UPDATE SO_TRAINING_FEATURES
SET successful = 0
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT b.Id AS ID
    FROM SO_BOUNTIES b
    WHERE b.HuntedBountyAmount IS NULL
  ) AS unsuccessful ON unsuccessful.Id = SO_TRAINING_FEATURES.Id;

-- Number of answers before bounty was posted

UPDATE SO_TRAINING_FEATURES
SET num_answers_bounty = num, log_num_answers = FLOOR(LOG(2, num))
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT
      b.Id,
      COUNT(answer.Id) AS num
    FROM SO_BOUNTIES b, SO_POSTS answer
    WHERE b.QuestionId = answer.ParentId AND answer.CreationDate < b.StartDate
    GROUP BY b.Id
  ) AS X ON X.Id = SO_TRAINING_FEATURES.Id;

-- Number of up-votes / down-votes. Difference will be the score of a question

UPDATE SO_TRAINING_FEATURES
SET question_score = num_up - num_down
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT
      b.Id,
      Count(v.Id) AS num_up
    FROM SO_BOUNTIES b, SO_VOTES v
    WHERE b.QuestionId = v.PostId AND v.VoteTypeId = 2 AND v.CreationDate < b.StartDate
    GROUP BY b.Id
  ) AS UP ON UP.Id = SO_TRAINING_FEATURES.Id
  JOIN
  (
    SELECT
      b.Id,
      Count(v.Id) AS num_down
    FROM SO_BOUNTIES b, SO_VOTES v
    WHERE b.QuestionId = v.PostId AND v.VoteTypeId = 3 AND v.CreationDate < b.StartDate
    GROUP BY b.Id
  ) AS DOWN ON DOWN.Id = SO_TRAINING_FEATURES.Id;

-- Calculate comment features

UPDATE SO_TRAINING_FEATURES
SET num_comments_bounty = num_comments, 
  log_num_comments = floor(log(2, num_comments)),
  avg_len_comments = len_comments / num_comments,
  len_comments_bounty = len_comments,
  log_len_comments = floor(log(2, len_comments))
FROM SO_TRAINING_FEATURES
  JOIN
  (
    SELECT
      b.Id, Count(comment.Id) as num_comments, SUM(LENGTH(comment.Text)) as len_comments
    FROM SO_BOUNTIES b, SO_COMMENTS comment
    WHERE b.QuestionId = comment.PostId
    GROUP BY b.Id
  ) AS X ON X.Id = SO_TRAINING_FEATURES.Id;

