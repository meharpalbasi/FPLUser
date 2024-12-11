import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import fetch_players, fetch_transfers, fetch_history
from func.utils import donate_message


def plot_total_points_over_weeks(df_history):
    """
    Plots the total points over weeks using Plotly.

    Args:
        df_history (pd.DataFrame): DataFrame containing performance history.
    """
    if 'Gameweek' in df_history.columns and 'Total Points' in df_history.columns:
        # Sort by gameweek
        df_history_sorted = df_history.sort_values(by='Gameweek')
        fig = px.line(df_history_sorted, x='Gameweek', y='Total Points', markers=True,
                      title='Total Points Over Gameweeks',
                      labels={'Gameweek': 'Gameweek', 'Total Points': 'TotalPoints'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("'event' or 'points' columns not found for plotting total points over weeks.")

def plot_rank_over_weeks(df_history):
    """
    Plots the rank over weeks using Plotly.

    Args:
        df_history (pd.DataFrame): DataFrame containing performance history.
    """
    if 'Gameweek' in df_history.columns and 'Rank' in df_history.columns:
        # Sort by gameweek
        df_history_sorted = df_history.sort_values(by='Gameweek')
        fig = px.line(
            df_history_sorted,
            x='Gameweek',
            y='Rank',
            markers=True,
            title='Rank Over Gameweeks',
            labels={'Gameweek': 'Gameweek', 'Rank': 'Rank'}
        )
        # Reverse the y-axis so that lower ranks appear higher
        fig.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("'Gameweek' or 'Rank' columns not found for plotting rank over weeks.")


def plot_transfers_per_gameweek(df_transfers):
    """
    Plots the number of transfers per gameweek using Plotly.

    Args:
        df_transfers (pd.DataFrame): DataFrame containing transfer history.
    """
    if 'Gameweek' in df_transfers.columns:
        transfers_per_gw = df_transfers.groupby('Gameweek').size().reset_index(name='Number of Transfers')
        fig = px.bar(transfers_per_gw, x='Gameweek', y='Number of Transfers',
                     title='Number of Transfers per Gameweek',
                     labels={'Gameweek': 'Gameweek', 'Number of Transfers': 'Transfers'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("'Gameweek' column not found for plotting transfers per gameweek.")

def plot_players_in_out(df_transfers):
    """
    Plots the number of players transferred in and out using Plotly.

    Args:
        df_transfers (pd.DataFrame): DataFrame containing transfer history.
    """
    if 'Player In' in df_transfers.columns and 'Player Out' in df_transfers.columns:
        players_in = df_transfers['Player In'].value_counts().reset_index()
        players_in.columns = ['Player', 'Transfers In']

        players_out = df_transfers['Player Out'].value_counts().reset_index()
        players_out.columns = ['Player', 'Transfers Out']

        # Merge in and out counts
        players_summary = pd.merge(players_in, players_out, on='Player', how='outer').fillna(0)
        players_summary['Transfers In'] = players_summary['Transfers In'].astype(int)
        players_summary['Transfers Out'] = players_summary['Transfers Out'].astype(int)

        # Select top 10 players by transfers in
        top_players = players_summary.sort_values(by='Transfers In', ascending=False).head(10)

        fig = px.bar(top_players, x='Player', y=['Transfers In', 'Transfers Out'],
                     title='Top 10 Players Transferred In and Out',
                     labels={'value': 'Number of Transfers', 'variable': 'Transfer Type'},
                     barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("'Player In' or 'Player Out' columns not found for plotting players in/out.")

def main():
    st.set_page_config(
        page_title="FPL Team Analyzer",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Fantasy Premier League Team Analyzer")
    st.write("""
        Welcome to the **Fantasy Premier League Team Analyzer**! 
        Enter your Team ID to view your transfer history and performance across gameweeks.
    """)

    # Input for Team ID in the sidebar for better layout
    TID = st.sidebar.text_input("Enter your Team ID (e.g., 7108828):", "")

    if TID:
        if TID.isdigit():
            try:
                # Fetch player data once as it's used in both tabs
                with st.spinner('Fetching player data...'):
                    player_id_to_name = fetch_players()
            except RuntimeError as e:
                st.error(e)
                st.stop()  # Exit the app if fetching players failed

            # Create Tabs for Transfer and History
            tabs = st.tabs(["Transfer History", "Performance History"])

            # Tab 1: Transfer History
            with tabs[0]:
                st.header("Your Transfer History")
                try:
                    transfers_data = fetch_transfers(TID)
                except RuntimeError as e:
                    st.error(e)
                    transfers_data = None

                if transfers_data is not None and not transfers_data.empty:
                    # Map player names
                    if 'element_in' in transfers_data.columns and 'element_out' in transfers_data.columns:
                        transfers_data['Player In'] = transfers_data['element_in'].map(player_id_to_name)
                        transfers_data['Player Out'] = transfers_data['element_out'].map(player_id_to_name)
                    else:
                        st.warning("Transfer data does not contain expected player ID columns.")

                    # Drop original ID columns if they exist
                    if 'element_in' in transfers_data.columns and 'element_out' in transfers_data.columns:
                        transfers_data = transfers_data.drop(['element_in', 'element_out'], axis=1)

                    # Select desired columns
                    desired_columns = ['Player In', 'Player Out', 'entry', 'event', 'time']
                    available_columns = [col for col in desired_columns if col in transfers_data.columns]
                    missing_columns = set(desired_columns) - set(available_columns)

                    if missing_columns:
                        st.warning(f"The following columns are missing and will be excluded: {missing_columns}")

                    # Select and rename columns
                    transfers_data = transfers_data[available_columns]
                    transfers_data = transfers_data.rename(columns={
                        'entry': 'Team ID',
                        'event': 'Gameweek',
                        'time': 'Transfer Time'
                    })

                    # Handle missing 'Transfer Time'
                    if 'Transfer Time' in transfers_data.columns:
                        transfers_data['Transfer Time'] = pd.to_datetime(transfers_data['Transfer Time'], errors='coerce')

                    # Sort by Transfer Time descending
                    if 'Transfer Time' in transfers_data.columns:
                        transfers_data = transfers_data.sort_values(by='Transfer Time', ascending=False).reset_index(drop=True)

                    # Display the DataFrame
                    st.dataframe(transfers_data, use_container_width=True)

                    # Plot Transfers Per Gameweek
                    st.subheader("Transfers Per Gameweek")
                    plot_transfers_per_gameweek(transfers_data)

                    # Plot Players In vs Out
                    st.subheader("Players Transferred In vs Out")
                    plot_players_in_out(transfers_data)

                    # Optional: Add a download button
                    csv_transfers = transfers_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Transfer History as CSV",
                        data=csv_transfers,
                        file_name='fpl_transfer_history.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No transfer data available for this Team ID.")

            # Tab 2: Performance History
            with tabs[1]:
                st.header("Your Performance History")
                try:
                    history_data = fetch_history(TID)
                except RuntimeError as e:
                    st.error(e)
                    history_data = None

                if history_data is not None and not history_data.empty:
                    # Rename columns based on availability
                    rename_columns = {}
                    if 'season_name' in history_data.columns:
                            rename_columns['season_name'] = 'Season'
                    if 'overall_rank' in history_data.columns:
                            rename_columns['overall_rank'] = 'Overall Rank'
                    if 'rank' in history_data.columns:
                            rename_columns['rank'] = 'Rank'
                    if 'total_points' in history_data.columns:
                            rename_columns['total_points'] = 'Total Points'
                    if 'bank' in history_data.columns:
                            rename_columns['bank'] = 'Bank'
                    if 'points' in history_data.columns:
                            rename_columns['points'] = 'Points'
                    if 'event_transfers' in history_data.columns:
                            rename_columns['event_transfers'] = 'Transfers'
                    if 'event_transfers_cost' in history_data.columns:
                            rename_columns['event_transfers_cost'] = 'Transfers Cost'
                    if 'points_on_bench' in history_data.columns:
                            rename_columns['points_on_bench'] = 'Bench Points'
                    if 'event' in history_data.columns:
                            rename_columns['event'] = 'Gameweek'

                    history_data = history_data.rename(columns=rename_columns)

                    # Select desired columns
                    desired_history_columns = ['Gameweek','Overall Rank', 'Rank', 'Points', 'Total Points', 'Bank', 'Transfers', 'Transfers Cost', 'Bench Points']
                    available_history_columns = [col for col in desired_history_columns if col in history_data.columns]
                    missing_history_columns = set(desired_history_columns) - set(available_history_columns)

                    if missing_history_columns:
                        st.warning(f"The following history columns are missing and will be excluded: {missing_history_columns}")

                    # Select available columns
                    history_data = history_data[available_history_columns]

                    # Sort by Gameweek ascending
                    if 'Gameweek' in history_data.columns:
                        history_data = history_data.sort_values(by='Gameweek', ascending=True).reset_index(drop=True)

                    # Display the DataFrame
                    st.dataframe(history_data, use_container_width=True)

                    # Plot Total Points Over Weeks
                    st.subheader("Total Points Over Gameweeks")
                    plot_total_points_over_weeks(history_data)

                    # Plot Rank Over Weeks
                    st.subheader("Rank Over Gameweeks")
                    plot_rank_over_weeks(history_data)

                    # Optional: Add a download button
                    csv_history = history_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Performance History as CSV",
                        data=csv_history,
                        file_name='fpl_performance_history.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No performance history data available for this Team ID.")
        else:
            st.info("Please enter your Team ID to proceed.")

    st.divider()
    donate_message()

if __name__ == "__main__":
    main()
