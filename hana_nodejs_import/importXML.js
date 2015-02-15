/**
A super simple NodeJS script to import the Stackoverflow Data Dump into SAP Hana.

It uses an streaming XM parser that reads blocks of 50k items at a time and
sends them to the HANA in 1k bulks.
**/

var path = require("path"),
    fs = require("fs"),
    XmlStream = require("xml-stream"),
    hdb = require("hdb"),
    Q = require("q");

// HANA Credentials
var client = hdb.createClient({
  host     : "192.168.42.38",
  port     : 30315,
  user     : "SMA1415",
  password : "Popcorn54"
});

// Path to Stackoverlflow XML dump
var DATA_DIR = "/Users/therold/Downloads/stackoverflow/" //__dirname + "/../"

// Buffer size for bulk send operation over the network
var SEND_SIZE = 1000

// Buffer size for reading from disk
var READ_BUFFER_SIZE = 50 * SEND_SIZE

var readCounter = 0;

function readXML(fileName, statement, schemaFunc) {
  var stream = fs.createReadStream(fileName); //path.join(DATA_DIR, fileName)),
      buffer = [],
      xml = new XmlStream(stream, "utf-8");

  xml.on("endElement: row", function(node) {
    buffer.push(schemaFunc(node));

    bufferLength = buffer.length
    if (bufferLength >= READ_BUFFER_SIZE ) {
      xml.pause();
      readCounter += bufferLength;

      sendToHana(statement, buffer).then(function(rowCounts){
        xml.resume();
        console.log("Imported rows: ", readCounter);
      }, function(err) {
        console.error(err);
      })
    }
  });

  xml.on("error", function(message) {
    console.log(message);
  });
  xml.on("end", function(message) {
    if (buffer.length > 0)
      sendToHana(statement, buffer);

    console.log("Done importing: " + fileName);
    console.timeEnd("dbimport");
    client.end();
  });
}


function importBadges() {
  console.log("Importing Badges...")
  var SQLQuery = "INSERT INTO SO_BADGES (ID, USERID, NAME, CREATIONDATE) VALUES (?, ?, ?, ?)"
  connectToDB(SQLQuery).then(function(statement) {
    readXML("Badges.xml", statement, function(node) {
      return [
        node.$.Id,
        node.$.UserId,
        node.$.Name,
        node.$.Date
      ]
    })
  })
}


function importComments() {
  console.log("Importing Comments...")
  var SQLQuery = "INSERT INTO SO_COMMENTS (ID, POSTID, SCORE, TEXT, CREATIONDATE, USERID) VALUES (?, ?, ?, ?, ?, ?)"
  connectToDB(SQLQuery).then(function(statement) {
    readXML("Comments.xml", statement, function(node) {
      return [
        node.$.Id,
        node.$.PostId,
        node.$.Score,
        node.$.Text,
        node.$.CreationDate,
        node.$.UserId
      ]
    })
  })
}

function importUsers() {
  console.log("Importing Users...")
  var SQLQuery = "INSERT INTO SO_USERS (ID, REPUTATION, CREATIONDATE, DISPLAYNAME, LASTACCESSDATE, VIEWS, WEBSITEURL, LOCATION, ABOUTME, AGE, UPVOTES, DOWNVOTES, EMAILHASH) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
  connectToDB(SQLQuery).then(function(statement) {
    readXML("Users.xml", statement, function(node) {
      return [
        node.$.Id,
        node.$.Reputation,
        node.$.CreationDate,
        node.$.DisplayName,
        node.$.LastAccessDate,
        node.$.Views,
        node.$.WebsiteUrl,
        node.$.Location,
        node.$.AboutMe,
        node.$.Age,
        node.$.UpVotes,
        node.$.DownVotes,
        node.$.EmailHash
      ]
    })
  })
}


function importPosts(fileName) {
  console.log("Importing Posts...")
  var SQLQuery = "INSERT INTO SO_POSTS (ID, POSTTYPEID, ACCEPTEDANSWERID, PARENTID, SCORE, VIEWCOUNT, BODY, OWNERUSERID, LASTEDITORUSERID, LASTEDITDATE, LASTACTIVITYDATE, TITLE, TAGS, ANSWERCOUNT, COMMENTCOUNT, FAVORITECOUNT, CREATIONDATE) VALUES (?, ?, ?, ?, ?, ?, TO_BLOB(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
  connectToDB(SQLQuery).then(function(statement) {
    readXML(fileName, statement, function(node) {
      return [
        node.$.Id,
        node.$.PostTypeId,
        node.$.AcceptedAnswerId,
        node.$.ParentId,
        node.$.Score,
        node.$.ViewCount,
        new Buffer(node.$.Body),
        node.$.OwnerUserId,
        node.$.LastEditorUserId,
        node.$.LastEditDate,
        node.$.LastActivityDate,
        node.$.Title,
        node.$.Tags,
        node.$.AnswerCount || 0,
        node.$.CommentCount || 0,
        node.$.FavoriteCount || 0,
        node.$.CreationDate
      ]
    })
  })
}


function importVotes(statement) {
  console.log("Importing Votes...")
  var SQLQuery = "INSERT INTO SO_VOTES (ID, POSTID, VOTETYPEID, CREATIONDATE) VALUES (?, ?, ?, ?)"
  connectToDB(SQLQuery).then(function(statement) {
    readXML("Votes.xml", statement, function(node) {
      return [
        node.$.Id,
        node.$.PostId,
        node.$.VoteTypeId,
        node.$.CreationDate
      ]
    })
  })
}


function sendToHana(statement, buffer) {
  var promises = [];
  // The HANA driver can handle Arrays > 1000 items
  for(var i=1; i <= 50; i++) {
    data = buffer.splice(0, SEND_SIZE);
    promises.push(executeSQLStatment(statement, data));
  }
  return Q.all(promises);
}


function executeSQLStatment(statement, data) {
  var deferred = new Q.defer();
  statement.exec(data, function (err, rows) {
    if (err) {
      return deferred.reject(err);
    }
    deferred.resolve(rows.length);
  });
  return deferred.promise;
}


function connectToDB(SQLQuery) {
  var deferred = new Q.defer();

  client.connect(function (err) {
    if (err) {
      defer.reject(err)
      return console.error('Connect error', err);
    }

    // create prepared statements for bulk import
    client.prepare(SQLQuery, function (err, statement){
      if (err) {
        return console.error('Error:', err);
      }
      console.time("dbimport");
      deferred.resolve(statement)
    });
  })

  return deferred.promise;
};

// #######################################
// Starting point
// Only run one import at a time
// #######################################

fileName = process.argv[2]
console.log(fileName)

//importBadges()
//importComments()
importPosts(fileName)
//importVotes()
//importUsers()
