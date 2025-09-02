# Job: Ingestão e OCR de Contratos

Este job realiza a ingestão de arquivos digitalizados (PDFs e imagens) e aplica OCR usando o serviço Azure Document Intelligence para extrair o conteúdo textual dos documentos.

## 🧩 Componentes

- `ingestao_openai.py`: pipeline principal de ingestão com OCR
- `utils.py`: funções auxiliares para leitura, parsing e logs

## 🛠️ Funcionalidades

- Leitura de arquivos do ADLS Gen2
- Envio para OCR via Azure Document Intelligence
- Parsing do conteúdo extraído
- Armazenamento estruturado em Delta Lake (camada bronze/silver)

## 🗝️ Requisitos

- Secrets configurados:
  - `sp-ocr-poc-tenant-id`
  - `sp-ocr-poc-client-id`
  - `sp-ocr-poc-secret`
  - `di-endpoint`
- ADLS container configurado para leitura e escrita
- Token de acesso válido ou service principal autorizado

## 📤 Outputs

- Arquivo OCR extraído (JSON/texto estruturado)
- Registro em camada bronze com metadados