"""
Скрипт для просмотра статистики использования бота
"""
import database
from datetime import datetime


def print_statistics():
    """Вывод статистики в консоль"""
    stats = database.get_statistics()
    
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА TELEGRAM-БОТА")
    print("="*60)
    
    print(f"\n👥 Всего пользователей: {stats['total_users']}")
    
    print("\n📈 Статистика действий:")
    print("-" * 60)
    if stats['actions_stats']:
        total_actions = sum(count for _, count in stats['actions_stats'])
        for action_type, count in stats['actions_stats']:
            action_names = {
                'start': '🚀 Команда /start',
                'button_about': '📌 Кнопка "О нас"',
                'button_cases': '💼 Кнопка "Кейсы"'
            }
            action_name = action_names.get(action_type, action_type)
            percentage = (count / total_actions * 100) if total_actions > 0 else 0
            print(f"  {action_name}: {count} раз ({percentage:.1f}%)")
        print(f"\n  ✅ Всего действий: {total_actions}")
    else:
        print("  Пока нет записанных действий")
    
    print("\n🏆 ТОП-10 активных пользователей:")
    print("-" * 60)
    if stats['top_users']:
        for i, (user_id, first_name, username, action_count) in enumerate(stats['top_users'], 1):
            username_str = f"@{username}" if username else "без username"
            print(f"  {i}. {first_name} ({username_str})")
            print(f"     ID: {user_id}, Действий: {action_count}")
    else:
        print("  Пока нет пользователей")
    
    print("\n" + "="*60)
    print(f"📅 Отчет сформирован: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        print_statistics()
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
        print("Убедитесь, что бот был запущен хотя бы один раз для создания БД.")
