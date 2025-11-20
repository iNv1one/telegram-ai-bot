import gspread
from google.oauth2.service_account import Credentials
import os
import logging

logger = logging.getLogger(__name__)

# Область доступа для Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

class GoogleSheetsManager:
    """Менеджер для работы с Google Sheets"""
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        """
        Инициализация менеджера Google Sheets
        
        Args:
            credentials_file: Путь к JSON файлу с credentials
            spreadsheet_id: ID таблицы Google Sheets
        """
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        
    def connect(self):
        """Подключение к Google Sheets API"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info(f"Успешное подключение к Google Sheets: {self.spreadsheet.title}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {e}")
            return False
    
    def get_system_prompt(self, worksheet_name: str = "Настройки") -> str:
        """
        Получение системного промпта из таблицы
        
        Args:
            worksheet_name: Название листа в таблице
            
        Returns:
            Текст системного промпта
        """
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            
            # Ожидается, что промпт находится в ячейке B2
            # A1: "System Prompt", B1: значение
            prompt = worksheet.acell('B1').value
            
            if prompt:
                logger.info("Системный промпт успешно загружен из Google Sheets")
                return prompt
            else:
                logger.warning("Промпт пуст, используется значение по умолчанию")
                return "Ты helpful AI-ассистент. Отвечай на русском языке кратко и по делу."
                
        except Exception as e:
            logger.error(f"Ошибка при чтении промпта из Google Sheets: {e}")
            return "Ты helpful AI-ассистент. Отвечай на русском языке кратко и по делу."
    
    def get_bot_settings(self, worksheet_name: str = "Настройки") -> dict:
        """
        Получение всех настроек бота из таблицы
        
        Args:
            worksheet_name: Название листа в таблице
            
        Returns:
            Словарь с настройками
        """
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            
            # Читаем все данные из первых двух колонок
            # Формат: A - название параметра, B - значение
            values = worksheet.get_all_values()
            
            settings = {}
            for row in values:
                if len(row) >= 2 and row[0] and row[1]:
                    settings[row[0]] = row[1]
            
            logger.info(f"Загружено настроек из Google Sheets: {len(settings)}")
            return settings
            
        except Exception as e:
            logger.error(f"Ошибка при чтении настроек из Google Sheets: {e}")
            return {}
    
    def get_ai_parameters(self, worksheet_name: str = "Настройки") -> dict:
        """
        Получение параметров для AI (temperature, model и т.д.)
        
        Args:
            worksheet_name: Название листа в таблице
            
        Returns:
            Словарь с параметрами AI
        """
        try:
            settings = self.get_bot_settings(worksheet_name)
            
            # Параметры по умолчанию
            default_params = {
                'model': 'grok-beta',
                'temperature': 0.7,
                'max_tokens': 1000
            }
            
            # Обновляем параметры из таблицы, если они есть
            ai_params = {}
            if 'AI_Model' in settings:
                ai_params['model'] = settings['AI_Model']
            if 'AI_Temperature' in settings:
                try:
                    ai_params['temperature'] = float(settings['AI_Temperature'])
                except ValueError:
                    pass
            if 'AI_MaxTokens' in settings:
                try:
                    ai_params['max_tokens'] = int(settings['AI_MaxTokens'])
                except ValueError:
                    pass
            
            # Объединяем с defaults
            return {**default_params, **ai_params}
            
        except Exception as e:
            logger.error(f"Ошибка при чтении параметров AI: {e}")
            return {
                'model': 'grok-beta',
                'temperature': 0.7,
                'max_tokens': 1000
            }


# Глобальный экземпляр менеджера
_sheets_manager = None

def init_sheets_manager(credentials_file: str, spreadsheet_id: str) -> GoogleSheetsManager:
    """Инициализация глобального менеджера Google Sheets"""
    global _sheets_manager
    _sheets_manager = GoogleSheetsManager(credentials_file, spreadsheet_id)
    if _sheets_manager.connect():
        return _sheets_manager
    return None

def get_sheets_manager() -> GoogleSheetsManager:
    """Получение глобального менеджера Google Sheets"""
    return _sheets_manager
