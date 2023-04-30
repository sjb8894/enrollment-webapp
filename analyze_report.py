import pandas as pd
import re

def preprocess(df):
    # Preprocess and Clean DF
    df = df.drop(['Supervised Account',
                'Expiration', 
                'Mobile Number', 
                'Phone Number', 
                'Export Value 2', 
                'Export Value 3', 
                'Export Value 4'], axis=1)
        
    df.rename(columns={'Title = Dept': 'Title', 'Department = Job Title': 
                    'Department', 'User Role(s)': 'Roles', 'Export Value': 
                    'ExportVal', 'Export Value 5': 'ExportVal5'}, inplace=True)

    titles = df.Title
    subtitles = df.ExportVal5


    # Append full titles to DF
    full_titles = []
    for (title, subtitle) in zip(titles, subtitles):
        if isinstance(subtitle,float):
            full_titles.append(title)
        else:
            full_titles.append(title + ': ' + subtitle)
    # add condensed to df
    df['fullTitle'] = full_titles

    permissions_db = pd.read_pickle('db.pkl')
    data = clean_data(df, permissions_db)
    data = data.fillna('')
    df = data.applymap(lambda x: list(x) if isinstance(x, set) else x)
    # Remove apostrophes and brackets from all columns
    return df


def split_string(string):
    '''
    Splits strings at ,
    '''
    if isinstance(string, float):
        return string
    else:
        return string.split(', ')
    

def xref_roles(title, permissions_db, user_report):
    '''
    Cross references roles in the permissions db and user report
    '''
    # Row that matches users fullTitle from DB
    row = permissions_db.loc[permissions_db['fullTitle'] == title]
    # Compliant roles for specified fullTitle
    compliant_roles = row['Roles Assigned']
    # Current users roles
    user_roles_curr = user_report.loc[user_report['fullTitle'] == title, 'Cleaned Roles']
    return compliant_roles.explode().tolist(), user_roles_curr.explode().tolist()


def clean_data(data, permissions_db):
    '''
    Cleans data for analysis
    '''

    # Build new DF for user reporting
    user_report = data[['Username', 'Title', 'fullTitle', 'Department', 'Updated', 'Roles']]
    user_report = user_report.reindex(columns= user_report.columns.tolist() + ['Cleaned Roles', 'Correct Roles', 'Missing Roles', 'Excess Roles'])
    
    # Update user_report w/ split string
    user_report['Roles'] = user_report['Roles'].apply(split_string)

    # Update Perms DB w/ split string
    permissions_db['Roles Assigned'] = permissions_db['Roles Assigned'].apply(split_string)

    ## NEW SECTION ##
    new_roles = []
    original_data = []
    # iterate over the 'Roles' column
    for i in range(len(user_report['Roles'])):
        # check if the element is a list or float
        if isinstance(user_report.at[i, 'Roles'], list):
            roles_list = user_report.at[i, 'Roles']
            new_roles_list = []
            original_row = []
            for role in roles_list:
                original_row.append(role)
                extracted = re.findall(r'\((.*?)\)', role)
                new_role = re.sub(r'\(.*?\)', '', role)
                new_roles_list.append(new_role.strip())
            # update the 'Roles' column with the modified list
            new_roles.append(new_roles_list)
        else:
            # if the element is not a list, append the original value to the modified roles list
            new_roles.append(user_report.at[i, 'Roles'])
    # add the modified 'Roles' columns to the DataFrame
    user_report['Cleaned Roles'] = new_roles

    ## NEW SECTION ##

    correct = []
    missing = []
    excess = []
    for title, username in zip(user_report['fullTitle'], user_report['Username']):
        x, y = xref_roles(title, permissions_db, user_report)
        if isinstance(y, float):
            pass
        else:
            db_roles = set(x)
            users_roles = set(y)

            correct_user_roles = db_roles.intersection(users_roles)
            missing_user_roles = db_roles - correct_user_roles
            excess_user_roles = users_roles - correct_user_roles
            correct.append(correct_user_roles)
            missing.append(missing_user_roles)
            excess.append(excess_user_roles)

    # Append findings to user_report
    user_report['Correct Roles'] = correct
    user_report['Missing Roles'] = missing
    user_report['Excess Roles'] = excess
    # import ipdb
    # ipdb.set_trace()
    return user_report


# def test():
#     df = pd.read_pickle('df.pkl')
#     data = preprocess(df)
#     data = data.applymap(lambda x: list(x) if isinstance(x, set) else x)

#     print(data.head())

# test()