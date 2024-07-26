import yaml
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    Diagnostic,
    DidChangeTextDocumentParams,
    Position,
    Range,
)
from ecoscope_workflows.compiler import Spec


server = LanguageServer("yaml-validator", "v0.1")


@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    diagnostics = validate_yaml(text_doc.source)
    await ls.publish_diagnostics(params.text_document.uri, diagnostics)


def validate_yaml(text: str):
    try:
        data = yaml.safe_load(text)
        Spec(**data)
        return []
    except Exception as e:
        return [
            Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=len(text.splitlines()), character=0),
                ),
                message=str(e),
            ),
        ]


server.start_io()
