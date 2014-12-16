name := "stackoverflow-media-mining"

organization := "de.dreamteam"

version := "1.0.0-SNAPSHOT"

scalaVersion := "2.10.4"

libraryDependencies ++= Seq(
  "org.specs2" %% "specs2" % "2.4.9" % "test",
  "org.scalaz" %% "scalaz-core" % "7.0.6",
  "org.apache.spark" %% "spark-core" % "1.1.0",
  "org.scalacheck" %% "scalacheck" % "1.10.0" % "test" withSources() withJavadoc()
)

scalacOptions in Test ++= Seq("-Yrangepos")

resolvers ++= Seq("snapshots", "releases").map(Resolver.sonatypeRepo)

resolvers += "Scalaz Bintray Repo" at "http://dl.bintray.com/scalaz/releases"