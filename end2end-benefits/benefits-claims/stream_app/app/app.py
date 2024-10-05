import streamlit as st
import time
import uuid
import datetime

from assistant import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats

def main():
    st.title("Benefits & Claims Assistant")

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    if "conversation_saved" not in st.session_state:
        st.session_state.conversation_saved = False
    if "count" not in st.session_state:
        st.session_state.count = 0

    # Debug: Confirm script is running
    st.write("Streamlit app is running.")

    # Claims selection
    section = st.selectbox("Select a claims type:", ["general claim benefits", "nhs claim benefits"])

    # Model selection
    model_choice = st.selectbox("Select a model:", ["ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"])

    # Search type selection
    search_type = st.radio("Select search type:", ["Text", "Vector", "Hybrid"])

    # User input
    user_input = st.text_input("Enter your question:")

    if st.button("Ask"):
        if user_input:  # Only process if user has input something
            with st.spinner("Processing..."):
                try:
                    start_time = time.time()
                    answer_data = get_answer(user_input, section, model_choice, search_type)
                    end_time = time.time()

                    # Display answer and metadata
                    st.write("**Answer:**")
                    st.write(answer_data["answer"])
                    st.write(f"**Response time:** {answer_data['response_time']:.2f} seconds")
                    st.write(f"**Relevance:** {answer_data['relevance']}")
                    st.write(f"**Relevance Explanation:** {answer_data['relevance_explanation']}")
                    st.write(f"**Model used:** {answer_data['model_used']}")
                    st.write(f"**Prompt tokens:** {answer_data['prompt_tokens']}")
                    st.write(f"**Completion tokens:** {answer_data['completion_tokens']}")
                    st.write(f"**Total tokens:** {answer_data['total_tokens']}")
                    st.write(f"**Evaluation Prompt tokens:** {answer_data['eval_prompt_tokens']}")
                    st.write(f"**Evaluation Completion tokens:** {answer_data['eval_completion_tokens']}")
                    st.write(f"**Evaluation Total tokens:** {answer_data['eval_total_tokens']}")

                    # OpenAI cost display, ensure float conversion is safe
                    openai_cost = answer_data.get("openai_cost", 0)
                    st.write(f"**OpenAI cost:** ${openai_cost:.4f}")

                    # Save conversation to the database
                    save_conversation(st.session_state.conversation_id, user_input, answer_data, section)
                    st.session_state.conversation_saved = True  # Set flag to True once saved
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+1"):
            if st.session_state.conversation_saved:
                st.session_state.count += 1
                save_feedback(st.session_state.conversation_id, 1)
                st.success("Positive feedback saved")
            else:
                st.error("Please ask a question before giving feedback.")

    with col2:
        if st.button("-1"):
            if st.session_state.conversation_saved:
                st.session_state.count -= 1
                save_feedback(st.session_state.conversation_id, -1)
                st.success("Negative feedback saved")
            else:
                st.error("Please ask a question before giving feedback.")

    # Relevance buttons
    st.subheader("Relevance Feedback")
    col3, col4, col5 = st.columns(3)
    with col3:
        if st.button("Relevant"):
            if st.session_state.conversation_saved:
                save_feedback(st.session_state.conversation_id, "RELEVANT")
                st.success("Marked as relevant")
            else:
                st.error("Please ask a question first.")

    with col4:
        if st.button("Partly Relevant"):
            if st.session_state.conversation_saved:
                save_feedback(st.session_state.conversation_id, "PARTLY_RELEVANT")
                st.success("Marked as partly relevant")
            else:
                st.error("Please ask a question first.")

    with col5:
        if st.button("Non-Relevant"):
            if st.session_state.conversation_saved:
                save_feedback(st.session_state.conversation_id, "NON_RELEVANT")
                st.success("Marked as non-relevant")
            else:
                st.error("Please ask a question first.")


    # Recent conversations
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox("Filter by relevance:", ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"])
    recent_conversations = get_recent_conversations(limit=5, relevance=relevance_filter if relevance_filter != "All" else None)
    for conv in recent_conversations:
        st.write(f"**Q:** {conv[0]}")
        st.write(f"**A:** {conv[1]}")
        st.write(f"**Relevance:** {conv[2]}")
        st.write(f"**Model Used:** {conv[3]}")

        # Convert cost safely to avoid ValueError
        try:
            openai_cost = float(conv[4]) if conv[4] is not None else 0
            st.write(f"**OpenAI Cost:** ${openai_cost:.4f}")
        except ValueError:
            st.write("**OpenAI Cost:** N/A")

        # Handle timestamp conversion correctly
        try:
            timestamp = float(conv[5])  # assuming it's a float representation of time
            dt_object = datetime.datetime.fromtimestamp(timestamp)  # Convert to datetime
            st.write(f"**Timestamp:** {dt_object.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            st.write(f"**Timestamp:** Error in converting timestamp - {e}")

        st.write("---")

    # Feedback statistics
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"**Thumbs up:** {feedback_stats['thumbs_up']}")
    st.write(f"**Thumbs down:** {feedback_stats['thumbs_down']}")
    st.write(f"**Relevant:** {feedback_stats['relevant']}")
    st.write(f"**Partly Relevant:** {feedback_stats['partly_relevant']}")
    st.write(f"**Non-Relevant:** {feedback_stats['non_relevant']}")

if __name__ == "__main__":
    main()
