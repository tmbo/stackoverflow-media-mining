data <- read.csv(file="query_result.csv",sep=";",head=TRUE)

jpeg('feature-boxplot.jpg')

# Do the boxplot but do not show it
b <- boxplot(data$time~data$feature)
# Now b$n holds the counts for each factor, we're going to write them in names
boxplot(data$time~data$feature, range=5, ylab='Response time after bounty start (minutes)', xlab='Height of bounty')#, names=paste(b$names, "\n#", b$n))

dev.off()
