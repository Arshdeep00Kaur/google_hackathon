from typing_extensions import TypedDict

class DocumentState(TypedDict):
    """State model for document processing workflow"""
    file_path: str
    content: str
    category: str