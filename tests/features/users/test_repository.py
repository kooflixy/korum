from src.features.users.repository import UserRepository


async def test_insert(session):
    await UserRepository.insert(session, "lelele", "bebebe".encode())
    await session.flush()
    user = await UserRepository.get_by_username(session, "lelele")
    assert user.hashed_password == "bebebe".encode()
