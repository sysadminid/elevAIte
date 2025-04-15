from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest

endpoint = "<ENDPOINT_URL_DOC_INTELLIGENCE>"
key = "<API_KEY_DOC_INTELLIGENCE>"

docUrl = "<DOCUMENT_URL>"

document_analysis_client = DocumentIntelligenceClient(endpoint=endpoint,
    credential=AzureKeyCredential(key))

poller = document_analysis_client.begin_analyze_document(
        "prebuilt-layout", AnalyzeDocumentRequest(url_source=docUrl
    ))
result: AnalyzeResult = poller.result()

for page in result.pages:
    print(f"Page number: {page.page_number}")
    for line in page.lines:
        print(f"Line: {line.content}")
    for table in page.tables:
        print("Table:")
        for cell in table.cells:
            print(f"  Cell[{cell.row_index}, {cell.column_index}]: {cell.content}")
