# -*- coding: utf-8 -*-
"""
Created py for the Python Guide to Creating your Own Functions

"""

import glob
import os
import pandas as pd
import numpy as np
import datetime

################### Initialize the py file
DIRECTORY_LOCATION = r'C:/Users/Kevin/Desktop/Data'
print(f"Database directory is {DIRECTORY_LOCATION}")

############################# Read in a file
def load_file(filename):
    """
    
    Attempts to load a csv file. The passed parameter, ``filename``, should be obtained by calling ``find_directory_file()``.
    
    If you already know the filename, then you could provide your own filename. 
    
    In addition, this function will remove any rows in the data that have no data (NA)

    Parameters
    ----------
    **filename**: string
    
    Example of how to use this function.
        
        ``df = load_file('my_file_name.csv')``
        
    OR you could use the ``find_directory_file()`` function
        
        ``file_name = find_directory_file(your_file_name.csv)``
        
        ``df = load_file(file_name)``

    Returns
    -------
    DataFrame
        A DataFrame representing the contents of the passed parameter 'filename'

    """
    
    df = pd.read_csv(filename)
    df.dropna(how='all', inplace=True) # remove rows with no data
    return df

def find_directory_file(string_search=''):
    """
    
    Attempts to find a file in your current directory folder. It will use the passed parameter, ``search_string`` on all files in your directory folder.
    
    You do not need to ensure the whole file name is inputted into the ``search_string`` parameter, only a portion is needed if the name is unique enough.
    
    If there is more than one file found, it will use the most recent file based on the "Modified time" according to your operating system's timestamp on the file
    
    Parameters
    ----------
    **string_search** : string
    
    
    Example of how to use this function.
    
        ``games_file = find_directory_file(my_data_file)``
    
    If you work with files that is appended the date at the end based on when you've extracted it, then you could omit the date portion of the file.
   
    As an example, if you have a file named Games_Jan252020.csv, you could do the following.
        
        ``games_file = find_directory_file(Games_)``

    Returns
    -------
    string
        The path and filename of the file if found, otherwise, an exception will be raised.

    """
    
    csv_file_list = glob.glob(DIRECTORY_LOCATION + "\*.csv") # use glob to match filename
    files_list = [i for i in csv_file_list if string_search in i]
    num_found_files = len(files_list)
    
    # Situation 1: no files found
    if num_found_files == 0:
        raise Exception(f'Could not find the {string_search} file in your directory folder.')
        
    # Situation 2: more than one matching found
    elif num_found_files > 1:
        files_list.sort(key=lambda x: os.path.getmtime(x), reverse=True) # use the most recent file
        print(f'Found more than one {string_search} file. Will use the most recent file based on "Date Modified" on your computer.')
        directory, file = os.path.split(files_list[0])
        print(f'Using directory file: {file}')
        return files_list[0]
    
    # Situation 3: one file found
    else:
        directory, file = os.path.split(files_list[0])
        print(f'Using directory file: {file}')
        return files_list[0]
    
    print()


############### Question 1: Best selling game by region this year
def generate_top_region_games_by_year(currentYear = datetime.datetime.now().year, filename='vgsales'):
    """
    
    Generates the top selling game by each region by year. By default, if no parameter is passed for ``currentYear``, then the function will use the systems' current year.

    The final Data Frame will be exported to the current directory location.  
    
    Parameters
    ----------
    currentYear : int, optional
        Will default to systems' current year if no input is given
        
    filename : string, optional
        Will default to ``vgsales`` if no input is given.
        

    Returns
    -------
    This function does not return a value but exports a dataframe to the current directory.

    """
    
    # Attempt to find the correct filename in the current directory
    games_file = find_directory_file(filename)
    
    # Load in the csv file into the dataframe, df
    df = load_file(games_file)
    
    # Filter for the current year
    df = df[df['Year'] == currentYear]
    
    # Find the top selling game by finding the highest value in each respective column using .argmax()
    df_NA = pd.DataFrame(df.iloc[df['NA_Sales'].values.argmax()])
    df_NA.columns = ['NA_Sales']
    
    df_EU = pd.DataFrame(df.iloc[df['EU_Sales'].values.argmax()])
    df_EU.columns = ['EU_Sales']

    df_JP = pd.DataFrame(df.iloc[df['JP_Sales'].values.argmax()])
    df_JP.columns = ['JP_Sales']

    df_Other = pd.DataFrame(df.iloc[df['Other_Sales'].values.argmax()])
    df_Other.columns = ['Other_Sales']
    
    # Concatenate the four pandas series into a finalized dataframe
    df_final = pd.concat([df_NA, df_EU, df_JP, df_Other], axis=1).reset_index()
    
    # Remove unecessary row
    df_final = df_final[df_final['index'] != 'Rank']
    
    # Export finalized dataframe
    filename = os.path.join(DIRECTORY_LOCATION, f'Top_Selling_Game_By_Region_{currentYear}.csv')
    df_final.to_csv(filename, index=False)   
    print(f'Exporting completed file to this folder path: {filename}')
    

############### Question 2: Top 3 Publishers by Total Sales Each Year
def top_three_publishers_by_year(filename='vgsales'):
    """
    
    Generates the top three publishers for all years found in the input file. If no parameter is passed, the default filename will be ``vgsales``.

    The final Data Frame will be exported to the current directory location. 
    
    Parameters
    ----------
    filename : string, optional
        Will default to ``vgsales`` if no input is given.

    Returns
    -------
    This function does not return a value but exports a dataframe to the current directory.

    """
    
    # Attempt to find the correct filename in the current directory
    games_file = find_directory_file(filename)
    
    # Load in the csv file into the dataframe, df
    df = load_file(games_file)
    
    # Calcuate the total global sales each for publisher for each year
    df2 = df.groupby(['Year', 'Publisher'])['Global_Sales'].sum().reset_index().sort_values(['Year', 'Global_Sales'], ascending=[True, False])
    
    # Once you've sorted by top sales per year, grab the top 3 values from each year
    df2 = df2.groupby('Year').head(3)
    
    # To calculate rank, create a new column with the values: [0, 1, 2]
    df2.insert(0, 'Rank', df2.groupby('Year').cumcount())
    
    # Drop the global sales column as we no longer need it
    del df2['Global_Sales']
    
    # Pivot your dataframe so the rankings are now columns for easier user readability
    df2 = df2.pivot(index='Year', columns='Rank', values='Publisher')
    
    # Clean the dataframe before exporting
    df2.reset_index(inplace=True)
    df2.rename(columns={0.0: 'Top_Publisher', 1.0: '2nd_Place', 2.0: '3rd_Place'}, inplace=True)
    df2.fillna("No Publisher", inplace=True)
    
    # Export finalized dataframe
    filename = os.path.join(DIRECTORY_LOCATION, f'Top_Three_Publishers_by_Sales_Each_Year.csv')
    df2.to_csv(filename, index=False)   
    print(f'Exporting completed file to this folder path: {filename}')

############### Question 3: Total Console Sales by Year - using user inputted years
def console_sales_per_year(filename='vgsales'):
    """
    
    Generates the top selling game by each region by year. This function requires the user input data once it has been invoked.
    
    The user must input a minimum of one year as a response. If the user wishes to input more than one year, each year must be seperated by a comma: ``,``
    
    The final Data Frame will be exported to the current directory location.  

    Parameters
    ----------
    filename : string, optional
        Will default to ``vgsales`` if no input is given.

    Returns
    -------
    This function does not return a value but exports a dataframe to the current directory.

    """

    # Attempt to find the correct filename in the current directory
    games_file = find_directory_file(filename)
    
    # Load in the csv file into the dataframe, df
    df = load_file(games_file)
    
    # Ask user to input years seperated by commas
    s = input("Type in the years you want to search up, seperated by commas:")
    years_inputted = list(map(int, s.split(',')))
    
    # Filter main dataframe for the years inputted by user
    df = df[df['Year'].isin(years_inputted)]
    
    # Groupby console to calculate total sales by year
    df = df.groupby(['Year', 'Platform'])['Global_Sales'].sum().reset_index()
    
    # Pivot results for easier user readability in exported file
    df = df.pivot(index='Platform', columns='Year', values='Global_Sales').reset_index().fillna(0)
    
    # Export finalized dataframe
    filename = os.path.join(DIRECTORY_LOCATION, f'Console_Sales_per_Year.csv')
    df.to_csv(filename, index=False)   
    print(f'Exporting completed file to this folder path: {filename}')