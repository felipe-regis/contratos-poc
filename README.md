# contratos-poc

Prova de conceito para automação e análise de contratos digitais utilizando Databricks, OCR com Azure Document Intelligence, e validação de conteúdo com Azure OpenAI.

## 📌 Objetivo

Construir uma solução robusta para extração, estruturação e validação de informações de documentos contratuais digitalizados, com foco em aplicações nos setores jurídico e de saúde.

## ⚙️ Tecnologias utilizadas

- **Databricks** (PySpark, Delta Lake)
- **Azure Document Intelligence (OCR)**
- **Azure OpenAI (LLM para validação)**
- **Azure Key Vault** (gerenciamento de segredos)
- **GitHub** (versionamento)
- **MongoDB** (opcional para persistência final)

## 🧭 Estrutura do projeto

```
contratos-poc/
│
├── job_ocr_ingestao/         # Ingestão de documentos e OCR
├── job_estrutura_dados/      # Extração e estruturação dos dados extraídos
├── shared/                   # Scripts auxiliares e funções comuns
├── .gitignore
└── README.md
```

## 🚀 Executando os jobs

Os jobs podem ser executados via Databricks Jobs ou manualmente via notebooks no Workspace. Certifique-se de configurar:

- Secrets no Azure Key Vault
- Token para autenticação
- Repositório Git conectado

## 📄 Documentação por job

Cada subpasta possui seu próprio `README.md` com detalhes sobre entradas, saídas e lógica.

---

## 👨‍💻 Autor

Felipe Regis  
Engenheiro de Dados e Especialista em Databricks, Azure & Soluções de IA aplicadas à Saúde
