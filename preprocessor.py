import pandas as pd

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure the 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Filter out rows where 'date' could not be parsed
    df = df.dropna(subset=['date'])

    # Extract additional columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.strftime('%B')
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.strftime('%A')
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Determine the period (hour-hour+1 format)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period
    
    return df