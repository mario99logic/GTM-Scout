# GTM Hunter — Generated Messages

Mock run · 7 qualified leads · dry-run mode

---

## Jane Smith — Staff Engineer · Netflix · Score 55

**LinkedIn Invite**
> Hey Jane — saw your Cassandra Summit talk on multi-region consistency. We're tackling similar problems at Scylla with C* compatibility but minus the GC pauses. Would be great to connect.

**Follow-up Email**

Subject: Cassandra Summit talk + GC pauses at scale

Jane, saw your Cassandra Summit talk on managing multi-region clusters at Netflix scale — the part about tuning G1GC during peak traffic hours hit close to home.

I've been talking to a few teams running Cassandra in the 100+ node range, and the pattern is always the same: they spend more time firefighting JVM behavior than actually improving their data model. The ops burden seems to grow exponentially past a certain cluster size.

Curious — at Netflix's scale, what ends up eating more engineering time: capacity planning and hardware costs, or the operational complexity of keeping latencies predictable during deployments?

---

## Bob Johnson — Data Platform Lead · Uber · Score 65

**LinkedIn Invite**
> Saw your cassandra-driver contributions and Uber's migration work — always curious how teams at your scale handle tail latency and compaction overhead in prod. Would be great to connect.

**Follow-up Email**

Subject: Trip data at scale + Cassandra ops

Bob – saw you led the MySQL → Cassandra migration for trip data at Uber. That's a gnarly domain to model in wide-column, especially with the read patterns around rider/driver matching and trip state.

I've noticed teams who've made that jump often hit a wall 12–18 months in — not with the data model, but with compaction tuning and GC pauses during peak traffic. The operational surface area starts to sprawl once you're chasing p99s across a few hundred nodes.

Curious what surprised you most on the ops side after you went live? Was it smoother than expected, or did you end up with a dedicated on-call rotation just for the cluster?

---

## Alice Chen — Principal Infrastructure Engineer · Discord · Score 50

**LinkedIn Invite**
> Curious how Discord handles Cassandra consistency tuning across regions for message ordering — we've seen wild latency variance at scale. Always keen to swap notes with folks running multi-region C* in prod.

**Follow-up Email**

Subject: Multi-region Cassandra at Discord's scale

Alice, managing multi-region Cassandra for message storage at Discord's traffic patterns must surface some gnarly edge cases — especially around cross-DC latency SLAs when a game launch or major event suddenly 10xs read load in specific regions.

I've noticed teams running message workloads at your scale often hit a wall where adding nodes for a traffic spike helps throughput but doesn't fix tail latency, and the JVM tuning becomes this endless game of whack-a-mole during peak hours.

Curious if you've seen similar patterns, or if Discord's architecture sidesteps that class of problem entirely?

---

## David Park — Senior Backend Engineer · Apple · Score 55

**LinkedIn Invite**
> Hey David — saw you're working on iCloud's data layer. Always curious how teams at your scale handle Cassandra's tail latency and ops overhead when consistency matters. Worth connecting.

**Follow-up Email**

Subject: iCloud scale + Cassandra ops

David — saw you're working on distributed data for iCloud. At that scale, I imagine Cassandra cluster ops and tail latency during traffic spikes are constant battles, especially when user-facing SLAs are non-negotiable.

I've been talking to a few teams running Cassandra at similar scale who've hit a wall where adding nodes for throughput actually made GC pauses worse during peak hours. The ops overhead of keeping p99s stable across hundreds of nodes becomes its own engineering problem.

Curious — are you seeing more pain from capacity planning complexity or from runtime unpredictability when load patterns shift?

---

## James Wright — Lead Database Engineer · Spotify · Score 60

**LinkedIn Invite**
> James – saw you're running Cassandra at Spotify's scale. We've been comparing notes with teams hitting similar throughput walls on playlist/user workloads. Worth connecting if you're ever exploring alternatives to JVM tuning hell.

**Follow-up Email**

Subject: Playlist state at 500M users

James – saw you're running Cassandra for playlist and user data at Spotify. That's one of those workloads where read latency can't slip even when you're pushing massive write volumes during peak listening hours.

We've been talking to a few teams managing similar user-state systems, and the pattern that keeps coming up is the tension between keeping p99s tight during traffic spikes and not overprovisioning by 3x just to handle GC pauses during compaction.

Curious if you've hit that wall, or if Spotify's scale has forced you into different tradeoffs entirely?

---

## Sarah Kim — Senior Data Engineer · Yelp · Score 50

**LinkedIn Invite**
> Sarah — impressed by your Cassandra compaction work. We're tackling similar problems at ScyllaDB around write amplification and predictable performance at scale. Would be great to connect.

**Follow-up Email**

Subject: Compaction tuning in production

Sarah, saw your commits on Cassandra's compaction strategies — that's some deep work. We've been hearing from teams running LCS at scale that they're hitting walls around write amplification during peak traffic, especially when trying to balance read performance with disk wear.

One pattern that keeps coming up: the gap between tuning compaction for steady-state versus surviving traffic spikes gets harder as datasets grow past a few TB per node. The knobs multiply but the observability doesn't always keep up.

Curious what you're seeing at Yelp's scale — are you finding the existing strategies flexible enough for your workload mix, or are you running custom configs per table?

---

## Carlos Mendez — VP of Engineering · Comcast · Score 80

**LinkedIn Invite**
> Carlos — saw you're running DataStax for retail pipelines at Comcast. We've been helping similar platform teams cut latency and ops overhead with Cassandra-compatible infra. Would be great to connect.

**Follow-up Email**

Subject: Retail pipelines at Comcast scale

Carlos – saw you're running the platform team behind Comcast's retail data pipeline on Astra. That's a gnarly domain: bursty traffic patterns during launches, tight SLA requirements, and I'm guessing some interesting challenges around predictable performance when query patterns shift.

I've been talking to a few other retail platform teams lately, and the common thread isn't raw throughput – it's the operational anxiety around tail latencies during peak windows. The ones running managed Cassandra mention spending cycles on capacity planning and fighting p99 spikes that seem to come out of nowhere.

Curious: are you seeing predictable behavior under load, or does your team still spend time firefighting latency during high-traffic events?
