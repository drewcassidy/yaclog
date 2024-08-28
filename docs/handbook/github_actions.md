# Github Actions

Yaclog makes an action available for Github Actions and compatible CI systems.

## The Yaclog Action

To use the Yaclog action add the following to your workflow steps

````{jinja}
```yaml
      - name: Get version info
        uses: drewcassidy/yaclog@{{ ref }}
        id: yaclog
```
````

### Inputs

```{confval} release
:type: string

  When set, creates a new release and commits it. Directly passed to the arguments of `yaclog release --yes --commit`.

  Can be a version number or an increment tag like `--major`, `--minor`, or `--patch`.
  The resulting commit and tag will NOT be pushed back to the repo. You must add a step to do this yourself
```

```{confval} markdown
:type: boolean
:default: true

If the output should be in markdown format or not. Equivalent to the `--markdown` flag
```

### Outputs

```{confval} version
The current version number, equivalent to the output of `yaclog show --version`. For example, `1.3.1`
```

```{confval} name
The most recent version name, equivalent to the output of `yaclog show --name`. For example, `Version 1.3.0`
```

```{confval} header
The entire header for the most recent version, equivalent to the output of `yaclog show --header`. For example, `Version 1.3.0 - 2024-08-08`
```

```{confval} body-file
The path to a temporary file containing the body of the most recent version. Contents equivalent to `yaclog show --body`
```

```{confval} changelog
The path to the changelog file. Usually `CHANGELOG.md` in the current directory.
```

## Example Usage

### Get changelog information in your Build workflow

````{jinja}
```yaml
name: Build

on:
  push:
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Mod Repo
        uses: actions/checkout@v4
        
      - uses: drewcassidy/yaclog@{{ ref }}
        id: yaclog
        
      # Your build and test actions go here
        
      - name: Publish to Github
        if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags')
        run: |
          gh release create {{ '${{ github.ref_name }}' }} \
            --notes-file "{{ '${{ steps.yaclog.outputs.body-file }}' }}" \
            --title "{{ '${{ steps.yaclog.outputs.name }}' }}" 
        env:
          GH_TOKEN: {{ '${{ github.token }}' }}

```
````

### Workflow to make a new release

If you want to be able to create a new release for your project directly from the Github UI, you can make a new workflow
you can dispatch directly. 

Please note that this workflow does NOT create any releases in Github or any package managers. Instead, your normal build workflow should do this when it detects a push to a tag.

````{jinja}
```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      release:
        description: 'type of release to use'
        required: true
        default: 'patch'
        type: choice
        options:
        - major 
        - minor
        - patch

permissions:
  contents: write

jobs:
  yaclog-release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Mod Repo
        uses: actions/checkout@v4
      
      - name: Yaclog Release
        uses: drewcassidy/yaclog@{{ ref }}
        with: 
          release: '--{{ '${{ inputs.release }}' }}'
          
      - name: Push Changes
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git push
          git push --tags
        env:
          GH_TOKEN: {{ '${{ github.token }}' }}
```
````