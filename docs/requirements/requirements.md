# ToDo - replace [domain] with the actual domain name
# IES [Domain] Requirements

## Overview
  - [Brief description of domain and its scope]
  - [Relationship to existing ontologies/standards]
  - [Key concepts and relationships]

## Use Cases
1. [Primary use case]
   - Context: [Business/technical context]
   - Problem: [Issue being addressed]
   - Solution: [How ontology helps]

2. [Secondary use case]
   [Same structure as above]

## Stories
### Data Modeller
- "As a data modeller, I want to [action] so that [benefit]"
- "As a data modeller, I want to [action] so that [benefit]"

### Domain Expert
- "As a domain expert, I want to [action] so that [benefit]"

## IES Review
### Current Limitations
[Why existing IES ontologies don't meet needs]

### Proposed Extensions
[How this ontology extends IES capabilities]

## Definition of Done
- [ ] All competency questions answerable
- [ ] Validation queries pass
- [ ] Documentation complete
- [ ] Exemplar data provided
- [ ] QA Review approval received

## Competency Questions
### CQ1: [Question in plain English]
**Context:** [Background]
**Query:**
```sparql
SELECT ?x WHERE {
    # SPARQL implementation
}
```

### CQ2: [Next question]
[Same structure as above]

## Exemplar Data
```turtle
@prefix domain: <http://ies.data.gov.uk/ontology/ies-domain#> .

domain:example1 a domain:Class ;
    # Properties and values
.
```