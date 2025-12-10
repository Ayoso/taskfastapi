from typing import Dict

def analyze_document_mock(metadata: Dict) -> str:

    file_size_bytes = metadata.get("file_size_bytes", 0)
    version = metadata.get("version", 1)
    file_name = metadata.get("original_name", "файл")

    if file_size_bytes < 100000: 
        size_comment = "очень небольшой"
    elif file_size_bytes < 1000000: 
        size_comment = "относительно небольшой"
    else:
        size_comment = "довольно крупный"

    if version == 1:
        version_comment = "это первая версия документа, требуется первичная оценка содержания."
    else:
        version_comment = "новое изменение внесено. Необходимо проверить, что именно было скорректировано."

    return f"Файл '{file_name}' (v{version}) размером {size_comment}. AI-комментарий: {version_comment}"