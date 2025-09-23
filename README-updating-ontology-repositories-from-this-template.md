# Update an Ontology Repository from the IES Ontology Template

This README explains how to update an ontology repository to re-align with an updated ies-ontology-template repo. Note: the template changes shouldn’t be in conflict with domain-specific files in the ontology repository.

1. In the target domain ontology, e.g. [ies-building][ies-building], switch to `main` branch:

```bash
git switch main
```

2. Add [ies-ontology-template][ies-ontology-template] as an additional remote:
>git remote add ies-ontology-template https://github.com/IES-Org/ies-ontology-template.git

3. Create a new branch `ontology-template` in the domain ontology (e.g. ies-building):

```bash
git fetch ies-ontology-template main:ontology-template
```

This command will create a new branch from the `main` branch of the `ies-ontology-template` repository in the domain ontology repository.

4. Create a temporary branch in the target domain ontology repo:

```bash
git checkout -b merge-updates main
```

5. Merge the changes from the ontology template into `merge-updates`:
```bash
git merge --allow-unrelated-histories ontology-template
```

Resolve conflicts and accept updates from the ontology template
**BE CAREFUL NOT TO OVERWRITE LOCALLY MODIFIED FILES.**

6. Once you are happy with the merge into `merge-updates` branch, merge on to `main`:

```bash
git switch main
git merge merge-updates
```

7. Consider 'pulling down' these updates to the `develop` and `rc` branches so that they have the template updates too.

8. When complete, remember to delete the temporary branches:

```bash
git branch -D merge-updates
git branch -D ontology-template
```

9. Remove the additional remote pointing to the ies-ontology-template repository:
>git remote remove ies-ontology-template

[ies-building]: https://github.com/IES-Org/ies-building
[ies-ontology-template]: https://github.com/IES-Org/ies-ontology-template
