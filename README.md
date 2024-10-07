# UK Benefits and Claims Assistant

The UK Benefits and Claims Assistant simplifies the process of querying information on various UK benefits and claims, improving accessibility and reducing the time it takes for users to get crucial answers. The integration of AI with a robust dataset enables the tool to serve as a reliable resource for citizens navigating these processes.

## Problem Description

Navigating the complex landscape of the UK benefits and claims system can be overwhelming, especially for individuals who need immediate and accurate information regarding their eligibility or rights. Whether it's updating benefit information, understanding NHS negligence claims, or filing for medical compensation, the system often leaves people with unanswered questions. Delays in receiving this information can lead to missed deadlines, incomplete filings, and unclaimed benefits.

The UK Benefits and Claims Assistant project addresses this issue by providing a user-friendly RAG (Retrieval-Augmented Generation) application. This assistant allows users to ask questions related to UK benefits, claims, and NHS negligence claims. By leveraging a pre-processed dataset and advanced AI models, it offers accurate, real-time answers on various topics like managing existing benefits, medical negligence claims, and statutory sick pay.

![Overview of Benefits and Claims Assistant](/workspaces/benefits-claims/end2end-benefits/benefits-claims/notebooks/data/benefits.png)

## Data

The dataset used in this project has been generated and compiled using ChatGPT. It consists of 425 records and is stored in the `data/claims.csv` file. The dataset is structured into four columns:

- category: Enables users to perform searches within a specific category, improving the relevance of search results (e.g., general claim benefits, NHS claim benefits).
- question: Captures the specific inquiries made by users, serving as the primary input for the system to generate relevant answers (e.g., "How do I update my benefit information?").
- answer: Delivers clear, concise, and actionable information to users based on their queries (e.g., "You can update your benefit information online through your account.").
- section: Applies context-based filters to ensure that responses are relevant to the specific section of the claims system (e.g., "general claim benefits" or "NHS claim benefits").

Here’s a snippet of the dataset:

```csv
category,question,answer,section
Manage existing benefit,How do I update my benefit information?,You can update your benefit information online through your account.,general claim benefits
Causation,What is the role of a second opinion in establishing causation?,A second opinion can provide critical evidence in establishing that the initial care was negligent and caused harm.,nhs claim benefits
Limitation,How does the limitation period apply to claims for minors?,The limitation period for minors typically begins when they turn 18 giving them until they are 21 to file a claim.,nhs claim benefits
Temporarily unable to work,How do I claim SSP?,Statutory Sick Pay is claimed through your employer if you’re too ill to work.,general claim benefits
Families,What is the Childcare Grant?,The Childcare Grant is available to students in full-time higher education who have children.,general claim benefits
```
## USAGE 

We used pipenv environment for managing dependencies and Python 3.12.

```bash
pip install pipenv
```

```
git clone <https://github.com/ctrl-A-del-specs/benefits-claims>
cd end2end-benefits/benefits-claims
```
Installing dependencies:

```bash
pipenv install
```
Running Jupyter notebook for experiemnts:

```bash
cd notebooks/benefits-claims.ipynb
pipenv run jupyter notebook
```

## RAG flow

We implemented a RAG flow using 3 search engines as knowledge base for indexing and retrieving documents - Minsearch, Elasticsearch(Text) and Elasticsearch(Vectorsearch). We also setup a LLM (ChatGpt4o), connected it to our knowledge using a prompt and queried the system. The code implementation for the RAG flow is at [benefit-claims.ipynb](benefits-claims/notebooks/benefit-claims.ipynb).

Note to run the elasticsearch,we used a docker container using this code:
`bash
docker run -it \
    --rm \
    --name elasticsearch \
    -m 4GB \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3`

## Evaluation

We generated 2055 questions to evaluate the relevance of answers by some models. The 3 Models were used for evaluating the system were ChatGpt-4o, ChatGpt-4o-mini and Google FlanT5. 
Using Cosine Similarity as an evaluating metric the average score (Mean) of ChatGpt-4o was `79%`, ChatGpt-4o-mini was `80%` and Google FlanT5 was `50%`. The code used for generating data and implementing the evaluation can be view here [offline-rag-evaluation.ipynb](benefits-claims/notebooks/offline-rag-evaluation.ipynb)
After establishing the fact that ChatGpt-4o-mini gave the best average, we also used LLM-as-a-judge to evaluate the answers that were of relevance to the questions generated my the model.

Cosine Similarity - Mean
`ChatGpt-4o-mini - 80%`
`ChatGpt-4o - 79%`
`Google FlanT5 - 50%`

LLM-as-a-judge

ChatGpt4o-mini
Relevance
`RELEVANT           1916`
`PARTLY_RELEVANT     102`
`NON_RELEVANT         37`

ChatGpt-4o
`Relevance`
`RELEVANT           1823`
`PARTLY_RELEVANT     214`
`NON_RELEVANT         18`

## Retrieval

 We implementated an evaluation of the retrieval of answers from the 3 search engines used (Minsearch, Textsearch and Vectorsearch). The evaluation was carried out using 2 metrics, Hitrate and Mean Recriprocal Rank. Without any boosting, these are the results:
 Minsearch:                   After Boosting
 `hitrate: 91%, MRR: 64%`     `hitrate: 95%, MRR: 73%`
Textsearch:
`hitrate: 77%, MRR: 62%`      `hitrate: 92%, MRR: 72%`
Vectorsearch:
Question Vector - 
`hitrate: 86%, MRR: 74%`
Answer Vector - 
`hitrate: 82%, MRR: 69%`
Hybridsearch - 
`hitrate: 92%, MRR: 80%`
Question Answer Vector -
`hitrate: 93%, MRR: 81%`     `hitrate: 96%, MRR: 82%`
Best Parameters -
` k: 23, num_candidates: 9000`

The code for implementing retieval can be found: [hyperparameter.ipynb](benefits-claims/notebooks/hyperparameter.ipynb)

## Interface

We created a simple interface using Streamlit to interact with the system. Code implementation can be found here [benefits-claims](benefits-claims/generate_data/qa.py)

## Monitoring


