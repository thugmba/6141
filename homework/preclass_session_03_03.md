# Before Session 3.3: Practice Your First Prediction Model

Course 6141: Business Analytics and AI Application | Pre-class homework, about 2 hours | Submit on iLearn

## Why this homework

In Session 3.3 you will train a model that suggests a price for a used phone. The class goes fast if you already know the few tools it uses. This homework teaches them on a smaller, simpler example, so that in class you can focus on the ideas instead of the typing.

When you finish, you will have done each step of Session 3.3 once on your own:

| You practice today | You will use it in Session 3.3 to |
|---|---|
| load a CSV file and look at it | load the 20 phone sales |
| draw a scatter plot | see how price falls with age |
| predict by hand with a formula, and measure the error | read the price formula and the typical error |
| train a model with `.fit()` and test it with `.predict()` | train and test the phone price model |
| compare the model with "guess the average" | judge whether the model is worth using |
| add a second clue | add storage and battery health |

**What you need:** your laptop with Python 3.13 and a `.venv` (see the Python Setup Clinic), Google Antigravity IDE, Microsoft Word (free for Tunghai University students from <https://software.thu.edu.tw/new/>), and the Word template `preclass_session_03_03_template.docx`.

---

## Part 1: The Example

A drink stand on campus sells cold drinks. The owner wrote down, for 16 days, the day's highest temperature, whether it was a weekend, and how many cups were sold. The owner wants to plan how many cups to prepare tomorrow.

File: `data/preclass_03_03_dataset.csv` (fictional teaching data).

| Column | Meaning |
|---|---|
| `Day_ID` | Day code, `DAY-01` to `DAY-16`. A label, not a clue. |
| `High_Temp_C` | The highest temperature of the day, in degrees Celsius. |
| `Weekend_Flag` | `1` = Saturday or Sunday, `0` = a weekday. |
| `Cups_Sold` | Cups sold that day. **This is what we want to predict (the target).** |

## Part 2: Five Ideas You Need

1. **Features and target.** The **target** is the number we want to predict (`Cups_Sold`). The **features** are the clues we use to predict it (`High_Temp_C`, later also `Weekend_Flag`). In code, the features are called `X` and the target `y`.
2. **A straight-line formula.** Linear regression learns a formula such as `cups = start value + effect x temperature`. The **effect** (the coefficient) is how many more cups are sold for each extra degree.
3. **Train and test.** The model learns from some days (the **training** days) and is checked on other days it has never seen (the **test** days). Only the test shows how it will do tomorrow.
4. **Error and typical error.** An error is predicted minus actual. **MAE** (Mean Absolute Error) is the average size of the errors, ignoring the sign: "the prediction is typically off by this much".
5. **A benchmark.** A model is only useful if it beats the simplest guess: "every day, prepare the average number of cups".

## Part 3: Get Ready

1. In your `6141_labs` folder, make a folder named `s33_preclass`, and inside it a folder named `data`.
2. Download the data file from the course page and save it in `s33_preclass/data`: <https://github.com/thugmba/6141/blob/main/data/preclass_03_03_dataset.csv> (click **Download raw file**, the download icon at the top right of the table).
3. Open `s33_preclass` in Antigravity (**File > Open Folder**) and open a Terminal.
4. Create and activate a `.venv`, then install three packages.

   Mac:

   ```text
   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install pandas scikit-learn matplotlib
   ```

   Windows (Command Prompt):

   ```text
   py -3.13 -m venv .venv
   .venv\Scripts\activate
   python -m pip install pandas scikit-learn matplotlib
   ```

5. For every task, create the script in `s33_preclass`, save it, and run it with `python` followed by the file name. Name each script with your name and the task number, for example `Reacher_P33_task1.py`.

**Screenshots:** every screenshot in your report must be readable. Capture only the Terminal, with the text made bigger first (see "How to Take a Readable Screenshot" in the Python Setup Clinic).

---

## Part 4: Six Tasks

### Task 1: Check Your Tools

**Do:** create `YourName_P33_task1.py`, then run it.

```python
import sys
import pandas
import sklearn
import matplotlib

print("Python:", sys.version.split()[0])
print("pandas:", pandas.__version__)
print("scikit-learn:", sklearn.__version__)
print("matplotlib:", matplotlib.__version__)
```

**Check:** four lines with version numbers, for example `Python: 3.13.17`. Any version of the three packages is fine. If you see `ModuleNotFoundError`, your `.venv` is not active or a package is missing (Part 3, step 4).

**Report:** a screenshot of the output.

### Task 2: Load the Data and Look at It

**Do:** create `YourName_P33_task2.py`, then run it.

```python
import pandas as pd

df = pd.read_csv("data/preclass_03_03_dataset.csv", index_col="Day_ID")
print(df.head())
print("Rows and columns:", df.shape)
print(df.describe().loc[["min", "mean", "max"]].round(1))
```

* `index_col="Day_ID"` uses the day codes as row labels, so they are never treated as a clue.
* `df.head()` shows the first 5 rows; `df.shape` gives (rows, columns).
* `df.describe()` computes summary numbers; `.loc[["min", "mean", "max"]]` keeps three of them.

**Check:** `Rows and columns: (16, 3)`; `6` weekend days; temperatures from `22.0` to `35.0`; cups from `99.0` to `196.0`, with a mean of `139.9`.

**Report:** a screenshot of the output, and answers: which column is the target? Which columns are the features? How many of the 16 days are weekends? (Add one line: `print(df["Weekend_Flag"].sum())`; the sum of a 0/1 column counts the 1s.)

### Task 3: Draw a Scatter Plot

**Do:** create `YourName_P33_task3.py`, then run it.

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/preclass_03_03_dataset.csv", index_col="Day_ID")
plt.scatter(df["High_Temp_C"], df["Cups_Sold"])
plt.xlabel("Highest temperature of the day (C)")
plt.ylabel("Cups sold")
plt.title("Cold drinks sold on 16 days")
plt.savefig("drinks_scatter.png")
print("Saved: drinks_scatter.png")
```

* `plt.scatter(x, y)` draws one dot per day.
* `plt.savefig(...)` saves the picture as a file next to your script. Open it from the File Explorer.

**Check:** a picture with 16 dots that rise from the bottom left to the top right.

**Report:** paste the picture itself (not a screenshot of it), and answer in one or two sentences: what happens to sales when it gets hotter? Do a few dots sit clearly above the others?

### Task 4: Predict by Hand

A model trained on 12 of the days learned this formula:

```text
cups = -15.3 + 5.51 x temperature
```

**Do:** with a calculator (or Python as a calculator), fill in the table in the template for the 4 test days. Round to 1 decimal.

| Day | Temperature | Predicted cups | Actual cups | Error (predicted - actual) |
|---|---|---|---|---|
| `DAY-01` | 24 | `-15.3 + 5.51 x 24 = ?` | 99 | ? |
| `DAY-02` | 27 | ? | 114 | ? |
| `DAY-06` | 29 | ? | 135 | ? |
| `DAY-15` | 35 | ? | 196 | ? |

Then compute the **MAE**: drop the minus signs, add the four errors, and divide by 4.

**Check:** `DAY-01`: predicted `116.9`, error `+17.9`. Your MAE should be about `16.3`. You will see the same number from Python in Task 5. A difference of `0.1` in a prediction (for example `177.6` by hand, `177.5` in Python) comes from rounding the formula to `5.51`.

**Report:** the completed table, the MAE calculation, and one sentence: what does `5.51` mean for the drink stand?

### Task 5: Train and Test a Model in Python

**Do:** create `YourName_P33_task5.py`, then run it.

```python
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("data/preclass_03_03_dataset.csv", index_col="Day_ID")
X = df[["High_Temp_C"]]
y = df["Cups_Sold"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
predicted = model.predict(X_test)

print("Start value:", round(model.intercept_, 1))
print("Cups per extra degree:", round(model.coef_[0], 2))
print("Test days:", list(X_test.index))
print("Predicted:", predicted.round(1).tolist())
print("Actual:", y_test.tolist())
print("Model, typical error:", round(mean_absolute_error(y_test, predicted), 1))
guess = [y_train.mean()] * len(y_test)
print("Guessing the average, typical error:", round(mean_absolute_error(y_test, guess), 1))
```

* `X = df[["High_Temp_C"]]` uses **double** brackets: the features must be a table, even with one column. `y` is one column, with single brackets.
* `train_test_split(..., test_size=0.25, random_state=42)` keeps 4 of the 16 days for the test; `random_state=42` gives everyone the same 4 days.
* **Create, fit, predict:** `LinearRegression()` creates an empty model, `.fit()` learns the formula from the 12 training days, and `.predict()` predicts the 4 test days.
* `model.intercept_` is the start value and `model.coef_` holds the effects. A trailing `_` marks something learned during `.fit()`.
* `[y_train.mean()] * len(y_test)` makes a list of 4 copies of the average: the "guess the average" benchmark.

**Check:**

```text
Start value: -15.3
Cups per extra degree: 5.51
Test days: ['DAY-01', 'DAY-02', 'DAY-06', 'DAY-15']
Predicted: [116.9, 133.4, 144.5, 177.5]
Actual: [99, 114, 135, 196]
Model, typical error: 16.3
Guessing the average, typical error: 32.6
```

**Report:** a screenshot of the output, and two sentences: do the numbers match your hand calculation in Task 4? Is the model worth using, compared with guessing the average?

### Task 6: Add a Second Clue

**Do:** copy Task 5 into `YourName_P33_task6.py` and change two lines:

* `X = df[["High_Temp_C"]]` becomes `X = df[["High_Temp_C", "Weekend_Flag"]]`
* after the line `print("Cups per extra degree:", ...)`, add `print("Extra cups on a weekend:", round(model.coef_[1], 2))`

**Check:** `Cups per extra degree: 6.07`, `Extra cups on a weekend: 22.81`, and `Model, typical error: 4.2`.

**Report:** a screenshot of the output, and two sentences: what does `22.81` mean? Why did the typical error fall from `16.3` to `4.2`? (Look back at the dots that sat above the others in Task 3.)

---

## Part 5: Submit Your Report

1. Open the Word template `preclass_session_03_03_template.docx` (A4) in **Microsoft Word**. Fill in page 1, then one section per task: screenshots, the Task 4 table, and short answers. The grey hint text is only a guide: delete it and paste or type in its place. The finished report is about 5 pages.
2. Save it as a PDF in Word (**File > Save As**, then choose **PDF**) named `StudentID_Name_PreClass_S33.pdf`, with your name in English letters and no spaces, for example `S11312345_JohnSmith_PreClass_S33.pdf`.
3. Upload it to iLearn by the deadline in the homework announcement.
4. Stuck on a task? Do not leave it blank: paste the error, write what you tried, and bring the same laptop to class.

## Common Errors

| You see | Fix |
|---|---|
| `FileNotFoundError: ... 'data/preclass_03_03_dataset.csv'` | the file is not in `s33_preclass/data`, or the Terminal is in another folder (check with `pwd` on a Mac, `cd` on Windows) |
| `ModuleNotFoundError: No module named 'sklearn'` | activate `.venv`, then `python -m pip install scikit-learn` |
| `ValueError: Expected a 2-dimensional container but got <class 'pandas.Series'> instead` | write `df[["High_Temp_C"]]` with double brackets for `X` |
| `KeyError: 'High_Temp_C'` | a column name is misspelled; names are case-sensitive |
