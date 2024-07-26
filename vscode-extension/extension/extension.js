const os = require('os');
const path = require('path');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');

let client;

function activate(context) {

    const serverPath = context.asAbsolutePath(path.join('languageserver', 'server.py'));

    // FIXME: select the python interpreter chosen in "settings.json" for vscode here
    const command = path.join(os.homedir(), '/miniconda3/envs/workflows/bin/python');
    const serverOptions = {
        command: command,
        args: [serverPath],
        transport: TransportKind.stdio
    };
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'yaml' }]
    };
    client = new LanguageClient('yaml-validator', 'YAML Validator', serverOptions, clientOptions, forceDebug=true);
    context.subscriptions.push(client.start());
}

function deactivate() {
    if (client) return client.stop();
}

module.exports = { activate, deactivate };
