# Architecture Design of Web Scraping System

## 1. General Flow

The diagram below illustrates the general flow of a web scraping system. This flow is designed based on the ELT pipeline approach.  
**Note:** The official architecture of this project follows the ETL method, as the data volume is not large enough to require batch processing and adapts the near real-time requirement.

![General flow of web scraping architecture](images\general-flow.png)

### Workflow Steps:
1. **Homepage Crawling**:  
   The web scraper accesses the homepage, searches for the desired product, and crawls all the links from the product list.

2. **Product Detail Crawling**:  
   The web scraper loops through the list of product links and visits each link to crawl the HTML and other resources (e.g., images, videos) from the product detail page. The crawling results are stored in data storage for later processing.

3. **Batch Data Processing**:  
   - HTML files are processed through an HTML parser and a text embedding model.  
   - Images are processed through an image embedding model.

4. **Storing Processed Data**:  
   All processed data is stored in an unstructured database that supports vector indexing.

By using the above concept of a web scraping system, two architectures and tech stacks have been designed: **on-premise** and **cloud-based**.

---

## 2. On-Premise Architecture

Based on the general architecture, the tech stacks for the on-premise approach are as follows:

![On-Premise architecture diagram](images\on-premise.png)

- **Web Scraper**: Playwright  
- **Data Storage**: Local HDD  
- **Data Processing**: Kafka + Spark Streaming  
- **Unstructured + Vector Database (supports RAG)**: Redis + RedisStack  
- **LLMs Orchestrator**: LangChain  
- **LLMs Local Hosting**: Hugging Face Text Generation Inference (TGI)  
- **Containerized Technology**: Docker  

**Note**: Applications marked with `*` are containerized.

---

## 3. Cloud-Based Architecture

Based on the general architecture, the tech stacks for the cloud-based approach are as follows:

![Cloud-Based architecture diagram](images\cloud-based.png)

- **Web Scraper**: Playwright + Azure Function  
- **Data Storage**: Azure Data Lake Gen 2  
- **Data Processing**: Kafka + Spark Streaming in Azure HDInsight  
- **Unstructured + Vector Database**: Azure Cosmos DB  
- **RAG**: Azure AI Search  
- **LLMs Orchestrator**: LangChain  
- **LLMs Local Hosting**: Azure OpenAI (TGI)  
- **Containerized Technology**: Docker  

**Note**: Applications marked with `*` are containerized.

