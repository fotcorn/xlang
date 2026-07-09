# XLang for VS Code and Cursor

Provides syntax highlighting, comment commands, bracket matching, and automatic bracket and quote closing for XLang (`.xl`) files.

## Use locally

For extension development, open the command palette and select `Developer: Install Extension from Location...` and browse to the `editors/vscode-xlang` directory.

Alternatively, open the repository in VS Code or Cursor and launch it with:

```bash
code --extensionDevelopmentPath="$PWD/editors/vscode-xlang"
```

To package a distributable extension, install `@vscode/vsce` and run `vsce package` from this directory, then install the generated `.vsix` from the editor's Extensions view.
