import pandas as pd
import numpy as np

def clean_premier_league_data():
    # Read the CSV file with UTF-8 encoding
    df = pd.read_csv('premier_league_teams.csv', encoding='utf-8')
    
    # Select only essential columns
    essential_columns = [
        'Rank',
        'Team',
        'Matches Played',
        'Wins',
        'Draws',
        'Losses',
        'Goals For',
        'Goals Against',
        'Goal Difference',
        'Points',
        'Points/Match',
        'Attendance',
        'Top Team Scorer',
        'Goalkeeper'
    ]
    
    # Keep only essential columns
    df = df[essential_columns]
    
    # Convert numeric columns to appropriate types
    numeric_columns = [
        'Rank',
        'Matches Played',
        'Wins',
        'Draws',
        'Losses',
        'Goals For',
        'Goals Against',
        'Points',
        'Points/Match',
        'Attendance'
    ]
    
    for col in numeric_columns:
        # First convert to string to handle any special characters
        df[col] = df[col].astype(str)
        # Remove any non-numeric characters
        df[col] = df[col].str.replace(',', '').str.replace('+', '')
        # Convert to numeric, coercing errors to NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Handle missing values
    df = df.fillna({
        'Matches Played': 0,
        'Wins': 0,
        'Draws': 0,
        'Losses': 0,
        'Goals For': 0,
        'Goals Against': 0,
        'Points': 0,
        'Points/Match': 0,
        'Attendance': 0
    })
    
    # Clean team names
    df['Team'] = df['Team'].astype(str).str.strip()
    
    # Clean player names
    df['Top Team Scorer'] = df['Top Team Scorer'].astype(str).str.strip()
    df['Goalkeeper'] = df['Goalkeeper'].astype(str).str.strip()
    
    # Remove any rows where team name is missing or empty
    df = df[df['Team'].str.strip() != '']
    
    # Sort by rank
    df = df.sort_values('Rank')
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Save cleaned data with UTF-8 encoding
    df.to_csv('premier_league_teams_cleaned.csv', index=False, encoding='utf-8-sig')
    
    # Print summary statistics
    print("\nData Cleaning Summary:")
    print(f"Total teams: {len(df)}")
    print("\nBasic Statistics:")
    print(df[['Points', 'Goals For', 'Goals Against', 'Attendance']].describe())
    
    return df

if __name__ == "__main__":
    cleaned_data = clean_premier_league_data()
    print("\nFirst few rows of cleaned data:")
    print(cleaned_data.head()) 