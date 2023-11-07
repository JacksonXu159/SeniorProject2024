from langchain.document_loaders import DirectoryLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from chromadb.config import Settings
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import chromadb
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain
import os
import sys

def main():

    os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE"
    default_ef = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


    if not os.path.exists("db"):
        text_loader_kwargs={'autodetect_encoding': True}
        loader = DirectoryLoader("data", glob="**/*.txt", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs,silent_errors=True)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0, length_function  = len)
        docs = text_splitter.split_documents(documents)
        db = Chroma.from_documents(documents=docs,embedding=default_ef,persist_directory="db")
        db.persist()

    db = Chroma(persist_directory="db",embedding_function=default_ef)
    turbo_llm = ChatOpenAI(temperature=0.3,model_name='gpt-3.5-turbo-16k')
    chain = load_qa_chain(turbo_llm, chain_type="stuff",verbose=True)

    query = sys.argv[1]
    template = """Scenario:
    You are a Vanguard helper clerk assisting a user with their Vanguard questions.
    Vanguard is an investment firm.
    Instructions:
    Convert the clients message into a search key in relation to actions the client can consider with the website. You have to key in the users intent into a vector database to get the results you want
    Provide your response in the form of words separated by commas, produce 2 to 8 results.
    The key terms must be strictly Vanguard related.
    Dont not add anything else, just the word groups.No formatting or bullet points.
    Customer Message:
    {text}

    Question:
    What actions would you suggest to the customer based on their message?"""
    prompt_template = PromptTemplate(input_variables=["text"], template=template)
    answer_chain = LLMChain(llm=turbo_llm, prompt=prompt_template)
    searchTerms = "".join(answer_chain.run(query))
    print(searchTerms)
    st = searchTerms.split(",")
    matching_docs = []

    for s in st:
        seen_content = set()
        unique_documents = []
        documents = db.similarity_search(s,k=2)
        for doc in documents:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                unique_documents.append(doc)

        matching_docs += unique_documents

    seen_content = set()
    unique_documents = []
    documents = db.similarity_search(query,k=1)
    for doc in documents:
        if doc.page_content not in seen_content:
            seen_content.add(doc.page_content)
            unique_documents.append(doc)


    prompt = "You are a customer support specialist helping Vanguard clients with their questions while browsing the Vanguard website.Vanguard is an investment firm.Use the following pieces of context and recommended actions to answer the question at the end. Find out what actions the client might need to make. If you don't know the answer, just say “Sorry, con’t answer your question, try to ask it in a different way”, don't try to make up an answer. Recommendation:"+ searchTerms + "User Message:"+query

    answer =  chain.run(input_documents=matching_docs, question=prompt)
    print(answer)

main()