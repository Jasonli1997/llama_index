import json
from pathlib import Path
from unittest.mock import MagicMock

from docling_core.types import DoclingDocument as DLDocument
from llama_index.readers.docling.base import DoclingReader

in_json_str = json.dumps(
    {
        "schema_name": "DoclingDocument",
        "version": "1.0.0",
        "name": "sample",
        "origin": {
            "mimetype": "text/html",
            "binary_hash": 42,
            "filename": "sample.html",
        },
        "furniture": {
            "self_ref": "#/furniture",
            "children": [],
            "name": "_root_",
            "label": "unspecified",
        },
        "body": {
            "self_ref": "#/body",
            "children": [{"$ref": "#/texts/0"}, {"$ref": "#/texts/1"}],
            "name": "_root_",
            "label": "unspecified",
        },
        "groups": [],
        "texts": [
            {
                "self_ref": "#/texts/0",
                "parent": {"$ref": "#/body"},
                "children": [],
                "label": "paragraph",
                "prov": [],
                "orig": "Some text",
                "text": "Some text",
            },
            {
                "self_ref": "#/texts/1",
                "parent": {"$ref": "#/body"},
                "children": [],
                "label": "paragraph",
                "prov": [],
                "orig": "Another paragraph",
                "text": "Another paragraph",
            },
        ],
        "pictures": [],
        "tables": [],
        "key_value_items": [],
        "pages": {},
    }
)


out_json_obj = {
    "root": [
        {
            "id_": "https://example.com/foo.pdf",
            "embedding": None,
            "metadata": {},
            "excluded_embed_metadata_keys": [],
            "excluded_llm_metadata_keys": [],
            "relationships": {},
            "text": '{"schema_name": "DoclingDocument", "version": "1.0.0", "name": "sample", "origin": {"mimetype": "text/html", "binary_hash": 42, "filename": "sample.html"}, "furniture": {"self_ref": "#/furniture", "children": [], "name": "_root_", "label": "unspecified"}, "body": {"self_ref": "#/body", "children": [{"$ref": "#/texts/0"}, {"$ref": "#/texts/1"}], "name": "_root_", "label": "unspecified"}, "groups": [], "texts": [{"self_ref": "#/texts/0", "parent": {"$ref": "#/body"}, "children": [], "label": "paragraph", "prov": [], "orig": "Some text", "text": "Some text"}, {"self_ref": "#/texts/1", "parent": {"$ref": "#/body"}, "children": [], "label": "paragraph", "prov": [], "orig": "Another paragraph", "text": "Another paragraph"}], "pictures": [], "tables": [], "key_value_items": [], "pages": {}}',
            "mimetype": "text/plain",
            "start_char_idx": None,
            "end_char_idx": None,
            "text_template": "{metadata_str}\n\n{content}",
            "metadata_template": "{key}: {value}",
            "metadata_seperator": "\n",
            "metadata_separator": "\n",
            "class_name": "Document",
        }
    ]
}

out_md_obj = {
    "root": [
        {
            "id_": "https://example.com/foo.pdf",
            "embedding": None,
            "metadata": {},
            "excluded_embed_metadata_keys": [],
            "excluded_llm_metadata_keys": [],
            "relationships": {},
            "text": "Some text\n\nAnother paragraph",
            "mimetype": "text/plain",
            "start_char_idx": None,
            "end_char_idx": None,
            "text_template": "{metadata_str}\n\n{content}",
            "metadata_template": "{key}: {value}",
            "metadata_seperator": "\n",
            "metadata_separator": "\n",
            "class_name": "Document",
        }
    ]
}


def _deterministic_id_func(doc: DLDocument, file_path: str | Path) -> str:
    return f"{file_path}"


def test_lazy_load_data_with_md_export(monkeypatch):
    mock_dl_doc = DLDocument.model_validate_json(in_json_str)
    mock_response = MagicMock()
    mock_response.document = mock_dl_doc

    monkeypatch.setattr(
        "docling.document_converter.DocumentConverter.__init__",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "docling.document_converter.DocumentConverter.convert",
        lambda *args, **kwargs: mock_response,
    )

    reader = DoclingReader(id_func=_deterministic_id_func)
    doc_iter = reader.lazy_load_data(file_path="https://example.com/foo.pdf")
    act_li_docs = list(doc_iter)
    assert len(act_li_docs) == 1

    act_data = {"root": [li_doc.model_dump() for li_doc in act_li_docs]}
    assert act_data == out_md_obj


def test_lazy_load_data_with_json_export(monkeypatch):
    mock_dl_doc = DLDocument.model_validate_json(in_json_str)
    mock_response = MagicMock()
    mock_response.document = mock_dl_doc

    monkeypatch.setattr(
        "docling.document_converter.DocumentConverter.__init__",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "docling.document_converter.DocumentConverter.convert",
        lambda *args, **kwargs: mock_response,
    )

    reader = DoclingReader(
        export_type=DoclingReader.ExportType.JSON,
        id_func=_deterministic_id_func,
    )
    doc_iter = reader.lazy_load_data(file_path="https://example.com/foo.pdf")
    act_li_docs = list(doc_iter)
    assert len(act_li_docs) == 1

    act_data = {"root": [li_doc.model_dump() for li_doc in act_li_docs]}
    assert act_data == out_json_obj