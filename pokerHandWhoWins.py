import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import itertools
import random

# Set page title and configuration

# Define card suits and ranks
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
SUIT_SYMBOLS = {'Hearts': '♥️', 'Diamonds': '♦️', 'Clubs': '♣️', 'Spades': '♠️'}
SUIT_COLORS = {'Hearts': 'red', 'Diamonds': 'red', 'Clubs': 'black', 'Spades': 'black'}
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUES = {r: i for i, r in enumerate(RANKS)}

# Create a full deck of cards
DECK = [(r, s) for r in RANKS for s in SUITS]

# Define hand rankings
HAND_RANKINGS = {
    9: "Royal Flush",
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card"
}

# Define hand rankings for sorting
HAND_RANKING_VALUES = {v: k for k, v in HAND_RANKINGS.items()}

# Function to calculate hand values (unchanged)
def evaluate_hand(cards):
    # [Keeping the original evaluate_hand function as it is]
    if len(cards) < 5:
        return 0, "Not enough cards", []
    
    ranks = [c[0] for c in cards]
    suits = [c[1] for c in cards]
    rank_values = [RANK_VALUES[r] for r in ranks]
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    
    # Check for flush
    is_flush = max(suit_counts.values()) >= 5
    flush_suit = max(suit_counts.items(), key=lambda x: x[1])[0] if is_flush else None
    
    # Check for straight
    sorted_values = sorted(set(rank_values))
    is_straight = False
    straight_high = None
    
    # Handle Ace low straight
    if set([0, 1, 2, 3, 12]).issubset(set(rank_values)):
        is_straight = True
        straight_high = 3  # 5 high
    
    # Check normal straights
    for i in range(len(sorted_values) - 4):
        if sorted_values[i:i+5] == list(range(sorted_values[i], sorted_values[i] + 5)):
            is_straight = True
            straight_high = sorted_values[i+4]
    
    # Get best 5 card combination
    best_hand = []
    
    # Royal Flush
    if is_flush and is_straight and 12 in rank_values and straight_high == 12:
        return 9, "Royal Flush", [c for c in cards if c[1] == flush_suit and RANK_VALUES[c[0]] >= 8][:5]
    
    # Straight Flush
    if is_flush and is_straight:
        flush_cards = [c for c in cards if c[1] == flush_suit]
        flush_values = [RANK_VALUES[c[0]] for c in flush_cards]
        # Check for A-5 straight flush
        if set([0, 1, 2, 3, 12]).issubset(set(flush_values)):
            return 8, "Straight Flush (5 high)", sorted([c for c in flush_cards if RANK_VALUES[c[0]] in [0, 1, 2, 3, 12]], 
                                                       key=lambda x: (RANK_VALUES[x[0]] if RANK_VALUES[x[0]] != 12 else -1))
        
        # Check normal straight flushes
        straight_flush_cards = []
        for i in range(len(sorted(flush_values)) - 4):
            if sorted(flush_values)[i:i+5] == list(range(sorted(flush_values)[i], sorted(flush_values)[i] + 5)):
                straight_flush_cards = [c for c in flush_cards if RANK_VALUES[c[0]] in range(sorted(flush_values)[i], sorted(flush_values)[i] + 5)]
                return 8, f"Straight Flush ({RANKS[sorted(flush_values)[i+4]]} high)", straight_flush_cards

    # Four of a Kind
    if 4 in rank_counts.values():
        quads_rank = [r for r, count in rank_counts.items() if count == 4][0]
        quads = [c for c in cards if c[0] == quads_rank]
        kickers = [c for c in cards if c[0] != quads_rank]
        kickers.sort(key=lambda x: RANK_VALUES[x[0]], reverse=True)
        return 7, f"Four of a Kind ({quads_rank}s)", quads + [kickers[0]]
    
    # Full House
    if 3 in rank_counts.values() and 2 in rank_counts.values():
        trips_rank = [r for r, count in rank_counts.items() if count == 3][0]
        pair_ranks = [r for r, count in rank_counts.items() if count == 2]
        trips = [c for c in cards if c[0] == trips_rank]
        pairs = [c for c in cards if c[0] == pair_ranks[0]]
        return 6, f"Full House ({trips_rank}s over {pair_ranks[0]}s)", trips + pairs[:2]
    
    # Check for trips with two pairs
    if 3 in rank_counts.values() and len([r for r, count in rank_counts.items() if count == 2]) >= 2:
        trips_rank = [r for r, count in rank_counts.items() if count == 3][0]
        pair_ranks = [r for r, count in rank_counts.items() if count == 2]
        pair_ranks.sort(key=lambda x: RANK_VALUES[x], reverse=True)
        trips = [c for c in cards if c[0] == trips_rank]
        best_pair = [c for c in cards if c[0] == pair_ranks[0]]
        return 6, f"Full House ({trips_rank}s over {pair_ranks[0]}s)", trips + best_pair[:2]
    
    # Flush
    if is_flush:
        flush_cards = [c for c in cards if c[1] == flush_suit]
        flush_cards.sort(key=lambda x: RANK_VALUES[x[0]], reverse=True)
        return 5, f"Flush ({flush_cards[0][0]} high)", flush_cards[:5]
    
    # Straight
    if is_straight:
        if set([0, 1, 2, 3, 12]).issubset(set(rank_values)):
            # A-5 straight
            return 4, "Straight (5 high)", sorted([c for c in cards if RANK_VALUES[c[0]] in [0, 1, 2, 3, 12]], 
                                                key=lambda x: (RANK_VALUES[x[0]] if RANK_VALUES[x[0]] != 12 else -1))
        else:
            # Normal straight
            high_rank = RANKS[straight_high]
            straight_cards = []
            needed_values = list(range(straight_high - 4, straight_high + 1))
            for val in needed_values:
                for card in cards:
                    if RANK_VALUES[card[0]] == val and card not in straight_cards:
                        straight_cards.append(card)
                        break
            return 4, f"Straight ({high_rank} high)", straight_cards
    
    # Three of a Kind
    if 3 in rank_counts.values():
        trips_rank = [r for r, count in rank_counts.items() if count == 3][0]
        trips = [c for c in cards if c[0] == trips_rank]
        kickers = [c for c in cards if c[0] != trips_rank]
        kickers.sort(key=lambda x: RANK_VALUES[x[0]], reverse=True)
        return 3, f"Three of a Kind ({trips_rank}s)", trips + kickers[:2]
    
    # Two Pair
    if len([r for r, count in rank_counts.items() if count >= 2]) >= 2:
        pair_ranks = [r for r, count in rank_counts.items() if count >= 2]
        pair_ranks.sort(key=lambda x: RANK_VALUES[x], reverse=True)
        first_pair = [c for c in cards if c[0] == pair_ranks[0]]
        second_pair = [c for c in cards if c[0] == pair_ranks[1]]
        kickers = [c for c in cards if c[0] not in [pair_ranks[0], pair_ranks[1]]]
        kickers.sort(key=lambda x: RANK_VALUES[x[0]], reverse=True)
        return 2, f"Two Pair ({pair_ranks[0]}s and {pair_ranks[1]}s)", first_pair[:2] + second_pair[:2] + [kickers[0]]
    
    # One Pair
    if 2 in rank_counts.values():
        pair_rank = [r for r, count in rank_counts.items() if count == 2][0]
        pair = [c for c in cards if c[0] == pair_rank]
        kickers = [c for c in cards if c[0] != pair_rank]
        kickers.sort(key=lambda x: RANK_VALUES[x[0]], reverse=True)
        return 1, f"One Pair ({pair_rank}s)", pair + kickers[:3]
    
    # High Card
    cards_sorted = sorted(cards, key=lambda x: RANK_VALUES[x[0]], reverse=True)
    return 0, f"High Card ({cards_sorted[0][0]})", cards_sorted[:5]

# Function to find helpful cards (unchanged)
def find_helpful_cards(hole_cards, community_cards):
    # [Keeping the original find_helpful_cards function as it is]
    combined_cards = hole_cards + community_cards
    
    # Current hand value
    current_value, current_name, _ = evaluate_hand(combined_cards)
    
    # Remaining cards in the deck
    remaining_cards = [card for card in DECK if card not in combined_cards]
    
    # Dictionary to store helpful cards by improvement
    helpful_cards = {}
    
    # Check each possible next card
    for next_card in remaining_cards:
        new_community = community_cards + [next_card]
        new_hand = hole_cards + new_community
        new_value, new_name, _ = evaluate_hand(new_hand)
        
        # If the hand improves
        if new_value > current_value:
            if new_name not in helpful_cards:
                helpful_cards[new_name] = []
            helpful_cards[new_name].append(next_card)
    
    return helpful_cards, current_value, current_name

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
            col_offset = 0
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

# Detect if we're on a mobile device
def is_mobile():
    try:
        # Get viewport width using JavaScript
        viewport_width = st.query_params().get('vw', ['1000'])[0]
        return int(viewport_width) < 768
    except:
        # Default to desktop if we can't detect
        return False
def run():
    # Add custom CSS for responsiveness
    st.markdown("""
    <style>
        /* Responsive containers */
        .responsive-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-start;
            align-items: flex-start;
        }
        
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        /* Card selection grid */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            gap: 5px;
        }
        
        .card-button {
            width: 100%;
            aspect-ratio: 2/3;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        /* Ensure select boxes don't overflow on mobile */
        .stSelectbox {
            max-width: 100%;
            overflow: hidden;
        }
        
        /* Mobile-specific styles */
        @media (max-width: 768px) {
            .mobile-full-width {
                width: 100% !important;
                flex-basis: 100% !important;
                max-width: 100% !important;
            }
            
            .mobile-centered {
                text-align: center;
            }
            
            .mobile-smaller-text {
                font-size: 0.9rem !important;
            }
            
            /* Make cards wrap appropriately on mobile */
            .card-wrapper {
                display: inline-block;
                width: 45%;
                margin: 2%;
            }
        }
        
        /* Custom styling for the tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px;
            padding: 8px 16px;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #e3e7ed;
            font-weight: bold;
        }
        
        /* Card placeholder hover effect */
        .card-placeholder:hover {
            background-color: #f0f0f0;
            border-color: #999;
        }
    </style>
    """, unsafe_allow_html=True)

    # Streamlit app layout
    st.title("Single Player Poker Hand Analyzer")

    # Sidebar for configuration
    st.sidebar.header("Game Settings")
    num_community = st.sidebar.slider("Number of Community Cards", 0, 5, 3)

    # Flag for mobile detection
    mobile_view = is_mobile()

    # Initialize session state to track selected cards
    if 'community_cards' not in st.session_state:
        st.session_state.community_cards = []
    if 'player_cards' not in st.session_state:
        st.session_state.player_cards = []
    if 'editing_card' not in st.session_state:
        st.session_state.editing_card = None

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

    # Community Cards - improved visual layout
    # st.header("Community Cards")

    # Check if we're in editing mode
    if st.session_state.editing_card:
        card_type, index = st.session_state.editing_card
        already_selected = st.session_state.community_cards + st.session_state.player_cards
        already_selected = [card for card in already_selected if card is not None]
        
        selected_card = card_selector(f"edit_{card_type}_{index}", already_selected)
        
        if selected_card:
            add_card_at_index(card_type, index, selected_card)
            st.session_state.editing_card = None
            st.rerun()  # Refresh the page
        
        if st.button("Cancel"):
            st.session_state.editing_card = None
            st.rerun()
    else:
        # Visual card display for community cards
        st.subheader("Community Cards")
        community_cols = st.columns(5)
        
        # Ensure community_cards has enough slots
        while len(st.session_state.community_cards) < 5:
            st.session_state.community_cards.append(None)
        for i in range(5):
            with community_cols[i]:
                # Check if this position should have a card based on num_community
                if i < num_community:
                    if st.session_state.community_cards[i]:
                        # Display the card
                        rank, suit = st.session_state.community_cards[i]
                        st.markdown(render_card(rank, suit), unsafe_allow_html=True)
                        
                        # Better button styling with CSS
                        st.markdown("""
                        <style>
                        .button-row {
                            display: flex;
                            gap: 8px;
                            margin-top: 5px;
                        }
                        .edit-btn, .remove-btn {
                            flex: 1;
                            text-align: center;
                            padding: 3px 0;
                            border-radius: 4px;
                            font-size: 0.8em;
                            cursor: pointer;
                            transition: background-color 0.3s;
                        }
                        .edit-btn {
                            background-color: #f0f2f6;
                            border: 1px solid #ddd;
                            color: #262730;
                        }
                        .remove-btn {
                            background-color: #ff4b4b;
                            border: 1px solid #ff4b4b;
                            color: white;
                        }
                        .edit-btn:hover {
                            background-color: #e6e9ef;
                        }
                        .remove-btn:hover {
                            background-color: #ff3333;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Create a container for the buttons
                        button_container = st.container()
                        
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
                        # Display a placeholder "+" card with improved styling
                        st.markdown("""
                        <style>
                        .add-card-btn {
                            background-color: #f0f2f6;
                            border: 1px dashed #ddd;
                            border-radius: 8px;
                            color: #262730;
                            padding: 20px 0;
                            text-align: center;
                            cursor: pointer;
                            margin-top: 10px;
                            transition: background-color 0.3s;
                        }
                        .add-card-btn:hover {
                            background-color: #e6e9ef;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        if st.button("➕ Add Card", key=f"add_comm_{i}", use_container_width=True):
                            st.session_state.editing_card = ("community", i)
                            st.rerun()
                else:
                    st.markdown("##")
                    st.markdown("*No card*")
        
        # Player hand - improved visual layout
        st.subheader("Your Hand")
        player_cols = st.columns(5)
        
        # Ensure player_cards has enough slots
        while len(st.session_state.player_cards) < 2:
            st.session_state.player_cards.append(None)
        
        for i in range(2):
            with player_cols[i]:
                if st.session_state.player_cards[i]:
                    # Display the card
                    rank, suit = st.session_state.player_cards[i]
                    st.markdown(render_card(rank, suit), unsafe_allow_html=True)
                    
                    # Better button styling with CSS
                    st.markdown("""
                    <style>
                    .button-row {
                        display: flex;
                        gap: 8px;
                        margin-top: 5px;
                    }
                    .edit-btn, .remove-btn {
                        flex: 1;
                        text-align: center;
                        padding: 3px 0;
                        border-radius: 4px;
                        font-size: 0.8em;
                        cursor: pointer;
                        transition: background-color 0.3s;
                    }
                    .edit-btn {
                        background-color: #f0f2f6;
                        border: 1px solid #ddd;
                        color: #262730;
                    }
                    .remove-btn {
                        background-color: #ff4b4b;
                        border: 1px solid #ff4b4b;
                        color: white;
                    }
                    .edit-btn:hover {
                        background-color: #e6e9ef;
                    }
                    .remove-btn:hover {
                        background-color: #ff3333;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Create a container for the buttons
                    button_container = st.container()
                    
                    # Use columns with better spacing
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_player_{i}", use_container_width=True):
                            st.session_state.editing_card = ("player", i)
                            st.rerun()
                    with col2:
                        if st.button("❌", key=f"remove_player_{i}", use_container_width=True):
                            remove_card("player", i)
                            st.rerun()
                else:
                    # Display a placeholder "+" card with improved styling
                    st.markdown("""
                    <style>
                    .add-card-btn {
                        background-color: #f0f2f6;
                        border: 1px dashed #ddd;
                        border-radius: 8px;
                        color: #262730;
                        padding: 20px 0;
                        text-align: center;
                        cursor: pointer;
                        margin-top: 10px;
                        transition: background-color 0.3s;
                    }
                    .add-card-btn:hover {
                        background-color: #e6e9ef;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    if st.button("➕ Add Card", key=f"add_player_{i}", use_container_width=True):
                        st.session_state.editing_card = ("player", i)
                        st.rerun()
        
        # Clean up community cards list to remove None values
        community_cards = [card for card in st.session_state.community_cards if card is not None]
        player_cards = [card for card in st.session_state.player_cards if card is not None]
        
        all_cards = community_cards + player_cards
        
        # Check for duplicate cards
        if len(all_cards) != len(set(all_cards)):
            st.error("Duplicate cards detected! Please choose different cards.")
        elif all_cards:  # Only analyze if we have cards
            # Analyze hand
            st.header("Hand Analysis")
            
            # Current hand
            hand_value, hand_name, best_cards = evaluate_hand(player_cards + community_cards)
            st.subheader(f"Current Hand: {hand_name}")
            
            # Show best 5 cards if we have at least 5 cards
            if best_cards:
                st.markdown("**Best Five Cards:**")
                
                # Create a responsive container for cards
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                best_card_html = ""
                for card in best_cards:
                    rank, suit = card
                    card_width = 60 if mobile_view else 80
                    card_height = 90 if mobile_view else 120
                    font_size_rank = 16 if mobile_view else 20
                    font_size_suit = 24 if mobile_view else 36
                    margin_top = 10 if mobile_view else 15
                    
                    if mobile_view:
                        best_card_html += f'<div class="card-wrapper">{render_card(rank, suit, width=card_width, height=card_height, font_size_rank=font_size_rank, font_size_suit=font_size_suit, margin_top=margin_top)}</div>'
                    else:
                        best_card_html += render_card(rank, suit, width=card_width, height=card_height, font_size_rank=font_size_rank, font_size_suit=font_size_suit, margin_top=margin_top)
                        
                st.markdown(best_card_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Find and display helpful cards
            if num_community < 5:
                st.header("Potential Helpful Cards")
                
                helpful_cards, current_value, current_name = find_helpful_cards(player_cards, community_cards)
                
                # Sorting options
                sort_options = ["Hand Ranking (Best to Worst)", "Probability (Highest to Lowest)"]
                sort_method = st.radio("Sort potential hands by:", sort_options)
                
                if helpful_cards:
                    # Create a list to hold hand data for sorting
                    hand_data = []
                    remaining_cards_count = 52 - len(all_cards)
                    
                    for hand_name, cards in helpful_cards.items():
                        # Calculate ranking value
                        hand_type = hand_name.split(" (")[0]  # Extract hand type without high card info
                        hand_rank = HAND_RANKING_VALUES.get(hand_type, 0)
                        if not hand_rank and "Straight Flush" in hand_type:
                            hand_rank = 8
                        elif not hand_rank and "Flush" in hand_type:
                            hand_rank = 5
                        
                        # Calculate probability
                        probability = (len(cards) / remaining_cards_count) * 100
                        
                        # Add to data list
                        hand_data.append({
                            'hand_name': hand_name,
                            'cards': cards,
                            'rank': hand_rank,
                            'probability': probability,
                            'card_count': len(cards)
                        })
                    
                    # Sort based on user choice
                    if sort_method == "Hand Ranking (Best to Worst)":
                        sorted_hands = sorted(hand_data, key=lambda x: (x['rank'], x['probability']), reverse=True)
                    else:  # Probability
                        sorted_hands = sorted(hand_data, key=lambda x: x['probability'], reverse=True)
                    
                    # Display sorted hands
                    for hand_info in sorted_hands:
                        hand_name = hand_info['hand_name']
                        cards = hand_info['cards']
                        probability = hand_info['probability']
                        
                        with st.expander(f"{hand_name} - {len(cards)} possible cards ({probability:.2f}%)"):
                            # Create a responsive container for cards
                            st.markdown('<div class="card-container">', unsafe_allow_html=True)
                            cards_html = ""
                            
                            # Group cards by rank for cleaner display
                            cards_by_rank = {}
                            for card in cards:
                                rank, suit = card
                                if rank not in cards_by_rank:
                                    cards_by_rank[rank] = []
                                cards_by_rank[rank].append(suit)
                            
                            # Sort ranks by value
                            sorted_ranks = sorted(cards_by_rank.keys(), key=lambda r: RANK_VALUES[r], reverse=True)
                            
                            for rank in sorted_ranks:
                                suits = cards_by_rank[rank]
                                # Sort suits for consistency
                                suits.sort()
                                for suit in suits:
                                    card_width = 60 if mobile_view else 80
                                    card_height = 90 if mobile_view else 120
                                    font_size_rank = 16 if mobile_view else 20
                                    font_size_suit = 24 if mobile_view else 36
                                    margin_top = 10 if mobile_view else 15
                                    
                                    if mobile_view:
                                        cards_html += f'<div class="card-wrapper">{render_card(rank, suit, width=card_width, height=card_height, font_size_rank=font_size_rank, font_size_suit=font_size_suit, margin_top=margin_top)}</div>'
                                    else:
                                        cards_html += render_card(rank, suit, width=card_width, height=card_height, font_size_rank=font_size_rank, font_size_suit=font_size_suit, margin_top=margin_top)
                            
                            st.markdown(cards_html, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Show probability details
                            st.markdown(f"**Probability:** {probability:.2f}% ({len(cards)} out of {remaining_cards_count} remaining cards)")
                else:
                    st.write("No cards in the deck will improve your current hand.")
            
            # Calculate outs and odds
            if num_community < 5:
                st.header("Outs and Odds")
                
                total_outs = sum(len(cards) for cards in helpful_cards.values())
                remaining_cards = 52 - len(all_cards)
                
                # Calculate probability based on remaining community cards
                cards_to_come = 5 - num_community
                
                if cards_to_come == 1:
                    probability = total_outs / remaining_cards
                    st.write(f"**Total Outs:** {total_outs}")
                    st.write(f"**Odds of Improving:** {probability*100:.2f}% (roughly {int(1/probability - 1) if probability > 0 else 'N/A'}-to-1)")
                elif cards_to_come == 2:
                    # Probability of hitting on either card
                    probability = 1 - ((remaining_cards - total_outs) / remaining_cards) * ((remaining_cards - total_outs - 1) / (remaining_cards - 1))
                    st.write(f"**Total Outs:** {total_outs}")
                    st.write(f"**Odds of Improving:** {probability*100:.2f}% with 2 cards to come")

    # Add hand rankings reference
    # with st.expander("Poker Hand Rankings Reference"):
    #     st.markdown("""
    #     1. **Royal Flush**: A, K, Q, J, 10, all the same suit
    #     2. **Straight Flush**: Five cards in a sequence, all in the same suit
    #     3. **Four of a Kind**: Four cards of the same rank
    # with st.expander("Poker Hand Rankings Reference"):
    #     st.markdown("""
    #     1. **Royal Flush**: A, K, Q, J, 10, all the same suit
    #     2. **Straight Flush**: Five cards in a sequence, all in the same suit
    #     3. **Four of a Kind**: Four cards of the same rank
    #     4. **Full House**: Three of a kind with a pair
    #     5. **Flush**: Any five cards of the same suit, not in sequence
    #     6. **Straight**: Five cards in a sequence, not of the same suit
    #     7. **Three of a Kind**: Three cards of the same rank
    #     8. **Two Pair**: Two different pairs
    #     9. **One Pair**: Two cards of the same rank
    #     10. **High Card**: Highest card wins if nobody has any of the above
    #     """)
