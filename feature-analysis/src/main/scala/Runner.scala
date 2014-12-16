package de.dreamteam.somediamining

object Runner {
  def main(args: Array[String]) {
    import scalikejdbc._

    // initialize JDBC driver & connection pool
    Class.forName("com.sap.db.jdbc.Driver")
    ConnectionPool.singleton("jdbc:sap://141.89.225.134:30315", "SMA1415", "pass")

    // ad-hoc session provider on the REPL
    implicit val session = AutoSession

    // table creation, you can run DDL by using #execute as same as JDBC
    sql"""
      create table members (
        id serial not null primary key,
        name varchar(64),
        created_at timestamp not null
      )
      """.execute.apply()
  }
}

