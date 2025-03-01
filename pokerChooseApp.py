import streamlit as st
import importlib

st.title("Poker Hands Analysis")

# Initialize player names and number of players in session state
if "num_players" not in st.session_state:
    st.session_state.num_players = 2  # Default number of players
if "player_names" not in st.session_state:
    st.session_state.player_names = [f"Player {i+1}" for i in range(st.session_state.num_players)]

# Dropdown to select which app to load
with st.expander("Poker Hand Rankings Reference"):
    st.markdown("""
    1. **Royal Flush**: A, K, Q, J, 10, all the same suit
    2. **Straight Flush**: Five cards in a sequence, all in the same suit
    3. **Four of a Kind**: Four cards of the same rank
    4. **Full House**: Three of a kind with a pair
    5. **Flush**: Any five cards of the same suit, not in sequence
    6. **Straight**: Five cards in a sequence, not of the same suit
    7. **Three of a Kind**: Three cards of the same rank
    8. **Two Pair**: Two different pairs
    9. **One Pair**: Two cards of the same rank
    10. **High Card**: Highest card wins if nobody has any of the above
    """)
option = st.selectbox("Select a tool:", ["Player Best Hand", "Poker Hands - Who Wins"])
st.write("---")  # Separator for clarity

# Mapping options to module names
module_map = {
    "Player Best Hand": "pokerHandWhoWins",
    "Poker Hands - Who Wins": "pokerHandWhoWinsDealer"
}

# Reset function to clear only selected cards, preserving player names
def reset_state():
    keys_to_keep = {"num_players", "player_names"}  # Keys to preserve
    keys_to_delete = [key for key in st.session_state.keys() if key not in keys_to_keep]
    
    for key in keys_to_delete:
        del st.session_state[key]


# Sidebar for player names
st.sidebar.header("Player Names")
for i in range(st.session_state.num_players):
    # Ensure the list is long enough
    if i >= len(st.session_state.player_names):
        st.session_state.player_names.append(f"Player {i+1}")
        
    player_name = st.sidebar.text_input(
        f"Player {i+1} Name",
        value=st.session_state.player_names[i],
        key=f"player_name_{i}"
    )
    # Update the name in session state
    st.session_state.player_names[i] = player_name

# Dynamically import and run the selected module
if option in module_map:
    module_name = module_map[option]
    loaded_module = importlib.import_module(module_name)
    importlib.reload(loaded_module)
    loaded_module.run()
# Add a refresh button to reset selected cards but keep player names
if st.sidebar.button("Refresh"):
    reset_state()
    st.rerun()  # Refresh the Streamlit app

st.markdown("---")
st.markdown("*Developed with ❤️ for ~~poker enthusiasts~~ ganjhedis who still can't calculate their hands.*")
st.markdown("*Sharam karo, khelne se pehle seekh lo.*")
st.markdown("*Ya toh win hota hai, ya toh lun*")
