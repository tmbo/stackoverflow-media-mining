data <- read.csv(file="query_result.csv",sep=";",head=TRUE)

jpeg('feature-boxplot.jpg')

boxplot(data$time~data$feature, ylab='Response time after bounty start (minutes)', xlab='Length of Title', xaxt="n")
atx <- axTicks(1)
labels <- sapply(atx,function(i)
  as.expression(bquote(2^ .(i)))
)
axis(1,at=atx,labels=expression(2^3, 2^4, 2^5, 2^6, 2^7))


# axis(side=1, at=data$feature, labels=sapply(axTicks(1),function(i)
#  as.expression(bquote(2^ .(i))))
dev.off()

