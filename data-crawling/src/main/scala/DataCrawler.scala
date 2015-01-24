package de.dreamteam.somediamining

import java.io.File
import java.nio.charset.StandardCharsets
import java.nio.file.{Paths, Files}
import java.text.{SimpleDateFormat, DateFormat}
import java.util.{TimeZone, Date}

import scala.io.Source
import scala.xml.{Node, XML}

object DataCrawler {
  def printToFile(f: java.io.File)(op: java.io.PrintWriter => Unit) {
    val p = new java.io.PrintWriter(f)
    try { op(p) } finally { p.close() }
  }

  def processStartBounties = {
    val outputFile = "output.csv"

    val bounties = XML.loadFile("../assets/Bounties.xml")

    var failed = List.empty[(Int, String, String, String,String)]

    val dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS")

    dateFormatter.setTimeZone(TimeZone.getTimeZone("GMT"))

    printToFile(new File(outputFile)) { p =>
      p.println("Id,CreationTime,CreationDate")
      (bounties \\ "row").view.zipWithIndex.foreach {
        case (node, idx) =>
          Thread.sleep(200)
          val uId = (node \ "@UserId").text
          val id = (node \ "@Id").text
          val qId = (node \ "@PostId").text
          val timeTxt = (node \ "@CreationDate").text
          val time = dateFormatter.parse(timeTxt).getTime / 1000
          TimeStampForVoteRequester.requestFor(id, uId, qId, time) match {
            case Left(Some(date)) =>
              p.println(s"$id,$date,$time")
              println(s"$idx $time -> $date")
            case Right(e) =>
              failed ::= ((idx, id, uId, qId, timeTxt))
              println(s"$idx FAILED $time")
            case _ =>
          }
      }
    }

    printToFile(new File("failed")) { p =>
      failed.foreach{ f =>
        p.println(s"${f._1},${f._2},${f._3},${f._4},${f._5}")
      }
    }
  }

  def processEndBounties = {

    def readValue(a: Array[String], i: Int) =
      if(a(i).startsWith("\""))
        a(i).drop(1).dropRight(1)
      else
        a(i)

    val outputFile = "output-end.csv"

    val bounties = Source.fromFile("../assets/end_bounties.csv")

    var failed = List.empty[(Int, String, String, String, String)]

    val dateFormatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")

    dateFormatter.setTimeZone(TimeZone.getTimeZone("GMT"))

    printToFile(new File(outputFile)) { p =>
      p.println("Id,CreationTime,CreationDate")
      bounties.getLines().drop(1).zipWithIndex.foreach {
        case (node, idx) =>
          val values = node.split(";")
          val id = readValue(values, 0)
          val qId = readValue(values, 1)
          val uId = readValue(values, 3)
          val timeTxt = readValue(values, 4)
          val bounty = readValue(values, 5)
          if(bounty != "NULL" && id != "NULL" && qId != "NULL" && uId != "NULL" && timeTxt != "NULL") {
            Thread.sleep(200)
            val time = dateFormatter.parse(timeTxt).getTime / 1000
            TimeStampForVoteRequester.requestFor(id, uId, qId, time) match {
              case Left(Some(date)) =>
                p.println(s"$id,$date,$timeTxt")
                println(s"$idx $timeTxt -> $date")
              case Right(e) =>
                failed ::= ((idx, id, uId, qId, timeTxt))
                println(s"$idx FAILED $time")
              case _ =>
            }
          }
      }
    }

    printToFile(new File("failed")) { p =>
      failed.foreach{ f =>
        p.println(s"${f._1},${f._2},${f._3},${f._4},${f._5}")
      }
    }
  }

  def main(args: Array[String]) {
    processEndBounties
  }

}


object TimeStampForVoteRequester {

  import scalaj.http._

  def containsQuestionLink(row: Node, questionId: String) = {
    !(row \ "td" \ "a" \ "@href").filter(_.text.startsWith(s"/questions/$questionId")).isEmpty
  }

  def requestFor(id: String, userId: String, questionId: String, time: Long): Either[Option[String], Exception] = try{
    val url = s"http://stackoverflow.com/ajax/users/$userId/rep/day/$time"
    val response: HttpResponse[String] = Http(url).asString
    if (response.code == 200) {
      val xml = XML.loadString(("&[^;]+;"r).replaceAllIn(response.body, ""))
      val dateOpt = for {
        row <- xml \ "table" \ "tbody" \ "tr"
        if containsQuestionLink(row, questionId)
        elems <- row \ "td"
        if (elems \ "@class").text == "rep-time"
        date <- elems \ "@title"
      } yield date.text
      dateOpt.headOption match {
        case Some(date) =>
          Left(Some(date))
        case _ =>
          println(s"Couldn't find date for $url . questionId: " + questionId)
          Left(None)
      }
    } else {
      println(s"Failed to request time for $url . Reason: " + response.body)
      Left(None)
    }
  } catch {
    case e: Exception =>
      e.printStackTrace()
      println(s"Exception at $id")
      Right(e)
  }
}