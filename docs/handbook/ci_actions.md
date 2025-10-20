# CI Actions

Yaclog makes an action available for Forgejo Actions and compatible CI systems like Gitea and Github actions.

```{gha:action}
:path: .
```

## Example Usage

### Get changelog information in your Build workflow

```{gha:example}
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
        
      - uses: .
        id: yaclog
        
      # Your build and test actions go here
        
      - name: Publish to Github
        if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags')
        run: >
          gh release create '${{ github.ref_name }}' 
            --notes-file "'${{ steps.yaclog.outputs.body-file }}'" 
            --title "'${{ steps.yaclog.outputs.name }}'" 
        env:
          GH_TOKEN: '${{ github.token }}'

```

### Workflow to make a new release

If you want to be able to create a new release for your project directly from the Github UI, you can make a new workflow
you can dispatch directly. 

Please note that this workflow does NOT create any releases in Github or any package managers. Instead, your normal build workflow should do this when it detects a push to a tag.

```{gha:example}
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
        uses: .
        with: 
          release: '--${{ inputs.release }}'
          
      - name: Push Changes
        run: |
          git config --global user.name "github-actions"
          git config --global user.email "github-actions@github.com"
          git push
          git push --tags
        env:
          GH_TOKEN: '${{ github.token }}'
```