from database import get_connection

try:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT version();")

    result = cursor.fetchone()

    print("Подключение успешно!")
    print(result)

    cursor.close()
    connection.close()

except Exception as error:
    print("Ошибка подключения:")
    print(error)