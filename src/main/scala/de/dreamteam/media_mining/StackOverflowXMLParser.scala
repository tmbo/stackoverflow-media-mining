package de.dreamteam.media_mining

import javax.xml.stream.{XMLInputFactory}
import de.dreamteam.media_mining.models.{QuestionBuilder, Question}
import org.codehaus.stax2._
import java.io._
import scalaz.EphemeralStream
import org.codehaus.staxmate.SMInputFactory
import org.codehaus.staxmate.in.{SMFilter, SMInputCursor, SMHierarchicCursor, SMFilterFactory}

class StackOverflowXMLParser{
  private def parseQuestion(pageCursorData: SMInputCursor): Option[Question] = {
    def buildPage(questionBuilder: QuestionBuilder): Option[Question] = {
      if(pageCursorData.getNext != null) {
        pageCursorData.getLocalName match {
          case "title" =>
            buildPage(pageBuilder.addTitle(pageCursorData.collectDescendantText(false)))
          case "id" =>
            buildPage(pageBuilder.addId(pageCursorData.collectDescendantText(false)))
          case "revision" =>
            buildPage(pageBuilder.addText(pageCursorData.childElementCursor("text").advance().collectDescendantText(false)))
          case "ns" =>
            val ns = pageCursorData.collectDescendantText(false)
            if (!allowedNamespaces.contains(ns))
              None
            else
              buildPage(pageBuilder)
          case _ =>
            buildPage(pageBuilder)
        }
      } else
        pageBuilder.build
    }

    try {
      buildPage(new WikiPageBuilder)
    } catch {
      case e: Exception =>
        println("Catched exception.")
        e.printStackTrace()
        None
    }
  }

  private def parsePages(pagesCursor: SMInputCursor): EphemeralStream[WikiPage] = {
    if(pagesCursor.getNext != null){
      parsePage(pagesCursor.childElementCursor()) match{
          case Some(page) =>
            EphemeralStream.cons(page, parsePages(pagesCursor))
          case _ =>
            parsePages(pagesCursor)
      }
    } else
      EphemeralStream.emptyEphemeralStream
  }

  private def readerFromInput[T](factory: XMLInputFactory2, input: T) = input match {
    case file: File => factory.createXMLStreamReader(file)
    case reader: Reader => factory.createXMLStreamReader(reader)
    case _ => throw new IllegalArgumentException("Invalid input type.")
  }

  private def createFactory(): XMLInputFactory2 = {
    System.setProperty("javax.xml.stream.XMLInputFactory", "com.ctc.wstx.stax.WstxInputFactory");
    val factory = XMLInputFactory.newInstance().asInstanceOf[XMLInputFactory2]
    factory.setProperty(XMLInputFactory.IS_NAMESPACE_AWARE, false)
    factory
  }

  private def createRootCursor[T](input: T) = {
    val factory = createFactory()
    val reader = readerFromInput(factory, input)
    val inf = new SMInputFactory(factory)
    val filter = SMFilterFactory.getElementOnlyFilter
    val voodoo = inf.getClass.getDeclaredMethod("constructHierarchic", classOf[XMLStreamReader2], classOf[SMFilter])

    voodoo.setAccessible(true)
    voodoo.invoke(inf, reader, filter).asInstanceOf[SMHierarchicCursor].advance()
  }

  def parse(file: File): EphmeralStream[WikiPage] = {
    val reader = new BufferedReader(new InputStreamReader(new FileInputStream(file), "UTF-8"))
    val rootCursor = createRootCursor(reader)
    val pageCursorData = rootCursor.childElementCursor("page")
    val stream = parsePages(pageCursorData) ++ {
      pageCursorData.getStreamReader.closeCompletely()
      EphemeralStream.emptyEphemeralStream
    }

    stream
  }
}