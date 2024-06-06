
import requests
import json
from . import main
from .. import db
from sqlalchemy import text

def update_chart_data():
  print('Updating chart data...')
  # Fetch the JSON data from the URL:

  response = requests.get('https://korkeasaarenkavijat.onrender.com/api/data/year')
  json_data = response.json()

  # Connect to the MySQL database:
  
  # Create a table in the MySQL database (if it doesn't exist):

  create_table_query = '''
  CREATE TABLE IF NOT EXISTS chart_data (
      id INT PRIMARY KEY,
      data JSON
  )
  '''
  db.session.execute(text(create_table_query))

  # Upsert (delete + insert) the JSON data into the table:

  current_year = '0'
  delete_query = text('DELETE FROM chart_data WHERE id = :id')
  db.session.execute(delete_query, {"id": 0})

  insert_query = text('INSERT INTO chart_data (id, data) VALUES (:id, :data)')
  db.session.execute(insert_query, {"id": current_year, "data": json.dumps(json_data)})
  
  db.session.commit()
  print('Updata completed')
  
