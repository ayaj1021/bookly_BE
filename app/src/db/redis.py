from redis.asyncio import Redis
from redis.exceptions import ConnectionError
from app.src.config import Config


JTI_EXPIRY = 3600


# token_blocklist = Redis(
#     host=Config.REDIS_HOST,
#     port=Config.REDIS_PORT,
#     db=0,
#     decode_responses=True,
# )

token_blocklist = Redis.from_url(
    Config.REDIS_URL
    # host=Config.REDIS_HOST,
    # port=Config.REDIS_PORT,
    # db=0,
    # decode_responses=True,
)


# async def add_jti_to_blocklist(jti: str) -> None:
#     await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)


# async def token_in_block_list(jti: str) -> bool:
#     jti = await token_blocklist.get(jti)



async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(jti, "", ex=JTI_EXPIRY)


async def token_in_block_list(jti: str) -> bool:
    try:
        return await token_blocklist.exists(jti) == 1
    except ConnectionError:
        print('No connection to redis')
        return False


    # return jti is not None
