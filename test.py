import time

from langchain_community.llms import Ollama

# Initialize the model
llm = Ollama(model="llama3")

while True:
    # Get user input
    user_input = input("Enter your question for the llama3 model (or type 'exit' to quit): ")

    # Check if the user wants to exit
    if user_input.lower() == "exit":
        print("Exiting...")
        break

    # Record the start time
    start_time = time.time()

    # Invoke the model
    response = llm.invoke(user_input)

    # Record the end time
    end_time = time.time()

    # Calculate the time difference in seconds
    time_difference = end_time - start_time

    # Convert the time difference to minutes
    time_difference_minutes = time_difference / 60

    # Display the response and time taken
    print(f"Response: {response}")
    print(f"Time taken for the request: {time_difference_minutes:.2f} minutes\n")
