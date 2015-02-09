library(RMySQL)
con <- dbConnect(MySQL(), user = 'root', host = '127.0.0.1', dbname='stackoverflow')

# data <- dbReadTable(conn = con, name = 'training_features')

data <- dbGetQuery(conn = con, statement = "SELECT * FROM SO_training_features WHERE AnswerDate is not null")

# data <- read.csv(file="query_result.csv",sep=";",head=TRUE)

jpeg('feature-boxplot.jpg')

boxplot(data$answer_duration~data$bounty_height, ylab='Response time after bounty start (minutes)', xlab='Height of bounty')

dev.off()
