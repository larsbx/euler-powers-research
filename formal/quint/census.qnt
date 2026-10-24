// State-machine specification of the bounded e <= 144 census publication.
// Assumes an independent arithmetic checker supplies the expected counts.
// This model verifies workflow safety, not the fifth-power arithmetic itself.
module census {
  type Job = str

  pure val JOBS: Set[Job] = Set("low", "high")
  pure val START: Job -> int = Map("low" -> 2, "high" -> 73)
  pure val END: Job -> int = Map("low" -> 72, "high" -> 144)
  pure val EXPECTED: Job -> int = Map("low" -> 0, "high" -> 1)

  // The corresponding all-heights partition is proved in Lean.
  pure val partitionOK: bool =
    START.get("low") == 2 and END.get("low") + 1 == START.get("high") and
    END.get("high") == 144

  // Stage: 0 = pending; 1 = submitted; 2 = independently verified;
  // 3 = rejected. A rejected report cannot later become verified.
  var stage: Job -> int
  var claimed: Job -> int
  var published: bool

  action init = all {
    stage' = Map("low" -> 0, "high" -> 0),
    claimed' = Map("low" -> 0, "high" -> 0),
    published' = false,
  }

  action submit(j: Job, n: int): bool = all {
    JOBS.contains(j),
    stage.get(j) == 0,
    Set(0, 1, 2).contains(n),
    stage' = stage.put(j, 1),
    claimed' = claimed.put(j, n),
    published' = published,
  }

  action inspect(j: Job): bool = all {
    JOBS.contains(j),
    stage.get(j) == 1,
    stage' = stage.put(j, if (claimed.get(j) == EXPECTED.get(j)) 2 else 3),
    claimed' = claimed,
    published' = published,
  }

  action publish = all {
    partitionOK,
    JOBS.forall(j => stage.get(j) == 2),
    not(published),
    stage' = stage,
    claimed' = claimed,
    published' = true,
  }

  action idle = all {
    stage' = stage,
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
      inspect(j),
    },
    publish,
    idle,
  }

  val verifiedSound: bool =
    JOBS.forall(j => stage.get(j) != 2 or claimed.get(j) == EXPECTED.get(j))

  val noPrematurePublication: bool =
    not(published) or JOBS.forall(j => stage.get(j) == 2)

  val safety: bool =
    partitionOK and verifiedSound and noPrematurePublication

  // Nonvacuous successful publication.
  run acceptsBothValidShardsTest =
    init
      .then(submit("low", 0))
      .then(inspect("low"))
      .then(submit("high", 1))
      .then(inspect("high"))
      .then(publish)
      .then(all { assert(published), assert(safety), idle })

  // Malformed/unverified or dishonest results must not be published.
  run refusesUnverifiedTest =
    init.then(submit("low", 0)).then(publish).fail()

  run refusesWrongCountTest =
    init
      .then(submit("low", 2))
      .then(inspect("low"))
      .then(submit("high", 1))
      .then(inspect("high"))
      .then(publish)
      .fail()

  run refusesRepeatedSubmissionTest =
    init
      .then(submit("low", 0))
      .then(submit("low", 1))
      .fail()
}
