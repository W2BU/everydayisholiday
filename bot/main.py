from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from bot.dbadapter import dbAdapter
from bot.calendfetcher import CalendFetcher
from datetime import datetime
import key as key

HELP_TEXT = "/help - подсказка по командам\n/info - информация о боте\n/я_снова_здесь - отметить еще один день праздником\n/stats узнать свою статистику"
BOT_INFO = "Говорят, что каждый день это праздник, хотя не уточняют в каком смысле: прямом или переносном. Настало время показать, что границы условны. Отмечайте праздник каждый день, а данный бот в этом поможет."

class PartyBot():    
        
    __bot = Bot(token = key.botKey)
    __dp = Dispatcher(bot = __bot)
    __calendar = CalendFetcher()
    __db = dbAdapter()
          
       
    def __initiate_handlers(self, dp):
        #defaut keyboard
        default_kb = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        ).add(
            KeyboardButton(text = "/я_снова_здесь"),
        )
        
        greet_kb = ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True
        ).add(
            KeyboardButton(text = "Я сегодня зажигаю"),
            KeyboardButton(text = "Нет настроения")
        )
        
        additionalInfo_kb = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        ).add(
            KeyboardButton(text = "Это вообще о чем?"),
            KeyboardButton(text = "Праздник не ждет")
        )
        
        changemind_kb = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        ).add(
            KeyboardButton(text = "Другой вопрос!"),
            KeyboardButton(text = "Все еще нет")
        )
                 
        @dp.message_handler(commands = ['start'])
        async def start (message: types.message):

            if not self.__db.userExists(message.from_user.id):
                self.__db.insertNewUser(message.from_user.id, message.from_user.full_name)
                await message.answer(
                    text = f"Вижу ты здесь новенький, {message.from_user.full_name}",
                )
                await message.answer(
                    text = f"Ничего сложного. Просто каждый день это праздник.",
                )
                await message.answer(
                    text = HELP_TEXT
                )
                
            else:
                                
                await message.answer(
                    text = f"Опять отмечаете, {message.from_user.full_name}?",
                    reply_markup = greet_kb
                )
            
        @dp.message_handler(commands = ['help'])
        async def help (message: types.message):
            
            await message.answer(
                text = HELP_TEXT,
            )
        
        @dp.message_handler(commands = ['info'])
        async def info (message: types.message):
            await message.answer(
                text = BOT_INFO,
            )
        
        @dp.message_handler(commands = ['stats'])
        async def stats (message: types.message):
            await message.answer(
                text = f"Серия: {self.__db.getDaysInRow(message.from_user.id)}\nВсего отмечено раз: {self.__db.totalTimesPartied(message.from_user.id)}"
            )      
               
        @dp.message_handler(commands = ['я_снова_здесь'])
        async def comeback (message: types.message):
                                    
            await message.answer(
                text = f"Опять отмечаете, {message.from_user.full_name}?",
                reply_markup = greet_kb
            )
        
        @dp.message_handler(text = "Я сегодня зажигаю")
        async def mainDialogue(message: types.Message):
            
            currentEventName = self.__calendar.getCurrentEventName(message.date)
            
            await message.answer (
                f"Безусловно правильное решение, ведь сегодня {currentEventName}",
                reply_markup = additionalInfo_kb
            )
            
            diff = (message.date - self.__db.getLastDate(message.from_user.id)).days
            if diff == 1:
                self.__db.incrementDaysInRow(message.from_user.id)
                self.__db.updateLastDate(message.from_user.id, str(message.date))
                self.__db.updateLastEvent(message.from_user.id, currentEventName)
            elif diff > 1:
                self.__db.resetDaysInRow(message.from_user.id)
                self.__db.updateLastDate(message.from_user.id, str(message.date))
                self.__db.updateLastEvent(message.from_user.id, currentEventName)
    
            else:
                await message.answer(
                    f"Праздник уже отмечается. Серия продолжается",
                    reply_markup = additionalInfo_kb
                )
                
            await message.answer (
                f"Ваш праздник длится: {self.__db.getDaysInRow(message.from_user.id)} суток"
            )
        
        @dp.message_handler(text = "Нет настроения")
        async def mainDialogue(message: types.Message):
            
            await message.answer (
                text = f"Как жаль будет пропустить {self.__calendar.getCurrentEventName(message.date)}"
            )
            await message.answer(
                text =f"До этого Вы отмечали {self.__db.getDaysInRow(message.from_user.id)} дней подряд"
            )
            
            await message.answer (
                f"Все еще отказываетесь?",
                reply_markup = changemind_kb,
            )
            
        @dp.message_handler(text = "Все еще нет")
        async def mainDialogue(message: types.message):

            await message.answer(
                f"До следующей вечеринки!",
                reply_markup = default_kb
            )
            # тогда до следующей вечеринки
          
        @dp.message_handler(text = "Другой вопрос!")
        async def mainDialogue(message: types.message):
                        
            diff = (message.date - self.__db.getLastDate(message.from_user.id)).days
            if diff == 1:
                self.__db.incrementDaysInRow(message.from_user.id)
                self.__db.updateLastDate(message.from_user.id, str(message.datetime))
                self.__db.updateLastEvent(message.from_user.id, self.__calendar.getCurrentEventName(message.date))
                
                await message.answer(
                    f"Так держать, продолжаем серию",
                    reply_markup = default_kb
                )
            elif diff > 1:
                self.__db.resetDaysInRow(message.from_user.id)
                self.__db.updateLastDate(message.from_user.id, str(message.datetime))
                self.__db.updateLastEvent(message.from_user.id, self.__calendar.getCurrentEventName(message.date))
                await message.answer(
                    f"О, нет! Целый один день не будет праздника. Серия прервана. Но, ничего, еще наверстаем",
                    reply_markup = default_kb
                )
            else:
                await message.answer(
                    f"Праздник уже отмечается. Серия продолжается",
                    reply_markup = default_kb
                )
                       
        
        @dp.message_handler(text = "Это вообще о чем?")
        async def mainDialogue(message: types.message):

            await self.__bot.send_photo(photo = self.__calendar.getCurrentEventExtraImage(), chat_id = message.from_user.id)
            await message.answer(
                text = self.__calendar.getCurrentEventExtraText(),
                reply_markup = default_kb
            )
            
        @dp.message_handler(text = "Праздник не ждет")
        async def mainDialogue(message: types.message):
            await message.answer(
                text = "Навстречу веселью",
                reply_markup = default_kb
            )
    
    
    def start_bot(self):
        self.__initiate_handlers(self.__dp)
        executor.start_polling(self.__dp) 
        

    

        

        