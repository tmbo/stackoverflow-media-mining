name := "stackoverflow-feature-analysis"

organization := "de.dreamteam"

version := "1.0.0-SNAPSHOT"

scalaVersion := "2.10.4"

libraryDependencies ++= Seq(
  "org.specs2" %% "specs2" % "2.4.9" % "test",
  "org.scalaz" %% "scalaz-core" % "7.0.6",
  "ch.qos.logback"  %  "logback-classic"   % "1.1.2",
  "org.scalikejdbc" %% "scalikejdbc"       % "2.2.0",
  // other dependencies here
  "org.scalanlp" %% "breeze" % "0.8.1",
  // native libraries are not included by default. add this if you want them (as of 0.7)
  // native libraries greatly improve performance, but increase jar sizes.
  "org.scalanlp" %% "breeze-natives" % "0.8.1",
  "org.scalacheck" %% "scalacheck" % "1.10.0" % "test" withSources() withJavadoc()
)

scalacOptions in Test ++= Seq("-Yrangepos")

resolvers ++= Seq("snapshots", "releases").map(Resolver.sonatypeRepo)

resolvers += "Scalaz Bintray Repo" at "http://dl.bintray.com/scalaz/releases"