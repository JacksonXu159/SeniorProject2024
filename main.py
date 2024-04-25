import os
os.environ["OPENAI_API_KEY"] = ""
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from ragas import evaluate
import re
from datasets import Dataset
from ragas.llms import LangchainLLM
from ragas.metrics import (
    answer_relevancy,
)



default_ef = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

if not os.path.exists("db"):
    text_loader_kwargs = {'autodetect_encoding': True}
    loader = DirectoryLoader("data_test", glob="**/*.txt", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs, silent_errors=True)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1400, chunk_overlap=0, length_function=len)
    docs = text_splitter.split_documents(documents)
    db = Chroma.from_documents(documents=docs, embedding=default_ef, persist_directory="db")
    db.persist()

db = Chroma(persist_directory="db", embedding_function=default_ef)
gpt_turbo = ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo-16k')

templateOne = """Scenario:
You are a Vanguard helper clerk assisting a user with their Vanguard questions.
Vanguard is an investment firm.
Instructions:
Convert the clients message into a search key in relation to actions the client can consider with the website. You have to key in the users intent into a vector database to get the results you want
Provide your response in the form of words separated by commas, produce up to 4 results.
Customer Message:
{text}
Question:
What actions would you suggest to the customer based on their message?"""

promptOne = PromptTemplate(input_variables=["text"], template=templateOne)
chainOne = LLMChain(llm=gpt_turbo, verbose=False,prompt= promptOne)

templateTwo = """You are a webpage directory navigation bot helping Vanguard clients navigate to the right page on the Vanguard website.
Vanguard is an investment firm.
Use the following context showing the available webpages and recommend the best webpage based on the users question.
Output must follow this format "pageName".
context: 
{context}
Human: {question}"""

promptTwo = PromptTemplate(
    input_variables=[ "question", "context"],
    template=templateTwo
)

chainTwo = load_qa_chain(gpt_turbo, chain_type="stuff", verbose=False, prompt=promptTwo)

def create_eval_data_set():
    passCount = 0
    failCount = 0
    count = 0
    try:
        with open('real_questions.txt', 'r') as file:
            for line in file:
                count += 1
                # Splitting the line into question and ground truth
                question, ground_truth = line.split("ground_truths:", 1)

                answer, contexts = chat(question)
                print(ground_truth.lower(), end='')
                print( answer.replace(".","").lower())
                print(count)
                print("STOP")
                if re.sub(r"\s+", "", ground_truth).lower() == re.sub(r"\s+", "", answer).replace(".","").lower():
                    passCount += 1 
                else:
                    failCount += 1

    except FileNotFoundError:
        print("Error: eval_questions.txt file not found.")
        return
    print(passCount,"/",passCount+failCount)


def evaluate_rag():
    loaded_dataset = Dataset.load_from_disk('eval_dataset')
    result = evaluate(
        loaded_dataset,
        metrics=[
            answer_relevancy,  # checks how relevant llm answer is to the question
        ],
    )
    return result


def chat(query,EvaluationToggle=True):
    
    searchTerms = "".join(chainOne.run(query))
    st = searchTerms.split(",")
    matching_docs = []

    for s in st:
        seen_content = set()
        unique_documents = []
        documents = db.similarity_search(s, k=2)
        for doc in documents:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                unique_documents.append(doc)

        matching_docs += unique_documents

    response = chainTwo(
        {
            "input_documents": matching_docs,
            "question": query,
        },
        return_only_outputs=True,
    )
    #print(searchTerms)
    #print([doc.page_content.replace("\n", " .") for doc in matching_docs])
    
    if EvaluationToggle:
        return response['output_text'],matching_docs
    else:
        return response['output_text']


def main():
    EvaluationToggle = False
    # toggle between chatting and evaluation
    if EvaluationToggle:
        # Create evaluation dataset if it doesn't exist
        if not os.path.exists("eval_dataset"):
            create_eval_data_set()
        #print(evaluate_rag())
    else:
        while True:
            query = input("Enter your query (type 'exit' to quit): ")
            if query == "exit":
                break
            print(chat(query,EvaluationToggle))


if __name__ == "__main__":
    main()
