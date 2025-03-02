import psycopg2
from psycopg2.extras import DictCursor
from database import connection_pool

def get_user_info(user_id):
    """
    Fetch user account details including name, gender, age, risk tolerance, and marital status.
    Also retrieves portfolio information.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Fetch user account details
            cursor.execute("""
                SELECT accountname, gender, age, risktolerance, maritalstatus
                FROM Accounts
                WHERE accountID = %s
            """, (user_id,))
            account_data = cursor.fetchone()

            if not account_data:
                print(f"User {user_id} not found.")
                return None

            # Fetch total balance
            cursor.execute("SELECT SUM(balance) FROM Portfolio WHERE accountID = %s", (user_id,))
            total_balance = cursor.fetchone()[0] or 0.0

            # Fetch portfolios
            cursor.execute("SELECT portfolioType, balance FROM Portfolio WHERE accountID = %s", (user_id,))
            portfolios = cursor.fetchall()

            return {
                "accountName": account_data["accountname"],
                "gender": account_data["gender"],
                "age": account_data["age"],
                "risktolerance": account_data["risktolerance"],
                "maritalstatus": account_data["maritalstatus"],
                "totalBalance": total_balance,
                "portfolios": [{"portfolioType": p["portfoliotype"], "balance": p["balance"]} for p in portfolios]
            }

    except psycopg2.Error as e:
        print(f"Database error in get_user_info: {e}")
        return None

    finally:
        connection_pool.putconn(conn)


def get_user_balance(user_id):
    """
    Fetches the total balance of the user's portfolio.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT SUM(balance) FROM Portfolio WHERE accountID = %s", (user_id,))
            balance = cursor.fetchone()[0] or 0.0
            return balance

    except psycopg2.Error as e:
        print(f"Database error in get_user_balance: {e}")
        return None

    finally:
        connection_pool.putconn(conn)


def get_user_services(user_id):
    """
    Fetches the list of services associated with a user's account.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM Services WHERE accountID = %s", (user_id,))
            services = [service[0] for service in cursor.fetchall()]
            return services if services else []

    except psycopg2.Error as e:
        print(f"Database error in get_user_services: {e}")
        return []

    finally:
        connection_pool.putconn(conn)


def get_all_users():
    """
    Fetch all users from the database.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM accounts")
            return [dict(row) for row in cursor.fetchall()]

    except psycopg2.Error as e:
        print(f"Database error in get_all_users: {e}")
        return []

    finally:
        connection_pool.putconn(conn)



def add_service(user_id, service_name):
    """
    Adds a service to a user's account.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO Services (accountID, name) VALUES (%s, %s)", (user_id, service_name))
            conn.commit()
            return f"Successfully added {service_name}."

    except psycopg2.Error as e:
        print(f"Database error in add_service: {e}")
        return "Failed to add service."

    finally:
        connection_pool.putconn(conn)


def remove_service(user_id, service_name):
    """
    Removes a service from a user's account.
    """
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Services WHERE accountID = %s AND name = %s", (user_id, service_name))
            conn.commit()
            return f"Successfully removed {service_name}."

    except psycopg2.Error as e:
        print(f"Database error in remove_service: {e}")
        return "Failed to remove service."

    finally:
        connection_pool.putconn(conn)

#### FOR TESTING  ###

# Main function to test the functions when running this file directly
def main():
    user_id = "5e655314-c264-4999-83ad-67c43cc6db5b"  # Replace with a valid user ID from your database

    print("Testing get_user_info:")
    print(get_user_info(user_id))

    print("\nTesting get_user_balance:")
    print(get_user_balance(user_id))

    print("\nTesting get_user_services:")
    print(get_user_services(user_id))

    print("\nTesting get_all_users:")
    print(get_all_users())

    print("\nTesting add_service:")
    print(add_service(user_id, "NewService"))

    print("\nTesting remove_service:")
    print(remove_service(user_id, "NewService"))

# Run main() if the script is executed directly
if __name__ == "__main__":
    main()