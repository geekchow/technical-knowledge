# How to debug Python with VS Code?

Debugging is a best way for you to understand a piece of code. However, do you know how to debug Python code with Visual Studio Code?

## Debug Python file
Before you you could debug a Python file, you have to create a Debug Configuration.
You can create it with the Debug Button on the left or compose it manually.

```JSON
// Directory: .vscode/launch.json
{
  // Use IntelliSense to learn about possible attributes.
  // Hover to view descriptions of existing attributes.
  // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      // Specify the Python executor path
      "pythonPath": "${command:python.interpreterPath}",
      "request": "launch",
      // Python file absolute path.
      "program": "${file}",
      "console": "integratedTerminal",
      // Pass in arguments 
      "args": ["--username", "phil", "--language", "Python"],
      // Inject environment variables
      "env": {"CERT_PATH": "~/.CA/CACERT.PEM", "DEBUG": "True" }
    }
  ]
}
```

## Debug Python module

```JSON
{
  // Use IntelliSense to learn about possible attributes.
  // Hover to view descriptions of existing attributes.
  // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Module",
      "type": "python",
      "request": "launch",
      // module to debug, first part is moudule name, second part is entry file without .py extension.
      "module": "module-test.main_script",
    }
  ]
}
```


After setup the debug confiure file, you can insert some break point on source code, then click the Debug Button on left,  at last click start button. 