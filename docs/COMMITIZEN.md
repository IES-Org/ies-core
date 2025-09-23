# Commitizen Commit Style Guide

## Overview
We use the Commitizen convention for our commit messages to ensure consistency and maintain a clear project history. Each commit message follows a specific format that makes it easier to generate changelogs and understand the purpose of changes.

## Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files

## Scope
The scope provides context about what part of the codebase is affected. For our ontology projects, common scopes include:
- `model`: Changes to the ontology model
- `validation`: Changes to validation rules or tests
- `tooling`: Changes to development tools
- `deps`: Dependency updates
- `release`: Release-related changes

## Subject
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No period (.) at the end
- Limited to 72 characters
- Describes what the commit does, not what you did

## Body
- Use the imperative, present tense
- Include motivation for the change and contrast with previous behavior
- Wrap lines at 72 characters
- Leave one blank line between subject and body

## Footer
- Reference GitHub issues and pull requests
- Note breaking changes starting with "BREAKING CHANGE:"
- List any breaking changes and migration instructions

## Examples

```
feat(model): add new property for temporal relationships

Add temporalRelation property to support time-based relationships 
between entities. This enables tracking of historical connections
and temporal dependencies.

Closes #123
```

```
fix(validation): correct cardinality check for optional properties

Previously, the validator would incorrectly flag optional properties
as required. This fix ensures proper handling of optional properties
in accordance with the schema specification.

Fixes #456
```

```
chore(deps): update development dependencies

Update Jest to v27 and ESLint to v8 to address security
vulnerabilities and gain access to new features.

Dependencies updated:
- jest: 26.6.3 → 27.0.0
- eslint: 7.32.0 → 8.0.0
```

## Setup

1. Install Commitizen globally:
   ```
   npm install -g commitizen
   ```

2. Initialize your project to use Commitizen:
   ```
   # First install the conventional changelog adapter
   npm install --save-dev cz-conventional-changelog
   
   # Then initialize commitizen configuration
   commitizen init cz-conventional-changelog --save-dev --save-exact
   ```

3. Add a script to your package.json:
   ```json
   {
     "scripts": {
       "commit": "cz"
     }
   }
   ```

## Integration with Your Workflow

1. When creating a feature branch:
   ```
   git checkout -b feature/temporal-relations develop
   ```

2. Make your changes and stage them:
   ```
   git add .
   ```

3. Commit using Commitizen (use either method):
   ```
   npm run commit
   # OR if installed globally
   git cz
   ```
   Follow the prompts to create a properly formatted commit message.

4. Before creating a PR:
   - Ensure all commits follow the convention
   - Use `git rebase -i` to clean up commit history if needed
   - Verify that commit messages are clear and informative

## Tips
- Keep commits atomic and focused on a single change
- Use the body to explain "why" rather than "what"
- Reference relevant issues and PRs in the footer
- When in doubt, run `git cz` to get proper prompts