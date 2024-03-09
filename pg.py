import os
os.environ["OPENAI_API_KEY"] = "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"
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ragas import evaluate
from datasets import Dataset
from ragas.metrics import (
    answer_relevancy,
    context_recall,
    context_precision,
)


gpt_turbo = ChatOpenAI(temperature=0.3, model_name='gpt-3.5-turbo-16k')

templateOne = """Scenario:
You are a Vanguard helper clerk assisting a user with their Vanguard questions.
Vanguard is an investment firm.
Instructions:
Convert the clients message into a search key in relation to actions the client can consider with the website. You have to key in the users intent into a vector database to get the results you want
Provide your response in the form of words separated by commas, produce up to 8 results.
Customer Message:
{text}
Question:
What actions would you suggest to the customer based on their message?"""

promptOne = PromptTemplate(input_variables=["text"], template=templateOne)
chainOne = LLMChain(llm=gpt_turbo, verbose=False,prompt= promptOne)




def create_eval_data_set():
    # Initialize a dictionary to hold data samples
    data_samples = {
        'question': [],
        'ground_truths': [],
        'answer': [],
        'contexts': []
    }
    try:
        with open('eval_questions.txt', 'r') as file:
            for line in file:
                # Splitting the line into question and ground truth
                question, ground_truth = line.split("ground_truths:", 1)

                memory.clear()
                answer, contexts = chat(question)
                # Combine and format context content
                formatted_contexts = [doc.page_content.replace("\n", " .") for doc in contexts]

                # Update the data_samples dictionary
                data_samples['question'].append(question)
                data_samples['contexts'].append(formatted_contexts)
                data_samples['answer'].append(answer)
                data_samples['ground_truths'].append([ground_truth])

    except FileNotFoundError:
        print("Error: eval_questions.txt file not found.")
        return

    # Convert to dataset and save
    dataset = Dataset.from_dict(data_samples)
    dataset.save_to_disk('eval_dataset')

    # Optional: Print dataset for verification
    print(dataset)


def evaluate_rag():
    loaded_dataset = Dataset.load_from_disk('eval_dataset')
    result = evaluate(
        loaded_dataset,
        metrics=[
            context_precision,  # checks if ground truth relevant items are in retrieved context
            answer_relevancy,  # checks how relevant llm answer is to the question
            context_recall,  # measures the extent to which the retrieved context aligns with the annotated answer
        ],
    )
    return result


def chat(query,EvaluationToggle=True):
    
    searchTerms = "".join(chainOne.run(query))
    return searchTerms


def main():
    EvaluationToggle = False
    # toggle between chatting and evaluation
    if EvaluationToggle:
        # Create evaluation dataset if it doesn't exist
        if not os.path.exists("eval_dataset"):
            create_eval_data_set()
        print(evaluate_rag())
    else:
        while True:
            query = input("Enter your query (type 'exit' to quit): ")
            if query == "exit":
                break
            print(chat(query,EvaluationToggle))


if __name__ == "__main__":
    main()
