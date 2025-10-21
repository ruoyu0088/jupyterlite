import json

text = """
0	"@jupyterlab/console-extension:tracker"	
"{\n    // Code Console\n    // @jupyterlab/console-extension:tracker\n    // Code Console settings.\n    // *************************************\n\n    // Prompt Cell Configuration\n    // The configuration for all prompt cells; it will override the CodeMirror default configuration.\n    \"promptCellConfig\": {\n        \"codeFolding\": false,\n        \"lineNumbers\": false,\n        \"autoClosingBrackets\": true\n    }\n}"
1	"@jupyterlab/fileeditor-extension:plugin"	
"{\n    // Text Editor\n    // @jupyterlab/fileeditor-extension:plugin\n    // Text editor settings.\n    // ***************************************\n\n    // Editor Configuration\n    // The configuration for all text editors; it will override the CodeMirror default configuration.\n    // If `fontFamily`, `fontSize` or `lineHeight` are `null`,\n    // values from current theme are used.\n    \"editorConfig\": {\n        \"lineNumbers\": true,\n        \"autoClosingBrackets\": true\n    }\n}"
2	"@jupyterlab/notebook-extension:tracker"	
"{\n    \"codeCellConfig\": {\n        \"lineNumbers\": false,\n        \"lineWrap\": false,\n        \"autoClosingBrackets\": true\n    },\n    \"markdownCellConfig\": {\n        \"lineNumbers\": false,\n        \"matchBrackets\": false,\n        \"autoClosingBrackets\": true\n    },\n    \"rawCellConfig\": {\n        \"lineNumbers\": false,\n        \"matchBrackets\": false,\n        \"autoClosingBrackets\": true\n    },\n    \"enableKernelInitNotification\": false,\n    \"defaultCell\": \"code\",\n    \"autoStartDefaultKernel\": false,\n    \"showInputPlaceholder\": true,\n    \"inputHistoryScope\": \"global\",\n    \"kernelShutdown\": false,\n    \"autoRenderMarkdownCells\": false,\n    \"scrollPastEnd\": true,\n    \"recordTiming\": false,\n    \"overscanCount\": 1,\n    \"maxNumberOutputs\": 50,\n    \"scrollHeadingToTop\": true,\n    \"showEditorForReadOnlyMarkdown\": true,\n    \"kernelStatus\": {\n        \"showOnStatusBar\": false,\n        \"showProgress\": true\n    },\n    \"documentWideUndoRedo\": false,\n    \"showHiddenCellsButton\": true,\n    \"renderingLayout\": \"default\",\n    \"sideBySideLeftMarginOverride\": \"10px\",\n    \"sideBySideRightMarginOverride\": \"10px\",\n    \"sideBySideOutputRatio\": 1,\n    \"windowingMode\": \"defer\",\n    \"accessKernelHistory\": false\n}"
"""

data = {}
lines = text.splitlines()

key = None
value = []
for line in lines:
    if not line:
        continue
    if line[0].isnumeric():
        if key is not None:
            data[key] = json.loads("\n".join(value).strip('"'))
        key = line.split('\t')[1].strip('"')
        value = []
    else:
        if line.strip().startswith('//'):
            continue
        value.append(line)
data[key] = json.loads("\n".join(value).strip('"'))

with open('overrides.json', 'w') as f:
    json.dump(data, f, indent=4)