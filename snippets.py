import psycopg2
import logging



# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)




# Connect to database
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")
#
# def put(name, snippet):
#   """Store a snippet with an associated name."""
#   logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
#   cursor = connection.cursor()
#   try:
#     command = "insert into snippets values (%s, %s)"
#     cursor.execute(command, (name, snippet))
#     connection.commit()
#     logging.debug("Snippet stored successfully.")
#   except psycopg2.IntegrityError:
#     connection.rollback()
#     command = "update snippets set message=%s where keyword=%s"
#     cursor.execute(command, (snippet, name))
#     logging.debug("Can't insert. There is already a %s snippet.".format(name))
#   return name, snippet


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
    cursor.execute("select message from snippets where keyword=%s", (name,))
    row = cursor.fetchone()
  if not row:
    # No snippet was found with that name.
    logging.debug("Snippet doesn't exist!")
    return None
  else:
    logging.debug("Snippet retrieved successfully.")
    return row[0]
    


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

  arguments = parser.parse_args()
    
  # Convert parsed arguments from Namespace to dictionary
  arguments = vars(arguments)
  command = arguments.pop("command")

  if command == "put":
    name, snippet, stored = put(**arguments)
    if stored == True:
      print("Stored {!r} as {!r}".format(snippet, name))
    else:
      print("Updated {!r} as {!r}".format(snippet, name))
    
  elif command == "get":
    snippet = get(**arguments)
    if snippet:
      print("Retrieved snippet: {!r}".format(snippet))
    else:
      print("snippet not found!")

if __name__ == "__main__":
  main()
