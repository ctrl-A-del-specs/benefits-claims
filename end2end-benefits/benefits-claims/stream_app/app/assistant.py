import os
import time
import json
import streamlit as st

from openai import OpenAI
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

ELASTIC_URL = os.getenv("ELASTIC_URL", "http://elasticsearch:9200")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")

es_client = Elasticsearch(ELASTIC_URL)
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


def elastic_search_text(query, section, index_name="benefit-claims"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "answer", "category"],
                        "type": "best_fields",
                    }
                },
                "filter": {"term": {"section": section}},
            }
        },
    }

    try:
        response = es_client.search(index=index_name, body=search_query)
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        st.error(f"Error in Elasticsearch query: {e}")
        return []


def elastic_search_knn(field, vector, section, index_name="benefit-claims"):
    knn_query = {
        "knn": {
            "field": field,
            "query_vector": vector,
            "k": 5,
            "num_candidates": 10000,
            "filter": {"term": {"section": section}}  # Filter for section
        }
    }

    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": [knn_query]  
            }
        },
        "_source": ["answer", "section", "question", "category", "id"],
    }

    try:
        es_results = es_client.search(index=index_name, body=search_query)
        return [hit["_source"] for hit in es_results["hits"]["hits"]]
    except Exception as e:
        st.error(f"Error in KNN Elasticsearch query: {e}")
        return []

def elastic_search_hybrid(query, vector, section, index_name="benefit-claims"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": [
                    {
                        "knn": {
                            "field": "question_answer_vector",
                            "query_vector": vector,
                            "k": 5,
                            "num_candidates": 10000
                            # "boost": 0.5  
                        }
                    },
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["question^3", "answer", "category"],
                            "type": "best_fields"
                            # "boost": 0.5  
                        }
                    }
                ],
                "filter": {
                    "term": {
                        "section": section 
                    }
                }
            }
        },
        "_source": ["answer", "section", "question", "category", "id"]
    }

    try:
        es_results = es_client.search(index=index_name, body=search_query)
        return [hit["_source"] for hit in es_results["hits"]["hits"]]
    except Exception as e:
        st.error(f"Error in hybrid Elasticsearch query: {e}")
        return []



def question_answer_hybrid(q):
    question = q['question']
    section = q['section'] 
    v_q = model.encode(question)
    return elastic_search_hybrid(question, v_q, section)


def build_prompt(query, search_results):
    prompt_template = """
You are an expert in United Kingdom Benefit Claims and Medical Negligence Claims. Answer the QUESTION based on the CONTEXT from 
the FAQ databases of Benefits database and NHS claims management. 
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = "\n\n".join(
        [
            f"category: {doc['category']}\nquestion: {doc['question']}\nanswer: {doc['answer']}\nsection: {doc['section']}\n\n"
            for doc in search_results
        ]
    )
    return prompt_template.format(question=query, context=context).strip()


def llm(prompt, model_choice):
    start_time = time.time()
    if model_choice.startswith('ollama/'):
        response = ollama_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    elif model_choice.startswith('openai/'):
        response = openai_client.chat.completions.create(
            model=model_choice.split('/')[-1],
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    return answer, tokens, response_time


def evaluate_relevance(question, answer):
    prompt_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
  "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
  "Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = llm(prompt, 'openai/gpt-4o-mini')

    try:
        json_eval = json.loads(evaluation)
        return json_eval.get('Relevance', 'UNKNOWN'), json_eval.get('Explanation', 'No explanation provided'), tokens
    except json.JSONDecodeError:
        st.error("Failed to parse evaluation JSON.")
        return "UNKNOWN", "Failed to parse evaluation", tokens



def calculate_openai_cost(model_choice, tokens):
    openai_cost = 0.0  

    if model_choice == 'openai/gpt-3.5-turbo':
        openai_cost = (tokens['prompt_tokens'] * 0.0015 + tokens['completion_tokens'] * 0.002) / 1000
    elif model_choice in ['openai/gpt-4o', 'openai/gpt-4o-mini']:
        openai_cost = (tokens['prompt_tokens'] * 0.03 + tokens['completion_tokens'] * 0.06) / 1000

    return float(openai_cost) 



def get_answer(query, section, model_choice, search_type='Hybrid'):
    if search_type == 'Vector':
        vector = model.encode(query)
        search_results = elastic_search_knn('question_answer_vector', vector, section)
    elif search_type == 'Hybrid':
        q = {'question': query, 'section': section}
        search_results = question_answer_hybrid(q)
    else:
        search_results = elastic_search_text(query, section)

    prompt = build_prompt(query, search_results)
    answer, tokens, response_time = llm(prompt, model_choice)
    
    relevance, explanation, eval_tokens = evaluate_relevance(query, answer)

    openai_cost = calculate_openai_cost(model_choice, tokens)
 
    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'model_used': model_choice,
        'prompt_tokens': tokens['prompt_tokens'],
        'completion_tokens': tokens['completion_tokens'],
        'total_tokens': tokens['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': openai_cost
    }
