import pandas as pd
import datetime

raw_dir = "../data/raw/"
TRAINING_FILE = f"{raw_dir}training.xlsx"
WEIGHT_FILE = f"{raw_dir}cronometer_weight.csv"
SLEEP_FILE = f"{raw_dir}cronometer_sleep.csv"
HR_FILE = f"{raw_dir}cronometer_heartrate.csv"
FOOD_FILE = f"{raw_dir}cronometer_food.csv"
BF_FILE = f"{raw_dir}cronometer_bodyfat.csv"


def _clean_cols(df):
    """Standardize column names: lowercase, strip whitespace, spaces -> underscores."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
    )
    return df


def _to_seconds_if_time(x):
    """Convert datetime.time / Timedelta to seconds; pass numbers through unchanged."""
    if isinstance(x, datetime.time):
        return x.hour * 3600 + x.minute * 60 + x.second
    if hasattr(x, "total_seconds"):
        return x.total_seconds()
    return x


def validate_duration_s(df, id_col="mobility_id"):
    """Raise an error listing rows where duration_s isn't a plain number."""
    bad = df[~df["duration_s"].apply(lambda x: isinstance(x, (int, float)))]
    if not bad.empty:
        raise ValueError(
            f"duration_s must be numeric (seconds). Bad rows ({id_col}): "
            f"{bad[id_col].tolist()} -> values: {bad['duration_s'].tolist()}"
        )


def load_sessions(file=TRAINING_FILE):
    df = pd.read_excel(file, sheet_name="sessions")
    df = _clean_cols(df).dropna(how="all")

    # Explicitly set data types
    df["session_id"] = df["session_id"].astype("string")
    df["date"] = pd.to_datetime(df["date"])
    df["session_type"] = df["session_type"].astype("string")
    df["notes"] = df["notes"].astype("string")

    return df[["session_id", "date", "session_type", "notes"]]


def load_strength_log(file=TRAINING_FILE):
    df = pd.read_excel(file, sheet_name="strength_log")
    df = _clean_cols(df).dropna(subset=["set_id"])
    df = df.rename(columns={"exercise_name": "exercise_name"})

    # Explicitly set data types
    df["set_id"] = df["set_id"].astype("Int64")
    df["session_id"] = df["session_id"].astype("string")
    df["exercise_name"] = df["exercise_name"].astype("string")
    df["exercise_id"] = df["exercise_id"].astype("string")
    df["load_kg"] = df["load_kg"].astype("float")
    df["reps"] = df["reps"].astype("Int64")
    df["rpe"] = df["rpe"].astype("float")
    df["e1rm"] = df["e1rm"].astype("float")

    # normalize exercise names for matching against the lookup table
    df["exercise_name"] = df["exercise_name"].str.strip().str.lower()


    return df[["set_id", "session_id", "exercise_id",
               "load_kg", "reps", "rpe", "e1rm"]]


def load_cardio_log(file=TRAINING_FILE):
    df = pd.read_excel(file, sheet_name="cardio_log")
    df = _clean_cols(df).dropna(subset=["cardio_id"])

    df["duration_s"] = df["duration_min"].apply(_to_seconds_if_time)
    df = df.drop(columns=["duration_min"])

    
    df["cardio_id"] = df["cardio_id"].astype("Int64")
    df["session_id"] = df["session_id"].astype("string")
    df["duration_s"] = df["duration_s"].astype("Int64")
    df["distance_km"] = df["distance_km"].astype("float")
    df["avg_hr"] = df["avg_hr"].astype("Int64")
    df["rpe"] = df["rpe"].astype("float")

    return df[["cardio_id", "session_id",
               "duration_s", "distance_km", "avg_hr", "rpe"]]


def load_mobility_log(file=TRAINING_FILE, auto_fix=False):
    df = pd.read_excel(file, sheet_name="mobility_log")
    df = _clean_cols(df).dropna(subset=["mobility_id"])

    # check that duration_s is in the right format, if not fix it
    if auto_fix:
        df["duration_s"] = df["duration_s"].apply(_to_seconds_if_time)
    else:
        validate_duration_s(df)

    df["duration_s"] = pd.to_numeric(df["duration_s"])

    # Explicitly set data types
    df["mobility_id"] = df["mobility_id"].astype("Int64")
    df["session_id"] = df["session_id"].astype("string")
    df["exercise_id"] = df["exercise_id"].astype("string")
    df["reps"] = df["reps"].astype("Int64")
    df["duration_s"] = df["duration_s"].astype("Int64")
    df["rpe"] = df["rpe"].astype("float")

    return df[["mobility_id", "session_id", "exercise_id", "reps", "duration_s", "rpe"]]


def load_exercise_lookup(file=TRAINING_FILE):
    df = pd.read_excel(file, sheet_name="exercise_type")
    df = _clean_cols(df).dropna(how="all")

    df["exercise_id"] = df["exercise_id"].astype("string")
    df["exercise_name"] = df["exercise_name"].astype("string").str.strip().str.lower()
    df["movement_pattern"] = df["movement_pattern"].astype("string")

    # split + explode multi-muscle entries (e.g. "hamstring, back, glute")
    # df["muscle_group"] = df["muscle_group"].astype("string").str.split(",")
    # df = df.explode("muscle_group")
    df["muscle_group"] = df["muscle_group"].str.strip().str.lower()

    return df[["exercise_id", "exercise_name", "movement_pattern", "muscle_group"]].reset_index(drop=True)


def load_weight(file=WEIGHT_FILE):
    df = pd.read_csv(file)
    df = _clean_cols(df).dropna(how="all")
    
    df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M:%S").dt.date
    df["weight"] = df["weight"].astype("float")

    df.rename(columns={"weight": "weight_kg", "datetime": "date"}, inplace=True)
    df.drop(columns=["fasting"], inplace=True)

    return df


def load_sleep(file=SLEEP_FILE):
    df = pd.read_csv(file)
    df = _clean_cols(df).dropna(how="all")

    df["datetime"] = pd.to_datetime(df["datetime"], format="%d/%m/%Y %H:%M").dt.date
    df["sleep"] = df["sleep"].astype("float")
    
    df.rename(columns={"sleep": "sleep_hr", "datetime": "date"}, inplace=True)
    df.drop(columns=["fasting"], inplace=True)

    return df


def load_hr(file=HR_FILE):
    df = pd.read_csv(file, dayfirst=True)
    df = _clean_cols(df).dropna(how="all")

    df["datetime"] = pd.to_datetime(df["datetime"], format="%d/%m/%Y %H:%M").dt.date
    df["heart_rate"] = df["heart_rate"].astype("Int64")
    
    df.rename(columns={"datetime": "date", "heart_rate": "hr_bpm"}, inplace=True)
    df.drop(columns=["fasting"], inplace=True)

    return df


def load_food(file=FOOD_FILE):
    df = pd.read_csv(file)
    df = _clean_cols(df).dropna(how="all")

    df["datetime"] = pd.to_datetime(df["datetime"], format="%d/%m/%Y %H:%M").dt.date
    df["calories_kcal"] = df["alcohol"] + df["fat"] + df["carbs"] + df["protein"]
    df["alcohol"] = round(df["alcohol"].astype("float") / 7., 2)
    df["fat"] = round(df["fat"].astype("float") / 9., 2)
    df["carbs"] = round(df["carbs"].astype("float") / 4. ,2)
    df["protein"] = round(df["protein"].astype("float") / 4., 2)

    
    df.rename(columns={
        "datetime": "date",
        "alcohol": "alcohol_g",
        "fat": "fat_g",
        "carbs": "carbs_g",
        "protein": "protein_g"}, inplace=True)
    df.drop(columns=["fasting"], inplace=True)

    return df


def load_bf(file=BF_FILE):
    df = pd.read_csv(file)
    df = _clean_cols(df).dropna(how="all")

    df["datetime"] = pd.to_datetime(df["datetime"], format="%d/%m/%Y %H:%M").dt.date
    df["body_fat"] = df["body_fat"].astype("float")
    
    df.rename(columns={"datetime": "date", "body_fat": "body_fat_percent"}, inplace=True)
    df.drop(columns=["fasting"], inplace=True)

    return df


# sessions_df = load_sessions(TRAINING_FILE)
# strength_df = load_strength_log(TRAINING_FILE)
# cardio_df = load_cardio_log(TRAINING_FILE)
# mobility_df = load_mobility_log(TRAINING_FILE, auto_fix=True)
# exercise_lookup_df = load_exercise_lookup(TRAINING_FILE)

# print(sessions_df.dtypes)
# print(sessions_df.head)
# print(strength_df.dtypes)
# print(strength_df.head)
# print(cardio_df.dtypes)
# print(cardio_df.head)
# print(mobility_df.dtypes)
# print(mobility_df.head)
# print(exercise_lookup_df.dtypes)
# print(exercise_lookup_df.head)