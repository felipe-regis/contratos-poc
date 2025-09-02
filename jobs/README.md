
# 📄 Job 01 — Extração OCR de PDFs com Azure Document Intelligence (PoC Contratos)

Este job realiza a extração de texto de arquivos PDF utilizando o modelo `prebuilt-read` do **Azure Document Intelligence**, com autenticação feita via **Service Principal** da Azure. Os arquivos devem estar previamente carregados em um volume do Databricks.

---

## 📌 Objetivo do Job

- Aplicar OCR (reconhecimento óptico de caracteres) em documentos PDF armazenados no volume `/Volumes/contratos_ia_poc/raw/clientea`.
- Persistir os resultados extraídos em uma tabela Delta na camada **bronze**:  
  `contratos_ia_poc.bronze.extracao_clientea`.

---

## 🔐 Autenticação com Service Principal

A autenticação com o Azure Document Intelligence é feita via `ClientSecretCredential`, usando as seguintes credenciais:

- `tenant_id`
- `client_id`
- `client_secret`
- `endpoint` do serviço Azure Document Intelligence

Estas credenciais devem estar armazenadas de forma segura no **Azure Key Vault**, integrado ao **Databricks Secret Scope**.

---

## 🔧 Pré-requisitos de Infraestrutura

### 1. Provisionamento do Azure Document Intelligence

Crie o recurso Azure AI Document Intelligence (ex-Form Recognizer):

```bash
az cognitiveservices account create   --name di-poc   --resource-group rg-poc   --kind FormRecognizer   --sku S0   --location brazilsouth   --yes
```

Recupere o `endpoint`:

```bash
az cognitiveservices account show --name di-poc --resource-group rg-poc --query "properties.endpoint" --output tsv
```

---

### 2. Criação do Service Principal (SP)

```bash
az ad sp create-for-rbac   --name "sp-di-poc"   --role "Cognitive Services User"   --scopes /subscriptions/<subscription-id>/resourceGroups/rg-poc/providers/Microsoft.CognitiveServices/accounts/di-poc
```

Armazene os valores retornados:

- `client_id`
- `client_secret`
- `tenant_id`

---

### 3. Armazenar as credenciais no Key Vault

```bash
az keyvault secret set --vault-name <your-kv-name> --name "sp-ocr-poc-tenant-id" --value "<tenant-id>"
az keyvault secret set --vault-name <your-kv-name> --name "sp-ocr-poc-client-id" --value "<client-id>"
az keyvault secret set --vault-name <your-kv-name> --name "sp-ocr-poc-secret" --value "<client-secret>"
az keyvault secret set --vault-name <your-kv-name> --name "di-endpoint" --value "<document-intelligence-endpoint>"
```

---

### 4. Criar Secret Scope no Databricks

> Isso conecta o Databricks ao Azure Key Vault.

```bash
databricks secrets create-scope --scope contratos-ocr-poc --scope-backend-type AZURE_KEYVAULT --resource-id "<key-vault-resource-id>" --dns-name "https://<your-kv-name>.vault.azure.net/"
```

---

## 📁 Estrutura esperada de arquivos

Volume de entrada:

```
/Volumes/contratos_ia_poc/raw/clientea/
├── contrato1.pdf
├── contrato2.pdf
└── ...
```

---

## ⚙️ Dependências Python

Certifique-se de que o cluster do Databricks tenha as seguintes bibliotecas instaladas (via `%pip install` ou interface de Libraries):

```bash
azure-identity==1.14.0
azure-core==1.29.5
azure-ai-formrecognizer==3.3.2
```

Instalação via notebook:

```python
%pip install azure-identity==1.14.0 azure-core==1.29.5 azure-ai-formrecognizer==3.3.2
```

---

## 🚀 Execução do Job

### Parâmetros importantes no código:

```python
KV_SCOPE = "contratos-ocr-poc"  # nome do Secret Scope no Databricks
VOLUME_PATH = "/Volumes/contratos_ia_poc/raw/clientea"
TABELA_BRONZE = "contratos_ia_poc.bronze.extracao_clientea"
OCR_MODEL = "prebuilt-read"
```

> O job varre todos os PDFs em `VOLUME_PATH`, aplica OCR e grava os dados estruturados em `TABELA_BRONZE`.

---

## 🧪 Output (camada bronze)

Tabela Delta `contratos_ia_poc.bronze.extracao_clientea` com as seguintes colunas:

| Coluna         | Tipo        | Descrição                                     |
|----------------|-------------|-----------------------------------------------|
| id             | string      | UUID único por arquivo                        |
| file_name      | string      | Nome do arquivo PDF                           |
| file_path      | string      | Caminho completo no volume                    |
| content        | string      | Texto extraído do OCR                         |
| ocr_model      | string      | Modelo utilizado no OCR (`prebuilt-read`)     |
| status         | string      | `OK` ou `FAILED`                              |
| error_message  | string      | Mensagem de erro, se falhou                   |
| extracted_at   | timestamp   | Timestamp de extração                         |

---

## ✅ Próximos passos

- Normalização e enriquecimento na camada Silver
- Extração de informações-chave por regras e modelos NLP
- Geração de metadados e persistência na camada Gold

---

## 👨‍💻 Autor

**Felipe Regis**  
_Data & AI Engineering Manager — Rede D'Or_
