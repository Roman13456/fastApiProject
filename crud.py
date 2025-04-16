from typing import List, Optional
from beanie import PydanticObjectId 
from models import TVProgram, TVChannel, User
from schemas import TVProgramCreate, UserCreate 
from security import hash_password

# --- TVProgram CRUD ---

async def create_tv_program(program_data: TVProgramCreate) -> Optional[TVProgram]:
    """Створює нову програму в MongoDB."""
    # Перевіряємо, чи існує канал з таким channel_id
    try:
        channel_object_id = PydanticObjectId(program_data.channel_id)
    except Exception: 
         print(f"Помилка: Невалідний формат channel_id: {program_data.channel_id}")
         return None 

    channel = await TVChannel.get(channel_object_id) 
    if not channel:
        print(f"Помилка: Канал з ID {program_data.channel_id} не знайдений.")
        return None # Повертаємо None, якщо канал не знайдено

    db_program = TVProgram(
        title=program_data.title,
        description=program_data.description,
        start_time=program_data.start_time,
        end_time=program_data.end_time,
        channel=channel, 
    )
    # Вставляємо документ у базу даних
    await db_program.insert()
    return db_program # Повертаємо створений документ

async def get_tv_program(program_id: PydanticObjectId) -> Optional[TVProgram]:
    """Отримує програму за її ID."""
    program = await TVProgram.get(program_id)
    if program and program.channel:
         await program.fetch_link(TVProgram.channel) # Завантажуємо дані каналу
    return program

async def get_all_tv_programs() -> List[TVProgram]:
    """Отримує всі програми."""
    programs = await TVProgram.find_all().to_list()
    # Завантажуємо пов'язані канали для кожної програми
    for program in programs:
        if program.channel:
            await program.fetch_link(TVProgram.channel)
    return programs

async def update_tv_program(program_id: PydanticObjectId, updated_data: TVProgramCreate) -> Optional[TVProgram]:
    """Оновлює існуючу програму."""
    program = await TVProgram.get(program_id)
    if not program:
        return None # Програма не знайдена
    
    if program.channel:
        await program.fetch_link(TVProgram.channel)

    # Перевіряємо, чи змінився channel_id і чи існує новий канал
    new_channel_id_str = str(updated_data.channel_id) # Конвертуємо в рядок для порівняння
    current_channel_id_str = str(program.channel.id) if program.channel else None

    new_channel = program.channel 
    if new_channel_id_str != current_channel_id_str:
        try:
            new_channel_object_id = PydanticObjectId(updated_data.channel_id)
            new_channel = await TVChannel.get(new_channel_object_id)
            if not new_channel:
                print(f"Помилка оновлення: Новий канал з ID {updated_data.channel_id} не знайдений.")
                return None # Новий канал не знайдено
        except Exception:
            print(f"Помилка оновлення: Невалідний формат нового channel_id: {updated_data.channel_id}")
            return None

    update_dict = updated_data.model_dump(exclude_unset=True)

    # Оновлюємо поля програми
    program.title = update_dict.get('title', program.title)
    program.description = update_dict.get('description', program.description)
    program.start_time = update_dict.get('start_time', program.start_time)
    program.end_time = update_dict.get('end_time', program.end_time)
    program.channel = new_channel # Оновлюємо посилання на канал
    # Зберігаємо зміни
    await program.save()
    # Перезавантажуємо посилання на канал після збереження
    await program.fetch_link(TVProgram.channel)
    return program

async def delete_tv_program(program_id: PydanticObjectId) -> bool:
    """Видаляє програму за ID."""
    program = await TVProgram.get(program_id)
    if program:
        await program.delete()
        return True # Успішно видалено
    return False # Програма не знайдена

# --- TVChannel CRUD ---

async def get_all_channels() -> List[TVChannel]:
    """Отримує всі канали (без програм)."""
    return await TVChannel.find_all().to_list()

async def get_channel_and_programs(channel_id: PydanticObjectId) -> Optional[TVChannel]:
    """Отримує канал за ID та пов'язані з ним програми."""
    channel = await TVChannel.get(channel_id)
    if not channel:
        return None

    programs = await TVProgram.find(TVProgram.channel.id == channel.id).to_list()

    # Завантажуємо посилання на канал для кожної програми (щоб уникнути помилок при серіалізації)
    for prog in programs:
         if prog.channel:
              await prog.fetch_link(TVProgram.channel)

    return channel, programs

# --- User CRUD ---

async def get_user_by_username(username: str) -> Optional[User]:
    """Отримує користувача за ім'ям."""
    return await User.find_one(User.username == username)

async def create_user(user_data: UserCreate) -> User:
    """Створює нового користувача."""
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        password_hash=hashed_password,
        role=user_data.role or 'user'
    )
    await db_user.insert()
    return db_user
