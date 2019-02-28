import uuid
import pandas as pd
from sqlalchemy import create_engine

# define variables
DB_NAME = "titanic.db"
TABLE_NAME = "titanic"
DB_TYPE = "sqlite"
CSV_FILE_PATH = "titanic.csv"


# the function
def create_database_from_csv(db_name, table_name, db_type, csv_file_path):
    connection_string = db_type + ":///" + db_name
    engine = create_engine(connection_string)
    with open(csv_file_path, "r") as file:
        csv_df = pd.read_csv(file)
		
	# Change binary values to boolean	
	survived_df = csv_df['Survived'].apply(binary_to_boolean)

        # Create uuid column
        uuid_df = csv_df['Name'].apply(lambda x: uuid.uuid4())
	#siblings_df = csv_df['Siblings/Spouses Aboard'].apply(binary_to_boolean)
	#parents_df = csv_df['Parents/Children Aboard'].apply(binary_to_boolean)
	
	# Replace the binary valued columns with the alternatives
	#csv_df.drop(columns=['Survived', 'Siblings/Spouses Aboard', 'Parents/Children Aboard'], inplace=True)
	csv_df['Survived'] = survived_df
        #csv_df['uuid'] = uuid_df
	#csv_df['Siblings/Spouses Aboard'] = siblings_df
	#csv_df['Parents/Children Aboard'] = parents_df 
	
	# Convert dataframe to sqlite database table
    csv_df.to_sql(table_name, con=engine, index=True, index_label="id", if_exists="replace")


def binary_to_boolean(n):
	if n == 0:
		return 'False'
	else:
		return 'True'

# calling the function
if __name__ == "__main__":
    create_database_from_csv(DB_NAME, TABLE_NAME, DB_TYPE, CSV_FILE_PATH)
