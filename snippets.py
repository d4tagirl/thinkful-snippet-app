import psycopg2
import logging



# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)




# Connect to database
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")




def put(name, snippet):
  """Store a snippet with an associated name."""
  logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
  try:
    with connection, connection.cursor() as cursor:
      cursor.execute("insert into snippets values (%s, %s)", (name, snippet))
      logging.debug("Snippet stored successfully.")
      stored = True
  except psycopg2.IntegrityError:
    with connection, connection.cursor() as cursor:
      cursor.execute("update snippets set message=%s where keyword=%s", (snippet, name))
      logging.debug("Can't insert. There is already a %s snippet.".format(name))
      stored = False
  return name, snippet, stored




def get(name):
  """Retrieve the snippet with a given name. """
  logging.info("Retrieving snippet {!r}".format(name))
  with connection, connection.cursor() as cursor:
    cursor.execute("select keyword, message from snippets where keyword=%s", (name,))
    row = cursor.fetchone()
  if not row:
    # No snippet was found with that name.
    logging.debug("Snippet {!r} doesn't exist!".format(name))
    return None
  else:
    logging.debug("Snippet {!r} retrieved successfully.".format(name))
    return row
    


def catalog():
  logging.info("Retrieving all keywords from snippets")
  with connection, connection.cursor() as cursor:
    cursor.execute("select keyword, message from snippets where hidden is false order by keyword")
    all = cursor.fetchall()
    logging.info("All snippets retrieved")
  return all



def search(word):
  """Retrieve the snippets that contain a word. """
  logging.info("Retrieving snippets with the word {!r} on the message".format(word))
  with connection, connection.cursor() as cursor:
    cursor.execute("select keyword, message from snippets where message like %s and hidden is false", ('%' + str(word) + '%',))
    search_snippets = cursor.fetchall()
    logging.info("All snippets with {!r} on the message retrieved".format(word))
  return search_snippets



import argparse

def main():
  """Main function"""
  logging.info("Constructing parser")
  parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

  subparsers = parser.add_subparsers(dest="command", help="Available commands")

  # Subparser for the put command
  logging.debug("Constructing put subparser")
  put_parser = subparsers.add_parser("put", help="Store a snippet")
  put_parser.add_argument("name", help="Name of the snippet")
  put_parser.add_argument("snippet", help="Snippet text")
    
  # Subparser for the get command
  logging.debug("Constructing get subparser")
  get_parser = subparsers.add_parser("get", help="Get a snippet")
  get_parser.add_argument("name", help="Name of the snippet")
  
  # Subparser for the catalog command
  logging.debug("Constructing catalog subparser")
  catalog_parser = subparsers.add_parser("catalog", help="Catalog of snippets available")
  
  # Subparser for the search command
  logging.debug("Constructing search subparser")
  search_parser = subparsers.add_parser("search", help="Serch for snippets by key word")
  search_parser.add_argument("word", help="Keyword for the snippet search")

  arguments = parser.parse_args()
    
  # Convert parsed arguments from Namespace to dictionary
  arguments = vars(arguments)
  command = arguments.pop("command")

  if command == "put":
    name, snippet, stored = put(**arguments)
    if stored:
      print("Stored {!r} as {!r}".format(snippet, name))
    else:
      print("Updated {!r} as {!r}".format(snippet, name))
    
  elif command == "get":
    snippet = get(**arguments)
    if snippet:
      print("Retrieved snippet: {!r}".format(snippet))
    else:
      print("snippet not found!")
  
  elif command == "catalog":
    all_snippets = catalog()
    print("Retrieved keywords:")
    for snippet in all_snippets:
      print(snippet)
      
  elif command == "search":
    filtered_snippets = search(**arguments)
    print("Retrieved keywords:")
    for snippet in filtered_snippets:
      print(snippet)

if __name__ == "__main__":
  main()
