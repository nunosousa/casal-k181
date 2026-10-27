# Requirements traceability

The [requirements register](requirements.md#requirements-register) is the
single source for objective, allocation, acceptance statement, verification
links and maturity. The [verification register](verification-plan.md#verification-register)
owns procedure state and evidence. Do not maintain a second handwritten
matrix that can diverge from them.

Generate the current matrix from the repository root:

```sh
python3 tools/traceability.py
```

The report joins objective -> requirement -> allocation -> verification ->
evidence, preserving requirement maturity separately from verification state.
It checks duplicate IDs, missing verification links and Pass records without
evidence. It does not assess requirement quality, safety, test adequacy or
baseline approval. A complete join is not verified implementation.

Run the generator's regression checks with:

```sh
python3 -m unittest discover -s tools -p 'test_traceability.py'
```

Architecture/interface allocation is expanded in the [ICD](../architecture/interfaces.md);
hazard links live in the [hazard register](hazards.md), and implementation
work links back through the [backlog](backlog.md). Review these links with
each affected change. Source rationale is retained in the specification;
do not trace every helper function.

For a review, generate against the exact Git baseline under discussion.
Retain result records as prescribed by the V&V plan; a generated table is
an index to evidence, not a replacement for it.
