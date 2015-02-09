library(RMySQL)

library(vioplot)

powers = [ ii*ii | ii <- [1 ..]]

con <- dbConnect(MySQL(), user = 'root', host = '127.0.0.1', dbname='stackoverflow')

# data <- dbReadTable(conn = con, name = 'training_features')

data <- dbGetQuery(conn = con, statement = "SELECT * FROM so_training_features WHERE AnswerDate is not null")

# data <- read.csv(file="query_result.csv",sep=";",head=TRUE)

jpeg('feature-boxplot.jpg')

boxplot(data$answer_duration~data$bounty_height, ylab='Response time after bounty start (minutes)', xlab='Height of bounty')

dev.off()

# Plot settings
par(fg="#D07636") # organge
par(fg="black")
# par(ps=1.5)
par(cex=1.4)
par(pty="s")
par(bg = "#CCD0CE") # grey

# 0E76AD blue

# PLOTT SECTION 

boxplot(data$answer_duration~trunc(log2(data$code_len)),  ylab='Response time after bounty start (minutes)', xlab='Number of code lines bucketed with trunc of log2')

boxplot(data$answer_duration~trunc(log2(data$body_len)),  ylab='Response time after bounty start (minutes)', xlab='Number of characters in question bucketed with trunc of log2')
)
boxplot(data$answer_duration~trunc(log2(data$percent_subs_t)),  ylab='Response time after bounty start (minutes)', xlab='% of responsive subscribers bucketed with trunc of log2')
)

boxplot(data$answer_duration~trunc(log2(data$body_cli)),  ylab='Response time after bounty start (minutes)', xlab='Coleman-Liau-Index of body bucketed with trunc of log2')
)

boxplot(data$answer_duration~trunc(log2(fre)),  ylab='Response time after bounty start (minutes)', xlab='Flesch-Reading-Ease of body bucketed with trunc of log2')
)

boxplot(data$answer_duration~trunc(log2(data$num_answers_bounty)), ylab='Response time after bounty start (minutes)', xlab='Number of answers bucketed with trunc of log2')
)

boxplot(data$answer_duration~trunc(log2(data$view_count)), ylab='Response time after bounty start (minutes)', xlab='Number of views bucketed with trunc of log2')
