data <- read.csv(file="query_result.csv",sep=";",head=TRUE)

jpeg('feature-boxplot.jpg')

boxplot(data$time~data$feature, ylab='Response time after bounty start (minutes)', xlab='Height of bounty')

dev.off()
