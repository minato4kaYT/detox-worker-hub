

MODELS_DATABASE = [
    {
        'id': 1,
        'name': 'Виктория',
        'age': 22,
        'city': 'Москва',
        'rating': 4.9,
        'reviews': 127,
        'price': '3000₽/ч',
        'bio': '💎 Премиум сервис\n🌟 Опыт работы 4+ года\n✨ Все виды услуг\n🎭 Любые фантазии',
        'availability': '24/7',
        'services': ['Встречи', 'Выезд', 'Шоу программа']
    },
    {
        'id': 2,
        'name': 'Анна',
        'age': 20,
        'city': 'Москва',
        'rating': 4.8,
        'reviews': 93,
        'price': '2500₽/ч',
        'bio': '👑 Молодая красавица\n💃 Энергичная и веселая\n🎉 VIP развлечения\n📸 Любит камеру',
        'availability': '16:00-06:00',
        'services': ['Встречи', 'Компания', 'Фотосессии']
    },
    {
        'id': 3,
        'name': 'Элена',
        'age': 25,
        'city': 'СПб',
        'rating': 5.0,
        'reviews': 156,
        'price': '3500₽/ч',
        'bio': '👸 Элегантная деловая леди\n💼 Встречи с бизнесменами\n🍾 Высокий уровень\n🎨 Интеллигентная',
        'availability': '24/7',
        'services': ['Бизнес встречи', 'Ужины', 'События']
    },
    {
        'id': 4,
        'name': 'Дарья',
        'age': 23,
        'city': 'Москва',
        'rating': 4.7,
        'reviews': 81,
        'price': '2800₽/ч',
        'bio': '🔥 Горячая латинка\n💃 Танцовщица\n🌺 Экзотическая красота\n⚡ Очень сексуальная',
        'availability': '18:00-05:00',
        'services': ['Встречи', 'Шоу', 'Развлечения']
    },
    {
        'id': 5,
        'name': 'Кристина',
        'age': 21,
        'city': 'Москва',
        'rating': 4.9,
        'reviews': 112,
        'price': '2700₽/ч',
        'bio': '✨ Нежная и ласковая\n🌸 Очень послушная\n💋 Любит целоваться\n🎀 Домашняя девочка',
        'availability': '20:00-08:00',
        'services': ['Встречи', 'Нежные услуги', 'Компания']
    },
    {
        'id': 6,
        'name': 'Маша',
        'age': 19,
        'city': 'Москва',
        'rating': 4.8,
        'reviews': 76,
        'price': '2400₽/ч',
        'bio': '👧 Совсем молодая\n🎓 Студентка\n😊 Веселая и наивная\n💕 Первый раз в деле',
        'availability': '17:00-02:00',
        'services': ['Встречи', 'Обучение', 'Первый опыт']
    },
    {
        'id': 7,
        'name': 'Наталья',
        'age': 28,
        'city': 'Москва',
        'rating': 4.9,
        'reviews': 203,
        'price': '4000₽/ч',
        'bio': '👠 Зрелая королева\n💎 Премиум+ класс\n🔞 Без табу\n👑 Доминирует',
        'availability': '24/7',
        'services': ['BDSM', 'Доминирование', 'VIP услуги']
    },
    {
        'id': 8,
        'name': 'Софья',
        'age': 24,
        'city': 'СПб',
        'rating': 4.8,
        'reviews': 98,
        'price': '3000₽/ч',
        'bio': '🧿 Мистическая красавица\n🔮 Эзотерика\n🕯️ Интересные игры\n✨ Магия тела',
        'availability': '14:00-04:00',
        'services': ['Встречи', 'Игры', 'Фантазии']
    },
    {
        'id': 9,
        'name': 'Карина',
        'age': 26,
        'city': 'Москва',
        'rating': 4.7,
        'reviews': 145,
        'price': '3200₽/ч',
        'bio': '💪 Спортивная красотка\n🏃 Фитнес модель\n🔥 Сексуальная фигура\n⚽ Активная',
        'availability': '18:00-06:00',
        'services': ['Встречи', 'Массаж', 'Спортивные игры']
    },
    {
        'id': 10,
        'name': 'Алина',
        'age': 20,
        'city': 'Москва',
        'rating': 4.9,
        'reviews': 134,
        'price': '2600₽/ч',
        'bio': '😇 Ангелочек\n👼 Невинный взгляд\n💋 А опытная в постели\n🎀 Русская красавица',
        'availability': '19:00-07:00',
        'services': ['Встречи', 'Компания', 'Развлечения']
    }
]

def get_all_models():

    return MODELS_DATABASE

def get_model_by_id(model_id):

    for model in MODELS_DATABASE:
        if model['id'] == model_id:
            return model
    return None

def get_vip_models():

    return [m for m in MODELS_DATABASE if m['rating'] >= 4.8]

def get_models_by_city(city):

    return [m for m in MODELS_DATABASE if m['city'] == city]
