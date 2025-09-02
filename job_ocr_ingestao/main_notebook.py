# Databricks notebook source
# MAGIC %md
# MAGIC ## 02. Azure Document Intelligence (Antigo Form Recognizer)

# COMMAND ----------

pip install azure-ai-formrecognizer azure-identity azure-core==1.29.5 azure-identity==1.14.0 azure-ai-formrecognizer==3.3.2

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

# ==== Parâmetros de ambiente ====
KV_SCOPE = "dbricks-keyvault-secrets"

# Computer Vision (Document Intelligence) - endpoint (ex.: https://<nome>.cognitiveservices.azure.com/)
try:
    DI_ENDPOINT = dbutils.secrets.get(KV_SCOPE, "di-endpoint")
    CV_ENDPOINT = dbutils.secrets.get(KV_SCOPE, "cv-endpoint")
except Exception:
    CV_ENDPOINT = "https://cv-read-ocr-hml.cognitiveservices.azure.com/"  # fallback manual
    DI_ENDPOINT = "https://di-ocr-poc-hml.cognitiveservices.azure.com/"

# Recuperar segredos seguros via Key Vault-backed scope
client_id = dbutils.secrets.get(scope="dbricks-keyvault-secrets", key="sp-ocr-poc-client-id")
tenant_id = dbutils.secrets.get(scope="dbricks-keyvault-secrets", key="sp-ocr-poc-tenant-id")
client_secret = dbutils.secrets.get(scope="dbricks-keyvault-secrets", key="sp-ocr-poc-secret")

# COMMAND ----------

import os
import uuid
from datetime import datetime
from azure.identity import ClientSecretCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

# === Configurações do Service Principal (substitua pelas secrets reais do Key Vault ou dbutils) ===
tenant_id = dbutils.secrets.get(scope=KV_SCOPE, key="sp-ocr-poc-tenant-id")
client_id = dbutils.secrets.get(scope=KV_SCOPE, key="sp-ocr-poc-client-id")
client_secret = dbutils.secrets.get(scope=KV_SCOPE, key="sp-ocr-poc-secret")
endpoint = dbutils.secrets.get(scope=KV_SCOPE, key="di-endpoint")  # ex: "https://<name>.cognitiveservices.azure.com/"

# === Autenticação com Service Principal ===
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# === Inicializar cliente Document Intelligence ===
ocr_model = "prebuilt-read"
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=credential
)

# === Caminho dos arquivos PDF no volume ===
volume_path = "/Volumes/contratos_ia_poc/raw/clientea"
files = [f.path for f in dbutils.fs.ls(volume_path) if f.path.endswith(".pdf")]

# === Inicializar Spark ===
spark = SparkSession.builder.getOrCreate()
records = []

for file_path in files:
    try:
        local_path = file_path.replace("dbfs:", "/dbfs")

        with open(local_path, "rb") as pdf_file:
            poller = document_analysis_client.begin_analyze_document(
                model_id=ocr_model,
                document=pdf_file
            )
            result = poller.result()

            content = "\n".join([line.content for page in result.pages for line in page.lines])

        records.append({
            "id": str(uuid.uuid4()),
            "file_name": file_path.split("/")[-1],
            "file_path": file_path,
            "content": content,
            "ocr_model": ocr_model,
            "status": "OK",
            "error_message": None,
            "extracted_at": datetime.now()
        })

    except Exception as e:
        records.append({
            "id": str(uuid.uuid4()),
            "file_name": file_path.split("/")[-1],
            "file_path": file_path,
            "content": None,
            "ocr_model": ocr_model,
            "status": "FAILED",
            "error_message": str(e),
            "extracted_at": datetime.now()
        })

# === Criar schema e gravar em tabela Delta bronze ===
schema = StructType([
    StructField("id", StringType(), False),
    StructField("file_name", StringType(), True),
    StructField("file_path", StringType(), True),
    StructField("content", StringType(), True),
    StructField("ocr_model", StringType(), True),
    StructField("status", StringType(), True),
    StructField("error_message", StringType(), True),
    StructField("extracted_at", TimestampType(), True)
])

df = spark.createDataFrame(records, schema=schema)
df.write.mode("overwrite").format("delta").saveAsTable("contratos_ia_poc.bronze.extracao_clientea")
display(df)
