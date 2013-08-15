package com.graphbrain.db

case class Edge(override val id: String,
                override val degree: Int = 0,
                override val ts: Long = -1)
  extends Vertex(id, degree, ts) {

  val ids = id.split(" ")
  val edgeType = ids.head
  val participantIds = ids.tail

  def this(id: String, map: Map[String, String]) =
    this(id,
      map("degree").toInt,
      map("ts").toLong)

  override def extraMap = Map()

  override def setId(newId: String): Vertex = copy(id=newId)

  override def setDegree(newDegree: Int): Vertex = copy(degree=newDegree)

  override def setTs(newTs: Long): Vertex = copy(ts=newTs)

  def negate = Edge.fromParticipants("neg/" + edgeType, participantIds)

  def isPositive = ID.parts(edgeType)(0) != "neg"

  def isGlobal: Boolean = {
    for (p <- participantIds)
      if (!ID.isUserNode(p) && ID.isInUserSpace(p))
        return false

    true
  }

  def isInUserSpace: Boolean = {
    for (p <- participantIds)
      if (ID.isInUserSpace(p))
        return true

    false
  }

  override def toUser(userId: String): Vertex = {
    val pids = for (pid <- ids) yield ID.globalToUser(pid, userId)
    Edge.fromParticipants(pids)
  }
  
  override def toGlobal: Vertex = {
    val pids = for (pid <- ids) yield ID.userToGlobal(pid)
    Edge.fromParticipants(pids)
  }

  def matches(pattern: Edge): Boolean = {
    for (i <- 0 until ids.length)
      if ((pattern.ids(i) != "*") && (pattern.ids(i) != ids(i)))
        return false

    true
  }

  def humanReadable2 = (ID.humanReadable(participantIds(0)) +
                        " [" +  ID.humanReadable(edgeType) + "] " +
                        ID.humanReadable(participantIds(1))).replace(",", "")
}

object Edge {
  def fromParticipants(participants: Array[String]) =
    new Edge(idFromParticipants(participants))

  def fromParticipants(participants: Array[Vertex]) =
    new Edge(idFromParticipants(participants))

  def fromParticipants(edgeType: String, participantIds: Array[String]) =
    new Edge(idFromParticipants(edgeType, participantIds))

  def idFromParticipants(participants: Array[String]) = participants.mkString(" ")

  def idFromParticipants(participants: Array[Vertex]): String =
    idFromParticipants(participants.map(v => v.id))

  def idFromParticipants(edgeType: String, participantIds: Array[String]): String =
    idFromParticipants(Array(edgeType) ++ participantIds)
}