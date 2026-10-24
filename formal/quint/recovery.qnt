// Recovery and stale-result safety for the two verified height shards.
//
// Finite model of a fail-closed certification controller, not an arithmetic
// verifier. Correct per-shard counts come from an external checked oracle.
// Attempts are deliberately capped at 2 to keep model checking finite.
module recovery {
  type Job = str

  pure val JOBS: Set[Job] = Set("low", "high")
  pure val EXPECTED: Job -> int = Map("low" -> 0, "high" -> 1)
  pure val START: Job -> int = Map("low" -> 2, "high" -> 73)
  pure val END: Job -> int = Map("low" -> 72, "high" -> 144)
  pure val planOK: bool =
    START.get("low") == 2 and END.get("low") + 1 == START.get("high")
      and END.get("high") == 144

  // stage: 0 pending, 1 submitted, 2 verified, 3 rejected.
  // A monotonically increasing per-shard ticket prevents stale verification
  // responses from accidentally approving a later attempt.
  var stage: Job -> int
  var ticket: Job -> int
  var claimed: Job -> int
  var published: bool

  action init = all {
    stage' = Map("low" -> 0, "high" -> 0),
    ticket' = Map("low" -> 0, "high" -> 0),
    claimed' = Map("low" -> 0, "high" -> 0),
    published' = false,
  }

  action submit(j: Job, n: int): bool = all {
    JOBS.contains(j),
    not(published),
    stage.get(j) == 0,
    ticket.get(j) < 2,
    Set(0, 1, 2).contains(n),
    stage' = stage.put(j, 1),
    ticket' = ticket.put(j, ticket.get(j) + 1),
    claimed' = claimed.put(j, n),
    published' = published,
  }

  // A failure cannot erase a verified or rejected terminal verdict.
  // The next submission must receive a strictly newer ticket.
  action crash(j: Job): bool = all {
    JOBS.contains(j),
    not(published),
    stage.get(j) == 1,
    stage' = stage.put(j, 0),
    ticket' = ticket,
    claimed' = claimed,
    published' = published,
  }

  action inspect(j: Job, observedTicket: int): bool = all {
    JOBS.contains(j),
    not(published),
    stage.get(j) == 1,
    observedTicket == ticket.get(j),
    stage' = stage.put(j, if (claimed.get(j) == EXPECTED.get(j)) 2 else 3),
    ticket' = ticket,
    claimed' = claimed,
    published' = published,
  }

  action publish = all {
    planOK,
    not(published),
    JOBS.forall(j => stage.get(j) == 2),
    stage' = stage,
    ticket' = ticket,
    claimed' = claimed,
    published' = true,
  }

  action idle = all {
    stage' = stage,
    ticket' = ticket,
    claimed' = claimed,
    published' = published,
  }

  action step = any {
    all {
      nondet j = JOBS.oneOf()
      nondet n = Set(0, 1, 2).oneOf()
      submit(j, n),
    },
    all {
      nondet j = JOBS.oneOf()
      crash(j),
    },
    all {
      nondet j = JOBS.oneOf()
      nondet observed = Set(1, 2).oneOf()
      inspect(j, observed),
    },
    publish,
    idle,
  }

  val verifiedSound: bool =
    JOBS.forall(j => stage.get(j) != 2 or claimed.get(j) == EXPECTED.get(j))

  val noPrematurePublication: bool =
    not(published) or JOBS.forall(j => stage.get(j) == 2)

  val attemptBounds: bool =
    JOBS.forall(j => 0 <= ticket.get(j) and ticket.get(j) <= 2)

  val safety: bool =
    planOK and verifiedSound and noPrematurePublication and attemptBounds

  run recoveredPublicationTest =
    init
      .then(submit("low", 0))
      .then(crash("low"))
      .then(submit("low", 0))
      .then(inspect("low", 2))
      .then(submit("high", 1))
      .then(inspect("high", 1))
      .then(publish)
      .then(all { assert(published), assert(safety), idle })

  run staleTicketRefusedTest =
    init
      .then(submit("low", 0))
      .then(crash("low"))
      .then(submit("low", 0))
      .then(inspect("low", 1))
      .fail()

  run wrongResultRefusedTest =
    init
      .then(submit("low", 2))
      .then(inspect("low", 1))
      .then(submit("high", 1))
      .then(inspect("high", 1))
      .then(publish)
      .fail()

  run cappedRetryTest =
    init
      .then(submit("low", 0))
      .then(crash("low"))
      .then(submit("low", 0))
      .then(crash("low"))
      .then(submit("low", 0))
      .fail()

  run finalizedShardCannotCrashTest =
    init
      .then(submit("low", 0))
      .then(inspect("low", 1))
      .then(crash("low"))
      .fail()
}
