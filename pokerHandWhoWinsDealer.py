import streamlit as st
import random
from itertools import combinations
import pandas as pd

# Define card constants
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
SUIT_SYMBOLS = {
    'Hearts': '♥️',
    'Diamonds': '♦️',
    'Clubs': '♣️',
    'Spades': '♠️'
}
SUIT_COLORS = {
    'Hearts': 'red',
    'Diamonds': 'red',
    'Clubs': 'black',
    'Spades': 'black'
}
HAND_RANKS = {
    9: "Royal Flush",
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "Pair",
    0: "High Card"
}

# Initialize session state variables
if 'num_players' not in st.session_state:
    st.session_state.num_players = 2
if 'community_cards' not in st.session_state:
    st.session_state.community_cards = [None] * 5
if 'player_cards' not in st.session_state:
    st.session_state.player_cards = [None] * 10  # Max 5 players with 2 cards each
if 'editing_card' not in st.session_state:
    st.session_state.editing_card = None
if 'results' not in st.session_state:
    st.session_state.results = None
# Add player names to session state
if 'player_names' not in st.session_state:
    st.session_state.player_names = ["Player 1", "Player 2"]

# Function to add a card to a specific location
def add_card_at_index(card_type, index, card):
    if card_type == "community":
        # Ensure the list is long enough
        while len(st.session_state.community_cards) <= index:
            st.session_state.community_cards.append(None)
        st.session_state.community_cards[index] = card
    else:  # player
        # Ensure the list is long enough
        while len(st.session_state.player_cards) <= index:
            st.session_state.player_cards.append(None)
        st.session_state.player_cards[index] = card

# Function to remove a card
def remove_card(card_type, index):
    if card_type == "community":
        if index < len(st.session_state.community_cards):
            st.session_state.community_cards[index] = None
    else:  # player
        if index < len(st.session_state.player_cards):
            st.session_state.player_cards[index] = None

# Function to render a card with responsive design
def render_card(rank, suit, width=80, height=120, font_size_rank=20, font_size_suit=36, margin_top=15):
    card_color = SUIT_COLORS[suit]
    
    # Make cards responsive using percentage and viewport units with min/max constraints
    return f"""
    <div style="width:{width}px;height:{height}px;border:1px solid black;border-radius:10px;padding:5px;text-align:center;background:white;display:inline-block;margin:5px;
                min-width:40px;max-width:100%;box-sizing:border-box;">
        <div style="font-size:{font_size_rank}px;color:{card_color};">{rank}{SUIT_SYMBOLS[suit]}</div>
        <div style="font-size:{font_size_suit}px;margin-top:{margin_top}px;color:{card_color};">{SUIT_SYMBOLS[suit]}</div>
    </div>
    """

# Function to display a card placeholder with "+" for adding a card
def render_card_placeholder(width=80, height=120, font_size=36):
    return f"""
    <div style="width:{width}px;height:{height}px;border:1px dashed #ccc;border-radius:10px;padding:5px;text-align:center;background:#f8f8f8;display:inline-block;margin:5px;
                min-width:40px;max-width:100%;box-sizing:border-box;cursor:pointer;">
        <div style="font-size:{font_size}px;color:#aaa;line-height:{height}px;">+</div>
    </div>
    """

# Function to render multiple cards in a row
def render_card_row(cards, width=60, height=90):
    html = '<div style="display:flex;flex-wrap:wrap;gap:5px;">'
    for card in cards:
        if card is not None:
            rank, suit = card
            html += render_card(rank, suit, width, height, 16, 28, 10)
    html += '</div>'
    return html

# Improved card selection function
def card_selector(key_prefix, selected_cards=[]):
    # Create a visual card selection grid
    st.write("Select a card:")
    
    # Create tabs for suits
    suit_tabs = st.tabs(["♥️ Hearts", "♦️ Diamonds", "♣️ Clubs", "♠️ Spades"])
    
    selected_card = None
    
    for i, suit in enumerate(SUITS):
        with suit_tabs[i]:
            cols = st.columns(7)  # 13 ranks, but we'll use 2 rows to make it more compact
            
            # First row (2-8)
            for j, rank in enumerate(RANKS[:7]):
                card = (rank, suit)
                disabled = card in selected_cards
                
                # Use a colored button with rank display
                if cols[j].button(
                    f"{rank}", 
                    key=f"{key_prefix}_{suit}_{rank}",
                    disabled=disabled,
                    use_container_width=True,
                    type="primary" if suit in ["Hearts", "Diamonds"] else "secondary"
                ):
                    selected_card = card
            
            # Second row (9-A)
            cols2 = st.columns(7)
            for j, rank in enumerate(RANKS[7:], 7):
                card = (rank, suit)
                disabled = card in selected_cards
                
                if cols2[j-7].button(
                    f"{rank}", 
                    key=f"{key_prefix}_{suit}_{rank}",
                    disabled=disabled,
                    use_container_width=True,
                    type="primary" if suit in ["Hearts", "Diamonds"] else "secondary"
                ):
                    selected_card = card
    
    return selected_card

# Function to get card rank value for comparison
def get_card_value(card):
    if card is None:
        return -1
    rank, _ = card
    return RANKS.index(rank)

# Poker hand evaluation functions
def evaluate_hand(hole_cards, community_cards):
    if None in hole_cards or None in community_cards:
        return -1, []
    
    all_cards = hole_cards + community_cards
    all_combos = list(combinations(all_cards, 5))
    best_hand_value = -1
    best_hand = []
    
    for combo in all_combos:
        hand_value, tie_breakers = evaluate_five_card_hand(combo)
        if hand_value > best_hand_value or (hand_value == best_hand_value and tie_breakers > best_tie_breakers):
            best_hand_value = hand_value
            best_hand = combo
            best_tie_breakers = tie_breakers
    
    return best_hand_value, best_hand

def evaluate_five_card_hand(hand):
    # Convert hand format for evaluation
    cards = [(card[0], card[1]) for card in hand]
    ranks = [card[0] for card in cards]
    suits = [card[1] for card in cards]
    
    # Count rank frequencies
    rank_counts = {}
    for rank in ranks:
        if rank in rank_counts:
            rank_counts[rank] += 1
        else:
            rank_counts[rank] = 1
    
    # Check for flush
    is_flush = len(set(suits)) == 1
    
    # Check for straight
    rank_values = [RANKS.index(rank) for rank in ranks]
    rank_values.sort()
    
    is_straight = False
    if len(set(rank_values)) == 5:  # All ranks are different
        if max(rank_values) - min(rank_values) == 4:
            is_straight = True
        # Special case: A-5 straight
        if set(rank_values) == set([0, 1, 2, 3, 12]):
            is_straight = True
            # Adjust for A-5 straight (A is low)
            rank_values = [0, 1, 2, 3, 4]
    
    # Determine hand type
    hand_value = 0
    hand_type = ""
    
    # Royal Flush
    if is_flush and is_straight and 12 in rank_values and 11 in rank_values:
        hand_value = 9
    # Straight Flush
    elif is_flush and is_straight:
        hand_value = 8
    # Four of a Kind
    elif 4 in rank_counts.values():
        hand_value = 7
    # Full House
    elif 3 in rank_counts.values() and 2 in rank_counts.values():
        hand_value = 6
    # Flush
    elif is_flush:
        hand_value = 5
    # Straight
    elif is_straight:
        hand_value = 4
    # Three of a Kind
    elif 3 in rank_counts.values():
        hand_value = 3
    # Two Pair
    elif list(rank_counts.values()).count(2) == 2:
        hand_value = 2
    # Pair
    elif 2 in rank_counts.values():
        hand_value = 1
    # High Card
    else:
        hand_value = 0
    
    # For tie-breaking, create a list of values in descending order of importance
    tie_breakers = []
    
    # Four of a Kind
    if hand_value == 7:
        for rank, count in rank_counts.items():
            if count == 4:
                tie_breakers.append(RANKS.index(rank))
    # Full House
    elif hand_value == 6:
        for rank, count in rank_counts.items():
            if count == 3:
                tie_breakers.append(RANKS.index(rank))
        for rank, count in rank_counts.items():
            if count == 2:
                tie_breakers.append(RANKS.index(rank))
    # Three of a Kind
    elif hand_value == 3:
        for rank, count in rank_counts.items():
            if count == 3:
                tie_breakers.append(RANKS.index(rank))
    # Two Pair or One Pair
    elif hand_value == 2 or hand_value == 1:
        pairs = []
        for rank, count in rank_counts.items():
            if count == 2:
                pairs.append(RANKS.index(rank))
        pairs.sort(reverse=True)
        tie_breakers.extend(pairs)
    
    # Add remaining cards as tie breakers
    sorted_values = sorted([RANKS.index(r) for r in ranks], reverse=True)
    for val in sorted_values:
        if val not in tie_breakers:
            tie_breakers.append(val)
    
    return hand_value, tie_breakers

# Function to get a description of the best hand
def get_hand_description(hand_value, best_hand):
    ranks = [card[0] for card in best_hand]
    rank_counts = {}
    for rank in ranks:
        if rank in rank_counts:
            rank_counts[rank] += 1
        else:
            rank_counts[rank] = 1
    
    rank_names = {
        '2': 'Deuce', '3': 'Three', '4': 'Four', '5': 'Five',
        '6': 'Six', '7': 'Seven', '8': 'Eight', '9': 'Nine',
        '10': 'Ten', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'
    }
    
    if hand_value == 9:  # Royal Flush
        suit = best_hand[0][1]
        return f"Royal Flush of {suit}"
    elif hand_value == 8:  # Straight Flush
        highest_card = max(best_hand, key=lambda x: RANKS.index(x[0]))
        suit = highest_card[1]
        return f"{rank_names[highest_card[0]]} High Straight Flush of {suit}"
    elif hand_value == 7:  # Four of a Kind
        four_rank = [r for r, c in rank_counts.items() if c == 4][0]
        kicker = [r for r, c in rank_counts.items() if c == 1][0]
        return f"Four {rank_names[four_rank]}s with {rank_names[kicker]} kicker"
    elif hand_value == 6:  # Full House
        three_rank = [r for r, c in rank_counts.items() if c == 3][0]
        two_rank = [r for r, c in rank_counts.items() if c == 2][0]
        return f"{rank_names[three_rank]}s full of {rank_names[two_rank]}s"
    elif hand_value == 5:  # Flush
        highest_card = max(best_hand, key=lambda x: RANKS.index(x[0]))
        suit = highest_card[1]
        return f"{rank_names[highest_card[0]]} High Flush of {suit}"
    elif hand_value == 4:  # Straight
        highest_card = max(best_hand, key=lambda x: RANKS.index(x[0]))
        return f"{rank_names[highest_card[0]]} High Straight"
    elif hand_value == 3:  # Three of a Kind
        three_rank = [r for r, c in rank_counts.items() if c == 3][0]
        return f"Three {rank_names[three_rank]}s"
    elif hand_value == 2:  # Two Pair
        pairs = [r for r, c in rank_counts.items() if c == 2]
        pairs.sort(key=lambda x: RANKS.index(x), reverse=True)
        return f"{rank_names[pairs[0]]}s and {rank_names[pairs[1]]}s"
    elif hand_value == 1:  # Pair
        pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
        return f"Pair of {rank_names[pair_rank]}s"
    else:  # High Card
        highest_card = max(best_hand, key=lambda x: RANKS.index(x[0]))
        return f"{rank_names[highest_card[0]]} High"

# Function to evaluate and get winner
def determine_winner():
    num_players = st.session_state.num_players
    community = [c for c in st.session_state.community_cards if c is not None]
    
    # Validate we have enough community cards
    if len(community) < 3:
        return "Need at least 3 community cards to determine a winner."
    
    player_hands = []
    
    # Get each player's hole cards
    for i in range(num_players):
        card1_idx = i * 2
        card2_idx = i * 2 + 1
        
        if card1_idx < len(st.session_state.player_cards) and card2_idx < len(st.session_state.player_cards):
            card1 = st.session_state.player_cards[card1_idx]
            card2 = st.session_state.player_cards[card2_idx]
            
            if card1 is not None and card2 is not None:
                player_hands.append((i+1, [card1, card2]))
    
    # Validate we have enough player hands
    if len(player_hands) < 2:
        return "Need at least 2 players with complete hands."
    
    results = []
    for player_num, hole_cards in player_hands:
        hand_value, best_hand = evaluate_hand(hole_cards, community)
        if hand_value >= 0:
            hand_type = HAND_RANKS[hand_value]
            hand_desc = get_hand_description(hand_value, best_hand)
            tie_breakers = evaluate_five_card_hand(best_hand)[1]
            
            # Get player name from session state (or use default if not found)
            player_name = st.session_state.player_names[player_num-1] if player_num-1 < len(st.session_state.player_names) else f"Player {player_num}"
            
            results.append({
                "player": player_num,
                "player_name": player_name,
                "hole_cards": hole_cards,
                "best_hand": best_hand,
                "hand_type": hand_type,
                "hand_desc": hand_desc,
                "hand_value": hand_value,
                "tie_breakers": tie_breakers
            })
    
    # Sort by hand value (descending) and tie breakers
    results.sort(key=lambda x: (x["hand_value"], x["tie_breakers"]), reverse=True)
    
    return results

def run():
    # Main app layout
    st.title("Poker Hand Evaluator")

    # Player selection
    st.sidebar.header("Game Settings")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        num_players = st.sidebar.slider("Number of Players", min_value=2, max_value=5, value=st.session_state.num_players)
        if num_players != st.session_state.num_players:
            # Adjust player names list if the number of players changes
            if num_players > st.session_state.num_players:
                # Add default names for new players
                for i in range(st.session_state.num_players, num_players):
                    st.session_state.player_names.append(f"Player {i+1}")
            else:
                # Truncate the list if reducing players
                st.session_state.player_names = st.session_state.player_names[:num_players]
                
            st.session_state.num_players = num_players
            st.session_state.results = None

    # Add player name inputs in the sidebar
    # st.sidebar.header("Player Names")
    # for i in range(st.session_state.num_players):
    #     # Initialize with default name if needed
    #     if i >= len(st.session_state.player_names):
    #         st.session_state.player_names.append(f"Player {i+1}")
            
    #     player_name = st.sidebar.text_input(
    #         f"Player {i+1} Name",
    #         value=st.session_state.player_names[i],
    #         key=f"player_name_{i}"
    #     )
    #     # Update the name in session state
    #     st.session_state.player_names[i] = player_name

    with col3:
        if st.button("Evaluate Winner", type="primary", use_container_width=True):
            st.session_state.results = determine_winner()

    # If we're currently editing a card
    if st.session_state.editing_card:
        card_type, index = st.session_state.editing_card
        already_selected = [card for card in st.session_state.community_cards + st.session_state.player_cards if card is not None]
        
        selected_card = card_selector(f"edit_{card_type}_{index}", already_selected)
        
        if selected_card:
            add_card_at_index(card_type, index, selected_card)
            st.session_state.editing_card = None
            st.rerun()  # Refresh the page
        
        if st.button("Cancel"):
            st.session_state.editing_card = None
            st.rerun()

    else:
        # Display community cards
        st.subheader("Community Cards")
        community_cols = st.columns(5)
        
        for i in range(5):
            with community_cols[i]:
                if i < len(st.session_state.community_cards) and st.session_state.community_cards[i]:
                    rank, suit = st.session_state.community_cards[i]
                    st.markdown(render_card(rank, suit), unsafe_allow_html=True)
                    
                    # Use columns with better spacing
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_comm_{i}", use_container_width=True):
                            st.session_state.editing_card = ("community", i)
                            st.rerun()
                    with col2:
                        if st.button("❌", key=f"remove_comm_{i}", use_container_width=True):
                            remove_card("community", i)
                            st.rerun()
                else:
                    if st.button("➕ Add Card", key=f"add_comm_{i}", use_container_width=True):
                        st.session_state.editing_card = ("community", i)
                        st.rerun()
        
        # Display player cards with names
        for player in range(1, st.session_state.num_players + 1):
            # Get player name from session state
            player_name = st.session_state.player_names[player-1] if player-1 < len(st.session_state.player_names) else f"Player {player}"
            
            st.subheader(f"{player_name}")
            player_cols = st.columns(5)
            
            for j in range(2):
                card_index = (player - 1) * 2 + j
                with player_cols[j]:
                    if card_index < len(st.session_state.player_cards) and st.session_state.player_cards[card_index]:
                        rank, suit = st.session_state.player_cards[card_index]
                        st.markdown(render_card(rank, suit), unsafe_allow_html=True)
                        
                        # Use columns with better spacing
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("✏️ Edit", key=f"edit_player_{card_index}", use_container_width=True):
                                st.session_state.editing_card = ("player", card_index)
                                st.rerun()
                        with col2:
                            if st.button("❌", key=f"remove_player_{card_index}", use_container_width=True):
                                remove_card("player", card_index)
                                st.rerun()
                    else:
                        if st.button("➕ Add Card", key=f"add_player_{card_index}", use_container_width=True):
                            st.session_state.editing_card = ("player", card_index)
                            st.rerun()
        
        # Display results
        if isinstance(st.session_state.results, str):
            st.warning(st.session_state.results)
        elif isinstance(st.session_state.results, list) and len(st.session_state.results) > 0:
            st.subheader("Results")
            
            # Display winner first
            winner = st.session_state.results[0]
            
            # Create a styled container for the winner announcement
            st.markdown(
                f"""
                <div style="padding:15px;background-color:#f0f8ff;border-radius:5px;margin-bottom:20px;border-left:5px solid #4169e1;">
                    <h3 style="margin:0;color:#4169e1;">🏆 Winner: {winner['player_name']}</h3>
                    <p style="margin:5px 0 0 0;font-size:18px;"><strong>{winner['hand_type']}:</strong> {winner['hand_desc']}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Create DataFrames for the results table (more intuitive visualization)
            data = []
            for result in st.session_state.results:
                player_num = result["player"]
                player_name = result["player_name"]
                hand_type = result["hand_type"]
                hand_desc = result["hand_desc"]
                
                # Mark the winner
                is_winner = result == winner
                player_label = f"{player_name} {'👑' if is_winner else ''}"
                
                data.append({
                    "Player": player_label,
                    "Hand Type": hand_type,
                    "Description": hand_desc,
                    "Rank": len(HAND_RANKS) - result["hand_value"],  # Convert to 1-10 scale where 1 is best
                })
            
            # Display the results table
            df = pd.DataFrame(data)
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}), hide_index=True, use_container_width=True)
            
            # Show each player's best hand with card visuals
            st.subheader("Best Hands")
            
            for result in st.session_state.results:
                player_name = result["player_name"]
                best_hand = result["best_hand"]
                hand_type = result["hand_type"]
                
                # Create a styled card display for each player's best hand
                st.markdown(
                    f"""
                    <div style="margin-bottom:15px;padding:10px;border:1px solid #ddd;border-radius:5px;">
                        <h4 style="margin:0 0 10px 0;">{player_name} - {hand_type}</h4>
                        {render_card_row(best_hand)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            # Show the community cards that were used
            community = [c for c in st.session_state.community_cards if c is not None]
            st.markdown(
                f"""
                <div style="margin-top:20px;padding:10px;border:1px solid #ddd;border-radius:5px;background-color:#f5f5f5;">
                    <h4 style="margin:0 0 10px 0;">Community Cards</h4>
                    {render_card_row(community)}
                </div>
                """,
                unsafe_allow_html=True
            )