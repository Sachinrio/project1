import asyncio
import asyncpg

async def main():
    try:
        conn = await asyncpg.connect('postgresql://postgres:Sankar%40722001@localhost:5432/postgres')
        # asyncpg requires to be outside of transaction block to create database
        # Execute 'COMMIT' or just use autocommit
        # 'CREATE DATABASE' cannot run inside a transaction block
        await conn.execute('COMMIT')
        await conn.execute('CREATE DATABASE infinitetechai')
        print("Database infinitetechai created successfully")
        await conn.close()
    except asyncpg.exceptions.DuplicateDatabaseError:
        print("Database already exists")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
